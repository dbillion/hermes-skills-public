# Notion MCP Server Reference

## mcp-cli Config Location

**Important:** mcp-cli reads from `~/.mcp_servers.json`, NOT from `~/.config/mcp-cli/mcp_servers.json`.

The config at `~/.config/mcp-cli/mcp_servers.json` is used by a different tool. Always check `~/.mcp_servers.json` first.

## Notion MCP Server Setup

### Installation

Add to `~/.mcp_servers.json` under `mcpServers`:

```json
{
  "mcpServers": {
    "notion": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server@latest"],
      "env": {
        "NOTION_TOKEN": "ntn_your_integration_token"
      }
    }
  }
}
```

**Critical:** Use `NOTION_TOKEN` as the env var name, NOT `NOTION_API_KEY`. The server specifically reads `NOTION_TOKEN`.

### Available Tools (22 total)

Key tools: `API-post-page`, `API-patch-page`, `API-retrieve-a-page`, `API-post-search`, `API-query-data-source`, `API-create-a-data-source`, `API-update-a-data-source`, `API-retrieve-a-data-source`, `API-retrieve-a-database`, `API-move-page`, `API-create-a-comment`, `API-retrieve-a-comment`, `API-get-block-children`, `API-patch-block-children`, `API-retrieve-a-block`, `API-update-a-block`, `API-delete-a-block`, `API-retrieve-a-page-property`, `API-list-data-source-templates`, `API-get-user`, `API-get-users`, `API-get-self`.

### Calling Patterns

**Small payload (inline JSON):**
```bash
mcp-cli call notion API-retrieve-a-page '{"page_id":"36321259-8cc5-818e-aad6-eda65de0b003"}'
```

**Large payload (file via stdin):**
```bash
cat /tmp/page_payload.json | mcp-cli call notion API-post-page -
```

**Force fresh connection (avoid cached daemon):**
```bash
MCP_NO_DAEMON=1 mcp-cli call notion API-post-page "$(cat /tmp/payload.json)"
```

### Creating Rich Pages

The MCP server's `API-post-page` accepts a `children` array with full block support:

- `callout` — highlighted boxes with icon and color
- `toggle` — expandable/collapsible sections
- `table` / `table_row` — structured tables
- `to_do` — checkbox items
- `bulleted_list_item` / `numbered_list_item`
- `heading_1`, `heading_2`, `heading_3`
- `paragraph`, `quote`, `divider`
- `code` — code blocks

**Block icon format:** Use `{"type": "emoji", "emoji": "☀️"}` (proper emoji unicode, NOT word names like "sun").

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Wrong env var name | Use `NOTION_TOKEN` not `NOTION_API_KEY` |
| Server not found | Config in wrong file | Put config in `~/.mcp_servers.json` |
| Stale connection | Cached daemon | Prefix with `MCP_NO_DAEMON=1` |
| Invalid JSON | Emoji encoding issues | Write payload via Python `json.dump()` to file, then pipe |
| Property not found | DB property not created | DB creation via API only creates `Name`; add properties via PATCH |

## Notion API 2025-09-03 Quirks

1. **Database creation** via `POST /v1/databases` only creates the title property. Additional properties must be added via `PATCH /v1/databases/{id}`.

2. **Parent field** in API calls requires `type` specified:
   - Pages: `{"parent": {"page_id": "xxx"}}` (type inferred)
   - Databases: `{"parent": {"type": "page_id", "page_id": "xxx"}}` (type REQUIRED)

3. **Internal integrations** cannot create workspace-level pages. Must specify a parent page ID.

4. **Data source vs database ID**: When querying, use the `data_source_id` from the database's `data_sources` array, not the `database_id`.
