---
name: osint-toolkit
description: |
  A thin Hermes wrapper around popular open-source OSINT CLIs:
  • theHarvester – e‑mail/sub‑domain harvesting
  • sherlock     – username hunting across social networks
  • phoneinfoga  – phone‑number reconnaissance
  Exposes three Python helper functions that can be called from
  `execute_code`, `delegate_task`, or via `mcp-cli`.
version: "0.1.0"
author: "Hermes Assistant"
tags: [osint, reconnaissance, email, username, phone]
---

## Setup

This skill assumes you have a Python virtual environment managed by `uv` at `$HOME/osint-venv`. The setup steps are:

1. Create the virtual environment:
   ```bash
   uv venv $HOME/osint-venv
   source $HOME/osint-venv/bin/activate
   ```
2. Install theHarvester:
   ```bash
   git clone https://github.com/laramies/theHarvester.git $HOME/osint-venv/src/theHarvester
   cd $HOME/osint-venv/src/theHarvester
   uv pip install -e .
   ```
3. Install sherlock:
   ```bash
   git clone https://github.com/sherlock-project/sherlock.git $HOME/osint-venv/src/sherlock
   cd $HOME/osint-venv/src/sherlock
   uv pip install -e .
   ```
4. Install phoneinfoga (binary):
   ```bash
   # Get latest release URL from GitHub API
   URL=$(curl -s https://api.github.com/repos/sundowndev/phoneinfoga/releases/latest | jq -r '.assets[] | select(.name | contains("Linux_x86_64")) | .browser_download_url')
   wget -q $URL -O phoneinfoga.tar.gz
   tar xzf phoneinfoga.tar.gz
   sudo mv phoneinfoga /usr/local/bin/
   sudo chmod +x /usr/local/bin/phoneinfoga
   ```

After these steps, the helper scripts in this skill will automatically activate the venv before invoking the CLIs.

# OSINT Toolkit Skill

## Provided functions (import via `from hermes_tools import ...`)

| Function | CLI wrapper | Returns |
|----------|-------------|---------|
| `harvest_emails(domain, sources=None, limit=500)` | `theHarvester -d <domain> -b <sources> -l <limit>` | List of dicts: `{email, source, fullname?, role?}` |
| `hunt_username(username, sites=None, timeout=60)` | `sherlock <username> [--site <site> ...]` | List of dicts: `{site, url_exists: true/false, url}` |
| `scan_phone(number, services=None)` | `phoneinfoga scan -n <number> [--services <svc>...]` | Dict with `{number, valid, carrier, line_type, reports}` |

All functions return pure Python objects (list/dict) that are automatically JSON‑serialisable by Hermes.

## Usage examples (from a Hermes agent)

```python
from hermes_tools import execute_code

# 1️⃣ Harvest e‑mails for a domain
emails = execute_code("""
from skills.osint-toolkit.scripts.harvest_emails import harvest_emails
result = harvest_emails('example.com', sources=['google','linkedin'], limit=200)
print(__import__('json').dumps(result, indent=2))
""")

# 2️⃣ Hunt a username across sites
usernames = execute_code("""
from skills.osint-toolkit.scripts.hunt_username import hunt_username
result = hunt_username('john_doe', sites=['twitter','github','reddit'])
print(__import__('json').dumps(result, indent=2))
""")

# 3️⃣ Scan a phone number
phone_info = execute_code("""
from skills.osint-toolkit.scripts.scan_phone import scan_phone
result = scan_phone('+1 555-123-4567')
print(__import__('json').dumps(result, indent=2))
""")
```

## How the scripts work

Each script lives under `scripts/` and simply:

1. Activates the shared OSINT virtual environment (`source $HOME/osint-venv/bin/activate`).
2. Calls the corresponding CLI via `subprocess.run(..., capture_output=True, text=True)`.
3. Parses the tool’s default output (JSON/CSV/plain‑text) into a clean Python structure.
4. Returns the structure (the `execute_code` wrapper prints the JSON to stdout, which Hermes captures).

You can inspect the source in the `scripts/` folder after installing the skill.