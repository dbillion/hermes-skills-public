# LinkedIn MCP Debugging — Reproduction & The Cross-Context Trap

## Symptom
`linkedin-scraper-mcp` (HTTP mode) returns on authed calls:
"Stale session detected; closing browser and triggering re-login"
or "Session expired. A login browser window has been opened."
`get_my_profile()` does not return the user's profile.

## Root-cause chain observed
1. Cookie import fails at the source:
   `agent-reach configure --from-browser chrome` and
   `linkedin-scraper-mcp --import-from-browser` use rookiepy / browser_cookie3,
   which cannot decrypt on-disk Chrome cookies (app-bound encryption / locked keyring).
   ⇒ No portable cookie file is produced.
2. Workaround attempt: extract `li_at` live via Chrome DevTools Protocol.
   - Launch a SECOND Chrome on a COPY of the real profile with
     `--remote-debugging-port=9222` (copy first; the original may be locked by a
     running instance — remove stale `SingletonLock`/`SingletonCookie` before relaunch).
   - Connect a Python websocket client to `http://127.0.0.1:9222/json` page WS;
     `Network.enable` → `Page.navigate https://www.linkedin.com/` → `Network.getCookies`
     (urls filtered to linkedin.com). This DOES return HttpOnly `li_at` (decrypted in memory).
   - Write `~/.linkedin-mcp/cookies.json` as a FLAT list (not `{"cookies":[...]}`),
     plus a valid `source-state.json` via the server's own `write_source_state()`.
3. The trap: the server replays those cookies in its OWN patchright Chromium.
   LinkedIn's feed auth check then redirects to `/login/` ⇒ "Stale session".
   LinkedIn binds sessions to browser/device context; a cookie lifted from one
   Chrome and replayed in another fingerprint is rejected. CDP extraction is
   therefore NOT a durable fix for LinkedIn (it works for sites without that binding).

## The fix that works
Use the server's first-party login in its own browser context:
- `linkedin-scraper-mcp --login` (interactive window; user completes 2FA).
  Session persists natively to `~/.linkedin-mcp/cookies.json`.
- OR start HTTP server and call any authed tool — it opens a window if session empty.
Verify: `mcporter call 'linkedin.get_my_profile()'` returns the profile URL.

## Profile discovery gotcha
The session was in `/home/<user>/.config/google-chrome/Default/Cookies`, NOT
`/home/<user>/.config/chromium/Default/Cookies`. Check BOTH with a read-only sqlite
query for the `li_at` row before assuming which profile to copy.

## Make it persistent (systemd user service)
`~/.config/systemd/user/linkedin-mcp.service`:
  [Service] Type=simple
  Environment=PATH=<venv>/bin:/usr/bin:/bin
  ExecStart=<venv>/bin/linkedin-scraper-mcp --transport streamable-http --host 127.0.0.1 --port 3000 --log-level WARNING
  Restart=always  RestartSec=5
  [Install] WantedBy=default.target
Then: `XDG_RUNTIME_DIR=/run/user/$(id -u) systemctl --user daemon-reload && systemctl --user enable --now linkedin-mcp.service`.
Re-verify `get_my_profile` after the switch.

## mcporter config gotcha
`mcporter` resolves config by CWD. From `/tmp` it writes `/tmp/config/mcporter.json`
and reports `Unknown MCP server 'linkedin'`. Always `cd ~` first. Real config:
`/home/<user>/config/mcporter.json` (exa + linkedin).
