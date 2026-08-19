---
name: linkedin-mcp-ops
description: LinkedIn MCP auth and ops for Agent Reach.
---

# LinkedIn MCP Ops (linkedin-scraper-mcp)

The LinkedIn channel in Agent Reach and the `opencli linkedin` adapter are both backed by
`linkedin-scraper-mcp` (pip package; also published as `mcp-server-linkedin`). This skill is the
operational playbook for authenticating and running it reliably.

## Trigger
Use when: installing/configuring the Agent Reach or OpenCLI LinkedIn channel; hitting "session expired",
"stale session detected", or "Opening browser for LinkedIn login…" loops; extracting / injecting `li_at`;
making the server persistent; or any LinkedIn auth troubleshooting for these tools.

## The ONE reliable auth path
LinkedIn binds sessions to the browser/device context. The server validates by loading `/feed/` and
redirecting to `/login/` if the session is rejected.

- ❌ `agent-reach configure --from-browser` and `linkedin-scraper-mcp --import-from-browser` FAIL.
  They rely on `rookiepy` / `browser_cookie3`, which cannot decrypt on-disk Chrome cookies
  (app-bound encryption / locked login keyring on Linux). Error: "could not decrypt its cookies
  (the keychain key was unavailable, or the cookies use app-bound encryption)".
- ❌ Extracting `li_at` (even via a LIVE CDP session on a logged-in Chrome) and injecting it into the
  server FAILS. LinkedIn rejects the cookie when replayed in the server's isolated Chromium
  (cross-context replay protection). Symptom in logs:
  `Feed auth check failed … auth blocker URL: https://www.linkedin.com/login/?session_redirect=…
  title='LinkedIn Login…'` → `Stale session detected; closing browser and triggering re-login`.
- ✅ The ONLY reliable path is the server's own FIRST-PARTY login:
  `linkedin-scraper-mcp --login` (or `--import-from-browser` ONLY if the keyring is unlocked AND the
  server reuses the exact same Chrome/profile — rare). `--login` opens a LinkedIn window in the SERVER's
  own browser context, which LinkedIn accepts. Log in there (handles 2FA / captcha). The session then
  persists natively to `~/.linkedin-mcp/cookies.json` + `~/.linkedin-mcp/source-state.json`.

PITFALL: Do NOT sink cycles into CDP cookie extraction for LinkedIn auth. It yields a valid-looking
`li_at` that LinkedIn will reject on replay. Go straight to `--login`.

## mcporter config pitfall (CRITICAL)
`mcporter` resolves its config by CURRENT WORKING DIRECTORY. Running it from `/tmp` writes a STRAY
`/tmp/config/mcporter.json`; later calls then fail with `Error: Unknown MCP server 'linkedin'`.
- Real config: `/home/deeone/config/mcporter.json` (contains `exa` + `linkedin`).
- RULE: always `cd /home/deeone` before any `mcporter call` / `mcporter config` command.
- Register: `mcporter config add linkedin http://127.0.0.1:3000/mcp` (run from /home/deeone).
- Verify: `mcporter call 'linkedin.get_my_profile()'` → must return the user's
  `https://www.linkedin.com/in/<slug>/` URL, NOT a login prompt.

## Making the server persistent
The server dies when its launching terminal closes. Use a systemd user service:

    [Unit]
    Description=LinkedIn MCP Server (streamable-http)
    After=network-online.target
    Wants=network-online.target
    [Service]
    Type=simple
    Environment=PATH=/home/deeone/.venv/bin:/usr/bin:/bin
    ExecStart=/home/deeone/.venv/bin/linkedin-scraper-mcp --transport streamable-http --host 127.0.0.1 --port 3000 --log-level WARNING
    Restart=always
    RestartSec=5
    [Install]
    WantedBy=default.target

Enable: `systemctl --user daemon-reload && systemctl --user enable --now linkedin-mcp.service`.
Verify: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000/mcp` (406 = alive) and re-run
`get_my_profile()`.

## CDP cookie diagnostics (read-only — NOT for auth)
To INSPECT the live session (e.g. confirm `li_at` exists), launch a SECOND Chrome on a COPY of the real
profile with `--remote-debugging-port=9222`, connect via Python `websockets` to the page WS URL from
`http://127.0.0.1:9222/json`, then `Network.getCookies` filtered to linkedin.com. `li_at` is HttpOnly
(invisible to `document.cookie` / `localStorage`). This PROVES a cookie exists — but recall LinkedIn
still rejects cross-context replay, so never use this for auth.

Profile discovery: LinkedIn cookies live in `~/.config/google-chrome/Default/Cookies` (NOT
`~/.config/chromium`). Find the real profile by grepping candidate DBs for the `li_at` row:
`sqlite3 <db> "SELECT name,host_key FROM cookies WHERE name='li_at'"`.

## Capability boundary (set expectations)
`linkedin-scraper-mcp` + `opencli linkedin` + `agent-reach` are READ / SEARCH / EXPORT plus
connect / message ONLY. There is NO tool to create or publish a LinkedIn post or article.
`opencli linkedin` exposes `posts` (read), `post-analytics` (read), `timeline` (read), and
`connect` / `safe-send` / `salesnav-message` (write connection request / DM) — but no `post` /
`article`. `agent-reach` has no post/article subcommand at all. To publish, the user must use
LinkedIn's UI or a custom browser-bridge publisher.

## Tool inventory (linkedin-scraper-mcp MCP)
get_my_profile, get_person_profile, search_people, get_company_profile, search_companies,
get_company_employees, get_company_posts, search_jobs, get_job_details, get_saved_jobs,
connect_with_person, send_message, get_inbox, get_conversation, search_conversations, get_feed,
search_posts, get_sidebar_profiles, close_session.
(No apply / upload-CV — Easy Apply is out of scope per ToS / ban risk. Realistic workflow:
search + shortlist; the user clicks Apply.)

## References
- `references/linkedin_mcp_auth.md` — exact error transcripts, the command sequence, and the
  "stale session" log signature to recognize at a glance.
