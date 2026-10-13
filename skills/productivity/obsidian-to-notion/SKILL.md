---
name: obsidian-to-notion
description: Export Obsidian markdown to Notion via the Notion MCP.
version: 1.0.0
author: hermes-curator
license: MIT
tags: [notion, obsidian, export, migration, mcp, markdown]
triggers:
  - export obsidian to notion
  - obsidian vault to notion
  - migrate notes to notion
  - bulk create notion pages from markdown
  - notion mcp page creation
---

# Obsidian → Notion (full-fidelity bulk export)

Export a vault's markdown into Notion **pages**, preserving structure. The whole job
is driven through the **Notion MCP** (`mcp-cli call notion ...`) — never raw curl by
default. The MCP's `API-post-page` accepts a `markdown` body and converts it server-side
into real blocks (headings, code, tables, images). This is far less brittle than building
block arrays by hand.

> **User correction that triggered this skill (2026-08-10):** "why are you not using the
> mcp that talks directly to notion api using mcp-cli." When the MCP is registered, USE IT.
> Raw curl is a fallback only.

## Prerequisites

- Notion integration token in `~/.mcp_servers.json` under `mcpServers.notion.env.NOTION_TOKEN`
  (the MCP server reads `NOTION_TOKEN`, NOT `NOTION_API_KEY`).
- `@notionhq/notion-mcp-server` reachable (registered in `~/.mcp_servers.json`; `mcp-cli`
  spawns it via `npx -y @notionhq/notion-mcp-server@latest`).
- A **parent page** in Notion. Internal integrations CANNOT create workspace-root pages —
  pick an existing page (or create one via `API-post-page` under a known parent first) and
  put all exported notes under it as child pages.
- Obsidian vault on disk (read markdown files directly; the Obsidian app need not be running).

## Verified tool calls (via `mcp-cli call notion <tool> '<json>'`)

| Tool | Use |
|---|---|
| `API-post-page` | Create a page. **Pass `markdown` at top level** → full block conversion. |
| `API-post-search` | Find pages / verify creation. |
| `API-get-block-children` | Read back blocks to verify fidelity. |
| `API-patch-page` | Archive pages (`{"archived": true}`) for cleanup. |
| `API-update-page-markdown` | **DIFF-BASED ONLY** — `type` must be `insert_content`/`replace_content` and it wants `new_str`/`old_str`. It CANNOT set a full page body. Do not use it to "replace all content." |

### mcp-cli response envelope (CRITICAL)

`mcp-cli` wraps every result: `{"content":[{"type":"text","text":"<json-string>"}]}`.
Before `json.loads`, unwrap:
```python
import json, subprocess
def mcp(tool, args):
    p = subprocess.run(["mcp-cli","call","notion",tool,json.dumps(args)],
                       capture_output=True, text=True, timeout=240)
    out = p.stdout.strip()
    try:
        env = json.loads(out)
        if isinstance(env, dict) and "content" in env:
            out = env["content"][0]["text"]
    except Exception:
        pass
    return p.returncode, json.loads(out)
```
A raw `json.loads(p.stdout)` will fail — the outer object is the envelope, not your data.

## The dupe trap (avoid creating 2× pages per note)

Notion accepts `markdown` **only on page CREATE**. There is no "set full content via PATCH."
A naive two-pass (create empty shell → fill) therefore produces 2 pages per note.

**Correct single-pass design:**
1. For each note, `API-post-page` with `parent` + `properties.title` + `markdown` (full body).
   One call, one page, full fidelity. No shells, no dupes.
2. Wikilinks `[[Note]]`: you do NOT have target IDs yet (they're created in the same run),
   so **single-pass cannot resolve them into clickable mentions**. Acceptable outcome:
   leave unresolved `[[Note]]` as literal text, OR resolve only links whose target already
   exists (e.g. a pre-scanned sibling vault). State this trade-off to the user — do NOT
   create duplicate shells to fake resolution.
3. Images `![[local image.png]]`: the MCP exposes no file-upload tool. Upload via raw API
   (see below) and rewrite `![[x]]` → `![](notion://file_upload/<id>)` before sending markdown.

## Local image upload (3-step, raw API)

```python
import json, urllib.request
def raw(m,p,body=None,binary=None,ctype=None,tok=None):
    h={"Authorization":f"Bearer {tok}","Notion-Version":"2022-06-28"}
    data=None
    if binary is not None: h["Content-Type"]=ctype; data=binary
    elif body is not None: h["Content-Type"]="application/json"; data=json.dumps(body).encode()
    r=urllib.request.Request("https://api.notion.com/v1"+p,data=data,headers=h,method=m)
    with urllib.request.urlopen(r,timeout=120) as x: return json.loads(x.read() or b"{}")

# 1. create upload
js=raw("POST","/file_uploads",{"filename":name,"content_type":ctype},tok=tok)
# 2. PUT bytes to js["upload_url"]
# 3. reference notion://file_upload/<js["id"]> in markdown
```
Token for raw calls: read `NOTION_TOKEN` from `~/.mcp_servers.json`.

## Gotchas (all hit and fixed in-session)

- **`obs` ≠ Obsidian.** `/usr/bin/obs` on Linux is OBS Studio. The Obsidian CLI is
  `/usr/bin/obsidian` (v1.13.4). Don't conflate them. (That correction belongs in the
  Obsidian CLI skill; this one is Notion-side.)
- **Directory named `*.md`.** Obsidian lets folders end in `.md` (e.g. `qwen research.md/`).
  `glob("**/*.md")` returns them as "files" and `open()` then throws `IsADirectoryError`.
  Filter with `os.path.isfile(f)` before reading.
- **Rate limit ~3 req/s.** For 460 pages, run in background (`terminal(background=True,
  notify_on_complete=True)`) — do not block on a foreground `timeout`.
- **`print(..., flush=True)` in background jobs** — redirection buffers; flush or the log
  looks empty until exit.
- **Verify, don't trust self-report.** After export, count child pages under the parent and
  read back blocks of a sample (`API-get-block-children`) to confirm fidelity. A script's
  "created=37" is not proof — count in Notion.
- **Cleanup is reversible.** Archive (don't delete) test pages via `API-patch-page
  {"archived":true}` so mistakes are recoverable.

## Reference

- `references/export_script.md` — the exact, runnable single-pass exporter used to move
  4 vaults (460 notes) into Notion via the MCP, with the envelope unwrap, image upload,
  and dir-`.md` filter baked in.
