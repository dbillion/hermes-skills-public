# MCP CLI Silent Failure Fallback

## Problem
`mcp-cli call notion <tool> '<json>'` returns exit code 0 but with completely empty stdout and stderr. This means the Notion MCP server failed silently — likely a startup/auth issue that isn't surfaced.

## Root Cause
The `@notionhq/notion-mcp-server` npx-launched process sometimes fails to initialize (cold start, auth token not read, npx cache miss) without producing any error output.

## Fallback: Direct curl

Read the token from `~/.mcp_servers.json` and call the Notion API directly:

```bash
# Extract token
TOKEN=$(python3 -c "import json; c=json.load(open('$HOME/.mcp_servers.json')); print(c['mcpServers']['notion']['env']['NOTION_TOKEN'])")

# Search for databases/pages
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"query":"your search term"}'

# Query a database
curl -s -X POST "https://api.notion.com/v1/databases/{database_id}/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"does_not_equal": "Complete"}},
    "sorts": [{"property": "Priority", "direction": "descending"}]
  }' > /tmp/notion_result.json
```

## Key Details
- **API Version**: Use `2022-06-28` (NOT `2025-09-03`)
- **Database queries** go to `/v1/databases/{id}/query` (POST)
- **Page reads** go to `/v1/pages/{id}` (GET)
- **Search** goes to `/v1/search` (POST)
- Always use `-s` flag on curl to suppress progress bars
- Write output to temp files when piping to interpreters (some environments block pipe-to-interpreter)
