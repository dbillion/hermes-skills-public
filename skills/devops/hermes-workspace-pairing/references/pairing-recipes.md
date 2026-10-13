# Hermes Workspace Pairing — Command Recipes

Exact sequences for the canonical three-service pair (gateway :8642 / dashboard :9119 / workspace :3000).

## A. Readiness probe (run first, every time)
```bash
curl -s http://127.0.0.1:8642/health        # -> {"status":"ok","platform":"hermes-agent"}
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9119/api/status   # -> 200
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3000/api/sessions  # -> 200 (real payload)
```

## B. Fix :8642 not binding (API_SERVER_ENABLED without key)
The gateway starts but `:8642` never listens when `API_SERVER_KEY` is absent.
```bash
# generate 32-char key, append to ~/.hermes/.env (do NOT echo the key)
python3 - <<'PY'
import secrets, pathlib
p = pathlib.Path("/home/deeone/.hermes/.env")
lines = [l for l in p.read_text().splitlines() if not l.startswith("API_SERVER_KEY=")]
key = secrets.token_urlsafe(24)
lines.append(f"API_SERVER_KEY={key}")
p.write_text("\n".join(lines)+"\n")
print("wrote key len", len(key))
PY
# restart gateway so it picks up the key
hermes gateway run --replace
# then in hermes-workspace/.env add the SAME value as:
#   HERMES_API_TOKEN=<same key>
```

## C. Stale pidfile blocks gateway start
```bash
rm -f ~/.hermes/gateway.pid ~/.hermes/gateway.lock
hermes gateway run --replace
```

## D. After `hermes update` — Vite "Failed to fetch dynamically imported module"
Cause: gateway PID changed mid-session; running `pnpm dev` proxy hit ECONNREFUSED, UI flipped to disconnected, browser tried to re-fetch a stale chunk. Module is fine.
```bash
# kill the pnpm dev background process, then:
cd ~/hermes-workspace && pnpm dev
# then hard-refresh the browser (Cmd/Ctrl+Shift+R)
```

## E. Tailscale / remote phone access (README "remote host")
Problem: `:3000` binds `0.0.0.0` (page loads) but `:8642`/`:9119` bind `127.0.0.1` only → phone sees Offline.
```bash
# 1. gateway listens on all interfaces
echo 'API_SERVER_HOST=0.0.0.0' >> ~/.hermes/.env
hermes gateway run --replace

# 2. dashboard on all interfaces
hermes dashboard --port 9119 --host 0.0.0.0 --no-open

# 3. workspace points at the TAILSCALE IP (not 127.0.0.1)
TSIP=$(tailscale ip -4)     # e.g. 100.71.136.81
# in hermes-workspace/.env:
#   HERMES_API_URL=http://$TSIP:8642
#   HERMES_DASHBOARD_URL=http://$TSIP:9119
#   HERMES_PASSWORD=<strong-secret>   # UI has no auth by default off-loopback
pnpm dev

# 4. phone hits http://$TSIP:3000
```
Note: phone must use the Tailscale IP (`tailscale ip -4`), not a LAN IP like 192.168.x.x unless the phone is on that same WiFi.

## F. Expected healthy workspace startup log
```
[gateway] gateway=http://127.0.0.1:8642 dashboard=http://127.0.0.1:9119
mode=zero-fork
core=[health, chatCompletions, models, streaming, dashboard]
enhanced=[sessions, skills, memory, config, jobs, mcpFallback]
missing=[]
```
