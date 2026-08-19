# mcp-cli + Notion — Command Patterns

## Reading from stdin vs inline args

`mcp-cli call` reads JSON from **stdin** when no inline args are given. Most Notion tools accept this:

```bash
# Preferred: pipe JSON via stdin
echo '{"data_source_id": "xxx"}' | mcp-cli call notion API-query-data-source

# Also works: inline JSON as single arg
mcp-cli call notion API-query-data-source '{"data_source_id": "xxx"}'
```

For queries with filters, write JSON to a file first to avoid shell escaping issues:

```bash
cat > /tmp/query.json << 'EOF'
{"data_source_id": "xxx", "filter": {"property": "Date", "date": {"equals": "2026-06-24"}}}
EOF
cat /tmp/query.json | mcp-cli call notion API-query-data-source
```

## Enumerating all accessible content

To find what the integration can actually see (databases, pages, etc.):

```bash
mcp-cli call notion API-post-search '{}' > /tmp/notion_all.json
```

Results include `object: "data_source"` entries. Each has an `id` field usable with `API-query-data-source`.

## Working with search results

Search results contain deeply nested JSON. Extract useful fields by writing to a file then reading:

```bash
mcp-cli call notion API-post-search '{"query":"tasks"}' > /tmp/results.json
# Then read /tmp/results.json and parse programmatically
```

**Note**: Piping directly to `python3 -c` may be blocked by security policies (pipe-to-interpreter pattern). Write to `/tmp/` first, then use `read_file` → Python.

## 404 "object_not_found" errors

This means the database exists but isn't shared with the integration bot. Fix: in Notion, open the page → menu `...` → `Connect to` → your integration name.
