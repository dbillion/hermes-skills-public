# Streamable-HTTP single-session MCP servers vs `mcp-cli`

## Symptom
First `mcp-cli` call works; every later call in a fresh process fails:
```
❌ [HTTP] Unhandled request error: Error: Already connected to a transport.
    Call close() before connecting to a new transport, or use a separate
    Protocol instance per connection.
```
or `Error [SERVER_CONNECTION_FAILED]: ... Streamable HTTP error: internal server error`.

## Root cause
`StreamableHTTPServerTransport` keeps ONE session per server process, keyed by
`Mcp-Session-Id`. `mcp-cli` opens a new connection per invocation, so call #2 has
no valid session → rejected. Not a config error.

## Reproduction (notebooklm-mcp v2.0.0, HTTP on :3955)
```bash
# server (background)
node dist/index.js --transport http --port 3955 --path /mcp
# call 1 -> works
mcp-cli -c /tmp/nlmv2-http.json call nlmv2 add_source '{...}'
# call 2 (new process) -> "Already connected to a transport"
mcp-cli -c /tmp/nlmv2-http.json info nlmv2 add_source
```

## Fix: stdio scope (one process = one persistent session)
`/tmp/nlmv2-stdio.json`:
```json
{ "mcpServers": {
    "nlmv2": {
      "command": "/home/deeone/.nvm/versions/node/v25.6.1/bin/node",
      "args": ["/home/deeone/notebooklm-mcp/dist/index.js"],
      "env": {}
    }
  } }
```
```bash
# both calls now succeed (same one-shot process per invocation)
mcp-cli -c /tmp/nlmv2-stdio.json info nlmv2 add_source
mcp-cli -c /tmp/nlmv2-stdio.json call nlmv2 add_source '{"type":"text","content":"..."}'
```

## Notes
- If the server MUST stay HTTP (persistent daemon), consume it via Hermes' native
  MCP client in `config.yaml` (one persistent connection) — not `mcp-cli`.
- Confirmed working example: `notebooklm-mcp` v2.0.0 `add_source`
  (`type: url | text`, returns `sourceCountBefore/After`) over stdio.
- OpenDesign `od` MCP server is a stdio proxy to a running daemon on :7456;
  scope it the same way (`command: node`, `args: [cli.js, mcp, --daemon-url,
  http://127.0.0.1:7456]`). Daemon must be up first (`curl :7456/api/health`).
