#!/usr/bin/env python3
import subprocess
import json
import os
import sys

def harvest_emails(domain, sources=None, limit=500):
    """Run theHarvester and return list of dict records."""
    venv_activate = os.path.expanduser("~/osint-venv/bin/activate")
    src = sources or ["duckduckgo"]  # default to a source that works without API key
    # Use JSON output mode
    cmd_str = f"source {venv_activate} && theHarvester -d {domain} -b {','.join(src)} -l {limit} -f -"
    proc = subprocess.run(["bash", "-c", cmd_str], capture_output=True, text=True, check=False)
    output = proc.stdout
    # Find the JSON part (last line that looks like a JSON object)
    json_str = None
    for line in reversed(output.splitlines()):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            json_str = line
            break
    if not json_str:
        # fallback: maybe the whole output is JSON if no banner? try whole output
        json_str = output.strip()
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        # If still fails, return empty list
        return []
    emails = []
    for entry in data.get('emails', []):
        # entry can be a string or dict depending on version
        if isinstance(entry, str):
            email = entry
            src_used = ",".join(src)
            fullname = None
            role = None
        elif isinstance(entry, dict):
            email = (entry.get('email') or entry.get('mail') or '').strip()
            src_used = (entry.get('source') or ",".join(src)).strip()
            first = (entry.get('first_name') or '').strip()
            last = (entry.get('last_name') or '').strip()
            if first and last:
                fullname = f"{first} {last}"
            elif first:
                fullname = first
            elif last:
                fullname = last
            else:
                fullname = None
            role = (entry.get('role') or '').strip() or None
        else:
            continue
        if email and email not in [e['email'] for e in emails]:
            emails.append({
                "email": email,
                "source": src_used,
                "fullname": fullname if fullname else None,
                "role": role if role else None
            })
    return emails

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: harvest_emails.py <domain> [sources] [limit]")
        sys.exit(1)
    domain = sys.argv[1]
    sources = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 500
    print(json.dumps(harvest_emails(domain, sources, limit), indent=2))