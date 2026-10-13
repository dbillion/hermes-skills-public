# Worked example: Open Design (github.com/nexu-io/open-design)

Open Design is a local daemon + web UI for design tasks. It exposes TWO
integration points with Hermes (see parent skill for the generic flow).

## Repo layout (developer install)
- Repo: `/home/deeone/open-design/open-design` (pnpm monorepo, apps/daemon is the daemon + `od` bin).
- Real CLI entrypoint: `apps/daemon/bin/od.mjs` (shebang `#!/usr/bin/env node`).
- Non-colliding launcher alias: `opendesign` → `/home/deeone/.local/bin/opendesign`.
- Daemon data dir: `<repo>/.od` (OD_DATA_DIR).
- Daemon default port: `127.0.0.1:7456`.

## Direction 1 — OD MCP server → Hermes (gives Hermes OD's design tools)
1. Start daemon: a Node-24-pinned wrapper (e.g. `/tmp/od-launch.sh`) running
   `node apps/daemon/bin/od.mjs --no-open --host 127.0.0.1 --port 7456`.
2. Verify health: `curl ... /api/health` → 200.
3. Launch spec: `od mcp install hermes --dry-run --json` or
   `GET /api/mcp/install-info` returns:
   ```
   command: <node24>/bin/node
   args:    [<repo>/apps/daemon/dist/cli.js, mcp, --daemon-url, http://127.0.0.1:7456]
   env:     OD_DATA_DIR: <repo>/.od
   ```
   (`od mcp install hermes` itself prints "manual setup required" — splice by hand.)
4. Insert `mcp_servers.open-design` into `~/.hermes/config.yaml` (surgical Python,
   not yaml.safe_dump). 22 tools registered as `mcp_open_design_*`.
5. Verify: stdio handshake → `initialize` → `serverInfo: open-design v0.2.0`,
   `tools/list` → 22 tools, live `list_projects` returns the user's real projects.

## Direction 2 — Hermes → OD agent adapter (OD drives Hermes via ACP)
- Repo ships `apps/daemon/src/runtimes/defs/hermes.ts`. It runs
  `hermes acp --accept-hooks`, auto-discovers installed models, injects MCP via
  `acp-merge`.
- Activates automatically when `hermes` is on PATH (`/home/deeone/.local/bin/hermes`).
- Result: inside the OD web UI, Hermes is selectable as the agent that executes
  OD's 164 skills + 150 plugins with live streaming.

## Content packs OD exposes (usable through either direction)
- `skills/`: 164 design skills (brandkit, design-md, apple-hig, deck builders, copywriting…).
- `plugins/`: ~150 bundled + community (hallmark, humanize-ppt, clone-audit…).
- `design-systems/`: 154 brand packs (Apple, Airbnb, BMW, Canva…).
- `design-templates/`: 115 (decks, dashboards, reports, landing pages).
- `craft/`: universal brand-agnostic craft rules (typography, color, accessibility, anti-ai-slop).

## The two pitfalls that actually bit (full fixes in parent skill)
- **Node ABI**: `better-sqlite3` built for Node 24 (ABI 137) crashed under Node 25
  (ABI 141) with `ERR_DLOPEN_FAILED`. Fixed by `pnpm rebuild better-sqlite3`
  under Node 24 and pinning the `opendesign` launcher to Node 24.19.0.
- **Symlink corruption**: `write_file` followed the `opendesign` symlink chain and
  overwrote `od.mjs` with a bash wrapper. Rule learned: trash the symlink first,
  then write the real launcher file.
