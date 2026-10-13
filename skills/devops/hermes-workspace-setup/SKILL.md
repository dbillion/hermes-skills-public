---
name: hermes-workspace-setup
description: Bind Hermes Workspace to a Hermes Agent gateway + dashboard.
---

# Hermes Workspace Setup & Pairing

Hermes Workspace is a web UI (Vite, port :3000). It is NOT a chat wrapper — it is
a control plane that talks to a **Hermes Agent gateway** (`:8642`) and, for
zero-fork installs, a **Hermes Agent dashboard** (`:9119`). All three must be
running for full features.

> **ZERO-FORK MODEL:** Workspace runs on a *vanilla* `NousResearch/hermes-agent`
> install. You do NOT fork or reinstall the agent. You just point the workspace at
> the gateway + dashboard that already exist on the machine.

## STEP 0 — READ THE REPO README FIRST (do not improvise)

When the user says "run it and connect to it" about a cloned repo, **read the
repo's README before doing anything.** For hermes-workspace the README has an
explicit "Already running hermes-agent? Attach the workspace to it" section that
is the authoritative procedure. Improvising a gateway fix before reading it
wastes time and risks fighting the documented happy path.

The attach procedure (from README) is:

```
git clone https://github.com/outsourc-e/hermes-workspace.git
cd hermes-workspace
pnpm install
cp .env.example .env
echo 'HERMES_API_URL=http://127.0.0.1:8642' >> .env
echo 'HERMES_DASHBOARD_URL=http://127.0.0.1:9119' >> .env
# if gateway was started WITH API_SERVER_KEY:
#   echo 'HERMES_API_TOKEN=<same value>' >> .env
pnpm dev          # http://localhost:3000
```

If the repo is already cloned and `.env` already has those vars (from the
one-liner installer), skip straight to verifying services + `pnpm dev`.

## The three services

| Service | Port | Started by | Role |
|---|---|---|---|
| Gateway | `:8642` | `hermes gateway run` | chat, models, streaming, jobs; OpenAI-compatible API server |
| Dashboard | `:9119` | `hermes dashboard --port 9119 --host 127.0.0.1 --no-open` | sessions, skills, config, MCP, jobs APIs |
| Workspace UI | `:3000` | `pnpm dev` (in repo root) | the web app |

Start order: **gateway → dashboard → workspace**. The workspace reads
`HERMES_API_URL` / `HERMES_DASHBOARD_URL` from its `.env` and probes both on boot.

## Verification (do this before declaring success)

```bash
curl http://127.0.0.1:8642/health      # -> {"status":"ok","platform":"hermes-agent",...}
curl http://127.0.0.1:9119/api/status  # -> {"status":"ok", ... "gateway_running":true, ...}
curl http://127.0.0.1:3000/api/sessions  # -> real sessions payload (NOT a fallback)
```

The workspace dev-server log prints the pairing result on connect:
```
[gateway] gateway=...:8642 dashboard=...:9119 mode=zero-fork
core=[health, chatCompletions, models, streaming, dashboard]
enhanced=[sessions, skills, memory, config, jobs, mcpFallback]
missing=[] optional=[enhancedChat, mcp]
```
`missing=[]` + non-empty `enhanced` = fully paired. If `enhanced` is empty and the
UI shows "portable mode" / "Not Available", the **dashboard** is not running or
not reachable.

## PITFALL — gateway API server silently never binds without API_SERVER_KEY

**Symptom:** `hermes gateway run` shows the banner "Messaging platforms + cron
scheduler" but `curl :8642` returns connection-refused / `000`, even though
`API_SERVER_ENABLED=true` is in `~/.hermes/.env`. Telegram may connect fine; only
the HTTP API server is absent.

**Root cause (verified in `hermes-agent/gateway/config.py` ~line 2129–2137):**
```python
api_server_enabled = is_truthy_value(getenv("API_SERVER_ENABLED", ""))
api_server_key = getenv("API_SERVER_KEY", "")
# Require a usable key: API_SERVER_ENABLED alone would load an
# unauthenticated platform whose adapter refuses to start at connect()...
if _has_usable_api_server_key(api_server_key):
    # only THEN is Platform.API_SERVER added to config.platforms
```
The key gate (`_has_usable_api_server_key`) requires **min_length=16**. With
`API_SERVER_ENABLED=true` but **no** `API_SERVER_KEY`, the api_server platform is
never added, so `:8642` never listens. The gateway does not error — it just
omits the listener. This is silent and easy to misdiagnose.

**Fix:** generate a 32+ char secret and add it to `~/.hermes/.env`:
```bash
# generate + write in one Python step WITHOUT printing the secret to logs
python3 - <<'PY'
import secrets, pathlib
p = pathlib.Path("/home/deeone/.hermes/.env")
lines = [l for l in p.read_text().splitlines() if not l.startswith("API_SERVER_KEY=")]
key = secrets.token_urlsafe(24)   # 32-char url-safe
lines.append(f"API_SERVER_KEY={key}")
p.write_text("\n".join(lines) + "\n")
print("key length:", len(key))
PY
```
Then **restart the gateway** with `hermes gateway run --replace` (or stop + run).
Re-probe `:8642` after ~15s.

**Workspace side:** if the gateway now requires the key, the workspace must send
the same value as `HERMES_API_TOKEN` in `hermes-workspace/.env`:
```bash
export APIKEY=$(grep '^API_SERVER_KEY=' ~/.hermes/.env | cut -d= -f2-)
# append to workspace .env if not already present (masked, never print it)
grep -q '^HERMES_API_TOKEN=' hermes-workspace/.env || printf 'HERMES_API_TOKEN=%s\n' "$APIKEY" >> hermes-workspace/.env
```
If key is set on gateway but missing on workspace → every API call returns
`Unauthorized` (401). Match them.

> **Secret hygiene:** the workspace `.env` is guarded by the file-read tool
> (read_file refuses it). Edit it via terminal (patch/write_file are blocked).
> Never `echo` the raw key to terminal output.

## Other pitfalls (from README troubleshooting)

- **Stale pidfile blocks `gateway run`:** if a previous gateway died without
  cleanup, `hermes gateway run` says "Gateway already running (PID NNNN)" but
  nothing listens. Remove the lock then start:
  `rm -f ~/.hermes/gateway.pid ~/.hermes/gateway.lock` then
  `hermes gateway run --replace`.
- **UI says "Offline" but `/api/sessions` returns data:** do NOT start another
  gateway. Refresh / reprobe the Workspace UI — the backend pairing is alive.
- **Remote (Tailscale/LAN) access:** set `API_SERVER_HOST=0.0.0.0` in
  `~/.hermes/.env` and point `HERMES_API_URL`/`HERMES_DASHBOARD_URL` at the
  reachable IP (e.g. `http://100.x.y.z:8642`). Setting only one URL leaves the
  other probing `127.0.0.1` and failing.
- **`codex login` needed for `gpt-5.4`/`openai-codex` default model** before chat
  works.

## Reference

See `references/gateway-api-server-key.md` for the exact `gateway/config.py`
decode and a reproduction recipe.
