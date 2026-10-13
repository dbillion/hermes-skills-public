---
name: netlify-static-deploy
description: "Deploy static sites to Netlify via --create-site."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [netlify, deploy, static-site, frontend, vercel, gh]
---

# Netlify Static Deploy

## When to use
- User wants to deploy a **static** site (plain HTML/CSS/JS, no server runtime) to Netlify.
- Building a landing page, portfolio, learning hub, or tool UI from local assets.
- "deploy to netlify", "ship this to netlify", "give it its own repo + netlify".

## CLI discovery (don't conclude "not installed" too early)
The Netlify CLI is often installed via **bun**, not npm — so it won't be on a
default `bash` PATH even when the user says they're "logged in".
- Check bun globals: `ls $HOME/.bun/bin` (e.g. `/home/deeone/.bun/bin/netlify`).
- The user's interactive shell may be **zsh** whose PATH the agent's bash lacks.
  Discover their binaries: `zsh -ic 'command -v netlify'`.
- Once found, prepend to PATH for the session:
  `export PATH="/home/deeone/.bun/bin:$PATH"`.
- Verify auth: `netlify status` (shows user/team). "not linked" is fine — use
  `--create-site` (below), which creates + links in one step.

## Build the static site
Backend-free: `index.html` + `styles.css` + `app.js` (+ asset subdirs).
Optional `netlify.toml`:
```toml
[build]
  publish = "."
  command = ""
```
Copy media assets (GIFs/videos) into the publish dir — optimize first (below).

## Non-interactive deploy (the key command)
```bash
cd /path/to/site
export PATH="/home/deeone/.bun/bin:$PATH"
netlify deploy --create-site <site-name> --prod --dir .
```
- `--create-site <name>` creates a NEW site AND deploys in one non-interactive
  call. This **avoids the interactive `netlify link` / "What would you like to
  do?" prompt** that otherwise blocks automation.
- `--prod` publishes to production immediately.
- `--dir .` publishes the current folder.
- Output gives both the production URL and a unique deploy URL.

## Pitfall: interactive prompt + top-level-await crash
- `netlify link` and bare `netlify deploy` (without `--create-site`) prompt
  interactively and can crash with
  `Detected unsettled top-level await ... Netlify CLI has terminated unexpectedly`
  under **Node 25 + bun**. Always pass `--create-site` to stay non-interactive.
- `netlify link --team` is NOT a valid flag (errors). Don't use it.

## Asset optimization (GIFs/videos are heavy)
83 × 480p GIFs ≈ 184 MB unoptimized — too heavy to deploy cleanly. Shrink with
ImageMagick (usually present):
```bash
mkdir -p /home/deeone/.trash/gifs-orig-$(date +%s) && cp gifs/*.gif $_   # backup first
mogrify -strip -resize 380x -layers optimize -colors 128 gifs/*.gif
```
- Run in **background** (`background=true`, `notify_on_complete=true`) — 83 GIFs
  can exceed a 180s foreground timeout.
- `-colors 128` + `-layers optimize` cuts size dramatically, keeps animation.

## GitHub repo + push (if user wants "its own repo")
`gh` is usually authed as the user (verify: `gh auth status`). Create + push:
```bash
git init -q && git add -A && git -c user.email=dev@local -c user.name=hermes commit -q -m "init"
gh repo create <name> --public --source=. --remote=origin --push
```

## Verify before declaring done
Do NOT claim "deployed & working" without checking:
- `web_extract` the production URL → confirm HTML title/brand renders.
- `web_extract` a JS asset (e.g. `media.js`) → confirm it serves.
- You cannot execute in-browser JS from here, so the live fetch/render path is
  unverified by the agent — state that honestly.

## User preference: isolate & verify tool upgrades
When adding a NEW version of a tool the user already has (e.g. NotebookLM MCP
v2.0.0 alongside the old `nlm` CLI, or `@21st-dev/magic` alongside existing UI
tooling), the standing rule:
- **Test the new version in isolation first** (scoped mcp-cli config / stdio
  transport) before wiring it.
- **Register it as a SEPARATE utility** (e.g. `notebooklm-v2`, `magic-21st`),
  do NOT modify or replace the working one.
- Only declare success after a real tool call / live fetch proves it works.
- Never persist API keys in memory or chat; if a config edit writes a secret,
  it needs explicit user approval (consent gate) — don't retry a blocked edit.

## Worked example: DSA Learning Hub
- Parsed `VIDEO_GIF_INDEX.md` (83 algos, 8 categories) → `media.js` data file.
- Copied + optimized 480p GIFs into `gifs/`.
- `index.html` tabbed (Hub grid + Dictionary), `styles.css` premium dark theme,
  `app.js` grid + category filters + modal (GIF + glossary def + live Mermaid
  diagram via CDN).
- Deployed: `netlify deploy --create-site dsa-dictionary-dbillion --prod --dir .`
  → live at `https://dsa-dictionary-dbillion.netlify.app`.

## Final step for the user
The site is live after `deploy --prod`. Give the user the URL and note they can
re-run `netlify deploy --prod --dir .` from their terminal to update.
