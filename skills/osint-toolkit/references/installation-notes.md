# OSINT Toolkit Installation Notes (Session-specific)

This document captures the exact steps taken during this session to get the OSINT tools working on an EndeavourOS host with Hermes.

## Prerequisites
- EndeavourOS (Arch-based) with `pacman`, `git`, `python`, `pip` (or `uv`).
- User has sudo rights.

## 1. Create a shared uv virtual environment
```bash
mkdir -p $HOME/osint-venv
cd $HOME
python3 -m venv osint-venv   # or: uv venv --seed
source $HOME/osint-venv/bin/activate
```

## 2. Install theHarvester
```bash
git clone https://github.com/laramies/theHarvester.git $HOME/osint-venv/src/theHarvester
cd $HOME/osint-venv/src/theHarvester
uv pip install -e .   # installs package in editable mode
# Additional deps needed for full functionality:
uv pip install ujson cffi greenlet playwright uvloop
```

## 3. Install Sherlock
```bash
git clone https://github.com/sherlock-project/sherlock.git $HOME/osint-venv/src/sherlock
cd $HOME/osint-venv/src/sherlock
uv pip install -e .
```

## 4. Install PhoneInfoga (binary)
```bash
# Get latest release URL via GitHub API (example for v2.11.0)
LATEST=$(curl -s https://api.github.com/repos/sundowndev/phoneinfoga/releases/latest | \
        jq -r '.assets[] | select(.name | contains("Linux_x86_64")) | .browser_download_url')
wget -q $LATEST -O phoneinfoga.tar.gz
tar xzf phoneinfoga.tar.gz
sudo mv phoneinfoga /usr/local/bin/
sudo chmod +x /usr/local/bin/phoneinfoga
rm phoneinfoga.tar.gz
```

## 5. Verify installations
```bash
source $HOME/osint-venv/bin/activate
theHarvester -h   # should show help
sherlock --version
phoneinfoga --version
```

## 6. Common issues & fixes observed
- **Missing `ujson`** → `uv pip install ujson`
- **Missing `_cffi_backend`** → `uv pip install cffi`
- **Missing `greenlet._greenlet`** → `uv pip install greenlet`
- **Missing `playwright` module** → `uv pip install playwright`
- **Missing `uvloop.loop`** → `uv pip install uvloop`
- **theHarvester reports “Invalid source” for google/bing** → use sources that work without API keys (e.g., `duckduckgo`).  
  Example: `theHarvester -d example.com -b duckduckgo -l 5 -f -`

## 7. Using the skill from Hermes
After placing the skill folder under `~/.hermes/skills/osint-toolkit`, the skill is automatically available.

Example calls from a Hermes agent:
```python
from hermes_tools import execute_code
emails = execute_code("""
from skills.osint-toolkit.scripts.harvest_emails import harvest_emails
data = harvest_emails('example.com', sources=['duckduckgo'], limit=20)
print(__import__('json').dumps(data, indent=2))
""")
```

## 8. Notes
- The skill prefers `duckduckgo` as default source because it requires no API key.
- For higher‑quality results, configure API keys in `~/.theHarvester/api-keys.yaml` (see theHarvester docs).
- PhoneInfoga output is parsed from human‑readable text; if your build supports `-o json`, adjust `scan_phone.py` accordingly.

--- 
*Captured during session on 2026-07-02.*