#!/usr/bin/env python3
"""Surgically insert the `open-design` MCP server into ~/.hermes/config.yaml.

Why surgical: config.yaml is hand-curated with comments. yaml.safe_dump or
patch/write_file would strip comments or corrupt it. This reads lines, finds the
end of the `mcp_servers:` block, and inserts the new entry after the LAST existing
server (preserving all other servers and comments).

Usage: python3 mcp_config_insert.py [--dry-run] [--path ~/.hermes/config.yaml]
"""
import sys, re, argparse

BLOCK = """  open-design:
    command: "/home/deeone/.nvm/versions/node/v24.19.0/bin/node"
    args:
      - "/home/deeone/open-design/open-design/apps/daemon/dist/cli.js"
      - "mcp"
      - "--daemon-url"
      - "http://127.0.0.1:7456"
    env:
      OD_DATA_DIR: "/home/deeone/open-design/open-design/.od"
"""

def find_insert_line(lines):
    # Locate `mcp_servers:` header
    start = next(i for i,l in enumerate(lines) if re.match(r"^mcp_servers:\s*$", l))
    # Indent of the header's children (2 spaces)
    child_indent = "  "
    # Find all top-level-ish server entries (2-space indent, no deeper) after start
    last = start
    i = start + 1
    while i < len(lines):
        ln = lines[i]
        if ln.strip() == "":
            i += 1; continue
        # A line at 0 indent (no leading spaces) ends the block
        if not ln.startswith(" ") and not ln.startswith("\t"):
            break
        # A 2-space-indented "key:" that is a sibling server entry
        if re.match(r"^  [A-Za-z0-9_-]+:\s*$", ln):
            last = i
        i += 1
    # Insert AFTER the last sibling entry. Skip its continuation lines (deeper indent).
    j = last + 1
    while j < len(lines) and (lines[j].startswith("   ") or lines[j].strip() == ""):
        # stop blank-line skip at next sibling or dedent
        if re.match(r"^  [A-Za-z0-9_-]+:\s*$", lines[j]):
            break
        j += 1
    return j

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=str(__import__("pathlib").Path.home()/".hermes"/"config.yaml"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with open(args.path) as f:
        lines = f.readlines()

    if any("open-design:" in l for l in lines):
        print("open-design already present — nothing to do.")
        return

    idx = find_insert_line(lines)
    new = [l if l.endswith("\n") else l+"\n" for l in BLOCK.splitlines()]
    out = lines[:idx] + ["\n"] + new + ["\n"] + lines[idx:]

    if args.dry_run:
        print("".join(out))
        return
    with open(args.path, "w") as f:
        f.writelines(out)
    print(f"Inserted open-design at line {idx} in {args.path}")

if __name__ == "__main__":
    main()
