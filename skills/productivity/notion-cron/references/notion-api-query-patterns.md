# Notion API Query Patterns for Cron Jobs

Proven patterns for querying Notion from Hermes cron jobs. All use `curl` + `jq` — no `mcp-cli`, no `python3 -c` (blocked in cron mode).

## Token Setup

```bash
NOTION_TOKEN=$(jq -r '.mcpServers.notion.env.NOTION_TOKEN' ~/.mcp_servers.json)
```

All subsequent commands assume `$NOTION_TOKEN` is exported.

## Search for Pages/Databases

```bash
# Basic search
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"query":"tasks"}' > /tmp/notion_search.json

# List titles from results
jq '[.results[] | {object, title: (if .object == "database" then .title[0].text.content elif .object == "page" then (.properties | to_entries | map(select(.value.type == "title")) | .[0].value.title[0].text.content // "unnamed") else "unknown" end), id}]' /tmp/notion_search.json

# Databases only
jq '[.results[] | select(.object == "database") | {title: .title[0].text.content, id}]' /tmp/notion_search.json

# Pages only
jq '[.results[] | select(.object == "page") | {title: (.properties | to_entries | map(select(.value.type == "title")) | .[0].value.title[0].text.content // "unnamed"), id}]' /tmp/notion_search.json
```

## Query a Database

```bash
# All items
curl -s -X POST "https://api.notion.com/v1/databases/{db_id}/query" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{}' > /tmp/notion_db.json

# Extract name + status (handles both status and select property types)
jq '[.results[] | {
  name: (.properties | to_entries | map(select(.value.type == "title")) | .[0].value.title[0].text.content // "unnamed"),
  status: (.properties | to_entries | map(select(.key == "Status")) | .[0].value | (.status.name // .select.name // null)),
}]' /tmp/notion_db.json

# Filtered query (completed items)
curl -s -X POST "https://api.notion.com/v1/databases/{db_id}/query" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"filter":{"property":"Status","status":{"equals":"Done"}}}' > /tmp/notion_done.json

# Date-filtered query (today)
curl -s -X POST "https://api.notion.com/v1/databases/{db_id}/query" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"filter":{"property":"Date","date":{"equals":"2026-06-29"}}}' > /tmp/notion_today.json

# Sorted query
curl -s -X POST "https://api.notion.com/v1/databases/{db_id}/query" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"sorts":[{"property":"Date","direction":"descending"}]}' > /tmp/notion_sorted.json
```

## Discover Database Schema

```bash
# Get database properties and their types
curl -s "https://api.notion.com/v1/databases/{db_id}" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" | jq '{title: .title[0].text.content, properties: (.properties | to_entries | map({key: .key, type: .value.type}))}'
```

## Read Page Content

```bash
# Page metadata (properties)
curl -s "https://api.notion.com/v1/pages/{page_id}" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28"

# Page block children (top level only)
curl -s "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" > /tmp/notion_blocks.json

# Check which blocks have children
jq '[.results[] | {type, id, text: (if .type == "callout" then .callout.rich_text[0].plain_text elif .type == "paragraph" then (.paragraph.rich_text | map(.plain_text) | join("")) else .type end), has_children}]' /tmp/notion_blocks.json

# Fetch children of a specific block (for nested content like callout items)
curl -s "https://api.notion.com/v1/blocks/{block_id}/children" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28"

# Extract text from block children (filters empty placeholders)
jq -r '[.results[] | .type as $t | .[$t].rich_text | map(.plain_text) | join("") | select(length > 0)] | join("\n")' /tmp/notion_block_children.json
```

## Recently Edited Items

```bash
# Search sorted by most recently edited
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"query":"","sort":{"direction":"descending","timestamp":"last_edited_time"},"page_size":20}' > /tmp/notion_recent.json

# Filter for today's edits
jq '[.results[] | select(.last_edited_time >= "2026-06-29") | {object, title: (if .object == "page" then (.properties | to_entries | map(select(.value.type == "title")) | .[0].value.title[0].text.content // "unnamed") elif .object == "database" then .title[0].text.content else "unknown" end), last_edited: .last_edited_time}]' /tmp/notion_recent.json
```

## Key Gotchas

1. **Empty `rich_text` arrays**: Template-generated pages create placeholder blocks with `rich_text: []`. Filter these with `select(length > 0)` after joining plain_text.
2. **`has_children: true`**: Children are NOT included in the parent response. Requires separate GET call per block.
3. **Property name volatility**: Title property can be `Name`, `Title`, `Task`, `Post`, etc. Use `to_entries | map(select(.value.type == "title"))` to find it dynamically.
4. **Status vs select**: Status property type uses `.status.name`, select uses `.select.name`. Try both: `(.status.name // .select.name)`.
5. **API version**: Always `2022-06-28`. Newer versions change property shapes.
6. **Page size limit**: Default 100, max 100 results per query. Use `next_cursor` for pagination if `has_more: true`.
