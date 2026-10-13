# Neon CLI / API Cookbook (verified commands)

## Auth
- `neon auth` — browser OAuth (e.g. <YOUR_EMAIL>). May log into the PERSONAL org only.
- API key: `neon` commands accept `--api-key <key>` when the key is needed for API calls.

## Project / org discovery
- `neon projects list` — only personal org by default.
- `neon orgs list` — lists orgs, e.g. `org-crimson-bush-48892848` ("Vercel: dbillion's projects").
- `neon projects list --org-id org-crimson-bush-48892848` — finds Vercel-managed projects like `weathered-forest-50229673`.

## Enable Lakebase (API preload — CLI cannot)
```bash
neon api POST /projects/weathered-forest-50229673 -X PATCH -d '{
  "project": { "settings": { "preload_libraries": {
    "enabled_libraries": ["timescaledb","pg_cron","pg_partman_bgw",
      "rag_bge_small_en_v15","rag_jina_reranker_v1_tiny_en",
      "lakebase_vector","lakebase_text"]
  }}}
}'
# Verify:
neon api GET /projects/weathered-forest-50229673
```

## Restart compute so preloads load
```bash
# endpoint id from: neon api GET /projects/<id>/endpoints
neon api POST /projects/<id>/endpoints/<endpointId>/actions/restart
```

## SQL execution
```bash
# Working CLI SQL path (role neondb_owner):
neon psql --project-id weathered-forest-50229673 --role-name neondb_owner -- -c "SHOW shared_preload_libraries;"
# Confirm output contains: lakebase_vector,lakebase_text
# NOTE: `neon sql` is NOT a valid subcommand in neon 2.x.
```

## MCP alternative (if configured)
`neon` MCP tool `run_sql` form:
```
mcp-cli -c ~/.config/mcp-cli/mcp_servers.json call neon run_sql \
  '{"params":{"projectId":"weathered-forest-50229673","sql":"<query>"}}'
```
