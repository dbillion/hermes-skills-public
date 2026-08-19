# Neon MCP via mcp-cli — quirks & confirmation recipes

## Reliable invocation
```
mcp-cli -c ~/.config/mcp-cli/mcp_servers.json call neon run_sql \
  '{"params":{"projectId":"<ID_STRING>","sql":"<ONE STATEMENT>"}}'
```
- Project id MUST be a quoted string, e.g. `"weathered-forest-50229673"`. A number fails silently.
- `neon` server lives in `~/.config/mcp-cli/mcp_servers.json`, NOT the default mcp-cli config.

## Confirm extensions are enabled (run after enabling)
```
SELECT extname FROM pg_extension WHERE extname IN ('postgis','vector','pg_graphql','postgis_topology');
```
Expected: rows for postgis, vector, pg_graphql (and postgis_topology if used).

## Confirm tables exist (RE-QUERY — never trust `[]`)
```
SELECT table_name FROM information_schema.tables
WHERE table_schema='public' AND table_type='BASE TABLE'
AND table_name NOT IN ('spatial_ref_sys') ORDER BY table_name;
```

## Confirm a specific table's columns (before seeding/querying)
```
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name='<table>' ORDER BY ordinal_position;
```

## One-statement loop pattern (bash)
```bash
for sql in \
  "CREATE TABLE IF NOT EXISTS users (id UUID PRIMARY KEY DEFAULT gen_random_uuid())" \
  "CREATE TABLE IF NOT EXISTS articles (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), title TEXT)" ; do
  mcp-cli -c ~/.config/mcp-cli/mcp_servers.json call neon run_sql \
    "{\"params\":{\"projectId\":\"<ID>\",\"sql\":\"$sql\"}}" 2>&1 | grep -E "text|Error" | head -2
done
```

## Known silent-failure modes
- Multiple statements in one `sql` -> `NeonDbError: cannot insert multiple commands into a prepared statement`.
- `[]` returned but table missing -> statement didn't persist (extension not active, or a later statement
  in the same loop dropped it). Re-run the single statement and re-query.
- `CREATE EXTENSION IF NOT EXISTS x` returns `[]` even when already present — harmless.

## Enable extensions individually
```
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_graphql;
```
(each as its own call)
