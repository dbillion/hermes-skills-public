# Stitch MCP API Reference

## Endpoint
`https://stitch.googleapis.com/mcp`

## Authentication
Header: `X-Goog-Api-Key: <your-api-key>`

## All calls use `tools/call` method

### Create Project
```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"create_project","arguments":{"title":"App Name"}}}
```
Returns: `{"name":"projects/<ID>","title":"App Name",...}`

### Upload DESIGN.md
Base64-encode the file first, then:
```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"upload_design_md","arguments":{"projectId":"<ID>","designMdBase64":"<base64>"}}}
```
Returns: `{"id":"<screen-id>","sourceScreen":"projects/<ID>/screens/<ID>",...}`

### Create Design System
```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"create_design_system_from_design_md","arguments":{"projectId":"<ID>","selectedScreenInstance":{"id":"<screen-id>","sourceScreen":"projects/<ID>/screens/<ID>"}}}}
```
Returns: `{"assetId":"<asset-id>"}`

### Generate Screen
```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"generate_screen_from_text","arguments":{"projectId":"<ID>","designSystem":"assets/<ASSET_ID>","deviceType":"DESKTOP","prompt":"..."}}}
```

**Response structure:**
```json
{
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"projectId\":\"...\",\"outputComponents\":[{\"design\":{\"screens\":[{\"screenshot\":{\"downloadUrl\":\"...\"},\"htmlCode\":{\"downloadUrl\":\"...\"}}]}]}]}"
    }]
  }
}
```

The inner `text` field is a JSON string that must be parsed again.

### List Screens
```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_screens","arguments":{"projectId":"<ID>"}}}
```

## Prompt Rules
- NEVER include hex codes, font names, or color palettes in generation prompts
- Describe layout, content, structure — not visual styling
- Use professional component terms: "navigation bar", "data table", "card grid"
- Each generation takes 60-120 seconds

## Downloading Assets
After generation, download both:
- `screenshot.downloadUrl` → `.stitch/designs/<name>.png`
- `htmlCode.downloadUrl` → `.stitch/designs/<name>.html`
