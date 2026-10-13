# Notion MCP via mcp-cli — bulk import & gotchas (from a 4-vault Obsidian→Notion export)

Discovered hands-on while exporting 460 Obsidian notes to Notion. These are the
non-obvious behaviors of the `@notionhq/notion-mcp-server` tool set as surfaced
through `mcp-cli call notion <tool>`.

## Response envelope
Every `mcp-cli call notion ...` returns a JSON object:
```
{"content":[{"type":"text","text":"{...real JSON...}"}]}
```
You MUST unwrap `content[0].text` before `json.loads`. A naive parse of the
outer object gives you the envelope, and `.get('results')` returns None.
Helper:
```python
import json, subprocess
def mcp(tool, args):
    p = subprocess.run(["mcp-cli","call","notion",tool],
                       input=json.dumps(args).encode(),
                       capture_output=True, text=False, timeout=240)
    o = p.stdout.decode().strip()
    try:
        e = json.loads(o)
        if isinstance(e, dict) and "content" in e:
            o = e["content"][0]["text"]
    except Exception:
        pass
    return json.loads(o)
```
Pass args via `input=` (subprocess.PIPE), NOT as an argv string. Passing a
large markdown as a command-line argument hits OS `ARG_MAX` ("Argument list
too long") for notes >~150 KB.

## API-post-page — the real bulk-import workhorse
- Accepts a `markdown` field at the top level. The server converts GitHub-style
  markdown (headings, fenced code, tables, blockquotes, images, dividers) into
  Notion blocks. Verified 31 blocks from one markdown with full fidelity.
- Minimal call:
  ```python
  mcp("API-post-page", {
    "parent": {"page_id": "<parent_id>"},
    "properties": {"title": [{"text": {"content": "Note Title"}}]},
    "markdown": "# Heading\n\n```python\ncode\n```\n\n| a | b |\n|---|---|\n| 1 | 2 |"
  })
  ```
- `page_id` must be a page the integration can write to (share the parent page
  with the integration in Notion first). Workspace-root pages cannot be created
  via API — pick an existing parent page.

## API-update-page-markdown — DIFF-based, NOT a body setter
Despite the name, this tool is for targeted edits, not full-page content
replacement. Required shape (easy to get wrong):
```json
{"page_id":"...","type":"replace_content","replace_content":{"markdown":"..."}}
```
- `type` must be the literal `"replace_content"` (or `"insert_content"`), NOT
  `"page"`.
- It expects a diff (`new_str`/`old_str`) semantics, not a fresh markdown body.
  Do NOT use it as a "set page content" call. For bulk import, create-with-
  markdown instead.

## Body size cap (~50 KB)
Notion rejects markdown bodies larger than roughly 50 KB per `API-post-page`
request with an HTML 413-style error page (`<!DOCTYPE html>...Notion`). For
large notes:
- Split into ~40 KB chunks.
- Create a parent page, then create each chunk as a child page under it:
  ```python
  parent = mcp("API-post-page", {"parent":{"page_id":PP},"properties":{"title":[{"text":{"content":"Big Note (split)"}]}})["id"]
  for i,chunk in enumerate(chunks):
      mcp("API-post-page", {"parent":{"page_id":parent},
                            "properties":{"title":[{"text":{"content":f"part {i+1}"}]},
                            "markdown":chunk})
  ```

## Listing children / titles
- `API-get-block-children` with `{"block_id": <page_id>, "page_size":100}` —
  paginate via `start_cursor` + `has_more`.
- The child title lives in the block object: `child_page.title` (a string),
  NOT in a nested `properties`. Do not call `API-retrieve-a-page` per child
  (that's 1 extra API call per note and is slow at scale).
- Count child pages: `sum(1 for c in results if c['type']=='child_page')`.

## Cost / speed
- Each `mcp-cli` call cold-spawns `npx` (~5–7 s). 460 calls ≈ 40–60 min. Run
  bulk jobs in `background=true` with `notify_on_complete=true`, and poll the
  live log — do not block on a foreground `sleep`.

## Idempotency (avoid duplicate pages)
- Notion only accepts markdown on page CREATE. You cannot re-set content via
  update. A "create shell, then fill" two-pass design therefore DOUBLES pages.
- Clean single-pass design: build a complete title→id map first (pre-pass of
  empty title-only pages OR know all titles), then create each page once with
  full markdown. If you must resolve wikilinks to target IDs, do an empty-shell
  pre-pass to build the map, create real pages in pass 2, then ARCHIVE the
  shells (archived pages still appear in search — verify they're actually
  trashed, not just "archived", before claiming no dupes).

## Wikilinks limitation
`[[Note]]` in markdown lands as literal text, not a clickable Notion mention —
target IDs don't exist until pages are created, and content is create-only. A
no-dupe single-pass cannot wire the graph. Accept literal `[[Note]]` or do a
post-hoc archive-and-recreate pass (expensive; usually not worth it).

## Embeds / images
`![[local-file]]` (Obsidian embed) uploads only if the referenced file exists
on disk at the path. Broken/missing local embeds fail silently per-note
(count them, don't let them abort the run). Remote URLs (http/https images)
carry through fine.
