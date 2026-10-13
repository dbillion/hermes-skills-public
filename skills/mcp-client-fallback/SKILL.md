---
name: mcp-client-fallback
description: Fallback workflow for when MCP CLI commands timeout or fail
version: 1.0.0
author: community
license: MIT
platforms: [linux, macos, windows]
---

# MCP Client Fallback

When MCP CLI commands timeout or fail, fall back to direct API calls.

## Why this happens
- MCP daemon issues can cause timeouts (exit code 124)
- Network issues between client and MCP server
- MCP server not responding

## Fallback workflow for Notion (example)

### 1. Extract MCP configuration
```bash
# Get NOTION_TOKEN from ~/.mcp_servers.json
NOTION_TOKEN=$(jq -r '.mcpServers.notion.env.NOTION_TOKEN' ~/.mcp_servers.json)
```

### 2. Use direct API calls with correct headers
- Authorization: Bearer $NOTION_TOKEN
- Notion-Version: 2022-06-28 (required for Notion)
- Content-Type: application/json

### 3. Common operations

**Search:**
```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"query": "tasks"}'
```

**Query a data source:**
```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/$ID/query" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "property": "Date",
      "date": {
        "equals": "2026-08-11"
      }
    }
  }'
```

### 4. Parsing results
Use `jq` to extract data from JSON responses.

## General pattern for other MCP services
1. Identify the service's MCP config entry in ~/.mcp_servers.json
2. Extract required environment variables (usually API tokens)
3. Find the service's HTTP API documentation
4. Replicate the MCP call with direct HTTP requests
5. Match the required headers (often including a version header)

## Verification
- Test the fallback manually before relying on it in cron
- Ensure API tokens have required permissions
- Monitor for rate limits when making direct calls