---
name: open-design-hermes-integration
description: "Wire Open Design od MCP + Hermes adapter; fix daemon."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mcp, open-design, od, integration, daemon, node, systemd]
---

# Open Design ↔ Hermes Integration

## When to Use
Use when the user wants to (a) install Open Design's `od mcp` server into Hermes,
(b) make Hermes the agent that executes Open Design skills/plugins (the OD Hermes
adapter), (c) start/keep the Open Design daemon healthy, or (d) fix a dead :7456
port, `ERR_DLOPEN_FAILED`, the `/usr/bin/od` coreutils collision, or symlink
launcher corruption.

Open Design (`od`) is a local daemon + web UI that delegates its **agent loop** to
external code-agent CLIs. It ships a first-class **Hermes adapter** and an **MCP
server**, so Hermes plugs in two ways at once:

1. **MCP server** (`od mcp`): 22 tools (`list_projects`, `get_active_context`,
   `create_artifact`, `write_file`, `start_run`, `list_skills`, `list_plugins`,
   `list_agents`, …) become `mcp_open_design_*` tools *inside* Hermes.
2. **Agent adapter** (Hermes as OD's brain): in the OD web UI you pick **Hermes**
   to execute OD's 164 skills + 150 plugins + 154 design systems. OD drives Hermes
   over **ACP** (`hermes acp --accept-hooks`).

Both depend on the OD **daemon** being up on `http://127.0.0.1:7456`. If the daemon
is down, MCP tools return nothing and the adapter can't dispatch.

> Generic MCP-into-Hermes config mechanics (why `~/.hermes/config.yaml` can't be
> edited with `patch`/`write_file`/`yaml.safe_dump`) live in the `native-mcp` skill.
> This skill covers the **Open Design specific** parts.

## Decision tree

- "install Open Design MCP in Hermes" / "wire od into hermes" → Phase A + B.
- "make Hermes the agent for Open Design" / "agent adapter" → Phase C (usually already satisfied).
- "OD daemon won't start" / "ERR_DLOPEN_FAILED" / port 7456 dead → Phase D.
- "survive reboot" → Phase E.

## Phase A — Daemon must be running (prereq for everything)

The OD MCP server is a **stdio proxy** to a running daemon. Start the daemon
(pinned to Node 24 — see Phase D for why) and confirm:

```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" --max-time 5 http://127.0.0.1:7456/api/health
ss -tlnp 2>/dev/null | grep 7456
```

## Phase B — Install the MCP server

`od mcp install hermes` is the intended tool, but it **refuses to auto-edit
Hermes' config** ("manual setup required. Hermes config format is unverified").
It WILL give you the byte-exact launch spec, so always dry-run first:

```bash
opendesign mcp install hermes --dry-run --json
# -> {"launchSpec":{"command":"/path/to/node24/bin/node",
#      "args":["/repo/apps/daemon/dist/cli.js","mcp","--daemon-url","http://127.0.0.1:7456"],
#      "env":{"OD_DATA_DIR":"/repo/.od"}}}
```

Then register it yourself (do **not** use `patch`/`write_file`/`yaml.safe_dump`
on `~/.hermes/config.yaml` — they strip comments or corrupt the file; see
`native-mcp` skill `verify-and-edit-mcp.md`). Surgical Python insertion:

```python
path = "/home/deeone/.hermes/config.yaml"
lines = open(path).readlines()
# insert after the last existing mcp_servers entry (e.g. mcp-cli)
# block = the YAML from the dry-run snippet, indented under mcp_servers:
#   open-design:
#     command: "<node24>/bin/node"
#     args: ["<repo>/apps/daemon/dist/cli.js", "mcp", "--daemon-url", "http://127.0.0.1:7456"]
#     env: { OD_DATA_DIR: "<repo>/.od" }
```

**The `command` is NOT `od`.** `/usr/bin/od` is GNU coreutils' octal dump. Use the
real Node-24 binary running `apps/daemon/dist/cli.js mcp`, exactly as the dry-run
reports. The `opendesign` alias (symlink → `node_modules/.bin/od` →
`apps/daemon/bin/od.mjs`) is the safe human-facing identifier.

## Phase C — Agent adapter (usually already satisfied)

OD's repo already registers Hermes: `apps/daemon/src/runtimes/registry.ts`
imports `hermesAgentDef` (`apps/daemon/src/runtimes/defs/hermes.ts`) into
`BASE_AGENT_DEFS`. The adapter talks ACP and auto-discovers your models. Verify:

```bash
command -v hermes                 # must be on PATH
hermes acp --check                # "Hermes ACP check OK"
```

OD runs `detectAgents()` at boot, so once `hermes` is on PATH it appears as a
selectable agent. No code change needed. (Note: `/api/agents` triggers a *full
fresh detection sweep* of every CLI on PATH and can **timeout** on curl/python —
that's the endpoint being slow, not a missing adapter. Trust `registry.ts` + `hermes acp --check`.)

## Phase D — Troubleshooting the daemon

### better-sqlite3 Node-ABI crash (ERR_DLOPEN_FAILED)
The daemon's native `better-sqlite3` is compiled for **Node 24 (ABI 137)**. If the
`opendesign` launcher resolves `node` to **v25 (ABI 141)** or **v22**, the daemon
dies on boot with `ERR_DLOPEN_FAILED` and never binds 7456.

Fix (run with Node 24 active):
```bash
export PATH=/home/deeone/.nvm/versions/node/v24.19.0/bin:$PATH
cd <repo>
pnpm rebuild better-sqlite3      # recompiles for the active node
```
Then **pin the launcher** to Node 24 (see `references/systemd-service.md`) so it
never picks up v25 again.

### `write_file` follows symlinks — LAUNCHER CORRUPTION PITFALL
`~/.local/bin/opendesign` is a **symlink** chain
(`node_modules/.bin/od` → `apps/daemon/bin/od.mjs`). If you `write_file` a wrapper
*to that path*, the tool follows the symlink and **overwrites `od.mjs`** (the real
Node entrypoint) with your wrapper text → OD hangs/corrupts.
**Always move the symlink to trash FIRST, then write the real file:**
```bash
mv /home/deeone/.local/bin/opendesign /home/deeone/.trash/opendesign.symlink.$(date +%s)
# now write_file /home/deeone/.local/bin/opendesign  (a real file, not a symlink)
```
And restore `od.mjs` to its correct content if it was clobbered:
```js
#!/usr/bin/env node
import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
const entryDir = dirname(fileURLToPath(import.meta.url));
const distEntry = resolve(entryDir, "../dist/cli.js");
if (!existsSync(distEntry)) throw new Error(`dist entry not found at ${distEntry}`);
await import(pathToFileURL(distEntry).href);
```

## Phase E — Durable auto-start (systemd --user)

Hand-run daemons die on reboot. Create `~/.config/systemd/user/open-design-daemon.service`
(see `references/systemd-service.md`) pinned to Node 24, then:
```bash
systemctl --user daemon-reload
systemctl --user enable --now open-design-daemon.service
systemctl --user status open-design-daemon.service
```
Requires `loginctl enable-linger $USER` for it to survive logout (already set on this host).

## Verify before claiming success

Config edit alone proves nothing. Run a real stdio JSON-RPC handshake
(`scripts/verify-od-mcp.mjs`) — `initialize` → `open-design v0.2.0`,
`tools/list` → 22 tools, and a live `list_projects` call returning real data.

## Final step for the user

MCP tools only become *natively callable* (`mcp_open_design_*`) after Hermes
restarts (`/reset` or relaunch) — the tool schema is frozen at session start. Say
so explicitly; don't claim the tools are live inline until a restart happens.

## Support files
- `references/systemd-service.md` — the full systemd unit + Node-24 pin.
- `scripts/verify-od-mcp.mjs` — deterministic stdio handshake + live `list_projects`.
- `references/troubleshooting.md` — symptom → cause → fix table (ABI crash, od collision, symlink corruption, port-dead).
- `references/instagram-carousel-skills.md` — verified OD skill ids + `start_run` recipe for building a Java DSA / Instagram carousel (swipeable-card skills, daemon health check, `list_skills` JSON-parsing note).
