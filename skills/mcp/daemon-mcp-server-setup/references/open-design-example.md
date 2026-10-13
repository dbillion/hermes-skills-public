# Open Design (od) — worked MCP install example

Reproduced from a real session wiring Open Design into Hermes Agent.

## Environment facts (this machine)
- Real OD CLI alias: `/home/deeone/.local/bin/opendesign` (was a symlink chain
  `opendesign -> node_modules/.bin/od -> apps/daemon/bin/od.mjs`; replaced with a
  Node-24-pinned wrapper file — see P1 in SKILL.md).
- OD repo: `/home/deeone/open-design/open-design`
- Daemon entry: `apps/daemon/bin/od.mjs` (shebang `#!/usr/bin/env node`), real
  runtime built file: `apps/daemon/dist/cli.js`.
- Daemon default port: `7456` (HTTP). Health: `GET /api/health` (200 when up).
- Install spec endpoint: `GET /api/mcp/install-info` (returns exact launch command).
- Node: multiple versions via nvm (`/home/deeone/.nvm/versions/node/`): v20.10.0,
  v24.11.0, v24.19.0, v25.6.1, v25.9.0. Repo targets ~24. `better-sqlite3` was
  compiled for Node 24 (ABI 137). Native module load fails on v25 (ABI 141) with
  `ERR_DLOPEN_FAILED`.

## Launch spec the daemon reported (install-info)
```
command: /home/deeone/.nvm/versions/node/v24.19.0/bin/node
args:    [/home/deeone/open-design/open-design/apps/daemon/dist/cli.js,
          mcp, --daemon-url, http://127.0.0.1:7456]
env:     OD_DATA_DIR=/home/deeone/open-design/open-design/.od
```
This is the exact value to register as the Hermes MCP server — NOT `od`
(coreutils octal dump) and NOT a bare `npx` guess.

## Node-24-pinned launcher wrapper (`/home/deeone/.local/bin/opendesign`)
```bash
#!/usr/bin/env bash
export PATH="/home/deeone/.nvm/versions/node/v24.19.0/bin:$PATH"
exec node /home/deeone/open-design/open-design/apps/daemon/bin/od.mjs "$@"
```

## Start the daemon (background) + verify
```bash
/home/deeone/.local/bin/opendesign --no-open        # background=true in agent
sleep 30
ss -tlnp | grep <daemon_pid>                          # confirms LISTEN on 127.0.0.1:7456
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:7456/api/health   # expect 200
```

## Install into Hermes
```bash
opendesign mcp install hermes --dry-run --json        # inspect resolved spec
# then register via surgical Python insertion into ~/.hermes/config.yaml:
#   mcp_servers.open-design:
#     command: /home/deeone/.nvm/versions/node/v24.19.0/bin/node
#     args: ["/home/deeone/open-design/open-design/apps/daemon/dist/cli.js",
#            "mcp", "--daemon-url", "http://127.0.0.1:7456"]
#     env: { OD_DATA_DIR: "/home/deeone/open-design/open-design/.od" }
#     timeout: 120
#     connect_timeout: 60
```

## Gotchas verified this session
- Early `ss | grep 7456` falsely reported "nothing" — the daemon took ~30-60s to
  bind AND a grep race. Use `ss -tlnp | grep <pid>` instead (see P3).
- Node buffers stdout when piped, so the daemon printed nothing yet was healthy
  (main thread in `do_epoll_wait`).
- Writing the launcher via `write_file` while it was a symlink corrupted `od.mjs`.
  Fix: move symlink to trash, write a real wrapper file, restore `od.mjs` from its
  known-good content (the 16-line Node entrypoint).
