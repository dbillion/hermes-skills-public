# Open Design — packaging & troubleshooting transcripts

Condensed, validated command recipes from a real EndeavourOS/KDE deployment.
Companion to the Packaging + desktop-launch section in SKILL.md.

## 1. AppImage build (allow-scripts guard)

Symptom: `pnpm tools-pack linux build --to appimage` dies with
`npm error code EALLOWSCRIPTS / --allow-scripts is not allowed in project-scoped installs`.

Fix — project `.npmrc` (repo root), minimal allow-list, guard stays on:
```ini
allow-scripts[]=app-builder-bin
allow-scripts[]=electron-builder
allow-scripts[]=@electron/rebuild
allow-scripts[]=better-sqlite3
```
If a later build fails naming a new package, append just that one.

## 2. Missing Electron binary

Symptom: desktop Electron process extracts but never spawns; or `tools-dev`
errors `Electron failed to install correctly`. `apps/desktop/node_modules/electron/dist/electron`
is absent even though `~/.cache/electron/electron-v41.3.0-linux-x64.zip` exists.

Fix (pnpm rebuild may no-op, so run the script directly):
```sh
cd /home/deeone/open-design/open-design/apps/desktop/node_modules/electron
node install.js          # extracts the cached zip -> dist/electron (~206MB)
```
Verify: `ls -la dist/electron` shows the binary.

## 3. Canvas / sheets / settings "Failed to fetch" (save bug)

Root cause: `tools-dev` (no flags) probes a random daemon port; web
`next.config.ts` rewrites `/api/*` -> `OD_PORT` (default 7456). Mismatch ->
renderer `PUT /api/app-config` hits 7456 (refused) -> "Failed to fetch".

Reproduce / verify (the browser does this exact call):
```sh
curl -s -X PUT http://127.0.0.1:4173/api/app-config \
  -H 'content-type: application/json' -d '{"installationId":"probe","telemetry":false}' \
  -w "\nHTTP %{http_code}\n"
# 200 = saves work; connection-refused/empty = port mismatch
```
Fix — relaunch with aligned ports (7456 canonical; 4173 free here):
```sh
pnpm tools-dev --daemon-port 7456 --web-port 4173
```
Bake into `~/open-design/launch-open-design.sh` so the desktop icon never
regresses. The daemon log will show `trustedWebOriginPort: 4173` and
`url: "http://127.0.0.1:7456"`.

Note: `PUT /api/app-config` is the real save endpoint (NOT `/api/artifacts`;
that path 404s — don't be misled). Project-scoped run lists need
`?projectId=`. `GET /api/active` returns the current active run without a
project scope.

## 4. KDE Plasma desktop icon

`update-desktop-database` is GTK-only — KDE ignores it.
```sh
kbuildsycoca6 --noincremental                       # rebuild menu cache
# .desktop Categories must be a SINGLE main category, e.g. Development;
# (Development;Utility; makes KDE flag/hide it)
# restart panel if it doesn't repaint:
kquitapp6 plasmashell; sleep 2; plasmashell --no-desktop &
```
Icon path: `~/.local/share/icons/hicolor/512x512/apps/open-design-default.png`.
Entry: `~/.local/share/applications/open-design-default.desktop`.

## 5. Hermes model inside OD

Symptom: task appears active (`GET /api/active` shows it) but Hermes never
responds. Daemon log: `Hermes -> not_found_model: Model 'hy3:free' not found`.

Fix — set `agentModels.hermes.model` to `default` (uses Hermes CLI config):
```sh
# fetch current, set hermes.model="default", PUT it back
curl -s -X PUT http://127.0.0.1:7456/api/app-config \
  -H 'content-type: application/json' --data-binary @fixed-config.json
```
The app-config shape for agent models:
`agentModels: { "hermes": {"model":"default"}, "kiro":{"model":"default"}, ... }`.
