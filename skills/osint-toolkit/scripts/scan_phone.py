#!/usr/bin/env python3
import subprocess
import json
import os
import sys
import re

def scan_phone(number, services=None, timeout=30):
    """Run phoneinfoga scan and return dict with parsed info."""
    venv_activate = os.path.expanduser("~/osint-venv/bin/activate")
    # Build command: phoneinfoga scan -n <number> [--services <svc>...]
    cmd_parts = ["phoneinfoga", "scan", "-n", number]
    if services:
        for s in services:
            cmd_parts.extend(["--services", s])
    cmd = [
        "bash", "-c",
        f"source {venv_activate} && {' '.join(cmd_parts)}"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    output = proc.stdout
    # Parse output lines
    result = {
        "number": number,
        "valid": False,
        "carrier": None,
        "line_type": None,
        "reports": []
    }
    # Example lines:
    # [+] Number: +1 555-123-4567
    # [+] Valid: Yes
    # [+] Carrier: Example Carrier
    # [+] Line type: Mobile
    # [!] No reports found.
    for line in output.splitlines():
        line = line.strip()
        if line.startswith('[+] Number:'):
            # Already have number
            pass
        elif line.startswith('[+] Valid:'):
            val = line.split(':',1)[1].strip().lower()
            result['valid'] = (val == 'yes' or val == 'true')
        elif line.startswith('[+] Carrier:'):
            result['carrier'] = line.split(':',1)[1].strip()
        elif line.startswith('[+] Line type:'):
            result['line_type'] = line.split(':',1)[1].strip()
        elif line.startswith('[+]') or line.startswith('[!]'):
            # treat as report line
            # Remove leading brackets and sign
            clean = re.sub(r'^\[\+|\[!\]', '', line).strip()
            if clean:
                result['reports'].append(clean)
    # If no specific fields found, maybe output is JSON? but we ignore.
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: scan_phone.py <number> [service1,service2,...] [timeout]")
        sys.exit(1)
    number = sys.argv[1]
    services = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    print(json.dumps(scan_phone(number, services, timeout), indent=2))