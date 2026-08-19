---
name: obsidian-notion-export
description: Export Obsidian vaults to Notion via the Notion MCP.
version: 1.0.0
author: hermes-agent
tags: [obsidian, notion, export, mcp, notes, migration]
triggers:
  - export obsidian to notion
  - obsidian vault to notion
  - push obsidian notes to notion
  - migrate obsidian into notion
  - notion mcp export
---

# Obsidian → Notion Export (via Notion MCP)

Bulk-import Obsidian markdown into Notion. Drive everything through the
registered Notion MCP server (`mcp-cli call notion ...`), NOT hand-rolled
curl/HTTP — the MCP's `API-post-page` accepts a `markdown` body that Notion
converts server-side into real blocks (headings, code, tables, images).

## Prerequisites

- Notion MCP registered in `~/.mcp_servers.json` as `notion` (type stdio,
  command `npx -y @notionhq/notion-mcp-server@latest`, env `NOTION_TOKEN`).
- Token also readable from that config for raw calls (file uploads).
- A parent page ID in Notion (API cannot create workspace-root pages —
  internal integrations need an existing parent; use an existing page like
  "Personal Home", or create one first via `API-post-page`).
- Obsidian CLI is `obsidian` (NOT `obs` — that is OBS Studio). Obsidian must
  be running for CLI calls.

## The core technique (verified working)

For each markdown file:
```python
import subprocess, json
def mcp(tool, args):
    p = subprocess.run(["mcp-cli", "call", "notion", tool],
                       input=json.dumps(args).encode(),
                       capture_output=True, text=False, timeout=240)
    out = p.stdout.decode().strip()
    try:
        e = json.loads(out)
        if isinstance(e, dict) and "content" in e:
            out = e["content"][0]["text"]
    except Exception:
        pass
    return p.returncode, json.loads(out)

mcp("API-post-page", {
    "parent": {"page_id": PARENT},
    "properties": {"title": [{"text": {"content": title[:100]}}]},
    "markdown": md,   # full markdown -> Notion converts to blocks
})
```
Result: headings, code blocks, tables, and images all land as proper blocks.
GitHub/remote image URLs work directly inside the markdown.

## CRITICAL gotchas (all hit and debugged in a real 4-vault run)

### 1. mcp-cli large-arg limit → use subprocess `input=`, not argv/file
Passing big JSON as an inline argv arg fails with `Argument list too long`
(the OS ARG_MAX is ~128–200KB, and one vault note was 834KB).
- DO: `subprocess.run([...], input=json.dumps(args).encode())`.
- DON'T: `stdin=open(path)` — it fails SILENTLY (server gets malformed input,
  returns 400 "Provide a parent", rc=0 so your code thinks it succeeded).
- DON'T: `cat file | mcp-cli` inside a Python subprocess (works in a shell,
  not as a file object).
- Verify success by checking `js.get('id') and js.get('object')=='page'`,
  NOT just `rc==0` — the MCP returns HTML error pages with rc=0.

### 2. Notion markdown import cap ≈ 50KB per request
Notes >~50KB return an HTML `413`-style error page (masquerading as rc=0
success). Split large notes into ~40KB child pages under a parent:
```python
CHUNK = 40000
parts = [md[i:i+CHUNK] for i in range(0, len(md), CHUNK)]
for i, part in enumerate(parts, 1):
    mcp("API-post-page", {"parent": {"page_id": SPLIT_PARENT},
        "properties": {"title": [{"text": {"content": f"part {i}"}}]},
        "markdown": part})
```
Always verify `js.get('id')` per chunk — a silent HTML-error failure leaves
an empty shell page.

### 3. Content is create-only
`PATCH /v1/pages/{id}/markdown` is DEAD (validation_error: body.type should
be defined). `API-update-page-markdown` is a diff tool (new_str/old_str), not
a full setter. You can only set markdown body at page CREATE. So:

### 4. Wikilinks [[Note]] — the no-dupe trade-off
To resolve `[[Note]]` → a clickable Notion mention you need the target page's
ID, which doesn't exist until that page is created. Options:
- **Single-pass (chosen):** create each page WITH markdown directly. Wikilinks
  to notes not yet created land as literal `[[Note]]` text. Zero duplicate
  pages. Acceptable for most exports.
- **Two-pass:** create empty title-only shells for all notes first (build
  title→id map), then create real content pages, then archive the shells.
  Produces duplicate (empty+real) pages that must be cleaned up — messy.
Prefer single-pass and accept literal wikilinks unless the user explicitly
needs the graph wired.

### 5. Local ![[embeds]] must be uploaded
`![[local image]]` points at a vault file. Upload each via raw API:
```python
st, js = raw("POST", "/file_uploads", {"filename": name, "content_type": ctype})
# PUT bytes to js["upload_url"], then reference as ![](notion://file_upload/<id>)
```
Remote URLs (https://…) work directly in the markdown body.

## Obsidian-side gotchas

- **Excalidraw libraries:** the plugin only reads ONE file —
  `libraryFileName` in its `data.json` (default `local-library.excalidrawlib`)
  in `libraryFolderPath`. Dropping more `.excalidrawlib` files in the folder
  does NOT activate them. To add libraries: merge all `libraryItems` into that
  one file, or import via the Excalidraw UI (Library panel → Load).
- **`obsidian files folder=X` returns EMPTY for non-markdown files.** Must
  pass `ext=` (e.g. `ext=excalidrawlib`) to see them.
- **`obs` ≠ `obsidian`.** `obs` is OBS Studio. The Obsidian CLI is `obsidian`.
- **`obsidian reload` can KILL the app** rather than reload it — relaunch
  afterward if needed.
- Skip directories when globbing: Obsidian lets folders end in `.md`
  (e.g. `qwen research.md/` is a folder). Use `os.path.isfile()` in `gather()`.

## Verification after export

- Count children under the parent: `API-get-block-children` (paginate with
  `start_cursor` — `page_size=100` caps at 100, so loop until `has_more` false).
- Spot-check one page's block count: should match the source structure
  (headings + code + tables + images).
- Confirm `archived` count is 0 in workspace (no leftover dupes/junk).
- A page with 0 blocks but a valid id = a SILENT failure (HTML-error
  masquerade). Re-create that note.

## Reference exporter

`scripts/obsidian_to_notion_mcp.py` (in the dsa-java-gradleqa repo, or adapt)
implements all of the above: gather → upload embeds → resolve wikilinks →
single-pass `API-post-page` with `markdown` → per-vault parent pages.

## Related references

- `references/excalidraw-libraries.md` — Obsidian Excalidraw library activation
  gotcha (plugin only reads `local-library.excalidrawlib`; merge or import via UI).
