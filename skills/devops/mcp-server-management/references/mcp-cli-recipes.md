# mcp-cli recipes — driving MCP servers outside Hermes/OpenClaw

`mcp-cli` is a standalone binary (v0.3.0+) that talks to servers registered in
`~/.config/mcp-cli/mcp_servers.json` (and its own default config). It is the
right tool when a server (neon, context7, stitch) is NOT in Hermes's
`~/.hermes/config.yaml mcp_servers`. It is functional — do not assume it is
silent/broken (that was a prior misdiagnosis from invoking it without `-c`).

## Invocation
```bash
CFG=~/.config/mcp-cli/mcp_servers.json
mcp-cli -c $CFG                                              # list servers
mcp-cli -c $CFG info <server>                               # server + tools
mcp-cli -c $CFG info <server>/<tool>                        # tool schema
mcp-cli -c $CFG call <server> <tool> '<json-args>'          # call (space form)
mcp-cli -c $CFG call <server>/<tool> '<json-args>'          # call (slash form)
```
- JSON args = LAST positional string, single-quoted; escape inner `'` as `'\''`.
- `mcp-cli info <server>/<tool>` ALSO needs `-c`, else it reads the wrong config
  and reports `SERVER_NOT_FOUND`.

## Neon MCP — managed Postgres (project id from user)
```bash
PID=weathered-forest-50229673
# version / connectivity
mcp-cli -c $CFG call neon run_sql \
  '{"params":{"projectId":"'"$PID"'","sql":"SELECT version();"}}'

# enable extensions (each its own call; single statement only)
mcp-cli -c $CFG call neon run_sql \
  '{"params":{"projectId":"'"$PID"'","sql":"CREATE EXTENSION IF NOT EXISTS postgis;"}}'
mcp-cli -c $CFG call neon run_sql \
  '{"params":{"projectId":"'"$PID"'","sql":"CREATE EXTENSION IF NOT EXISTS vector;"}}'

# create a table with PostGIS + pgvector columns (persists)
mcp-cli -c $CFG call neon run_sql \
  '{"params":{"projectId":"'"$PID"'","sql":"CREATE TABLE IF NOT EXISTS graph_nodes (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), label TEXT NOT NULL, geom geometry(Point,4326), embedding vector(1536));"}}'

# VERIFY it actually persisted (never trust a bare [] response)
mcp-cli -c $CFG call neon run_sql \
  '{"params":{"projectId":"'"$PID"'","sql":"SELECT table_name FROM information_schema.tables WHERE table_schema='"'"'public'"'"' AND table_name='"'"'graph_nodes'"'"';"}}'
```

### Gotchas (proven this session)
- **Single statement only.** `run_sql` prepares one statement; multiple commands
  error: "cannot insert multiple commands into a prepared statement". Split DDL
  and call once per statement.
- **`[]` is ambiguous.** Returned for success AND for some silent no-ops. Always
  re-query `information_schema.tables` (or `SELECT count(*) FROM <t>`) to confirm
  DDL persisted. Several bulk CREATEs appeared to "succeed" (empty `[]`) but did
  not all land — apply + verify each, individually.
- Available extensions on Neon: `postgis`, `postgis_topology`, `vector`,
  `pg_graphql`. Confirmed present; DDL using `geometry(Point,4326)`,
  `vector(1536)`, `JSONB` all persist.
- Optional params: `branchId`, `databaseName`.

## Context7 MCP — research a library before integrating
```bash
# 1) resolve (needs BOTH libraryName AND query keys)
mcp-cli -c $CFG call context7/resolve-library-id \
  '{"libraryName":"mastra","query":"mastra agent framework"}'
# -> "/mastra-ai/mastra"  (High reputation, 18k+ snippets) is the canonical ID

# 2) fetch docs
mcp-cli -c $CFG call context7/get-library-docs \
  '{"context7CompatibleLibraryID":"/mastra-ai/mastra","topic":"agents rag memory workflows","tokens":6000}'
```
- Sending only `libraryName` (or only `query`) -> input-validation error.
- For agentic TS backends, default to `/mastra-ai/mastra`.

## Verification snippet (bash)
After applying schema, confirm expected tables exist:
```bash
for t in users articles graph_nodes graph_edges agent_history map_features; do
  mcp-cli -c $CFG call neon run_sql \
    '{"params":{"projectId":"'"$PID"'","sql":"SELECT 1 FROM information_schema.tables WHERE table_name='"'"''"$t"''"';"}}'
done
```
