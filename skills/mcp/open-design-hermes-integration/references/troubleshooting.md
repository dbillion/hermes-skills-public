# Open Design daemon — troubleshooting table

| Symptom | Cause | Fix |
|---|---|---|
| Daemon won't bind :7456; log shows `ERR_DLOPEN_FAILED` / `NODE_MODULE_VERSION 137 vs 141` | `better-sqlite3` compiled for Node 24 (ABI 137); launcher picked Node 25/22 | `pnpm rebuild better-sqlite3` under Node 24; pin launcher to Node 24 (see `systemd-service.md`) |
| `od mcp` config uses `command: "od"` | `/usr/bin/od` is GNU coreutils octal dump, not Open Design | Use the Node-24 binary + `apps/daemon/dist/cli.js mcp` exactly as `od mcp install hermes --dry-run` reports |
| `opendesign` hangs / OD breaks after editing the launcher | `write_file` followed the `opendesign` symlink and clobbered `apps/daemon/bin/od.mjs` | Move symlink to trash first, then write the real file; restore `od.mjs` to its `#!/usr/bin/env node` + `import dist/cli.js` form |
| MCP tools not callable inline | Tool schema frozen at Hermes session start | Restart Hermes (`/reset` or relaunch); `mcp_open_design_*` appear after |
| `/api/agents` times out on curl/python | Endpoint triggers a full fresh detection sweep of every CLI on PATH | Not a failure — trust `registry.ts` (hermesAgentDef present) + `hermes acp --check` |
| Daemon dies on reboot | Hand-run background process | systemd --user service (see `systemd-service.md`), `loginctl enable-linger` |
