# Substack MCP — Auth / Captcha Workflow (verified this session)

## The problem
Both `substack-mcp` and `substack-mcp-plus` need a valid `substack.sid` session cookie. The
setup wizards (`substack-mcp-plus-setup`) launch a visible browser and wait for the human to solve
a CloudFlare captcha. On a headless box (Telegram/Hermes agent) you CANNOT solve it.

## What was tried and FAILED (don't repeat)
1. CDP-driven Brave (already had `cf_clearance`) → filled email/password, but Substack redirected
   to "Check your email" magic-link screen; "Sign in with password" link did not reveal a password
   field. No captcha element appeared, but login never completed.
2. Playwright (package venv `venv/bin/python`, chromium-1228 already installed) headless=True →
   console showed `429`, `401`, `requestStorageAccess: Permission denied`, `redirect-timeout`.
   CloudFlare blocked the automated browser.

Conclusion: automated login to Substack is captcha-walled. Not solvable headlessly.

## What WORKS — magic-link email (no captcha)
Substack's login sends a magic link to the user's email. Opening that link in a browser that
already holds a valid `cf_clearance` sets `substack.sid` WITHOUT a captcha challenge.

Flow:
1. User enters email at substack.com/sign-in → Substack emails a login link to that address.
2. User clicks the link (or copies the URL and gives it to the agent).
3. Agent opens the link in the trusted Brave (CDP, port 9224) OR user opens it in their own browser.
4. Capture `substack.sid`:
   - Via CDP: `Storage.getCookies` → find cookie `name=="substack.sid"`.
     NOTE: `Storage.getCookies` takes NO browserContextId; passing a targetId errors with
     "Failed to find browser context". Call it with `params: {}`.
   - Or in the user's browser DevTools → Application → Cookies → copy `substack.sid` value.
5. Drop the value into:
   - `substack-mcp`: `SUBSTACK_SESSION_TOKEN` env (the full cookie string, or just `substack.sid=...`)
   - `substack-mcp-plus`: `SUBSTACK_SESSION_TOKEN` env, OR run its setup and let it store encrypted.
6. Re-run the handshake/draft test to confirm `200` instead of `403`.

## How to get SUBSTACK_USER_ID when the user "can't find it"
The session token includes `substack.lli=<JWT>`. Decode the middle segment:
```python
import base64, json
seg = "eyJ1c2VySWQiOjM2MTk2NDI1...<middle segment, base64url>"
seg += "=" * (-len(seg) % 4)
print(json.loads(base64.urlsafe_b64decode(seg)))
# -> {"userId": 36196425, ...}
```
`userId` is the `SUBSTACK_USER_ID`.

## Browser CDP notes (Hermes)
- `browser_cdp` (the tool) routes to the *browser* session only. `Runtime.evaluate` on a page
  errors with "'Runtime.evaluate' wasn't found" at browser scope.
- For page-level eval, fetch `http://localhost:9224/json`, find the page's `webSocketDebuggerUrl`,
  and connect with a `websockets` client (stdlib `asyncio` + `websockets` 15.x is available).
- Launch headless Brave for CDP:
  `brave --headless=new --remote-debugging-port=9224 --no-sandbox --user-data-dir=/tmp/brave-X`
  (Brave binary at `/opt/brave-bin/brave` on this box; no DISPLAY → must be headless.)
- `Network.getAllCookies` is NOT a valid method in this Chrome build (moved to `Storage`).
  Use `Storage.getCookies` with `params: {}`.

## Verified facts
- `substack-mcp` server info: `Substack MCP v1.0.0`, tool `create_draft_post` (title, subtitle, body).
- Transport: newline-delimited JSON (NOT LSP framing).
- A real `POST`/draft call returned `403` with the stale pasted token → confirmed token-expiry
  diagnosis, not a server bug.
