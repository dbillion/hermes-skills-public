# mcp-cli as a Local MCP Router — Full Pattern

## Why
Loading 30+ MCP servers into an agent's context burns ~47k tokens of tool schemas. `philschmid/mcp-cli`
inverts this: list servers with one command, inspect a tool's schema on demand, call only what you
need. ~400 tokens typical. This is how to wire it on this box.

## Install (correct package)
```bash
# Bun-based client. Requires bun (already at /usr/bin/bun here).
bun install -g philschmid/mcp-cli
# Remove the WRONG package if present (gkctou/mcp-cli = filesystem server, not client)
npm uninstall -g mcp-cli
# Confirm
which mcp-cli          # should resolve to ~/.local/bin/mcp-cli
mcp-cli --version      # "mcp-cli v0.3.0"
```
If `which mcp-cli` still points at `~/.nvm/.../bin/mcp-cli` after install, the old `gkctou` package
shadows it — `npm uninstall -g mcp-cli` from the nvm node, then `hash -r`.

## Config file (default path)
`~/.config/mcp-cli/mcp_servers.json` — NOT `~/.config/mcp/`, NOT Hermes `config.yaml`.
Format is Claude-Desktop-compatible:
```json
{
  "mcpServers": {
    "nova3d": { "command": "uvx", "args": ["nova3d-mcp"] },
    "substack-api": { "command": "npx", "args": ["-y","substack-mcp@latest"],
      "env": { "SUBSTACK_PUBLICATION_URL": "https://dbillion.substack.com/" } },
    "lightpanda": { "command": "/home/deeone/bin/lightpanda", "args": ["mcp"] },
    "zapier": { "url": "https://mcp.zapier.com/api/v1/connect" }
  }
}
```

## Aggregate from all your tool configs
Every IDE/client stores servers in a `mcpServers` block. Gather + dedupe:
- `~/.vscode/mcp.json`
- `~/.config/Code/User/mcp.json`  (and `~/.config/Code - OSS/User/mcp.json`)
- `~/.claude.json`, `~/.claude/.mcp.json`
- `~/.cursor/mcp.json`
- `~/.warp/.mcp.json`   (these point at `/tmp/bin/mcp-*.go` — often missing; safe to drop)
- `~/.copilot/mcp.json`, `~/.kiro/settings/mcp.json`, `~/.lmstudio/mcp.json`, `~/.config/mcp-cli/mcp_servers.json`

Python one-liner to merge + dedupe by server name, then write the canonical file.

## Usage
```bash
mcp-cli -c ~/.config/mcp-cli/mcp_servers.json list          # all servers + tools
mcp-cli -c ~/.config/mcp-cli/mcp_servers.json grep "*search*" -d   # glob search w/ desc
mcp-cli -c ~/.config/mcp-cli/mcp_servers.json info neon run_sql   # tool schema
mcp-cli -c ~/.config/mcp-cli/mcp_servers.json call neon run_sql '{"params":{"projectId":"X","sql":"..."}}'
```
Omit `-c` to use the default `~/.config/mcp-cli/mcp_servers.json`.

## Neon MCP — worked example
API key from neon.tech -> Account -> API Keys. Then in the config:
```json
"neon": {
  "command": "npx",
  "args": ["-y","@neondatabase/mcp-server-neon","start","<NEON_API_KEY>"],
  "description": "Neon Postgres MCP. graph (pg_graphql), PostGIS (geo), vector (RAG)."
}
```
Enable extensions (one statement each — no batching):
```bash
P=weathered-forest-50229673
for EXT in vector postgis pg_graphql; do
  mcp-cli -c ~/.config/mcp-cli/mcp_servers.json call neon run_sql \
    "{\"params\":{\"projectId\":\"$P\",\"sql\":\"CREATE EXTENSION IF NOT EXISTS $EXT;\"}}"
done
```
Verify: `SELECT extname FROM pg_extension WHERE extname IN ('vector','postgis','pg_graphql');`

### Neon pitfalls
- Package `@neondatabase/mcp-server-neon` is deprecated but functional; key goes in `args` as
  positional after `start`, not only in env.
- `run_sql` param is camelCase `projectId`.
- Single statement only.
- Apache AGE (`age`) is NOT on Neon -> use `pg_graphql` for graph queries.

## Pruning broken servers
Drop entries whose binaries are missing (`/tmp/bin/mcp-*.go`), packages 404 (`@gumroad/mcp-server`),
or need unavailable runtimes (docker daemon off, gcloud missing). Keep `MCP_DOCKER` if docker can
be reconnected. This keeps `mcp-cli list` clean and fast.
