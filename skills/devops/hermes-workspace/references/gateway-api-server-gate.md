# Gateway API_SERVER_KEY gate (proof)

Verified in hermes-agent source `gateway/config.py` (around line 2129):

```python
api_server_enabled = is_truthy_value(getenv("API_SERVER_ENABLED", ""))
api_server_key = getenv("API_SERVER_KEY", "")
...
# Require a usable key: API_SERVER_ENABLED alone would load an
# unauthenticated platform whose adapter refuses to start at connect()
# anyway (startup guard in gateway/platforms/api_server.py), leaving the
# reconnect watcher spinning and logging errors forever. Same strength
# bar as the startup guard (has_usable_secret, min_length=16).
if _has_usable_api_server_key(api_server_key):
    if Platform.API_SERVER not in config.platforms:
        config.platforms[Platform.API_SERVER] = PlatformConfig()
    ...
```

Takeaways:
- `API_SERVER_ENABLED=true` with NO `API_SERVER_KEY` → the `if` is false → `Platform.API_SERVER` is never added → port 8642 never opens, no error, just "running" banner. This is the silent failure.
- Key must be ≥16 chars (`has_usable_secret`). `secrets.token_urlsafe(24)` yields 32 chars — safe.
- When the key IS set: workspace `.env` needs `HERMES_API_TOKEN=<same key>`, else every `/api/*` call returns 401.
- The workspace UI shows `mode=disconnected` / portable (missing=health,models,...) when 8642 is unreachable, even though `hermes gateway run` looked "up".
- git-grep anchors: `gateway/config.py` `_has_usable_api_server_key`, `Platform.API_SERVER`.
