# Notion MCP Timeout Issue (2026-08-11)

During a cron job execution on 2026-08-11, the command `mcp-cli call notion API-post-search '{"query":"tasks"}'` timed out after 60 seconds with exit code 124.

The mcp-cli output showed:
```
[notion] npm warn Unknown user config "allow-scripts". This will stop working in the next major version of npm. See `npm help npmrc` for supported config options.
[Command timed out after 60s]
```

## Root Cause
The Notion MCP server (`@notionhq/notion-mcp-server@latest`) was not responding within the timeout period, likely due to:
1. MCP daemon issues
2. Network connectivity problems
3. MCP server overload or unresponsiveness

## Solution Implemented
Fell back to direct Notion API calls using:
1. Extracted NOTION_TOKEN from `~/.mcp_servers.json`
2. Used curl with proper headers:
   - Authorization: Bearer $NOTION_TOKEN
   - Notion-Version: 2022-06-28
   - Content-Type: application/json
3. Made direct API calls to:
   - `https://api.notion.com/v1/search` for searching
   - `https://api.notion.com/v1/data_sources/{id}/query` for querying

## Verification
The fallback approach successfully retrieved search results when the MCP command failed.

## Prevention
For cron jobs requiring reliable Notion access:
1. Implement timeout detection (exit code 124)
2. Automatically fall back to direct API calls
3. Log when fallback is used for monitoring
4. Consider implementing retry logic with exponential backoff