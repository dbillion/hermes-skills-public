# MCP Tool Matrix: What Works What

Quick-reference for MCP tools available in this environment and their actual capabilities vs marketing claims.

## Zapier YouTube MCP

| Tool | Works? | Notes |
|---|---|---|
| `youtube_find_video` | ✅ Yes | Search by keywords, natural language instructions |
| `youtube_get_report` | ⚠️ Partial | Requires proper "channels" field; returns 400 without it |
| `youtube_upload_video` | ✅ Yes | Upload to your channel |
| `youtube_update_video_thumbnail` | ✅ Yes | |
| `youtube_add_video_to_playlist` | ✅ Yes | |
| `youtube_make_api_get_request` | ✅ Yes | Any YouTube Data API v3 GET endpoint |
| `youtube_make_api_mutating_request` | ✅ Yes | POST/PUT/PATCH/DELETE |
| `get_configuration_url` | ✅ Yes | Returns OAuth config URL |

### What Does NOT Work
- **Transcript extraction** — `captions.list` works, `captions.download` returns 401 (missing OAuth scope)
- **Analytics without channel param** — must specify `channels` field in `youtube_get_report`

### Connection Issues
- Token expires — regenerate at mcp.zapier.com
- Connection drops frequently (seen in logs from May 18-1401 = token expired, not a config error

## Notion MCP (`@notionhq/notion-mcp-server`)

| Tool | Works? | Notes |
|---|---|---|
| `API-post-search` | ✅ Yes | Search pages/databases by query |
| `API-post-page` | ✅ Yes | Create/read/update pages |
| `API-post-database` | ✅ Yes | Create/query databases |
| `API-post-search` | ✅ Yes | |

### Env Var Gotcha
- MCP server reads `NOTION_TOKEN` (not `NOTION_API_KEY`)
- Hermes redacts the token in logs/output
- Cron sessions need the token available at startup
- Config lives in `~/.mcp_servers.json` AND `~/.hermes/config.yaml`

## mcp-cli Tool
- Only supports **stdio transport** (command-based servers)
- DoesSE transport servers (like Zapier)
- Available servers: notion, github, lightpanda, stitch, aws, gemini, gcloud, etc.
- Run `mcp-cli list` to see all available tools

## Cron Sessions
- Default model in cron: `nvidia/nemotron-mini-4b-instruct` (4K context) — too small for heavy skills
- Override via `model` field in cronjob create/update
- Use `openrouter/owl-alpha` for any cron that loads skills
