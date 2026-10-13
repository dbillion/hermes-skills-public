#!/usr/bin/env python3
"""
jobhunt-track.template.py — TEMPLATE response tracker (copy + fill paths).
Read-only on Gmail. Scans +triage, matches reply From-domains to sent domains,
marks rows responded / successful / bounced in the Outreach tab.

Fill in: SHEET_ID, GWS, NODE.
"""
import json, os, re, subprocess, datetime

SHEET_ID = "REPLACE_WITH_SPREADSHEET_ID"
GWS = "/home/deeone/.nvm/versions/node/v25.6.1/lib/node_modules/@googleworkspace/cli/run-gws.js"
NODE = "/home/deeone/.nvm/versions/node/v25.6.1/bin"
ENV = dict(os.environ, PATH=f"{NODE}:{os.environ.get('HOME','/home/deeone')}/.local/bin:/usr/local/bin:/usr/bin:/bin")
POS_KEYWORDS = ["interview", "application", "offer", "phone screen", "next step", "coding challenge"]

def run(cmd, timeout=90):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=ENV)
    except subprocess.TimeoutExpired:
        return None

def read_outreach():
    r = run([NODE, GWS, "sheets", "+read", "--spreadsheet", SHEET_ID, "--range", "Outreach!A2:J"], 60)
    if not r or r.returncode != 0:
        return []
    try:
        return json.loads(r.stdout).get("values", [])
    except Exception:
        return []

def update_status(row_idx, status):
    sheet_row = row_idx + 2
    today = datetime.date.today().isoformat()
    run([NODE, GWS, "sheets", "spreadsheets", "values", "update",
         "--params", json.dumps({"spreadsheetId": SHEET_ID, "range": f"Outreach!H{sheet_row}:J{sheet_row}", "valueInputOption": "RAW"}),
         "--json", {"values": [[status, "", today]]}], 60)

def main():
    rows = read_outreach()
    if not rows:
        print("_No rows._"); return
    sent_domains = {row[5].split("@")[-1].lower() for row in rows if len(row) > 5 and "@" in row[5]}
    t = run([NODE, GWS, "gmail", "+triage"], 60)
    if not t or t.returncode != 0:
        print("_triage failed._"); return
    responded = bounced = 0
    for line in t.stdout.splitlines()[2:]:
        low = line.lower()
        if "mailer-daemon" in low:
            bounced += 1; continue
        from_dom = re.search(r"@([a-z0-9.-]+\.[a-z]{2,})", low)
        if not from_dom or from_dom.group(1) not in sent_domains:
            continue
        dom = from_dom.group(1)
        for i, row in enumerate(rows):
            if len(row) > 5 and row[5] and row[5].split("@")[-1].lower() == dom:
                status = "successful" if any(k in low for k in POS_KEYWORDS) else "responded"
                update_status(i, status); responded += 1; break
    print(f"Bounced: {bounced} | Responded: {responded}. Tab updated.")

if __name__ == "__main__":
    main()
