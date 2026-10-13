---
name: notion-mcp-cli
description: "Notion MCP CLI usage: output format and curl fallback."
version: 1.0.0
author: community
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: [NOTION_TOKEN]
  alt_config_path: ~/.mcp_servers.json
metadata:
  hermes:
    tags: [Notion, MCP, CLI, Productivity]
    homepage: https://developers.notion.com
---

# Notion MCP CLI Usage

This skill covers the specifics of using the Notion MCP server via `mcp-cli`, including handling the output format and falling back to curl when needed.

## MCP CLI Output Format

The `mcp-cli call notion` command returns a JSON object with a `content` array. The actual Notion API response is in the `text` field of the first element of `content` as a JSON string. You may need to parse it twice.

**Note on execution environment restrictions**: In some environments (like cron jobs with security policies), direct command substitution or piping to interpreters may be blocked. In such cases, write the output to a file first:
```bash
# Save MCP output to file
mcp-cli call notion API-post-search '{"query":"tasks"}' 2>/dev/null > /tmp/mcp_output.json
# Extract the inner JSON string from the wrapper
inner_json=$(jq -r '.content[0].text' /tmp/mcp_output.json)
# Save the inner JSON for processing
echo "$inner_json" > /tmp/mcp_response.json
# Now work with /tmp/mcp_response.json as you would with raw MCP output
# For example, to get data source IDs:
jq -r '.results[] | select(.object=="data_source") | .id' /tmp/mcp_response.json
```

Example (for environments without restrictions):
```bash
output=$(mcp-cli call notion API-post-search '{"query":"tasks"}')
# Extract the inner JSON string
inner_json=$(echo "$output" | jq -r '.content[0].text')
# Then parse the inner JSON
notion_response=$(echo "$inner_json" | jq '.')
```

## Fallback to Curl

If the MCP server fails silently (returns exit 0 with empty stdout and stderr), fall back to direct curl calls using the token from `~/.mcp_servers.json`.

Example:
```bash
token=$(grep -o '"NOTION_TOKEN": *"[^"]*"' ~/.mcp_servers.json | cut -d'"' -f4)
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $token" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"query": "tasks"}'
```

## Best Practices

- Always use `Notion-Version: 2022-06-28` for compatibility.
- When parsing mcp-cli output, use `jq -r '.content[0].text'` to extract the inner JSON string.
- For complex queries, write JSON to a file and use stdin to avoid shell escaping issues.
- In cron jobs, prefer the curl fallback for reliability.