#!/usr/bin/env python3
"""
jobhunt-outreach.template.py — TEMPLATE outreach engine (copy + fill paths).
Collect (Exa) -> find contact -> draft -> dry-run -> send -> log to Sheet.

Fill in: SCOPE, SHEET_ID, MCP_CLI, GWS, NODE, and CANDIDATE (your real projects).
Safety: never fabricate emails; reject aggregator domains; dry-run gate; real sends
only when JOBHUNT_LIVE=1.
"""
import json, os, re, subprocess, sys, datetime

# --- FILL THESE ---
SCOPE = "/home/deeone/.hermes/scripts/jobhunt-mcp-scope.json"
SHEET_ID = "REPLACE_WITH_SPREADSHEET_ID"
MCP_CLI = "/home/deeone/.local/bin/mcp-cli"
GWS = "/home/deeone/.nvm/versions/node/v25.6.1/lib/node_modules/@googleworkspace/cli/run-gws.js"
NODE = "/home/deeone/.nvm/versions/node/v25.6.1/bin"
ENV = dict(os.environ, PATH=f"{NODE}:{os.environ.get('HOME','/home/deeone')}/.local/bin:/usr/local/bin:/usr/bin:/bin")

CANDIDATE = {
    "name": "YOUR NAME",
    "email": "you@example.com",
    "projects": [
        ("Project A", "https://...", "one-line description"),
        ("Project B", "https://...", "one-line description"),
    ],
    "value": ["value prop 1", "value prop 2", "value prop 3"],
}

AGGREGATOR_DOMAINS = {
    "jobgether.com", "hiretik.com", "remoterocketship.com", "remote.com", "jobera.com",
    "linkedin.com", "indeed.com", "glassdoor.com", "greenhouse.io", "lever.co",
    "ashbyhq.com", "workable.com", "breezy.hr", "wellfound.com",
}
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

def run(cmd, timeout=90):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=ENV)
    except subprocess.TimeoutExpired:
        return None

def exa_search(query, n=8):
    out = run([MCP_CLI, "-c", SCOPE, "call", "exa", "web_search_exa",
               json.dumps({"query": query, "numResults": n})], 70)
    if not out or out.returncode != 0:
        return ""
    try:
        data = json.loads(out.stdout)
        return " ".join(b.get("text", "") for b in data.get("content", []) if isinstance(b, dict))
    except Exception:
        return out.stdout

def extract_leads(text):
    leads = []
    for p in re.split(r"(?i)\n\s*Title:\s*", text)[1:]:
        title = p.strip().splitlines()[0].strip()
        url_m = re.search(r"(?i)URL:\s*(\S+)", p) or re.search(r"https?://\S+", p)
        if not url_m:
            continue
        link = url_m.group(1).rstrip(")")
        m = re.search(r"\bat\s+([A-Za-z0-9&.]+(?:\s+[A-Za-z0-9&.]+)*?)(?:\s*[|\-–]|@|$)", title)
        company = m.group(1).strip() if m else ""
        if not company:
            m2 = re.search(r"^([A-Za-z0-9&.]+(?:\s+[A-Za-z0-9&.]+)*?)\s*[|–-]\s", title)
            company = m2.group(1).strip() if m2 else ""
        leads.append({"title": title, "company": company, "location": "", "link": link})
    seen, uniq = set(), []
    for l in leads:
        if l["link"] not in seen:
            seen.add(l["link"]); uniq.append(l)
    return uniq[:8]

def find_contact(lead, full_text):
    for e in EMAIL_RE.findall(full_text):
        dom = e.split("@")[-1].lower()
        if any(x in dom for x in ["linkedin", "example", "noreply"]) or dom in AGGREGATOR_DOMAINS:
            continue
        return e, "found"
    m = re.search(r"https?://(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})", lead["link"])
    if m:
        dom = m.group(1).lower()
        if dom not in AGGREGATOR_DOMAINS and "job" not in dom and "career" not in dom:
            return f"careers@{dom}", "guessed"
    return None, None

def draft_email(lead, contact, source):
    proj = "\n".join(f"- {n}: {url} — {d}" for n, url, d in CANDIDATE["projects"])
    val = "\n".join(f"- {v}" for v in CANDIDATE["value"])
    subject = f"Java/AI backend engineer — {CANDIDATE['name']} (built {CANDIDATE['projects'][0][0]})"
    body = f"""Hi {lead['company'] or 'hiring team'},

I'm {CANDIDATE['name']}, a backend engineer. Saw your opening ({lead['title']}).

What I've shipped:
{proj}

Why useful here:
{val}

If this isn't the right inbox, point me to the hiring manager — happy to forward.
Portfolio: {CANDIDATE['projects'][0][1]}
Email: {CANDIDATE['email']}

Thanks,
{CANDIDATE['name']}
"""
    return subject, body

def send_email(to, subject, body, dry=True):
    cmd = [NODE, GWS, "gmail", "+send", "--to", to, "--subject", subject, "--body", body]
    if dry:
        cmd.append("--dry-run")
    return run(cmd, 60)

def append_row(row):
    vals = json.dumps({"values": [row]})
    return run([NODE, GWS, "sheets", "spreadsheets", "values", "append",
                "--params", json.dumps({"spreadsheetId": SHEET_ID, "range": "Outreach!A:J", "valueInputOption": "RAW"}),
                "--json", vals], 60)

def main():
    LIVE = os.environ.get("JOBHUNT_LIVE") == "1"
    today = datetime.date.today().isoformat()
    print(f"## Outreach — {today}" + ("" if LIVE else "  [DRY-RUN]") + "\n")
    text = exa_search("Java AI backend engineer jobs Canada remote hiring 2026", 8)
    if not text:
        print("_No Exa results._"); return
    leads = extract_leads(text)
    for lead in leads:
        contact, source = find_contact(lead, text)
        if not contact:
            append_row([today, lead["title"], lead["company"], lead["location"], lead["link"], "", "none", "needs_contact", "", today])
            print(f"- [needs_contact] {lead['title']} @ {lead['company']}")
            continue
        subject, body = draft_email(lead, contact, source)
        if not send_email(contact, subject, body, dry=True).returncode == 0:
            append_row([today, lead["title"], lead["company"], lead["location"], lead["link"], contact, source, "dryrun_fail", subject, today])
            continue
        status = "dryrun_ok"
        if LIVE and send_email(contact, subject, body, dry=False).returncode == 0:
            status = "sent"
        append_row([today, lead["title"], lead["company"], lead["location"], lead["link"], contact, source, status, subject, today])
        print(f"- [{status}] {lead['title']} @ {lead['company']} -> {contact}")

if __name__ == "__main__":
    main()
