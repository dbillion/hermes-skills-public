---
name: social-mcp-auth
description: Debug social MCP/CLI auth (LinkedIn, OpenCLI, Agent Reach).
---

# Social MCP Auth & Debugging

Getting agent-faced social platforms authenticated and keeping them alive:
- **Agent Reach** (orchestrator CLI/skill) + **OpenCLI** (browser-bridge CLI) for Reddit / Facebook / Instagram / X(Twitter) / LinkedIn.
- **linkedin-scraper-mcp** — the LinkedIn backend Agent Reach calls; has its own auth lifecycle.

## When to use
- User asks to install/configure Agent Reach or connect social platforms.
- `agent-reach doctor` shows a platform as not-connected.
- LinkedIn MCP returns "Stale session detected; triggering re-login" or opens a login window on every call.
- Cookie import (`--import-from-browser`, `agent-reach configure --from-browser`) fails with keychain / app-bound-encryption errors.

## The reliable auth path (LinkedIn especially)
1. **Do NOT rely on cookie extraction.** `rookiepy` / `browser_cookie3` (used by `agent-reach configure --from-browser` and linkedin `--import-from-browser`) cannot decrypt on-disk Chrome cookies on Linux when the login keyring is locked or cookies use app-bound encryption. Symptom: "could not decrypt its cookies (the keychain key was unavailable, or the cookies use app-bound encryption)".
2. **CDP extraction gets the value but LinkedIn rejects replay.** You CAN read `li_at` (HttpOnly) via Chrome DevTools Protocol `Network.getCookies` from a live, logged-in Chrome (see references/linkedin-mcp-debugging.md). But when the MCP server replays that cookie in its OWN isolated Chromium (patchright), LinkedIn redirects to `/login` — sessions are bound to browser/device context. Cross-context replay fails. (The CDP technique is still useful for sites that don't bind sessions; just not LinkedIn.)
3. **Use the server's own first-party `--login`.** This opens a login window in the SAME browser context the server validates against, so LinkedIn accepts it. The session persists natively to `~/.linkedin-mcp/cookies.json`. This is the supported, reliable fix.
   - Interactive: `linkedin-scraper-mcp --login` (opens a window; user completes 2FA).
   - Or start the HTTP server and call any authed tool — it opens a window if the session is missing/empty.
   - Verify: `mcporter call 'linkedin.get_my_profile()'` must return the user's profile URL, NOT a re-login prompt.

## LinkedIn MCP server operation
- Binary lives in a venv (e.g. `~/.venv/bin/linkedin-scraper-mcp`). NOT on default PATH — prefix commands with `export PATH="$HOME/.venv/bin:$PATH"`.
- HTTP mode: `linkedin-scraper-mcp --transport streamable-http --host 127.0.0.1 --port 3000 --log-level WARNING`.
- Cookie file: `~/.linkedin-mcp/cookies.json` — a **flat JSON list** of cookie dicts (`[{name,value,domain,path,expires,httpOnly,secure,sameSite}, ...]`), NOT `{"cookies":[...]}`. Source-state: `~/.linkedin-mcp/source-state.json`.
- Tool inventory: see references/social-platform-tool-inventory.md. Capabilities are **read + connect + message only** — there is NO apply / fill-form / upload-CV tool. Realistic workflow: search + shortlist, the user clicks Apply.
- Job search: `search_jobs(keywords, location, max_pages, easy_apply, ...)`. LinkedIn's result text is a messy blob; parse carefully (title/company/location interleave with status lines like "Promoted", "Actively reviewing applicants", "Easy Apply").

## Persistence (keep the server alive across terminal sessions)
A foreground server dies when the shell closes. Make it a systemd user service:
- Unit at `~/.config/systemd/user/linkedin-mcp.service`: `Type=simple`, `Environment=PATH=<venv>/bin:/usr/bin:/bin`, `ExecStart=<venv>/bin/linkedin-scraper-mcp --transport streamable-http --host 127.0.0.1 --port 3000 --log-level WARNING`, `Restart=always`, `RestartSec=5`, `WantedBy=default.target`.
- `systemctl --user daemon-reload && systemctl --user enable --now linkedin-mcp.service`.
- `systemctl --user` requires `XDG_RUNTIME_DIR=/run/user/$(id -u)`.
- Verify after switch: the server still returns the user's profile (confirms the persisted cookie is loaded, not a fresh empty session).

## mcporter config gotcha (general, not LinkedIn-specific)
`mcporter` resolves its config by **CURRENT WORKING DIRECTORY**. Running from `/tmp` writes/reads a stray `/tmp/config/mcporter.json` and yields `Unknown MCP server 'linkedin'`. **Always `cd ~` (or the dir holding the real `/home/<user>/config/mcporter.json`) before any `mcporter` call.** The authoritative config is `/home/<user>/config/mcporter.json` (holds `exa` + `linkedin` entries).

## Profile discovery (don't assume)
The LinkedIn session may live in a non-obvious Chrome profile. Check ALL candidate cookie DBs for the `li_at` row (read-only sqlite):
`/home/<user>/.config/google-chrome/Default/Cookies` AND `/home/<user>/.config/chromium/Default/Cookies`. In the session that produced this skill, the real session was in `google-chrome`, not `chromium` — assuming `chromium` wasted a cycle.

## Workflow note
When a reliable path is clear (e.g. server-native `--login`), **execute it** rather than looping option questions to the user. Reserve clarifying questions for genuine ambiguity or disruptive/shared-state actions (killing their browser, relaunching Chrome). The user expects action over deliberation.

## References
- references/social-platform-tool-inventory.md — exact functions per platform (LinkedIn via opencli + linkedin-scraper-mcp, Twitter/X, Reddit, Instagram, Facebook) and the OpenCLI browser-bridge command set.
- references/linkedin-mcp-debugging.md — reproduction recipe + the cross-context rejection transcript and the `--login` fix.

## Scripts
- scripts/verify_linkedin.sh — checks the server port is up and `get_my_profile` returns the user's URL (auth OK vs re-login).
