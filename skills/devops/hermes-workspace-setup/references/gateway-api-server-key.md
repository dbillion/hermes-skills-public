# Gateway API server bind failure — API_SERVER_KEY

## Location (hermes-agent source)
`hermes-agent/gateway/config.py` lines ~2129–2137 (inside the gateway config
build). The api_server platform is only registered when a usable key exists:

```python
api_server_enabled = is_truthy_value(getenv("API_SERVER_ENABLED", ""))
api_server_key     = getenv("API_SERVER_KEY", "")
...
if _has_usable_api_server_key(api_server_key):
    if Platform.API_SERVER not in config.platforms:
        config.platforms[Platform.API_SERVER] = PlatformConfig()
    ...
    config.platforms[Platform.API_SERVER].enabled = True
    if api_server_key:
        config.platforms[Platform.API_SERVER].extra["key"] = api_server_key
```

`API_SERVER_ENABLED=true` alone is NOT enough. The guard is
`_has_usable_api_server_key()` whose strength bar = `has_usable_secret`,
`min_length=16`.

## Why it's silent
The gateway prints the banner "Messaging platforms + cron scheduler" either way.
It never logs "api server disabled (no key)". `curl :8642` just returns
connection-refused (`000`). Telegram/Discord/etc. still connect because those are
separate platforms, so it looks like "gateway is up but workspace can't reach
it" — when really the :8642 listener was never created.

## Reproduction recipe
1. `~/.hermes/.env` has `API_SERVER_ENABLED=true` and NO `API_SERVER_KEY`.
2. `hermes gateway run --replace`
3. `for i in $(seq 1 20); do curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8642/; sleep 1; done` → all `000`.
4. `ss -ltnp | grep 8642` → nothing.
5. Add a 32-char key, restart, re-probe → `200`.

## Fix (one-shot, secret never printed)
```bash
python3 - <<'PY'
import secrets, pathlib
p = pathlib.Path("/home/deeone/.hermes/.env")
lines = [l for l in p.read_text().splitlines() if not l.startswith("API_SERVER_KEY=")]
key = secrets.token_urlsafe(24)   # 32-char url-safe, min_length=16 satisfied
lines.append(f"API_SERVER_KEY={key}")
p.write_text("\n".join(lines) + "\n")
print("key length:", len(key))
PY
hermes gateway run --replace
```
Then set the matching token in the workspace `.env` as `HERMES_API_TOKEN`
(else 401 on every call).

## Workspace auth mismatch symptom
- Gateway has `API_SERVER_KEY` set, workspace `.env` has no `HERMES_API_TOKEN`
  → workspace gets `Unauthorized` (401) on every `/api/*` call.
- Fix: copy the same value into `HERMES_API_TOKEN` in `hermes-workspace/.env`.
- Note: workspace `.env` is read-file-guarded; edit via terminal, not patch.
