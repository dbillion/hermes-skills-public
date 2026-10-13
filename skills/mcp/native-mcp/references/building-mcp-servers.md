# Building MCP Servers from Source — Pitfalls & Fixes

## MCP SDK Version Compatibility

When building community MCP servers from source, the installed `@modelcontextprotocol/sdk` version may not match what the server's `src/` expects. Common symptoms:

### `resourceTemplates` not recognized (SDK ≥ 1.28)

**Symptom:** TypeScript build fails with:
```
error TS2353: Object literal may only specify known properties, and 'resourceTemplates' does not exist in type '{ ... }'
```

**Cause:** `resourceTemplates` was removed from the SDK's `ServerOptions` type in a newer version than the server was written for.

**Fix:** Remove the `resourceTemplates: {}` line from the server capabilities in `src/index.ts`:

```typescript
// Before:
capabilities: {
  tools: {},
  resources: {},
  resourceTemplates: {},  // ← remove this
  prompts: {},
},

// After:
capabilities: {
  tools: {},
  resources: {},
  prompts: {},
},
```

**Affected servers:** `notebooklm-mcp` v2.0.0 (and potentially others written against older SDK versions).

### Checking SDK version

```bash
cd /path/to/mcp-server
cat node_modules/@modelcontextprotocol/sdk/package.json | grep '"version"'
```

If the server was written for an older SDK but `npm install` pulled a newer one, pin the version:

```bash
npm install @modelcontextprotocol/sdk@<version-from-server's-peer-dep>
```

## npm install ETXTBSY Errors

**Symptom:** `npm install` fails with `spawnSync .../esbuild/bin/esbuild ETXTBSY`

**Cause:** esbuild postinstall script tries to validate its binary while it's still being written (race condition, common on fast machines or after rapid retries).

**Fix:** Clean and retry once:

```bash
rm -rf node_modules package-lock.json
npm install
```

If it persists, it's a transient lock — wait a few seconds and retry.

## npm install Fails in Postinstall Build

Some MCP servers run `npm run build` in a `prepare` script (auto-runs after `npm install`):

```json
"scripts": {
  "prepare": "npm run build"
}
```

If the build fails (e.g., type errors from SDK mismatch), `npm install` itself fails. Fix:

1. First install without running scripts
2. Fix the source
3. Build manually

```bash
npm install --ignore-scripts
# fix src/index.ts
npm run build
```

## Verifying the Built Server

After building, verify the server starts correctly:

```bash
timeout 5 node dist/index.js 2>&1 || true
```

Look for:
- Server initialization messages
- Tool inventory listing
- `✅ MCP Server connected via stdio` (or equivalent)

No crash or "Cannot find module" errors = good.

## Adding Built MCP Servers to Hermes

Once built, add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  notebooklm:
    command: "node"
    args: ["/absolute/path/to/notebooklm-mcp/dist/index.js"]
    timeout: 120
```

Restart Hermes Agent. Tools will appear as `mcp_notebooklm_*`.
