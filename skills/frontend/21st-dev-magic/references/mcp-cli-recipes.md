# mcp-cli recipes for 21st.dev magic

Scoped config (no literal key; key comes from the shell env var `TWENTY_FIRST_DEV_KEY`):
```json
{
  "mcpServers": {
    "magic-21st": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@21st-dev/magic@latest"]
    }
  }
}
```
Save as `/tmp/magic-scope.json`.

## Set the key (env only)
```bash
export TWENTY_FIRST_DEV_KEY="21st_sk_..."
export API_KEY="$TWENTY_FIRST_DEV_KEY"
```

## Search (free, find component id)
```bash
mcp-cli -c /tmp/magic-scope.json call magic-21st/search \
  '{"query":"bento grid responsive cards with icons and badges","framework":"react"}'
```

## Get component code (free, 2/day) — port this
```bash
mcp-cli -c /tmp/magic-scope.json call magic-21st/get_component '{"id":622}'
# returns componentCode (tsx), demoCode, previewUrl
```

## Generate (PAID on free tier — returns locked:true)
```bash
mcp-cli -c /tmp/magic-scope.json call magic-21st/generate \
  '{"prompt":"...","mode":"sketch","variantCount":3}'
# free tier: {"structuredContent":{"locked":true,"reason":"generation_limit_reached"}}
```

## Check quota
```bash
mcp-cli -c /tmp/magic-scope.json call magic-21st/get_usage '{}'
# freeRetrievalsPerDay: 2, freeRetrievalsRemaining: N
```

Notes:
- Always pass the key as `TWENTY_FIRST_DEV_KEY`/`API_KEY` env to the `mcp-cli` process; never put the literal on the command line.
- `generate` does NOT consume the daily retrieval quota — it is a separate paid gate.
- Scope `mcp-cli` with `-c` (per policy: never bare `mcp-cli`).
