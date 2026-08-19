---
name: open-design-desktop-linux
description: Fix Open Design desktop on Linux save bugs and wire agents.
---

# Open Design Desktop on Linux

Use when: the user wants to install/launch/autostart the Open Design desktop app on Linux; the canvas or sheets aren't saving ("Failed to fetch"); an OD agent (deepseek-harness, vela, pi, hermes, claude, codex, ...) shows as unavailable; or OD's web/daemon ports look wrong.

Open Design = local daemon (`:7456` default) + Next.js web (`:4173`/`:3000`) + Electron desktop shell. The desktop discovers the web URL via sidecar IPC and loads it; all `/api/*` calls are proxied by the web to the daemon.

## Hard-won facts (verify, don't guess)

### 1. The canvas/sheet save bug = port mismatch (the #1 issue)
`apps/web/next.config.ts` rewrites `/api/*`, `/artifacts/*`, `/frames/*` to `OD_PORT`, whose **default is 7456**. If the daemon is NOT actually on 7456, every save from the Electron renderer fails with `TypeError: Failed to fetch` (status 0) — the UI renders but nothing persists. The browser log shows `handleConfigPersist ... Failed to fetch` and `projects failed to refresh ... Failed to fetch`.

- `pnpm tools-dev` assigns RANDOM free ports unless you force them. A plain `pnpm tools-dev` often puts the daemon on e.g. `37131` while the web proxies to `7456` → silent save failure with no error dialog.
- **Always launch with explicit ports:** `pnpm tools-dev --daemon-port 7456 --web-port 4173`.
- End-to-end verify (this is exactly what the browser does): `PUT http://127.0.0.1:4173/api/app-config` must return 200. If 200, saves work.
- Config save endpoint is `PUT /api/app-config` (NOT `/api/artifacts`, which 404s). Body shape: `{ agentModels: {...}, installationId, telemetry, ... }`.
- Your other apps occupy `3000` (linkedin-scrape) and `3001` (RedAmon) — never use those for OD. `7456` + `4173` are kept free for OD.

### 2. AppImage is flaky standalone; prefer tools-dev
The packaged AppImage extracts but the Electron window often won't spawn a renderable window reliably here (Electron sandbox + port collisions). `pnpm tools-dev` (daemon + web + desktop together) is the reliable runtime. The AppImage at `~/.local/bin/Open-Design.default.AppImage` is a fine fallback but the idempotent launcher below is what the desktop icon should call.

### 3. Idempotent launcher (avoid EADDRINUSE)
An orphaned OD daemon from a previous session holds `7456` with no web/desktop. Clicking the launcher then does `tools-dev start` → `EADDRINUSE: 7456` → abort ("launching and failing"). Make the launcher check if the daemon is up; if so, start ONLY the desktop window (`tools-dev start desktop`), never re-bind the port. `tools-dev start` with `--daemon-port` when the daemon is already up = "conflict quick-fails". See `templates/launch-open-design.sh`.

### 4. KDE Plasma menu registration
- KDE uses `kbuildsycoca6`, NOT `update-desktop-database` (that's GTK-only). After writing the `.desktop`, run `kbuildsycoca6 --noincremental`, then restart plasmashell (`kquitapp6 plasmashell; plasmashell --no-desktop &`) to repaint the menu.
- `.desktop` `Categories` must be a SINGLE main category (e.g. `Development;`). Two main categories triggers a validator warning and can hide the entry.
- Autostart: copy the same `.desktop` into `~/.config/autostart/` (with `X-KDE-autostart-enable=true`).
- Icon referenced by `Icon=open-design-default` must exist at `~/.local/share/icons/hicolor/512x512/apps/open-design-default.png` (or KDE hides/breaks the entry).

### 5. Stopping the stack — exact PIDs, never pkill -f
On this host, a broad `pkill -f "next dev"` / `pkill -f "tools/dev"` pattern SIGTERMs the agent's OWN shell (exit -15). Extract exact PIDs: `D=$(ss -ltnp | grep 7456 | grep -oE 'pid=[0-9]+' | cut -d= -f2)` and `kill $D`. Never `pkill -f`.

### 6. Hermes agent model fix
OD's Hermes adapter lists models; if `agentModels.hermes.model` is `hy3:free`, Hermes's runtime rejects it (`Model 'hy3:free' not found`) → task stalls. Set it to `default` (uses Hermes CLI config). Patch via `PUT /api/app-config` with `agentModels.hermes={model:"default"}`. `installationId` is analytics-only — don't leave test strings there.

### 7. deepseek-harness (`dsh`)
- Real binary: `@deepseek-ai/dsh` on npm. OD pins **v0.1.0-rc.6** (`requireVersion: true`, `supportedVersions:['0.1.0-rc.6']`). Install: `npm install -g @deepseek-ai/dsh@0.1.0-rc.6` (Node 24 on PATH). The PyPI package `deepseek-harness` is a DIFFERENT package (no binary) — ignore it.
- OD's `compatibilityProbe` preflight requires `~/.dsh/profiles/open-design/package.json` to exist. Create it with `dsh plugin --profile open-design --help` — the `--help` side-effect initializes the profile at `~/.dsh/profiles/open-design`.
- OD's executable resolver does NOT detect the global npm bin (it's a symlink) even when `~/.nvm/.../bin` is in its `searchedDirs`. OD's own diagnostics list `fixActions: [{kind:"setEnv", envKey:"DSH_BIN"}]`. As of this session, setting `DSH_BIN` to the dsh path and restarting the daemon is the documented fix; a `~/.local/bin/dsh` wrapper (real exec file calling the symlink) was tried but OD's scanner STILL reported `not-on-path` — VERIFY `DSH_BIN` works before relying on it. Only treat deepseek-harness as usable once OD reports `available: true`.

## Commands
- Start (idempotent): `bash ~/open-design/launch-open-design.sh` (see `templates/`).
- Agent availability: `curl -s http://127.0.0.1:7456/api/agents | node -e 'const d=JSON.parse(require("fs").readFileSync(0,"utf8"));console.log(d.agents.filter(a=>!a.available).map(a=>a.id+": "+(a.diagnostics||[]).map(x=>x.reason).join(",")))'`
- Daemon health: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:7456/`
- Save probe: `curl -s -X PUT http://127.0.0.1:4173/api/app-config -H 'content-type: application/json' -d '{"installationId":"x","telemetry":false}' -w " %{http_code}"`

## Sharing your Hermes setup (separate repo, not OD)
`dbillion/hermes-setup` (private) is the reproducible reinstall bundle: `config.yaml.template` + `mcp_servers.json.template` (both `${ENV:VAR}` placeholders — NO secrets), `skills/` (~143), `bootstrap.sh`, `scripts/mask_secrets.py`. Another Hermes instance clones it and runs `./bootstrap.sh` after filling `secrets.env`. Audit for leaks: `grep -rniE 'ghp_|gho_|ghu_|sk-[A-Za-z0-9]{12}|AKIA[0-9A-Z]{12}|xox[baprs]-|eyJ[A-Za-z0-9_-]{10}\.' . --include=*.yaml --include=*.json --include=*.template | grep -v '\${ENV:'` — clean if only test-fixture tokens (`gho_abc123`) and redacted samples (`xoxb-Y...OKEN`) remain. Live secret files are gitignored and never tracked.

## Pitfalls
- Never `pnpm tools-dev` without `--daemon-port/--web-port` → random ports → silent save failures.
- Never `pkill -f` the stack → kills your own shell.
- Don't leave `agentModels.hermes.model = "hy3:free"`.
- dsh detection is finicky; trust `DSH_BIN` over PATH scanning, and verify `available:true` before claiming deepseek-harness works.
- `update-desktop-database` does nothing on KDE — use `kbuildsycoca6`.

## References
- `references/deployment-notes.md` — exact error transcripts + verified command sequences from the working session.
