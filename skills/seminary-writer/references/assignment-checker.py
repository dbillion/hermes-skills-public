#!/usr/bin/env python3
"""
Reliable script to check seminary assignments in Notion.
Handles MCP fallback, proper JSON parsing, and cron limitations.
Based on lessons learned from real-world usage.

Usage: python3 assignment-checker.py
Outputs formatted assignment check results to stdout.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta


def get_notion_token():
    """Extract NOTION_TOKEN from ~/.mcp_servers.json."""
    try:
        with open(os.path.expanduser("~/.mcp_servers.json"), "r") as f:
            data = json.load(f)
    except Exception:
        data = {}
    notion_config = data.get("mcpServers", {}).get("notion", {})
    env = notion_config.get("env", {})
    token = env.get("NOTION_TOKEN")
    if token:
        return token
    # Fallback to environment variable
    token = os.environ.get("NOTION_TOKEN")
    if token:
        return token
    return None


def mcp_call(tool, args, max_attempts=2):
    """Call mcp-cli notion <tool> '<json_args>' and return parsed inner JSON.
    Retries on failure up to max_attempts."""
    cmd = ['mcp-cli', 'call', 'notion', tool, json.dumps(args)]
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                if attempt == max_attempts - 1:
                    return None  # MCP call failed after retries
                continue  # retry
            output = result.stdout.strip()
            # Parse MCP response (outer JSON)
            try:
                outer = json.loads(output)
            except json.JSONDecodeError:
                if attempt == max_attempts - 1:
                    return None
                continue
            # Extract inner JSON from content[0].text
            content = outer.get('content')
            if not content or len(content) == 0:
                if attempt == max_attempts - 1:
                    return None
                continue
            text = content[0].get('text', '')
            if not text:
                if attempt == max_attempts - 1:
                    return None
                continue
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                if attempt == max_attempts - 1:
                    return None
                continue
        except subprocess.TimeoutExpired:
            if attempt == max_attempts - 1:
                return None
            continue
        except Exception:
            if attempt == max_attempts - 1:
                return None
            continue
    return None


def curl_request(method, endpoint, data=None, max_attempts=2):
    """Make direct curl request to Notion API.
    Retries on failure up to max_attempts."""
    token = get_notion_token()
    if not token:
        return None
    url = f"https://api.notion.com/v1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    import json as json_module
    cmd = ["curl", "-s", "-X", method, url]
    for h_key, h_val in headers.items():
        cmd.extend(["-H", f"{h_key}: {h_val}"])
    if data is not None:
        cmd.extend(["-d", json_module.dumps(data)])
    for attempt in range(max_attempts):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                if attempt == max_attempts - 1:
                    return None
                continue
            return json_module.loads(result.stdout)
        except Exception:
            if attempt == max_attempts - 1:
                return None
            continue
    return None


def extract_title(properties):
    """Extract title from properties by type."""
    for prop in properties.values():
        if prop.get('type') == 'title':
            title_arr = prop.get('title', [])
            if title_arr:
                return title_arr[0].get('text', {}).get('content', '')
    return ''


def extract_due_date(properties):
    """Extract due date from properties by type."""
    for prop in properties.values():
        if prop.get('type') == 'date':
            date_obj = prop.get('date')
            if date_obj:
                return date_obj.get('start')
    return None


def extract_status(properties):
    """Extract status from properties by type."""
    for prop in properties.values():
        ptype = prop.get('type')
        if ptype == 'select':
            select_obj = prop.get('select')
            if select_obj:
                return select_obj.get('name', 'Not Started')
        elif ptype == 'status':
            status_obj = prop.get('status')
            if status_obj:
                return status_obj.get('name', 'Not Started')
        elif ptype == 'checkbox' and prop.get('checkbox') is True:
            # Treat checked checkbox as 'Done' status
            return 'Done'
    return 'Not Started'


def main():
    """Main function to check assignments and print formatted results."""
    token = get_notion_token()
    if not token:
        print("ERROR: NOTION_TOKEN not found", file=sys.stderr)
        # Still output the expected format but with empty results
        print("📝 Seminary Writing Check")
        print()
        print("📚 Active Assignments")
        print("(No assignments found)")
        print()
        print("🔜 Upcoming Deadlines (next 7 days)")
        print("(No upcoming deadlines)")
        print()
        print("💡 Suggested Action")
        print("Consider creating a writing tracker database in Notion.")
        return

    today = datetime.today().date()
    week_later = today + timedelta(days=7)

    # Search terms to try
    search_terms = ["assignment", "paper", "essay", "exegesis"]
    all_results = []

    # Try MCP first for each term
    for term in search_terms:
        mcp_res = mcp_call("API-post-search", {"query": term})
        # Check for MCP silent failure: result is None or empty results
        if mcp_res is None or not mcp_res.get('results'):
            # Fall back to curl for this term
            curl_res = curl_request("POST", "search", {"query": term})
            if curl_res and "results" in curl_res:
                all_results.extend(curl_res["results"])
        else:
            all_results.extend(mcp_res.get("results", []))

    # Deduplicate by ID
    seen_ids = set()
    unique_results = []
    for res in all_results:
        rid = res.get('id')
        if rid and rid not in seen_ids:
            seen_ids.add(rid)
            unique_results.append(res)

    # Process results to get pages
    pages = []  # each will be dict with title, due_date, status
    for res in unique_results:
        obj = res.get('object')
        if obj == 'page':
            page_id = res.get('id')
            # Try MCP first
            page_data = mcp_call("API-retrieve-a-page", {"page_id": page_id})
            if page_data is None:
                # Fall back to curl
                page_data = curl_request("GET", f"pages/{page_id}")
            if page_data:
                props = page_data.get('properties', {})
                pages.append({
                    'title': extract_title(props),
                    'due_date': extract_due_date(props),
                    'status': extract_status(props)
                })
        elif obj == 'database':
            db_id = res.get('id')
            # Try MCP first (note: API-query-data-source reads from stdin in MCP)
            query_res = mcp_call('API-query-data-source', {'data_source_id': db_id, 'page_size': 100})
            if query_res is None:
                # Fall back to curl
                query_res = curl_request("POST", f"databases/{db_id}/query", {"page_size": 100})
            if query_res and "results" in query_res:
                for page in query_res["results"]:
                    props = page.get('properties', {})
                    pages.append({
                        'title': extract_title(props),
                        'due_date': extract_due_date(props),
                        'status': extract_status(props)
                    })

    # Filter and process pages
    done_statuses = {"Done", "Completed", "Finished", "Closed", "Archived", "Submitted", "Mark received"}
    active = []  # (title, due_date_str, status)
    upcoming = []  # (title, due_date_str, status)

    for p in pages:
        title = p['title']
        due_date_str = p['due_date']
        status = p['status']

        if not title or not due_date_str:
            continue

        # Process due_date string
        try:
            if "T" in due_date_str:
                due_date_str = due_date_str.split("T")[0]
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        # Skip if past due
        if due_date < today:
            continue

        # Skip if status indicates completion
        if status in done_statuses:
            continue

        active.append((title, due_date_str, status))
        if due_date <= week_later:
            upcoming.append((title, due_date_str, status))

    # Deduplicate by (title, due_date)
    def dedupe(lst):
        seen = set()
        res = []
        for t, d, s in lst:
            key = (t, d)
            if key not in seen:
                seen.add(key)
                res.append((t, d, s))
        return res

    active = dedupe(active)
    upcoming = dedupe(upcoming)

    # Sort upcoming by date
    upcoming.sort(key=lambda x: x[1])

    # Output formatted results
    print("📝 Seminary Writing Check")
    print()
    print("📚 Active Assignments")
    if active:
        for title, due_date, status in active:
            print(f"- [{title}] — due {due_date} — {status}")
    else:
        print("(No assignments found)")
    print()
    print("🔜 Upcoming Deadlines (next 7 days)")
    if upcoming:
        for title, due_date, status in upcoming:
            print(f"- {due_date}: {title}")
    else:
        print("(No upcoming deadlines)")
    print()
    print("💡 Suggested Action")
    if active:
        # Sort by due date ascending
        active_sorted = sorted(active, key=lambda x: x[1])
        title, due_date, _ = active_sorted[0]
        print(f"Work on '{title}' (due {due_date})")
    else:
        print("Consider creating a writing tracker database in Notion.")


if __name__ == "__main__":
    main()