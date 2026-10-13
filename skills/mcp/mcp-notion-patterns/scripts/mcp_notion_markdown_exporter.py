#!/usr/bin/env python3
"""
Generic bulk exporter: a list of (title, markdown, parent_page_id) -> Notion pages
via the Notion MCP (`mcp-cli call notion API-post-page`), using the hard-won
patterns from references/mcp-cli-notion-bulk-import.md.

Features baked in (do not re-discover these):
- Unwraps the mcp-cli `content[0].text` envelope.
- Sends args via subprocess stdin (input=), never as argv (avoids ARG_MAX on big notes).
- Uses the `markdown` field on API-post-page for full-fidelity block import.
- Auto-splits notes >40 KB to dodge Notion's ~50 KB body cap, creating a parent
  page + sequential child pages.
- Enumerates existing children via `child_page.title` (no per-child API retrieve).
- Prints progress with flush=True so a background run's log is readable.

Usage:
    python3 mcp_notion_markdown_exporter.py notes.tsv  PARENT_PAGE_ID
where notes.tsv has columns:  title <TAB> markdown_file_path
Parent page must already be shared with the integration in Notion.

Run with `background=true` + `notify_on_complete=true` for large batches;
each mcp-cli call cold-spawns npx (~5-7s), so 100 notes ~ 10-15 min.
"""
import json, subprocess, sys, os, time

MCP_TIMEOUT = 240
CHUNK = 40000  # bytes; Notion caps markdown body ~50KB, stay safely under

def mcp(tool, args):
    p = subprocess.run(["mcp-cli", "call", "notion", tool],
                       input=json.dumps(args).encode(),
                       capture_output=True, text=False, timeout=MCP_TIMEOUT)
    o = p.stdout.decode().strip()
    try:
        e = json.loads(o)
        if isinstance(e, dict) and "content" in e:
            o = e["content"][0]["text"]
    except Exception:
        pass
    try:
        return p.returncode, json.loads(o)
    except Exception:
        return p.returncode, {"_raw": o[:200]}

def create_page(parent_id, title, markdown=None):
    body = {
        "parent": {"page_id": parent_id},
        "properties": {"title": [{"text": {"content": title[:100]}}]},
    }
    if markdown:
        body["markdown"] = markdown
    rc, js = mcp("API-post-page", body)
    if rc == 0 and js.get("id") and js.get("object") == "page":
        return js["id"]
    print(f"  [FAIL] create '{title}': {js.get('message', str(js)[:80])}", flush=True)
    return None

def split_and_create(parent_id, title, md):
    """Create a parent + chunked children if md exceeds CHUNK."""
    pid = create_page(parent_id, title)
    if not pid:
        return None
    if len(md.encode()) <= CHUNK:
        return pid
    parts = [md[i:i+CHUNK] for i in range(0, len(md), CHUNK)]
    print(f"  split '{title}' into {len(parts)} parts", flush=True)
    for i, part in enumerate(parts, 1):
        create_page(pid, f"{title} (part {i})", part)
    return pid

def main():
    if len(sys.argv) != 3:
        print("usage: mcp_notion_markdown_exporter.py notes.tsv PARENT_PAGE_ID")
        sys.exit(1)
    tsv, parent = sys.argv[1], sys.argv[2]
    rows = [l.rstrip("\n").split("\t", 1) for l in open(tsv, encoding="utf-8") if l.strip()]
    print(f"[*] {len(rows)} notes -> parent {parent}", flush=True)
    ok = 0
    for title, path in rows:
        md = open(path, encoding="utf-8", errors="ignore").read() if os.path.exists(path) else path
        if split_and_create(parent, title, md):
            ok += 1
        time.sleep(0.3)
    print(f"[*] DONE: {ok}/{len(rows)} created", flush=True)

if __name__ == "__main__":
    main()
