---
name: social-mcp-ops
description: >-
  Fix LinkedIn MCP / Agent Reach auth and persistence.
---

# Social MCP Ops (Agent Reach / LinkedIn)

Operating the LinkedIn MCP server (`linkedin-scraper-mcp`, pinned at
`~/.venv`) for Agent Reach / OpenCLI. The recurring failure mode is
authentication: the session goes "stale" and the server re-prompts for login
because every cookie-injection path gets rejected by LinkedIn.

## The auth trap (read before trying anything)

LinkedIn binds a session to the browser/device context that created it. Any
cookie lifted out of one browser and replayed in another is rejected (the
server hits `/feed/`, gets redirected to `/login/`, and invalidates the
session). This kills THREE otherwise-obvious approaches:

1. `agent-reach configure --from-browser` / LinkedIn `--import-from-browser`
   → rely on `rookiepy`/`browser_cookie3`, which CANNOT decrypt on-disk Chrome
   cookies on Linux (app-bound encryption / locked login keyring). Fails with
   "could not decrypt its cookies".
2. CDP cookie extraction (`--remote-debugging-port=9222` + `Network.getCookies`
   over a `websockets` client) → successfully reads `li_at` (HttpOnly) from a
   live Chrome memory, BUT the value is rejected when the server replays it in
   its own isolated Chromium. Confirmed: `get_my_profile` after injection
   returns "Session expired / re-login".
3. Copying the cookie DB to a temp profile and launching debug Chrome there →
   same cross-context rejection.

**The only reliable auth path: the server's own first-party `--login`.** It
opens a LinkedIn login window in THE SAME browser context the server
validates against, so LinkedIn accepts it. Run it, the user logs in (handles
2FA), the session persists natively to `~/.linkedin-mcp/cookies.json`.

## Step-by-step: fix a stale LinkedIn session

1. Kill any running server instance (background proc or systemd).
2. `export PATH="/home/deeone/.venv/bin:$PATH"`
3. `linkedin-scraper-mcp --login --log-level WARNING` → wait for "Opening
   browser for LinkedIn login" → user authenticates in the window.
4. Verify: `cd /home/deeone && mcporter call 'linkedin.get_my_profile()'`
   should return the user's `linkedin.com/in/...` URL, not a re-login prompt.

## Pitfall: mcporter resolves config by CWD

`mcporter` reads its config from the CURRENT WORKING DIRECTORY. Running a
`mcporter` command from `/tmp` writes/reads a STRAY `/tmp/config/mcporter.json`
and then reports `Unknown MCP server 'linkedin'`. The real config is
`/home/deeone/config/mcporter.json` (has `exa` + `linkedin`).

**Rule: always `cd /home/deeone` before any `mcporter` call.** Add
`linkedin` to the real config with `mcporter config add linkedin
http://127.0.0.1:3000/mcp` while in `/home/deeone`.

## Make the server persistent (systemd user service)

A foreground `linkedin-scraper-mcp` dies when the terminal closes. Create
`~/.config/systemd/user/linkedin-mcp.service`:

```
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
```

Then: `systemctl --user daemon-reload && systemctl --user enable --now
linkedin-mcp.service`. Verify `systemctl --user is-active linkedin-mcp.service`
and a `get_my_profile` call. (Set `XDG_RUNTIME_DIR=/run/user/$(id -u)` if
systemctl complains.)

## Tool inventory (linkedin-scraper-mcp MCP)

get_my_profile, get_person_profile, search_people, get_company_profile,
search_jobs (easy_apply filter), get_job_details, get_saved_jobs,
connect_with_person, send_message, get_inbox, get_conversation,
search_conversations. NOTE: no `post`/`apply`/`upload_cv` tool — LinkedIn
Easy Apply and CV upload are OUT OF SCOPE (ToS + ban risk). Job-search
shortlisting (search + save + read) is the realistic workflow.

## OpenCLI social adapters (the other Agent Reach channels)

`opencli <platform> --help` for reddit / facebook / instagram / twitter /
linkedin / xiaohongshu / xiaoyuzhou / xueqiu. Most are READ/export + connect/
message; none publish feed posts or articles. Twitter/X also works via the
standalone `twitter` CLI (needs `auth_token` + `ct0` env vars) but Agent Reach
uses the OpenCLI route. Verify each via a real auth-gated call (whoami / feed /
saved) rather than assuming.

## Workflow note

When the user hands you a cluster of related setup/verify tasks ("persist it,
wire it into my profile, run a job search"), EXECUTE them in one pass — don't
ask per step. This user expects execution, not incremental confirmation.
Verify at the end with one live call.
