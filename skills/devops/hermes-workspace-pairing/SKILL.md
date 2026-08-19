---
name: hermes-workspace-pairing
description: Run hermes-workspace UI against a running gateway.
---

# Hermes Workspace Pairing (to an existing Hermes Agent)

## When to use
- User cloned `outsourc-e/hermes-workspace` and wants it running against an already-installed/running hermes-agent.
- Phrases: "run hermes-workspace", "connect it to my hermes agent", "bind the workspace to my gateway", "can't open :3000 from my phone", "it says Offline".
- Symptom triage: `:8642` not listening, `:3000` loads but shows Offline/portable mode, Vite "Failed to fetch dynamically imported module".

## ⚠ READ THE REPO README FIRST
The workspace README has an explicit **"Already running hermes-agent? Attach the workspace to it"** section. Follow it before improvising gateway fixes. The one-liner `install.sh` already writes `HERMES_API_URL` + `HERMES_DASHBOARD_URL` into the workspace `.env`; if those are present you usually only need to (a) confirm the gateway API server is bound and (b) start the dashboard + `pnpm dev`. Do not go hunting in `gateway/config.py` before checking the documented attach path.

## Architecture (canonical three services)
- **Gateway :8642** — Hermes Agent core APIs (chat, models, streaming, jobs). The HTTP API server is opt-in.
- **Dashboard :9119** — sessions, skills, config, MCP, jobs UI + JSON APIs. Zero-fork installs need it for the enhanced panes.
- **Workspace :3000** — the web UI (Vite dev server in dev). It is ONLY a UI; the agent is the brain.

They talk over localhost or any reachable network. Workspace → gateway/dashboard over HTTP.

## Steps (attach mode — zero-fork)
1. **Verify the gateway API is bound.** `curl http://127.0.0.1:8642/health` → `{"status":"ok","platform":"hermes-agent",...}`.
   - If `000`/refused: the API server isn't bound. `API_SERVER_ENABLED=true` alone is NOT enough — see Pitfalls.
2. **Start the dashboard** (needs it for sessions/skills/config/jobs): `hermes dashboard --port 9119 --host 127.0.0.1 --no-open`. Wait for `HERMES_DASHBOARD_READY port=9119`. Verify `curl http://127.0.0.1:9119/api/status` → `200` with `"gateway_running":true`.
3. **Point the workspace `.env` at the services** (one-liner install usually did this; verify):
   - `HERMES_API_URL=http://127.0.0.1:8642`
   - `HERMES_DASHBOARD_URL=http://127.0.0.1:9119`
   - If the gateway was started with `API_SERVER_KEY`, the workspace MUST send the same value as `HERMES_API_TOKEN` (else every API call is `401`). Append `HERMES_API_TOKEN=<same key>` to the workspace `.env`.
4. **Run the workspace:** `cd hermes-workspace && pnpm dev` → http://localhost:3000. The startup log should print `mode=zero-fork ... missing=[]`. Confirm live pairing: `curl http://127.0.0.1:3000/api/sessions` returns a real sessions payload (not a fallback/empty error).

## Pitfalls / gotchas
- **`API_SERVER_ENABLED=true` without `API_SERVER_KEY` → :8642 never binds.** In `hermes-agent/gateway/config.py` the api_server platform is only added when `_has_usable_api_server_key()` is true (min 16 chars). With `ENABLED=true` but no key, the gateway starts, serves messaging, but the HTTP API on :8642 silently never binds. Fix: generate a 32-char key (`python3 -c "import secrets;print(secrets.token_urlsafe(24))"`), append `API_SERVER_KEY=<key>` to `~/.hermes/.env`, then `hermes gateway run --replace`. The workspace `.env` then needs `HERMES_API_TOKEN=<same key>`.
- **Stale pidfile blocks gateway start.** If `hermes gateway run` says `Gateway already running (PID x)` but nothing listens on :8642, that PID is dead. Remove `~/.hermes/gateway.pid` and `~/.hermes/gateway.lock`, then retry (or just `hermes gateway run --replace`).
- **`hermes update` → Vite "Failed to fetch dynamically imported module".** During an update the gateway restarts (PID changes). The running `pnpm dev` proxy hits `ECONNREFUSED 127.0.0.1:8642` in that window, the UI flips to `mode=disconnected`, and the browser later fails to re-fetch a now-stale dynamic-import chunk for some `.tsx`. The module file is NOT broken (it serves `200` with valid transformed JS; all its imports resolve). Fix: kill the `pnpm dev` process and start a fresh one, then hard-refresh the browser (Cmd/Ctrl+Shift+R). Do not "fix" the module.
- **Phone/Tailscale can't reach the backend.** The workspace UI binds `0.0.0.0:3000` (page loads), but gateway (:8642) and dashboard (:9119) bind `127.0.0.1` only — so from the phone the UI shows Offline/portable mode. Fix (README "remote host"): set `API_SERVER_HOST=0.0.0.0` in `~/.hermes/.env` and restart gateway; restart dashboard with `--host 0.0.0.0`; in workspace `.env` set `HERMES_API_URL=http://<tailscale-ip>:8642` and `HERMES_DASHBOARD_URL=http://<tailscale-ip>:9119` (get the IP via `tailscale ip -4`); restart `pnpm dev`. Phone then hits `http://<tailscale-ip>:3000`. Add `HERMES_PASSWORD=<strong>` to the workspace `.env` so the UI isn't naked on the tailnet.

## Verification (all must pass)
- `curl :8642/health` → `{"status":"ok",...}`
- `curl :9119/api/status` → `200`, `gateway_running:true`
- `curl :3000/api/sessions` → real sessions payload (live pairing, not fallback)
- Workspace startup log: `mode=zero-fork core=[health,chatCompletions,models,streaming,dashboard] enhanced=[sessions,skills,memory,config,jobs,mcpFallback] missing=[]`

See `references/pairing-recipes.md` for exact copy-paste command sequences: API_SERVER_KEY fix, pidfile clear, post-update Vite restart, the Tailscale remote-access recipe, and the expected healthy startup log.
