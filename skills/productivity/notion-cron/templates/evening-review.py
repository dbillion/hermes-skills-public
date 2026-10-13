#!/usr/bin/env python3
"""Evening review from Notion — run via cron or manually.

Reads task databases, categorizes items by status, and outputs
a concise evening review with wins, blockers, tomorrow's agenda,
and top 3 priorities.

Usage:
  1. Set NOTION_TOKEN env var or extract from ~/.mcp_servers.json
  2. Run: python3 evening-review.py

Requires: requests (or use urllib for zero-dep cron)
"""

import json
import os
import subprocess
from datetime import datetime, timedelta

# ─── Config ───────────────────────────────────────────────────────
NOTION_VERSION = "2022-06-28"

# Token: prefer env var, else extract from mcp_servers.json
def get_token():
    token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if token:
        return token
    # Fallback: read from mcp_servers.json
    config_path = os.path.expanduser("~/.mcp_servers.json")
    if os.path.exists(config_path):
        c = json.load(open(config_path))
        return c["mcpServers"]["notion"]["env"]["NOTION_TOKEN"]
    raise RuntimeError("No Notion token found. Set NOTION_TOKEN or configure ~/.mcp_servers.json")

def notion_search(token, query):
    """Search Notion pages/databases by title."""
    import urllib.request
    req = urllib.request.Request(
        "https://api.notion.com/v1/search",
        data=json.dumps({"query": query}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def notion_query_db(token, database_id, filter_payload=None):
    """Query a Notion database."""
    import urllib.request
    body = {}
    if filter_payload:
        body["filter"] = filter_payload
    req = urllib.request.Request(
        f"https://api.notion.com/v1/databases/{database_id}/query",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def extract_title(props):
    for k, v in props.items():
        if v.get("type") == "title":
            text = "".join(t.get("plain_text", "") for t in v.get("title", []))
            return text if text.strip() else "(untitled)"
    return "(untitled)"

def extract_status(props):
    for k, v in props.items():
        if v.get("type") == "status":
            return v.get("status", {}).get("name", "")
        if v.get("type") == "select":
            return (v.get("select") or {}).get("name", "")
        if v.get("type") == "checkbox":
            return "Done" if v.get("checkbox") else ""
    return ""

def extract_date(props):
    for k, v in props.items():
        if v.get("type") == "date" and v.get("date"):
            return v["date"].get("start", "")
    return ""

def extract_category(props):
    for k, v in props.items():
        if v.get("type") == "select" and v.get("select"):
            return v["select"].get("name", "")
        if v.get("type") == "multi_select":
            return ", ".join(s.get("name", "") for s in v.get("multi_select", []))
    return ""

def extract_block_text(block):
    """Extract readable text from a block. Returns '' for empty template placeholders."""
    btype = block.get("type", "")
    rt = block.get(btype, {}).get("rich_text", [])
    if not rt:
        return ""  # Empty placeholder — not real content
    return "".join(t.get("plain_text", "") for t in rt)

def get_block_children(token, block_id):
    """Fetch children of a block (for nested callouts, toggles, etc.)."""
    import urllib.request
    req = urllib.request.Request(
        f"https://api.notion.com/v1/blocks/{block_id}/children",
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read()).get("results", [])

# ─── Main ─────────────────────────────────────────────────────────
def main():
    token = get_token()
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    # Search for task databases
    # Replace these IDs with your actual database IDs after first run
    # Use notion_search(token, "tasks") to discover them
    DB_IDS = os.environ.get("NOTION_TASK_DBS", "").split(",")

    completed = []
    in_progress = []
    blocked = []
    to_do = []

    for db_id in DB_IDS:
        if not db_id.strip():
            continue
        try:
            result = notion_query_db(token, db_id.strip())
            for r in result.get("results", []):
                if r.get("object") != "page":
                    continue
                props = r.get("properties", {})
                name = extract_title(props)
                status = extract_status(props)
                cat = extract_category(props)
                date = extract_date(props)

                entry = name
                if cat:
                    entry += f" [{cat}]"

                sl = status.lower()
                if sl in ("done", "completed", "complete", "finished"):
                    completed.append(entry)
                elif sl in ("blocked", "stuck", "quality check"):
                    blocked.append(entry)
                elif sl in ("doing", "in progress", "in-progress"):
                    in_progress.append(entry)
                else:
                    to_do.append(entry)
        except Exception as e:
            blocked.append(f"(query error for {db_id[:8]}...: {e})")

    # ─── Output ───────────────────────────────────────────────────
    print(f"🌙 Evening Review — {today.strftime('%B %d, %Y')}")
    print()
    print("✅ Today's Wins")
    if completed:
        for w in completed:
            print(f"- {w}")
    elif in_progress:
        print(f"- Made progress on: {', '.join(in_progress)}")
    else:
        print("No completed tasks logged")
    print()

    print("🚧 Blockers")
    if blocked:
        for b in blocked:
            print(f"- {b}")
    else:
        print("None")
    print()

    print(f"📅 Tomorrow's Agenda ({tomorrow.strftime('%A')})")
    agenda = [f"Continue: {i}" for i in in_progress] + to_do
    if agenda:
        for a in agenda[:8]:
            print(f"- {a}")
    else:
        print("Nothing scheduled")
    print()

    print("🎯 Top 3 for Tomorrow")
    top3 = []
    # Priority: in-progress → to-do
    for i in in_progress:
        if len(top3) < 3:
            top3.append(i)
    for t in to_do:
        if len(top3) < 3:
            top3.append(t)
    for idx, t in enumerate(top3, 1):
        print(f"{idx}. {t}")

if __name__ == "__main__":
    main()
