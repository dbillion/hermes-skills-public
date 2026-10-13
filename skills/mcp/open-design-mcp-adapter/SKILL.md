---
name: open-design-mcp-adapter
description: "Wire Open Design into Hermes as an MCP server and adapter."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [MCP, OpenDesign, Integrations, AgentAdapter, ACP]
    related_skills: [native-mcp, mcporter]
---

# Open Design → Hermes (MCP server + Agent Adapter)

Open Design (OD, `nexu-io/open-design`) is a local daemon (`od` CLI) that exposes
**two** complementary surfaces you usually want at once:

1. **MCP server** → OD's design tools become `mcp_open_design_*` tools *inside*
   Hermes (list projects, create artifacts, start runs, list skills/plugins).
2. **Agent adapter** (`apps/daemon/src/runtimes/defs/hermes.ts`) → OD dispatches
   its 164 skills / 150 plugins *to Hermes* as the execution engine, over ACP
   (`hermes acp --accept-hooks`). So "use OD's skills" == "Hermes runs them."

Both depend on the **daemon being up and healthy** on `127.0.0.1:7456`.

## When to use
- User wants OD's design/carousel/video skills available inside Hermes.
- User wants Hermes to execute OD runs (OD web UI picks "Hermes" as the agent).
- Building a deliverable FROM OD (e.g. a travel carousel) — see "Driving OD directly".

## Step 1 — Daemon must be Node-24 pinned (recurring footgun)
OD's `better-sqlite3` is compiled for **Node 24 (ABI 137)**. Launching under
Node 25 (ABI 141) or 22 crashes on boot with `ERR_DLOPEN_FAILED`. Also note:
the bare `od` on PATH is often GNU coreutils' octal dump — use the real launcher
(an alias, e.g. `opendesign`, pointing at `apps/daemon/bin/od.mjs`).

Reliable launch wrapper (pin Node 24, set data dir):
```bash
#!/usr/bin/env bash
export PATH=/home/deeone/.nvm/versions/node/v24.19.0/bin:$PATH
export OD_DATA_DIR=/home/deeone/open-design/open-design/.od
exec node /home/deeone/open-design/open-design/apps/daemon/bin/od.mjs "$@"
```
For durability, run it as a **systemd --user service** (Type=simple,
`WantedBy=default.target`) so it survives reboot (needs `loginctl enable-linger`
or already set). Verify: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:7456/api/health` → `200`.

## Step 2 — Register the MCP server (resolver + verify, don't hand-edit blindly)
`od mcp install hermes --dry-run --json` resolves the **byte-exact** launch spec
(command = Node-24 bin + `apps/daemon/dist/cli.js mcp --daemon-url <url>`,
env `OD_DATA_DIR`). It refuses to auto-edit Hermes config ("manual setup
required") → insert the block yourself.

**CRITICAL:** never use `patch` / `write_file` / `yaml.safe_dump` on
`~/.hermes/config.yaml` — they strip comments or reorder keys. Use surgical
Python text-insertion (read lines, find the last `mcp_servers:` entry, insert
after it). See `references/open-design-mcp.md` for the exact block + insertion
snippet.

Config block:
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

**Verify with a real stdio JSON-RPC handshake** (config edit alone is NOT proof):
spawn the exact `command`+`args`, send `initialize` then `tools/list` as
**newline-delimited JSON** (OD speaks NDJSON, NOT LSP `Content-Length` framing —
LSP framing makes it hang). Expect `serverInfo: open-design v0.2.0` and ~22
tools. Then **restart Hermes** so `mcp_open_design_*` load inline.

> A 403 from an *upstream API* during the handshake is still a PASS for the MCP
> transport — only credentials are missing.

## Step 3 — Confirm the agent adapter (Hermes as OD's engine)
`hermes` must be on PATH. Run `hermes acp --check` → "Hermes ACP check OK". The
daemon auto-runs `detectAgents()` at boot and loads `hermes.ts`. The adapter
auto-discovers Hermes's installed models and supports `acp-merge` MCP injection.

## Driving OD directly (when /api/runs fails headlessly)
Probe the daemon over HTTP (port 7456): `/api/health`, `/api/projects`,
`/api/skills` (162 skills), `/api/plugins`. Skill **assets are directly usable**:
read `skills/<id>/SKILL.md` + `example.html` and build the artifact yourself.
e.g. `card-xiaohongshu` is a real swipeable 1080×1440 (3:4) carousel template —
author HTML/Tailwind from its `example.html`.

**Pitfall:** `POST /api/runs` returns `202` (runId) but the run **executes via
an agent adapter** and can end `status: failed` when no adapter is reachable
headlessly. If a `start_run` fails, fall back to reading the skill assets and
producing the deliverable directly — the skill content is real even when the
orchestration pipeline isn't.

## Media for designs (video / images)
- **fal.ai** (`fal-generate`, `fal-kling-o3`, `fal-video-edit`): needs a fal.ai
  key, sent as `Authorization: Key <id:secret>`. Account can be **locked
  (TOP_UP)** → `403 {"detail":"User is locked. Reason: TOP_UP."}` until topped
  up. That's an account state, not a key-format bug.
- **Pexels** (free API key, instant at pexels.com/api): real licensed stock.
  `GET https://api.pexels.com/videos/search?query=<q>&per_page=5&min_width=1080`
  with `Authorization: <key>`; pick a `video_files[].link` with `width>=1080`
  and `curl -L` it. Reliable fallback when fal.ai is locked.

## Deliverable layout
OD artifacts live under `<OD_DATA_DIR>/artifacts/<name>/` (e.g.
`.od/artifacts/travel-carousel/index.html` + dropped `*.mp4`). Open via
`file://` to preview. A restart of Hermes does NOT affect the OD daemon — it
runs independently and the MCP/ACP wiring reconnects automatically.

## Related
- `native-mcp` — general MCP client config + verification (the parent technique).
- `mcporter` — ad-hoc MCP calls from terminal without config.
