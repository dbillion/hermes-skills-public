---
name: agent-reach
description: "Configure Agent Reach: install, verify, LinkedIn, OpenCLI."
version: 1.1.0
author: Hermes Agent
platforms: [linux, macos, windows]
categories: [devops, web]
---

# Agent Reach Skill

Agent Reach (https://github.com/Panniantong/Agent-Reach) is a Python CLI + library that gives AI agents read/search access to 15 internet platforms. It ships as a self-contained binary (`agent-reach`) plus per-agent skill files — NOT a PyPI package (the PyPI "agent-reach" name is a different/unrelated package; never `pip install agent-reach`).

## Triggers
- User asks to install Agent Reach ("install agent-reach", shares the github.com/Panniantong/agent-reach URL)
- User wants to verify/test Agent Reach functionality
- User wants to enable/unlock a specific platform channel (Reddit, Facebook, Instagram, LinkedIn, Twitter/X, XiaoHongShu, Bilibili, Xueqiu, Xiaoyuzhou, etc.)
- User mentions OpenCLI and wants to know what it provides or how to use it with Agent Reach

## Distribution reality (important)
- Installed form: a binary at `~/.local/bin/agent-reach` + skill files under `~/.agents/skills/agent-reach`, `~/.openclaw/skills/agent-reach`, `~/.claude/skills/agent-reach`.
- There is NO git clone dir and NO pip package needed for the core CLI. The binary is the project's own build, not PyPI.
- The repo's own `SKILL.md` (under `.agents` etc.) references `https://github.com/Panniantong/agent-reach` — that URL is **case-sensitive and correct on GitHub** but some copies mistakenly point at the lowercase `agent-reach` slug which 404s on case-sensitive filesystems. Always use the capital-R `Agent-Reach` URL.
- Skills auto-install for Hermes/OpenClaw/Claude Code during the official install. The Hermes-managed copy at `~/.hermes/skills/devops/agent-reach` is a SEPARATE, optional convenience copy — it is safe to remove if stale (its embedded clone URL can be wrong); the live skills under `~/.agents`/`~/.openclaw`/`~/.claude` are the authoritative ones.

## Commands
- `agent-reach version` — prints "Agent Reach vX.Y.Z"
- `agent-reach doctor` — shows channel availability (Chinese UI; ✅ available / [!] installed-but-needs-config / [X] not installed)
- `agent-reach doctor --json` — machine-readable; per-platform `active_backend` and `status`. USE THIS before enabling any login-backed platform to see which backend is active.
- `agent-reach check-update` — one API call; reports if a newer version exists
- `agent-reach configure [proxy|github-token|groq-key|openai-key|twitter-cookies|youtube-cookies|xhs-cookies]` or `agent-reach configure --from-browser chrome` (auto-extract all cookies from browser)

## Install / verify steps
1. Check current state first (don't assume missing):
   `which agent-reach`, `agent-reach version`, `timeout 30 agent-reach doctor`
2. If absent: clone `https://github.com/Panniantong/Agent-Reach.git` (capital R), `cd Agent-Reach`, `bash test.sh` (creates venv, installs, runs doctor + channel tests).
3. Verify: `agent-reach version` returns "Agent Reach v1.5.0"+; doctor shows ≥7/15 (GitHub, YouTube, V2EX, RSS, semantic search, arbitrary web, B站 search).
4. Doctor may hang on slow network — ALWAYS wrap with `timeout 30`.

## Channel tiers (what needs what)
- **Zero-config (work immediately):** GitHub (gh CLI), YouTube (yt-dlp subtitles), V2EX (public API), RSS/Atom (feedparser), Any web page (Jina Reader: `curl -s "https://r.jina.ai/URL"`), B站 search (bili search API).
- **One free config step (no key):** 全网语义搜索 = Exa MCP. `mcporter config add exa https://mcp.exa.ai/mcp` (free, no API key). After this, doctor shows 7/15.
- **Login-backed (use OpenCLI + your Chrome session):** Reddit, Facebook, Instagram, XiaoHongShu, Bilibili subtitles. These report `active_backend: OpenCLI` in doctor. They work the moment you're logged into the site in Chrome — NO extra install. Commands: `opencli reddit/facebook/instagram/instagram search|read|profile|feed|subreddit/hot ... -f yaml`.
- **Separate MCP server install:** LinkedIn (see references/linkedin.md).
- **Cookie/key gated:** Twitter/X (OpenCLI or Cookie-Editor export → TWITTER_AUTH_TOKEN + TWITTER_CT0 env), XiaoHongShu (OpenCLI preferred), Xueqiu, Xiaoyuzhou (Whisper key via groq/openai).

## Pitfalls (learned the hard way — encode these)
- **mcporter config fragmentation (CRITICAL):** `mcporter config add <name> <url>` resolves a **cwd-relative project config** (`<cwd>/config/mcporter.json`) when run from a non-home directory, and ALSO a system config at `~/.mcporter/mcporter.json` (often missing). `agent-reach doctor` and the node `mcporter` (from nvm) read the HOME project config at `~/.config/mcporter.json`/equivalent. If a server appears in doctor but `mcporter call <name>` says "Unknown MCP server", you wrote to the wrong config. FIX: always `cd ~` (or pass the absolute config path) before `mcporter config add`, then verify with `mcporter config list` from `$HOME`. Delete any stray `<somepath>/config/mcporter.json` that isn't the home one.
- **Argument shape mismatches:** LinkedIn MCP tool `get_person_profile` expects `linkedin_username` (the handle, e.g. "williamhgates"), NOT `linkedin_url`. Passing `linkedin_url` errors as "Unexpected keyword argument". When a call errors with pydantic validation, read the error — it names the correct arg.
- **LinkedIn server is a background process:** it must be running for `mcporter call linkedin.*` to work. Launch as `linkedin-scraper-mcp --transport streamable-http --host 127.0.0.1 --port 3000` (background). A bare `curl http://127.0.0.1:3000/mcp` returns HTTP 406 — that's EXPECTED for an MCP streamable-http endpoint; it is NOT a failure.
- **Doctor status vs real call (VERIFY, don't trust):** doctor reports a login-backed channel "ok" as soon as OpenCLI can reach the browser — NOT when you're actually authenticated to that site. A channel can show ✅ "OpenCLI 可用（复用浏览器登录态）" while being logged OUT. ALWAYS confirm with an auth-required call before claiming it works. Concrete verifiers:
  - Reddit: `opencli reddit whoami` → logged-out shows `AUTH_REQUIRED` / "Not logged in to reddit.com". (Real case: doctor said Reddit ok, but `whoami` returned AUTH_REQUIRED until the user logged in — `hot`/`read` only worked because they hit public/anonymous data.)
  - X/Twitter: `opencli twitter whoami` → `logged_in: true, username: <handle>`. NOTE: OpenCLI uses `timeline`, NOT `feed` (`opencli twitter timeline`, `opencli twitter search`). The standalone `twitter` CLI BINARY (twitter-cli) is SEPARATE and often fails `not_authenticated` (keyring/keychain) — that is a RED HERRING; Agent Reach routes X through OpenCLI, so ignore the binary's failure.
  - Facebook: `opencli facebook feed --limit 3 -f yaml` (real posts = logged in).
  - Instagram: `opencli instagram saved --limit 3 -f yaml` (your saved posts = logged in).
  - LinkedIn: `mcporter call 'linkedin.get_my_profile()'` → returns your profile URL/identity.
  If a verifier fails with AUTH_REQUIRED, the fix is for the USER to log into that site in Chrome (OpenCLI reuses the browser session), or run `opencli <platform> login`.
- **LinkedIn: NO apply / fill-form / upload-CV.** The `linkedin-scraper-mcp` server exposes only reads + `connect_with_person` + `send_message`. There is no Easy-Apply / form-fill / resume-upload tool. Automated LinkedIn applying is NOT available and is against ToS (ban risk) — safe workflow = search + shortlist, user clicks apply. Also: `get_person_profile` takes `linkedin_username` (handle), NOT `linkedin_url` (pydantic errors "Unexpected keyword argument").
- **LinkedIn stale-session re-login:** the server runs a periodic `/feed/` auth check. If it logs "foreign runtime (fresh bridge each startup)" or "Stale session detected; triggering re-login", the cached session expired and it opens a 30-min manual-login window (every call fails until you complete it). `--import-from-browser chrome` also fails here on app-bound encryption (see references/cookie-cdp-extraction.md for the CDP fix).
- **Cookie extraction fails on app-bound encryption (use CDP):** `agent-reach configure --from-browser chrome` AND LinkedIn `--import-from-browser` both use `rookiepy`/`browser_cookie3`, which FAIL with "could not decrypt its cookies (the keychain key was unavailable, or the cookies use app-bound encryption)". The fix is to read cookies from the LIVE browser via CDP (Chrome DevTools Protocol) — CDP reads from process memory, bypassing on-disk encryption. Caveats: `document.cookie` (via `opencli browser <session> eval`) does NOT expose HttpOnly cookies like `li_at`; OpenCLI's `browser network` capture shows response SHAPES, not request `Cookie` headers — so neither yields `li_at`. You need CDP `Network.getCookies` against a Chrome launched with `--remote-debugging-port=9222` (against a profile COPY to avoid clashing with the running instance). `lightpanda` MCP is pre-wired to `ws://127.0.0.1:9222` but that port is closed until Chrome is launched with it. Full steps in references/cookie-cdp-extraction.md.
  - **CDP→inject is REJECTED by LinkedIn (don't loop on it):** A debug-Chrome-on-profile-copy CAN extract a real `li_at` via CDP, and you can write it to `~/.linkedin-mcp/cookies.json` (flat list, server's own `import_cookies` format) + a `source-state.json` (via the server's `write_source_state()`). BUT when the server replays that cookie in its OWN isolated Chromium, LinkedIn redirects `/feed/` → `/login/`: LinkedIn binds sessions to browser/device context and rejects cross-context replay. So CDP extraction produces a valid-looking-but-dead session. **Reliable fix = first-party login:** `linkedin-scraper-mcp --login` opens LinkedIn login in the server's OWN browser context (same fingerprint it validates against) → LinkedIn accepts it. OR have the user paste a FRESH `li_at` from DevTools (Application → Cookies → linkedin.com) and inject it, relaunching the server within the same minute to beat expiry. Prefer `--login`; treat CDP→inject as a last resort, not the default.
- **Subagents / `which` PATH gotchas:** when invoking venv-installed MCP servers, the venv bin may not be on the shell PATH. Use the absolute venv bin path or `export PATH="/home/deeone/.venv/bin:$PATH"`.

## OpenCLI capability inventory (what the Chrome bridge gives you)
OpenCLI ("make any website your CLI") is the reason login-backed platforms work without pasting cookies. It is far broader than social — see references/opencli-inventory.md.

## Reference files
- references/linkedin-mcp.md — LinkedIn MCP server: install, first-party `--login` (only reliable auth), HTTP launch, mcporter registration, session files, tools, and the cross-context cookie-replay rejection pitfall (supersedes old linkedin.md)
- references/mcporter-config.md — the cwd-relative config fragmentation pitfall, detailed
- references/opencli-inventory.md — full list of OpenCLI adapters (social, AI apps, external CLIs, browser)
- references/channels.md — interpreting doctor output, command groups per platform
- references/cookie-cdp-extraction.md — CDP cookie extraction when rookiepy/on-disk decryption fails (app-bound encryption)
- scripts/cdp_get_cookies.py — re-runnable CDP client (dumps a site's cookies incl. HttpOnly `li_at` from a debug-enabled Chrome; writes Playwright storage_state JSON)

## What cookies does each platform actually need?
If the user offers to paste cookies instead of fighting CDP, ask for the right ones:
- **LinkedIn** (for linkedin-scraper-mcp): `li_at` (the auth token, HttpOnly, ~150 chars) is MANDATORY; `JSESSIONID` helpful. Written to `/home/deeone/.linkedin-mcp/cookies.json` in Playwright storage_state shape. The full linkedin.com set also works.
- **X/Twitter**: OpenCLI already reuses the Chrome session, so agent-reach needs NOTHING for X. Only the standalone `twitter` CLI binary wants `auth_token` + `ct0` (from x.com) as `TWITTER_AUTH_TOKEN` / `TWITTER_CT0` env vars — that's optional and a red herring for agent-reach.
- **Reddit / Facebook / Instagram**: OpenCLI reuses the Chrome login; no cookies to paste.
