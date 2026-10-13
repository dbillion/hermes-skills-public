# Stitch MCP registration (Gemini → mcp-cli)

Use this when Stitch MCP works in Gemini CLI but **mcp-cli** shows no Stitch tools.

## Goal
Register the Stitch MCP server for **mcp-cli** by copying the Gemini extension config.

## Steps
1) Read Gemini Stitch extension config:
   - `~/.gemini/extensions/Stitch/gemini-extension.json`
   - Look for:
     - `mcpServers.stitch.httpUrl`
     - `mcpServers.stitch.headers` (e.g., `X-Goog-Api-Key`)
     - optional `timeout`

2) Add/merge into `~/.mcp_servers.json`:
```json
{
  "mcpServers": {
    "stitch": {
      "type": "http",
      "url": "https://stitch.googleapis.com/mcp",
      "headers": {
        "X-Goog-Api-Key": "<your key>"
      },
      "timeout": 300000
    }
  }
}
```

3) Verify with:
- `mcp-cli info stitch` (preferred)
- `mcp-cli grep "*stitch*"`

## Notes
- `mcp-cli grep` matches **tool names only**, not server names. Use `mcp-cli info stitch` to confirm the server is registered.
- If `mcp-cli info stitch` shows connect errors, re-check auth (API key vs ADC) and the URL/headers.

## Hermes (critical if "I have Stitch MCP" but tools are missing)
Hermes loads MCP servers from `~/.hermes/config.yaml` (the `mcp_servers:` block), NOT from `~/.mcp_servers.json`. A server present only in the latter will NOT be in the active toolset.

Steps to register for Hermes:
1. Read the key from the Gemini extension: `~/.gemini/extensions/Stitch/gemini-extension.json` -> `mcpServers.stitch.headers.X-Goog-Api-Key`.
2. Register with the CLI (direct config.yaml edits are guard-blocked):
   ```
   hermes config set mcp_servers.stitch '{"type":"http","url":"https://stitch.googleapis.com/mcp","headers":{"X-Goog-Api-Key":"<key>"},"timeout":300000}'
   ```
3. **Restart Hermes / open a new session.** MCP servers are read at session boot; the tools are NOT available in the session where you ran the command. Verify next session by checking the tool list for `stitch_*` tools.
4. If the session cannot be restarted, do NOT claim Stitch is usable. Fall back to design synthesis (principles + real image placeholders) and tell the user Stitch needs a restart.
