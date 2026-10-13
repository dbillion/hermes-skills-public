# Extracting fresh session cookies via headless Brave (CDP)

Use this when an MCP server needs a session cookie/token that has expired
(e.g. `SUBSTACK_SESSION_TOKEN` 403s) and the user says "grab a fresh one from
the browser." This is the headless, no-interaction path on a Linux box.

## 1. Launch headless Brave with remote debugging
Brave is installed at `/opt/brave-bin/brave` on this machine. `DISPLAY` is empty
(headless server), so use `--headless=new`. The Hermes `cdp_url` config points
at `http://localhost:9224` but **nothing is listening by default — you must
launch the browser first.**

```bash
# background=true in the agent terminal tool
/opt/brave-bin/brave --headless=new --remote-debugging-port=9224 \
  --no-sandbox --user-data-dir=/tmp/brave-substack --disable-gpu --disable-dev-shm-usage
```

Verify it's up (returns a JSON version blob with `webSocketDebuggerUrl`):
```bash
curl -s -m 5 http://localhost:9224/json/version
```

## 2. The `browser_cdp` tool needs a ws:// URL, not http://
`browser_cdp` with `method=Target.getTargets` against `http://localhost:9224`
fails with "not a WebSocket URL." Either:
- Let the agent's browser stack resolve it, OR
- Drive CDP directly via a WebSocket client (see step 4).

## 3. Open the target site, then READ COOKIES
```bash
# open a tab
curl -s -X PUT "http://localhost:9224/json/new?https://dbillion.substack.com/"
# list targets + their page websocket URLs
curl -s http://localhost:9224/json
```
Via `browser_cdp` (browser-level): `Storage.getCookies` returns ALL cookies the
browser holds (name, value, domain, httpOnly, session). This is the key diagnostic.

## 4. Diagnostic signature: are you even logged in?
A Substack session needs the `substack.sid` cookie. If `Storage.getCookies`
shows `cf_clearance`, `AWSALBTG`, `ab_testing_id` but **NO `substack.sid`**, and
`substack.lli` == `0` ("likely-logged-in" JWT is the logged-OUT sentinel), then:
- The profile is **logged out** → every API call returns 403.
- A pasted/old `substack.sid` will also 403.
- Fix: log in (browser at /login, magic-link, or user pastes a fresh
  `Cookie:` header from their own logged-in browser via DevTools → Network).

## 5. Page-level eval needs the PAGE websocket, not the browser one
`Runtime.evaluate` and `Network.*` are NOT available on the browser-target CDP
endpoint (`Target.getTargets` / `Runtime.evaluate` there → method not found).
Connect to the page's own `webSocketDebuggerUrl` (from `/json`) with a WebSocket
client (Python `websockets` is installed: `websockets 15.0.1`).

Minimal pattern (async, `websockets`):
```python
import asyncio, json, websockets
WS = "ws://localhost:9224/devtools/page/<PAGE_TARGET_ID>"
async def main():
    async with websockets.connect(WS, max_size=10*1024*1024) as ws:
        mid = 0
        def nxt():
            nonlocal mid; mid += 1; return mid
        await ws.send(json.dumps({"id": nxt(), "method": "Network.enable", "params": {}}))
        await ws.send(json.dumps({"id": nxt(), "method": "Runtime.enable", "params": {}}))
        # same-origin fetch to avoid CORS (page is on dbillion.substack.com)
        await ws.send(json.dumps({"id": nxt(), "method": "Runtime.evaluate",
            "params": {"expression": "(async()=>{try{const r=await fetch('/api/v1/user/current',{credentials:'include'});return r.status+' '+await r.text();}catch(e){return 'ERR:'+e;}})()",
                       "awaitPromise": True, "returnByValue": True}}))
        for _ in range(50):
            m = json.loads(await asyncio.wait_for(ws.recv(), timeout=8))
            if m.get("id") and m.get("result",{}).get("result",{}).get("value") is not None:
                print(m["result"]["result"]["value"]); break
asyncio.run(main())
```
Note: cross-origin fetch (`substack.com` from a `dbillion.substack.com` page)
fails with "Failed to fetch" due to CORS — fetch the **same origin** endpoint.

## 6. Capturing the live Cookie string
Enable `Network` on the page, then navigate (`Page.navigate`) so a real request
fires; read `Network.requestWillBeSent` → `params.request.headers["Cookie"]`.
That exact string is what goes into `SUBSTACK_SESSION_TOKEN`.
