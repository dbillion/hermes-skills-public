---
name: notetaking-migration
description: "Migrate notes/markdown into Notion with full fidelity."
version: 1.0.0
author: hermes-curator
license: MIT
tags: [notion, obsidian, migration, export, notes, automation]
triggers:
  - obsidian to notion
  - export vault to notion
  - migrate notes to notion
  - notion bulk import
  - export markdown to notion
---

# Notetaking Migration (Obsidian → Notion verified)

Bulk-moving notes between systems. Verified live against the Notion API with an internal
integration token + the official Obsidian CLI on Linux. The lesson: the naive path
(create page, then PATCH markdown) FAILS, and "200 OK" lies — content can be dropped silently.

## Preconditions
- Notion internal integration token (`NOTION_TOKEN`, starts `ntn_`). SHARE a PARENT page with
  the integration (Settings → Connections → your integration). Without this, API returns 404.
- Obsidian CLI (`obsidian`) needs a RUNNING Obsidian instance (IPC). `/usr/bin/obs` is OBS Studio — NOT Obsidian.
- Internal integrations CANNOT create workspace-root pages — you must target an existing `page_id`.

## CRITICAL API quirks (each verified the hard way)
1. **PATCH /v1/pages/{id}/markdown FAILS** — `validation_error: body.type should be defined`.
   Do NOT create-then-patch. Instead **POST /v1/pages with `markdown` in the body** — Notion
   converts markdown → blocks server-side (headings, code, tables, images all render).
   Verified: a ~3 KB note became 31 blocks (h2, code, table, image, quote).
2. **Parent required**: `parent: {"page_id": "<existing id>"}`. No workspace-root creation.
3. **`[[wikilinks]]` are unknown to Notion** — they land as literal `[[Name]]` text. For fidelity,
   do 2-pass: (a) create all pages, build a title→page_id map; (b) rewrite `[[Name]]` → a Notion
   mention `<mention-page url="...">Name</mention-page>` before creating. Counts grow fast
   (1,600+ across 4 vaults).
4. **`![[local embed]]`** points at a vault file. If it is already an http(s) URL
   (e.g. `raw.githubusercontent.com/...`), Notion stores it as an external image automatically.
   If local, upload via the file_uploads 3-step flow and reference `file_upload_id`.
5. Rate limit ~3 req/s. 460 pages ≈ 3–4 min single pass, ~8 min with link resolution.

## Pipeline (full fidelity, 2-pass)
1. Enumerate `*.md` per vault (exclude `/.obsidian/`, `/.trash/`).
2. POST each as a child of the parent; body `markdown` = file contents. Collect `{title: page_id}`.
3. Wikilink fidelity: pre-scan all notes for `[[...]]`; on create, substitute resolved page ids.
4. Local embeds: upload each unique asset; substitute `![[asset]]` with the uploaded reference.

## VERIFY — do not trust HTTP 200
`GET /v1/blocks/{page_id}/children` — confirm block count > 0 and types match
(heading/code/table/image). A 200 with 0 blocks means content was silently dropped.

## No Notion equivalent
`.obsidian/` config, `.canvas`, `.base`, `.excalidraw` stencil drawings (the plugin keeps its
library in one merged file), rich frontmatter → markdown only.

## Token sourcing for bulk one-shot writes
Read from `~/.mcp_servers.json` → `mcpServers.notion.env.NOTION_TOKEN`. Call the API directly
with `curl` to avoid MCP server-startup latency per call. For reads, the MCP server is fine.

## Related
- `mcp-server-install-verify` → references/obsidian-excalidraw-mcp.md (Obsidian CLI binary
  confusion, `ext=` gotcha, on-disk-vs-active plugin state, stencil merge recipe).
- `notion` skill (bundled) for the full API surface; note it documents `PATCH /markdown` as
  working — it is NOT for an internal integration. Use POST-with-markdown instead.
