# Notion push — working recipe (this user's integration)

## Confirm the integration (do this FIRST)
This user was explicit: *"always confirm with mcp-cli before you say nonsense."*
Never assert "Notion isn't set up" from env-var checks alone — the MCP server is
configured even when `ntn` CLI and `hermes mcp list` show nothing.

```bash
# list everything the integration can see
mcp-cli call notion API-post-search '{}' > /tmp/notion_search.json
# parse (read the saved file; don't pipe mcp-cli | python3 — scanner blocks it)
```

The server entry lives in `~/.mcp_servers.json` as `notion` (type `stdio`,
`command: npx`, `args: [@notionhq/notion-mcp-server@latest]`, `env: NOTION_TOKEN`).

## Create a page (markdown body)
```bash
# payload via stdin: last arg '-' means "read JSON from stdin"
echo '{"parent":{"page_id":"<PARENT>"},"properties":{"title":[{"text":{"content":"Hermes Journal"}}]},"markdown":"# Hermes Journal\n\nbody here"}' \
  | mcp-cli call notion API-post-page -
```
`API-post-page` accepts a `markdown` field -> one-shot page from markdown.
Child pages are created the same way with a different `parent.page_id`.

## HARD CONSTRAINT — internal integration + workspace-level parent
An internal integration CANNOT create child pages under a page whose ancestry
reaches `parent: workspace`. Symptom: parent page creates fine, but every child
creation returns:
```
400 "Provide a parent.page_id or parent.database_id parameter to create a page,
or use a public integration with insert_content capability. Internal
integrations aren't owned by a single user, so creating workspace-level
private pages is not supported."
```
This is NOT a malformed payload and NOT a size limit (a tiny body fails too).
Fix: create the container under a normal `page_id` child (e.g. an Operations
Report leaf page), NOT under a top-level/workspace page. Test child creation
under the candidate parent before pushing 100+ pages:
```bash
echo '{"parent":{"page_id":"<LEAF_PAGE_ID>"},"properties":{"title":[{"text":{"content":"__probe__"}}]},"markdown":"probe"}' \
  | mcp-cli call notion API-post-page -
```

## Delete / clean up
- Archive (not delete): `echo '{"page_id":"<ID>","archived":true}' | mcp-cli call notion API-patch-page -`
- There is NO `API-delete-a-page` tool — don't guess that name.

## Scale + rate limits
- ~3 req/sec. For 100+ pages run the push in `background=true` (each `mcp-cli`
  call cold-starts npx, so a foreground run exceeds the 600s terminal cap).
- Feed JSON from a temp file via stdin in a Python script; do NOT use
  `shell=True` + `$(cat ...)` (code-scanner flags it). Use list-form args:
  `subprocess.run([MCP, "call", TOOL, CALL, "-"], stdin=open(path))`.

## This session's specifics (for re-runs)
- Working parent actually used: created "Hermes Journal" under an Operations
  Report leaf (`31a21259-8cc5-810c-b37d-d52a1e4e4277`). The earlier attempt
  under the "marketing campaign" top-level page was workspace-level and rejected
  all child pages — that page was archived.
- Push script: `~/.hermes/scripts/push_journal_notion.py`
  (`NOTION_PARENT_ID=<id> python3 push_journal_notion.py`).
