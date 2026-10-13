#!/usr/bin/env python3
"""
Safely insert a new block into ~/.hermes/config.yaml WITHOUT reparsing/dumping
(strips comments + reorders keys). Finds an anchor line and inserts raw text before it.

USAGE:
  python3 safe_config_insert.py

Edit ANCHOR and BLOCK below for your change. Dry-run safe: prints diff, writes only on confirm.
"""
import sys

PATH = "/home/deeone/.hermes/config.yaml"

# Line that marks where to insert BEFORE (first exact match, column 0).
# For a new mcp_servers entry, insert before the next top-level block, e.g. "plugins:".
ANCHOR = "plugins:\n"

# The block to insert (must be valid YAML at the correct indent for its parent).
BLOCK = '''  substack-api:
    command: npx
    args:
      - -y
      - substack-mcp@latest
    env:
      SUBSTACK_PUBLICATION_URL: "https://dbillion.substack.com/"
      SUBSTACK_SESSION_TOKEN: "PASTE_TOKEN_HERE"
      SUBSTACK_USER_ID: "36196425"
    timeout: 120
    connect_timeout: 60
'''

def main():
    lines = open(PATH).readlines()
    try:
        at = next(i for i, l in enumerate(lines) if l == ANCHOR)
    except StopIteration:
        print(f"ANCHOR {ANCHOR!r} not found. Aborting (no change written).")
        sys.exit(1)
    new = lines[:at] + [BLOCK] + lines[at:]
    print(f"Will insert {BLOCK.count(chr(10))} lines before line {at+1} ({ANCHOR.strip()}).")
    if "--write" not in sys.argv:
        print("DRY RUN. Re-run with --write to apply.")
        return
    open(PATH, "w").writelines(new)
    print("WRITTEN. Verify: grep -c '^#'", PATH, "and yaml.safe_load parse.")

if __name__ == "__main__":
    main()
