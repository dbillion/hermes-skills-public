---
name: mcp-notion-patterns
description: "Patterns for using the Notion MCP server with mcp-cli."
version: 0.2.0
author: community
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: [NOTION_TOKEN]
  alt_config_path: ~/.mcp_servers.json
metadata:
  hermes:
    tags: [MCP, Notion, Productivity, Database, API, CLI]
    homepage: https://developers.notion.com
---

# MCP Notion Patterns

This skill provides patterns for working with the Notion MCP server (`@notionhq/notion-mcp-server`) via `mcp-cli`.

## WORKFLOW RULE (user preference — non-negotiable on this project)

**When a Notion MCP is configured and reachable, drive page create/import/read through `mcp-cli call notion ...` — do NOT hand-roll raw `curl`/`urllib` blocks against the Notion REST API.** The user explicitly pushed back when an export was done via raw HTTP instead of the MCP ("why are you not using the mcp that talks directly to notion api using mcp-cli that can direct it accurately"). The MCP path is:
- less error-prone (no manual auth header juggling),
- the path the user expects by default,
- fully capable of full-fidelity page import via the `markdown` body (see references/mcp-cli-notion-bulk-import.md).

Use raw HTTP only as a fallback when the MCP tool genuinely lacks the needed capability (e.g. archiving many pages in bulk, or paginating >100 children).

### Why this rule exists (user signal)
During a 4-vault Obsidian→Notion export the agent first used hand-rolled `curl`/`urllib` against the REST API. The user stopped it with: *"why are you not using the mcp that talks directly to notion api using mcp-cli that can direct it accurately"*. Lesson: when a Notion MCP is configured, **default to `mcp-cli call notion ...`** without being asked. Reaching for curl first reads as the wrong path to this user even when curl would work.

### Dispatch gotchas (learned hands-on)
- **Pass args via `subprocess input=`, never as an argv string.** Large markdown bodies hit OS `ARG_MAX` ("Argument list too long") for notes >~150 KB. In Python: `subprocess.run(["mcp-cli","call","notion",tool], input=json.dumps(args).encode(), capture_output=True, text=False)`.
- **Empty search:** `API-post-search` with no args or `{}` returns 0 results. To enumerate everything, pass `{"query":""}` (empty string, not omitted). Broad `query:"a"` also returns 0 — search matches titles/text, not wildcards.
- **Response envelope:** unwrap `content[0].text` before `json.loads`. See `references/mcp-cli-notion-bulk-import.md`.
- **Run bulk jobs in background** (`background=true`, `notify_on_complete=true`) — each call cold-spawns `npx` (~5–7 s); 400+ calls block a foreground loop.

## Setup

Ensure you have the Notion MCP server configured in `~/.mcp_servers.json`:

```json
{
  "mcpServers": {
    "notion": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server@latest"],
      "env": {
        "NOTION_TOKEN": "ntn_your_token_here"
      }
    }
  }
}
```

The server reads `NOTION_TOKEN` from the environment.

## Pattern: Enumerating Accessible Databases

To find which databases (data sources) the integration can access, use `API-post-search` with an empty query. The results may include pages inside databases and the data sources themselves.

```bash
mcp-cli call notion API-post-search '{}' 2>/dev/null > /tmp/notion_search.json
```

### Extracting Data Source IDs

Filter the results for objects with `"object": "data_source"` to get the database IDs needed for `API-query-data-source`.

**Using jq:**
```bash
jq '.results[] | select(.object == "data_source") | .id' /tmp/notion_search.json
```

**Using python3:**
```bash
python3 -c "import json; data=json.load(open('/tmp/notion_search.json')); [print(r['id']) for r in data['results'] if r.get('object') == 'data_source']"
```

### If No Data Sources Appear

If the filtering returns no results, the integration likely has not been granted access to any databases. In Notion, share the desired database with the integration:
1. Open the database in Notion.
2. Click "Share" → "Connect" → select your integration.

## Pattern: Querying a Database

Once you have a `data_source_id`, use `API-query-data-source` to retrieve rows. The tool expects JSON input via stdin.

Example: Get all rows from a database:
```bash
echo '{"data_source_id": "your-data-source-id-here"}' | mcp-cli call notion API-query-data-source
```

Example: Filter by a select property:
```bash
echo '{"data_source_id": "your-data-source-id-here", "filter": {"property": "Status", "select": {"equals": "Done"}}}' | mcp-cli call notion API-query-data-source
```

## Pattern: Creating a Page in a Database

To create a new page in a database, use `API-post-page`. You need the `database_id` (not the data_source_id). The `database_id` can be found in the parent of a page inside the database, or by retrieving the data source and looking for `database_id` in its properties (though the MCP server may not expose it directly).

Alternatively, you can use the `ntn` CLI or HTTP API to create a page if you have the `database_id`.

## Bulk import / Obsidian export (deep dive)

The reference `references/mcp-cli-notion-bulk-import.md` covers the non-obvious, hard-won behaviors for bulk page creation:
- the `mcp-cli` response envelope (unwrap `content[0].text`),
- `API-post-page` accepting a `markdown` body for full-fidelity import,
- `API-update-page-markdown` is diff-based (NOT a body setter),
- the ~50 KB markdown body cap and how to split large notes,
- `child_page.title` location for fast child enumeration,
- idempotency / duplicate-page avoidance,
- wikilink and embed limitations.

A ready-to-run bulk exporter lives at `scripts/mcp_notion_markdown_exporter.py` (TSV of title+markdown-file → Notion pages, with auto-chunking and envelope unwrap). Read the reference before any multi-page export.

## Troubleshooting

- **401 Unauthorized**: Verify `NOTION_TOKEN` is set correctly (not `NOTION_API_KEY`).
- **Empty results from API-post-search**: Check that the integration is shared with the desired pages/databases.
- **Tool call timeouts**: Use `MCP_NO_DAEMON=1` prefix to force fresh connections.
- **mcp-cli returns zero bytes**: The MCP server may be failing silently. Fall back to direct HTTP calls using the token from `~/.mcp_servers.json`.

## Notes

- The Notion MCP server uses the API version specified by the server; ensure it matches your integration's expectations.
- Rate limits apply (~3 requests/second average).
- For rich page creation with blocks, prefer the MCP server over raw API calls.
