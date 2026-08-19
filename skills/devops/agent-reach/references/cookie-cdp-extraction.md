# CDP cookie extraction (when on-disk decryption fails)

## Symptom
`agent-reach configure --from-browser chrome` OR
`linkedin-scraper-mcp --import-from-browser chrome` fails with:
```
Could not import session: Found a logged-in browser session but could not
decrypt its cookies (the keychain key was unavailable, or the cookies use
app-bound encryption). Run --login to create a session instead.
```
Both tools use `rookiepy` / `browser_cookie3`, which decrypt the on-disk
Chrome cookie DB. On Linux with a locked login keyring, or on Chrome's
app-bound encryption, that decryption fails.

## Why CDP works
Chrome DevTools Protocol (CDP) `Network.getCookies` reads cookies from the
**live browser process memory**, not the on-disk DB. HttpOnly cookies
(`li_at`, `JSESSIONID`) are readable this way even though:
- `document.cookie` (JS eval) cannot see HttpOnly cookies, and
- OpenCLI's `browser network` capture only records response shapes, NOT the
  outgoing request `Cookie` header.

## Verification that the session IS live (even when on-disk tools fail)
The OpenCLI bridge is a live controller of the user's Chrome:
```
opencli doctor                              # shows daemon + connected profile (e.g. hg5rwhdy)
opencli browser hg5rwhdy open https://www.linkedin.com/feed/
opencli browser hg5rwhdy eval "document.cookie"   # non-HttpOnly cookies present
opencli browser hg5rwhdy eval "localStorage"      # e.g. voyager-web badges => authenticated
```
If `localStorage` shows real feed/profile data, the session is valid — only
the *export* path is blocked by encryption.

## Bringing up a CDP endpoint
1. Find the browser + profile:
   - `env | grep AGENT_BROWSER_EXECUTABLE_PATH` (e.g. `/usr/local/bin/google-chrome`)
   - Profile dir: `~/.config/chromium/` or `~/.config/google-chrome/`
2. Copy the profile to a temp dir (avoids clashing with the running instance
   that holds the same profile lock):
   ```
   cp -r ~/.config/chromium /tmp/chrome-cdp-profile
   ```
3. Launch a debug-enabled Chrome on the COPY:
   ```
   /usr/local/bin/google-chrome \
     --remote-debugging-port=9222 \
     --user-data-dir=/tmp/chrome-cdp-profile \
     --no-first-run --no-default-browser-check &
   ```
4. Confirm the endpoint is up:
   ```
   curl -s http://127.0.0.1:9222/json/version
   ```
5. Read cookies via CDP `Network.getCookies` (needs a websocket client, e.g.
   Python `websocket-client`, or the `lightpanda` MCP already wired to
   `ws://127.0.0.1:9222`). Look for `li_at`, `JSESSIONID`, `bcookie`,
   `lidc` for LinkedIn.
6. Feed the extracted cookies to the consumer in the format it expects
   (Playwright `storage_state.json` shape: cookies array with
   name/value/domain/path/expires/secure/httpOnly).

## Gotchas learned the hard way (this session)

### PICK THE RIGHT PROFILE — the copy may have NO LinkedIn cookies
The OpenCLI browser env var is `AGENT_BROWSER_EXECUTABLE_PATH=/usr/local/bin/google-chrome`,
but LinkedIn cookies may NOT live in `~/.config/chromium/`. Verify the row exists
in the copy's DB BEFORE launching (read-only sqlite; values are encrypted but the
row presence is informative):
```bash
for db in ~/.config/chromium/Default/Cookies ~/.config/google-chrome/Default/Cookies; do
  [ -f "$db" ] && python3 -c "import sqlite3;c=sqlite3.connect('$db');print('$db',c.execute(\"SELECT name,host_key FROM cookies WHERE name='li_at'\").fetchall())"
done
```
In this environment the `li_at` row was only in `~/.config/google-chrome/Default/Cookies`
— copying `~/.config/chromium` produced a Chrome that launched fine but returned
ZERO LinkedIn cookies (no `li_at`). Copy the profile that actually contains the row.

### "Opening in existing browser session." — stale SingletonLock
If step 3 exits immediately with `Opening in existing browser session.` and CDP
never comes up, a stale lock from a prior launch of the same copy block it:
```bash
rm -f /tmp/chrome-cdp-profile/SingletonLock /tmp/chrome-cdp-profile/SingletonCookie
```
Then relaunch. (No real Chrome was running; the lock was leftover from the copy's
first aborted launch.)

### Wrong websocket target → HTTP 404
Connecting to the browser-level `webSocketDebuggerUrl` (`/devtools/browser/...`)
with `websockets` 15.x can raise `InvalidStatus: server rejected WebSocket
connection: HTTP 404`. Instead fetch `/json`, take a **page** target's
`webSocketDebuggerUrl` (`/devtools/page/<id>`), and connect there. See
`scripts/cdp_get_cookies.py`.

### `li_at` must be present to count as logged in
`Network.getCookies` returns many LinkedIn cookies; only `li_at` (HttpOnly,
~150 chars) is the actual auth token. If `HAS_LI_AT: False`, the profile copy
was wrong or the session had expired — recheck the profile DB step above.
`bcookie`/`bscookie` alone are NOT proof of authentication.

## Notes
- Do NOT kill/relaunch the user's PRIMARY Chrome to add a debug port — launch
  a second instance against a profile COPY.
- Once cookies are persisted by the consumer (e.g. LinkedIn server's
  `portable_cookie_path`), the CDP Chrome can be closed.
- The `lightpanda` MCP in `~/.mcp_servers.json` already has
  `"LIGHTPANDA_CDP_URL": "ws://127.0.0.1:9222"` — it becomes usable the moment
  step 3 runs.
- A re-runnable client is provided at `scripts/cdp_get_cookies.py` (writes
  `/tmp/li_cookies.json` in Playwright storage_state shape, prints cookie names
  + `HAS_LI_AT`).
