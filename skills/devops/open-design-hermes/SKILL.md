---
name: open-design-hermes
description: Wire Open Design into Hermes as MCP and agent adapter
version: 1
author: hermes
license: mit
metadata:
  hermes:
    tags: ["mcp", "open-design", "nexu-io", "agent-adapter", "integration", "systemd"]
    related_skills: ["native-mcp", "hermes-agent"]
---

# Open Design ↔ Hermes Agent Integration

## When to Use
- User says "install open design", "wire open design to hermes", "od mcp", "open design MCP hermes", or references `nexu-io/open-design` / making Hermes the Open Design agent.
- You are setting up or repairing the OD daemon (silent no-bind, Node ABI crash) or registering its MCP server / agent adapter in Hermes.

Open Design (repo `nexu-io/open-design`) is a local daemon + web UI for AI design
work (164 skills, 150 plugins, 154 design systems). It integrates with Hermes TWO
ways, and you usually want BOTH:

1. **MCP server** (`od mcp`) — OD's 22 design tools become `mcp_open_design_*`
   tools callable *inside* Hermes.
2. **Agent adapter** (`apps/daemon/src/runtimes/defs/hermes.ts`) — OD detects
   Hermes on PATH and can dispatch its runs *to* Hermes as the execution engine
   (over the ACP protocol, `hermes acp --accept-hooks`).

The daemon must be running for either to work. It listens on `127.0.0.1:7456`.

## Critical traps (read before touching anything)

### TRAP 1 — `od` is GNU coreutils, NOT Open Design
`command: "od"` in any config points at `/usr/bin/od` (octal dump). The real OD
CLI is the `opendesign` alias/symlink. The MCP launch command the daemon reports
via `/api/mcp/install-info` is:
```
<node24> <repo>/apps/daemon/dist/cli.js mcp --daemon-url http://127.0.0.1:7456
```
Never hardcode `od`.

### TRAP 2 — better-sqlite3 ABI crash (the #1 boot failure)
OD's `better-sqlite3` is a NATIVE module. If the daemon launches under the wrong
Node major version it dies at startup with:
`ERR_DLOPEN_FAILED ... was compiled against a different Node.js version using NODE_MODULE_VERSION`
Fix: the native module must be rebuilt under the Node version that launches it.
This session's recipe (match the version `package.json`/pnpm expects):
- Find the right Node: `ls ~/.nvm/versions/node/` and pick the one `pnpm`/the
  repo targets (this session used **Node 24.19.0**).
- Rebuild: `cd <repo> && ~/.nvm/versions/node/v<VER>/bin/pnpm rebuild better-sqlite3`
- Pin the launcher to that Node (see TRAP 3).
Symptom that misleads: daemon process is alive but never binds 7456, emits NO
stdout (buffered). Verify the bind with `ss -tlnp | grep 7456`, NOT by "it printed
nothing so it's dead".

### TRAP 3 — `write_file` follows symlinks and can clobber OD's entrypoint
If `opendesign` is a symlink to `apps/daemon/bin/od.mjs`, using `write_file` to put
a wrapper there OVERWRITES `od.mjs` (the real Node entrypoint) and corrupts OD.
Fix: keep `od.mjs` pristine; put the Node-version-pin wrapper at the launcher path
(`~/.local/bin/opendesign`) as a REAL file:
```bash
#!/usr/bin/env bash
export PATH="/home/deeone/.nvm/versions/node/v24.19.0/bin:$PATH"
exec node "/home/deeone/open-design/open-design/apps/daemon/bin/od.mjs" "$@"
```
If you ever clobber it, restore with `git checkout -- apps/daemon/bin/od.mjs` and
move the bad symlink to trash (never hard-delete).

## Wiring steps

### A. Install / fix the daemon (Node-24 pinned)
1. Clone if needed; `corepack enable` + `pnpm install` per repo README.
2. Rebuild `better-sqlite3` under the target Node (TRAP 2).
3. Ensure launcher is a real Node-24-pinned file (TRAP 3).
4. Start it: `opendesign --no-open` (or the launcher). Wait ~12s, then
   `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:7456/api/health`
   → expect `200`.

### B. Register the MCP server in Hermes config (SURGICAL — do not use patch/write_file/yaml.safe_dump)
`~/.hermes/config.yaml` is hand-curated with comments. `patch`/`write_file`/
`yaml.safe_dump` will strip comments or corrupt it. Use a Python script that
reads lines, finds the end of the `mcp_servers:` block, and inserts after the last
existing entry (preserving everything else). Insert exactly this (paths from the
daemon's `/api/mcp/install-info`):
```yaml
  open-design:
    command: "/home/deeone/.nvm/versions/node/v24.19.0/bin/node"
    args:
      - "/home/deeone/open-design/open-design/apps/daemon/dist/cli.js"
      - "mcp"
      - "--daemon-url"
      - "http://127.0.0.1:7456"
    env:
      OD_DATA_DIR: "/home/deeone/open-design/open-design/.od"
```
Validate with `yaml.safe_load` and assert `"open-design" in data["mcp_servers"]`.
Reference script: `references/mcp_config_insert.py`.

### C. Verify MCP with a real stdio handshake (not just "config edited")
Spawn the server command directly and do `initialize` → `tools/list`:
```python
import subprocess, json
p = subprocess.Popen([cmd, *args], stdin=PIPE, stdout=PIPE, env={**os.environ, **env})
# send {"jsonrpc":"2.0","id":1,"method":"initialize",...} then {"method":"tools/list"}
```
Expect `serverInfo` name `open-design` and >=20 tools. Only after this does the
user restart Hermes to get `mcp_open_design_*` inline.

### D. Confirm the agent adapter (Hermes as OD's engine)
- `hermes acp --check` → "Hermes ACP check OK".
- Source `apps/daemon/src/runtimes/registry.ts` imports `hermesAgentDef` into
  `BASE_AGENT_DEFS` → Hermes is a detectable adapter.
- Note: the `/api/agents` route triggers a slow full agent sweep (probes every
  CLI on PATH) and will TIME OUT if you curl it directly. Don't treat the timeout
  as "adapter broken" — trust the source registry + `hermes acp --check`.

### E. Auto-start the daemon (systemd --user)
So both surfaces survive reboot. Template: `references/open-design-daemon.service`.
Enable: `systemctl --user daemon-reload && systemctl --user enable --now
open-design-daemon.service`. Requires Linger=yes for headless survival
(`loginctl show-user $USER -p Linger`).

## Verification checklist
- [ ] `ss -tlnp | grep 7456` shows a LISTEN socket owned by the daemon pid.
- [ ] `curl .../api/health` → 200.
- [ ] `od mcp install hermes --dry-run --json` returns byte-exact launch spec.
- [ ] MCP stdio handshake → `open-design` serverInfo + tools/list >=20.
- [ ] `hermes acp --check` → OK.
- [ ] systemd service `active (running)` + `enabled`.

## Pitfalls summary
- `od` != Open Design CLI (TRAP 1).
- Native module + wrong Node = silent no-bind (TRAP 2).
- `write_file` on a symlinked launcher clobbers OD (TRAP 3).
- Config.yaml edits must be surgical Python, not YAML dump (B).
- `/api/agents` curl times out by design (D).
- MCP tools are frozen into a session at startup; new servers need a Hermes
  restart to appear inline even after config + daemon are correct.
