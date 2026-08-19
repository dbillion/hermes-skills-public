# notebooklm-mcp Setup Reference

## What It Is

MCP server for Google NotebookLM — chat, source ingestion, audio overviews, citations. Uses Patchright (stealth Chrome) to drive a real browser session with NotebookLM.

- **Repo:** https://github.com/PleasePrompto/notebooklm-mcp
- **Version:** 2.0.0
- **License:** MIT
- **Location (this install):** `/home/deeone/notebooklm-mcp`

## Install Steps (from source)

```bash
git clone https://github.com/PleasePrompto/notebooklm-mcp.git
cd notebooklm-mcp
npm install
npm run build
```

## Known Build Fix (required)

The source has a TypeScript incompatibility with MCP SDK ≥ 1.28. Patch before building:

Remove `resourceTemplates: {},` from `src/index.ts` around line 162:

```typescript
// Before:
capabilities: {
  tools: {},
  resources: {},
  resourceTemplates: {},  // ← remove this line
  prompts: {},
},

// After:
capabilities: {
  tools: {},
  resources: {},
  prompts: {},
},
```

Then build: `npm run build`

## First-Time Auth

The first run requires Google login via a visible browser window. On a headless server, use `xvfb-run`:

```bash
xvfb-run -a node dist/index.js
```

After login, the persistent Chrome profile allows subsequent runs to go fully headless.

## Tools Available (20 total)

- `ask_question` — Chat with Gemini 2.5 through NotebookLM
- `add_notebook` — Register a NotebookLM notebook
- `list_notebooks` — List all notebooks
- `get_notebook` — Get notebook metadata
- `select_notebook` — Set active notebook
- `update_notebook` — Patch notebook metadata
- `remove_notebook` — Remove from local library
- `search_notebooks` — Free-text search
- `get_library_stats` — Aggregate stats
- `list_sessions` — List browser sessions
- `close_session` — Close a session
- `reset_session` — Clear chat history
- `get_health` — Server health check
- `setup_auth` — First-time Google login
- `re_auth` — Switch Google account
- `cleanup_data` — Deep cleanup of all data
- `add_source` — Ingest a source (URL, PDF, text, YouTube, etc.)
- `generate_audio` — Trigger Audio Overview generation
- `get_audio_status` — Check Audio Overview status
- `download_audio` — Save Audio Overview as .m4a

## Connecting to Hermes

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  notebooklm:
    command: "node"
    args: ["/home/deeone/notebooklm-mcp/dist/index.js"]
    timeout: 120
```

Tools appear as `mcp_notebooklm_*`.
