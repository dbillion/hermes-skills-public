# Hermes Workspace connect — command recipe

## 1. Ensure gateway key exists (Pitfall 1)
```bash
# check
grep -c '^API_SERVER_KEY=' ~/.hermes/.env
# generate + append (terminal only; patch tool denies .env)
KW=$(python3 -c "import secrets;print(secrets.token_urlsafe(24))")
grep -q '^API_SERVER_KEY=' ~/.hermes/.env || printf 'API_SERVER_KEY=%s\n' "$KW" >> ~/.hermes/.env
# for Tailscale remote, also:
# sed -i 's/^API_SERVER_HOST=127.0.0.1/API_SERVER_HOST=0.0.0.0/' ~/.hermes/.env
```

## 2. Clear stale lock if "already running" but :8642 closed (Pitfall 2)
```bash
rm -f ~/.hermes/gateway.pid ~/.hermes/gateway.lock
hermes gateway run --replace
```

## 3. Start the trio
```bash
hermes gateway run &
hermes dashboard --port 9119 --host 127.0.0.1 --no-open &
cd ~/hermes-workspace && pnpm dev &
```

## 4. Wire workspace .env (Pitfall 4 / 5)
```bash
cd ~/hermes-workspace
# same-host:
# HERMES_API_URL=http://127.0.0.1:8642
# HERMES_DASHBOARD_URL=http://127.0.0.1:9119
# Tailscale remote (TS_IP from: tailscale ip -4):
# HERMES_API_URL=http://<TS_IP>:8642
# HERMES_DASHBOARD_URL=http://127.0.0.1:9119
# HERMES_PASSWORD=<secret>      # set for any 0.0.0.0 exposure
# HERMES_API_TOKEN=<same as API_SERVER_KEY>   # if gateway key set
```

## 5. Verify
```bash
curl -s http://127.0.0.1:8642/health
curl -s -o /dev/null -w "dash=%{http_code}\n" http://127.0.0.1:9119/api/status
curl -s -o /dev/null -w "ws=%{http_code}\n" http://127.0.0.1:3000/api/sessions
ss -ltnp | grep -E ':3000|:8642|:9119'
# phone (Tailscale): curl -s -o /dev/null -w "%{http_code}\n" http://<TS_IP>:3000/
```

## 6. Restart on .env change
gateway → dashboard → workspace, in that order.
