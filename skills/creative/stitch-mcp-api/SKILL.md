---
name: stitch-mcp-api
description: >-
  Direct HTTP calling pattern for Google Stitch MCP server. Use when the task
  involves generating UI screens, creating design systems, or downloading
  Stitch-generated HTML/screenshots. Covers the curl-based API pattern, response
  parsing, tool names, and performance characteristics discovered through live
  usage. Trigger: stitch, generate screen, design system, UI generation, Stitch
  API, DESIGN.md upload.
---

# Stitch MCP API — Direct HTTP Reference

Stitch exposes an HTTP-based MCP server. All tool calls go through a single POST endpoint.

## Endpoint

```
POST https://stitch.googleapis.com/mcp
Headers:
  X-Goog-Api-Key: <your-api-key>
  Content-Type: application/json
```

## Calling Tools

All Stitch operations use `tools/call` method. Never use the tool name directly as the method.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "<tool-name>",
    "arguments": { ... }
  }
}
```

### Example via curl

```bash
curl -s -X POST 'https://stitch.googleapis.com/mcp' \
  -H 'X-Goog-Api-Key: <key>' \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"create_project","arguments":{"title":"My App"}}}'
```

**IMPORTANT**: For complex arguments with special characters, write the payload to a temp file first to avoid shell escaping issues:

```bash
cat > /tmp/stitch_payload.json << 'EOF'
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"generate_screen_from_text","arguments":{...}}}
EOF
curl -s -X POST 'https://stitch.googleapis.com/mcp' \
  -H 'X-Goog-Api-Key: <key>' \
  -H 'Content-Type: application/json' \
  -d @/tmp/stitch_payload.json
```

## Response Structure

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"projectId\":\"...\",\"outputComponents\":[...],...}"
      }
    ]
  }
}
```

The `result.content[0].text` is a **JSON string** that must be parsed again to access the actual data.

### For generate_screen_from_text responses (CORRECTED):
The nested JSON contains `sessionId`, `outputComponents`, inline `downloadUrl` values, and `screens/<id>` references. There is NO guaranteed `outputComponents[0].design.screens[0]` path — extract asset URLs by regex over the text:
- `https://...download...` → screenshot / HTML download URLs
- `screens/([a-zA-Z0-9_-]{20,})` → screen id

The screen is generated synchronously in this response (no separate polling needed). See `scripts/stitch_client.js` for a tested extractor.

## Key Tools

| Tool | Purpose | Key Arguments |
|------|---------|---------------|
| `create_project` | Create new project | `title` |
| `list_projects` | List projects | (none) |
| `list_screens` | List screens in project | `projectId` |
| `get_screen` | Get screen details | `projectId`, `screenId` |
| `generate_screen_from_text` | Generate from prompt | `projectId`, `prompt`, `designSystem`, `deviceType` |
| `edit_screens` | Edit existing screen | `projectId`, `selectedScreenIds`, `prompt` |
| `generate_variants` | Create variations | `projectId`, `selectedScreenIds`, `prompt`, `variantOptions` |
| `upload_design_md` | Upload DESIGN.md | `projectId`, `designMdBase64` |
| `create_design_system_from_design_md` | Create design system | `projectId`, `selectedScreenInstance` |
| `apply_design_system` | Apply to screens | `projectId`, `assetId`, `selectedScreenInstances` |

## Performance

- `generate_screen_from_text`: **60-120 seconds** per call
- `create_design_system_from_design_md`: **30+ seconds**
- Always use `timeout=180` for terminal calls
- Generate screens **sequentially**, not in parallel (API rate limits)

## Downloading Generated Assets

```bash
# Screenshot
curl -sL -o .stitch/designs/{name}.png "{downloadUrl}"

# HTML
curl -sL -o .stitch/designs/{name}.html "{downloadUrl}"
```

Download URLs are short-lived (minutes), so download immediately after generation.

## Typical Workflow

1. `create_project` → get projectId
2. `upload_design_md` (base64 encode DESIGN.md) → get sourceScreen + screenInstance
3. `create_design_system_from_design_md` → get assetId
4. For each screen: `generate_screen_from_text` with designSystem=assetId → download PNG + HTML
5. Optionally: `edit_screens` for targeted adjustments, then re-download

## Pitfalls

- **Shell escaping**: Complex prompts with quotes/brackets WILL break curl inline. Always use temp file (`@/tmp/stitch_payload.json`) for `generate_screen_from_text`. Even better, use the runnable Node client in `scripts/stitch_client.js` (avoids all shell-quoting pain).
- **Double JSON parse**: Response is JSON containing a JSON string in `content[0].text`. Parse twice.
- **403 errors**: Stitch API key may be missing or expired. Check `X-Goog-Api-Key` header. The key lives in `~/.gemini/extensions/Stitch/gemini-extension.json` under `mcpServers.stitch.headers.X-Goog-Api-Key`.
- **Rate limiting**: Stitch may return 429 if you send too many requests. Wait and retry.

### CRITICAL gotchas confirmed via live usage (2026-07)
1. **`mcp-cli` is unreliable / silent.** In a real session `mcp-cli`, `mcp-cli info stitch`, and `mcp-cli --help` produced ZERO output (no error, no result). Do NOT depend on `mcp-cli` to reach Stitch. Drive the endpoint directly via the JSON-RPC HTTP client below. This is the working path.
2. **`hermes config set mcp_servers.stitch '...'` writes a MALFORMED entry** — it stores the server as a quoted JSON *string* under the key instead of a nested object, so Hermes never loads it (and `hermes mcp list` shows nothing). To register for a future session use: `hermes mcp add stitch --url "https://stitch.googleapis.com/mcp" --auth header`. MCP servers only become callable tools after a Hermes restart.
3. **`projectId` MUST be a STRING.** Passing it as a number (e.g. `1228...`) returns `{"error":{"code":-32601,"message":"Method not supported"}}` or `Request contains an invalid argument.` Always pass the numeric id as a quoted string `"1228..."` (no `projects/` prefix).
4. **`generate_screen_from_text` response shape is session-based**, not always `outputComponents[0].design.screens[0]`. The real response is `result.content[0].text` (a JSON string) containing `sessionId`, `outputComponents`, inline `downloadUrl` values, and `screens/<id>` references. Extract asset URLs by regex over the text (`https://...download...`, `screens/<id>`), not by a fixed nested path. The screen is generated synchronously in this response.
5. **Stitch output is web HTML (Tailwind CDN + Google Fonts, e.g. Inter).** The "screenshot" `downloadUrl` for some calls returns an HTML document, not a binary PNG. To see it styled, open in a browser WITH network access (CDN must load). A headless `--screenshot` of the saved file without network renders unstyled/blank. The HTML itself is the real deliverable.
6. **Don't make excuses — drive the endpoint.** If the Stitch API key is present and the endpoint is reachable, call it directly via HTTP before declaring the tool "unavailable." The `tools/list` and `tools/call` envelope below is proven working.

## Runnable client

`scripts/stitch_client.js` — a tested Node JSON-RPC client. Usage:
```bash
node scripts/stitch_client.js create_project '{"title":"My App"}'
node scripts/stitch_client.js gen <projectId> <DEVICE:DESKTOP|MOBILE> <"prompt">
# gen auto-creates + downloads screens to ./stitch-designs/
```
It handles: string projectId, `tools/call` envelope, double-parse, URL/screen-id regex extraction, and rate-limited sequential generation.
