#!/usr/bin/env python3
import subprocess
import json
import os
import sys

def hunt_username(username, sites=None, timeout=30):
    """Run sherlock and return list of dict results."""
    venv_activate = os.path.expanduser("~/osint-venv/bin/activate")
    # Build sherlock command: sherlock <username> [--site <site> ...] --print-found
    cmd_parts = ["sherlock", username]
    if sites:
        for s in sites:
            cmd_parts.extend(["--site", s])
    cmd_parts.append("--print-found")
    cmd = [
        "bash", "-c",
        f"source {venv_activate} && {' '.join(cmd_parts)}"
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        # Return partial results if any captured? For simplicity, return empty list with error flag?
        return [{"error": "timeout", "username": username}]
    # sherlock output lines like: [+] twitter: https://twitter.com/username
    results = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("[+]"):
            # format: [+] <site>: <url>
            try:
                rest = line[3:].strip()
                if ": " in rest:
                    site, url = rest.split(": ", 1)
                else:
                    # fallback
                    site = rest.split()[0] if rest else "unknown"
                    url = rest
                results.append({
                    "site": site.strip(),
                    "url_exists": True,
                    "url": url.strip()
                })
            except Exception:
                # ignore malformed line
                pass
    # Also detect negatives? sherlock prints [-] site: ... maybe we ignore.
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: hunt_username.py <username> [site1,site2,...] [timeout]")
        sys.exit(1)
    username = sys.argv[1]
    sites = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    print(json.dumps(hunt_username(username, sites, timeout), indent=2))