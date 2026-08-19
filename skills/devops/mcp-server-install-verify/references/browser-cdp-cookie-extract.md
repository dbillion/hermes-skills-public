# Browser CDP: launch + extract cookies/tokens from a live browser

Used when a task needs a token/session that lives in a browser the user has open
(e.g. Substack `substack.sid`, CloudFlare `cf_clearance`), or when driving a
login through an already-authenticated browser to bypass a captcha.

## 1. Launch Brave headless with a debug port (if none is listening)
`browser_cdp` returns `CDP endpoint is not a WebSocket URL: 'http://localhost:9224'`
when nothing is on the port. Fix: launch a browser with `--remote-debugging-port`.

```bash
# background=true — do NOT use nohup/disown; let Hermes track it
/opt/brave-bin/brave --headless=new --remote-debugging-port=9224 \
  --no-sandbox --user-data-dir=/tmp/brave-substack --disable-gpu --disable-dev-shm-usage
```
Verify: `curl -s http://localhost:9224/json/version` → returns `webSocketDebuggerUrl`.
Brave binary locations seen: `/opt/brave-bin/brave`, `/usr/bin/brave`.

## 2. Page-level work needs the PAGE's websocket, not the browser one
`browser_cdp` Runtime.evaluate / Network.* route to the *browser* session and
return `'-32601' method not found` for page-level calls. Get the page's own URL:

```bash
curl -s http://localhost:9224/json
# -> find the target with "webSocketDebuggerUrl": "ws://localhost:9224/devtools/page/<id>"
```

Then connect with a websocket client (Python `websockets` is available;
`websocket-client` is NOT). Pattern:

```python
import asyncio, json, websockets
WS = "ws://localhost:9224/devtools/page/<id>"
async def main():
    async with websockets.connect(WS, max_size=20*1024*1024) as ws:
        await ws.send(json.dumps({"id":1,"method":"Runtime.enable","params":{}}))
        await ws.send(json.dumps({"id":2,"method":"Storage.getCookies","params":{}}))
        # read until method=="Storage.getCookies" -> result.cookies[]
```

## 3. Read cookies (the fresh-token source)
`Storage.getCookies` (no filter) returns ALL cookies the browser holds, including
httpOnly ones `document.cookie` JS cannot see. Filter by `name`/`domain`.
For Substack the session cookie is `substack.sid` (domain `substack.com`).
`substack.lli` is a JWT whose `userId` claim == `SUBSTACK_USER_ID` (decode middle
base64 segment). `cf_clearance` proves CloudFlare trust was passed.

## 4. Drive a login in the trusted browser (captcha bypass)
A browser that already holds a valid `cf_clearance` is usually NOT re-challenged
by CloudFlare on login. Use page-level `Runtime.evaluate` to fill+submit the form:
- set input value via `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set`
  then dispatch `input`+`change` events (avoids React-controlled-input dead-ends)
- click submit, then poll `location.href` until it leaves `sign-in`
- read `substack.sid` via `Storage.getCookies`

## 5. substack-mcp-plus specifics
- Install: `npm install -g substack-mcp-plus` (it's a Python pkg wrapped in npm; venv
  with Playwright + Chromium 1228 already bundled at `<pkg>/venv`, `<pkg>/node_modules/.../chromium-1228`).
- Setup: `substack-mcp-plus-setup` → `src/setup.js` spawns `setup_auth.py`.
- Auth: `src/handlers/auth_handler.py` reads `SUBSTACK_SESSION_TOKEN` env and uses it
  as `substack.sid={token}` (line ~264). So the same token format works for both
  `substack-mcp` and `substack-mcp-plus`.
- Login flow hits CloudFlare captcha on fresh/headless browsers (429/401/
  `requestStorageAccess: Permission denied`). Magic-link email is the reliable path:
  Substack sends a link; opening it in a `cf_clearance`-trusted browser sets
  `substack.sid` with no captcha. See substack-auth-workflow.md.
