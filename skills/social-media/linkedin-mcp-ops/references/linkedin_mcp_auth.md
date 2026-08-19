# LinkedIn MCP — Auth Failure Transcripts & Command Sequence

## Symptom → root cause map

| Log / error | Meaning | Fix |
|---|---|---|
| `could not decrypt its cookies (the keychain key was unavailable, or the cookies use app-bound encryption)` | On-disk Chrome cookie DB uses app-bound encryption / locked keyring; `rookiepy`/`browser_cookie3` can't read it. | Don't use `--import-from-browser` / `agent-reach configure --from-browser`. Use `--login`. |
| `Feed auth check failed on https://www.linkedin.com/login/?session_redirect=… title='LinkedIn Login…'` → `Stale session detected; closing browser and triggering re-login` | Server loaded injected `li_at` but LinkedIn rejected it (cross-context replay). | Injected cookie is invalid for the server's context. Re-run `--login` in the server's own browser. |
| `Error: Unknown MCP server 'linkedin'.` | `mcporter` read a stray config (e.g. `/tmp/config/mcporter.json`) because CWD wasn't `/home/deeone`. | `cd /home/deeone` then re-run. Real config: `/home/deeone/config/mcporter.json`. |
| `Session expired. A login browser window has been opened.` | Server has no valid session file. | Complete the `--login` window, then re-call. |

## Verified working command sequence (2026-08-09)

1. Kill any stale server, then launch login window:
   `linkedin-scraper-mcp --login --log-level WARNING`  (venv: `/home/deeone/.venv/bin`)
   → wait for "Opening browser for LinkedIn login… Please log in manually."
2. User logs in (handles 2FA). Session saved to:
   `~/.linkedin-mcp/cookies.json` + `~/.linkedin-mcp/source-state.json`
3. Kill the `--login` proc; start the HTTP server:
   `linkedin-scraper-mcp --transport streamable-http --host 127.0.0.1 --port 3000 --log-level WARNING`
4. From `/home/deeone`: `mcporter call 'linkedin.get_my_profile()'`
   → expect `{"url":"https://www.linkedin.com/in/<slug>/", ...}`, NOT a login prompt.

## Persistence (systemd user service)
File: `~/.config/systemd/user/linkedin-mcp.service`
`systemctl --user daemon-reload && systemctl --user enable --now linkedin-mcp.service`
`is-active` → `active`; port 3000 → HTTP 406.

## CDP diagnostic (read-only, NOT auth)
Launch 2nd Chrome on a COPY of `~/.config/google-chrome` with `--remote-debugging-port=9222`,
then Python `websockets` to the page WS from `http://127.0.0.1:9222/json`, `Network.getCookies`
(urls=linkedin.com). Confirms `li_at` exists (HttpOnly) — but LinkedIn rejects replay, so never
inject it for auth.

## Key takeaways (do NOT repeat these mistakes)
- CDP cookie extraction for LinkedIn auth = wasted cycles. LinkedIn rejects cross-context cookies.
- Wrong profile copy: LinkedIn cookies are in `~/.config/google-chrome`, NOT `~/.config/chromium`.
- mcporter is CWD-sensitive: always `cd /home/deeone` first.
- Agent Reach / OpenCLI / linkedin-scraper-mcp cannot PUBLISH posts/articles — read/search/connect/message only.
