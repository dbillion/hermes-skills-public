---
name: open-design-mcp-agent-workflow
description: "Build via Open Design MCP; drive agentic CLIs as sub-agents."
version: 1.0.0
author: Hermes Agent (captured from user workflow)
license: MIT
platforms: [linux, macos, windows]
tags: [open-design, mcp, acp, design-automation, carousel, pdf, agent-adapter, subagent]
related_skills: [build-discipline, writing-plans, verification-loop]
---

# Open Design MCP + Agent-CLI Workflow

How to use Open Design (github.com/nexu-io/open-design) as a **toolbox** that Hermes
drives, and how to extend it with other agentic CLIs as sub-agents. Captured from a
real end-to-end build: a travel carousel → 8 PNG cards + PDF, plus enumerating/harvesting
a Telegram account's channels.

## Mental model: two directions, only one we use

- **MCP (Hermes → OD)** — Hermes reaches INTO OD and calls its tools. OD is the
  toolbox; Hermes is the builder. **This is the path we use.** It works regardless of
  OD's run/execution state.
- **Agent adapter / ACP (OD → Hermes)** — OD dispatches tasks TO Hermes as an execution
  engine. Useful only when *OD's* UI is driving. In practice the `start_run` execution
  path was **broken** in our setup (returns `202` then `status: failed`), so we do NOT
  rely on it. We build by reading OD skill assets directly via MCP and rendering locally.
  Don't claim OD "executes" a skill for you — it didn't, and it's the reverse direction.

**User's own framing (verbatim intent):** *"we can just call its mcp to build, we are
the one building by using its mcps."* — the builder is Hermes; OD supplies skills/templates.

## Daemon (the MCP server host)

- OD runs a local privileged daemon. Keep it alive as a `systemd --user` service
  (`open-design-daemon.service`), pinned to the Node version its native addons need
  (Node 24.19.0 for `better-sqlite3` ABI 137). Auto-starts on boot.
- Health: `GET http://127.0.0.1:7456/api/health` → `200`. Also `/api/skills`
  (162 skills), `/api/plugins` (150), `/api/projects`.
- The agent adapter is registered (`hermes.ts` in the daemon's defs) and passes
  `hermes acp --check`, but that does NOT mean OD can execute runs — see caveat above.

## MCP tool surface (the real interface)

- After a gateway restart that reloads MCP, the tools appear as `mcp_open_design_*`.
  In a continuing session they may not be inline until a `/reset` — but you can always
  drive them directly via the daemon's stdio JSON-RPC (`node cli.js mcp --daemon-url
  http://127.0.0.1:7456`), which returns **22 tools** including:
  `list_skills`, `list_plugins`, `create_project`, `create_artifact`, `write_file`,
  `get_file`, `start_run`, `get_run`, `list_agents`, `collect_brief`, `confirm_brief`.
- Working build loop (proven): `create_project` → `write_file` (base64) ×N → files land
  in OD's artifact/project store. `start_run` is the broken execution path; don't use it.

## Building a deliverable (proven: travel carousel)

1. **Read the skill** via MCP `list_skills`; pick the template (e.g. `card-xiaohongshu`
   for a swipeable carousel, `deck-swiss-international` for a deck, `brandkit` for brand
   assets, `canvas-design` for PNG/PDF). Skill assets live under `skills/<id>/` in the OD
   repo; copy the HTML/Tailwind scaffold.
2. **Author the content** (cards, copy, palette) as HTML/CSS. Keep the template's
   structure (vertical `.deck` of `.card` divs, 1080×1440 / 3:4).
3. **Media**: OD's `fal-*` image/video skills need a fal.ai key — which was **LOCKED
   (HTTP 403, reason TOP_UP)** in our run. Fallback that worked: **Pexels** via API key
   (`api.pexels.com/v1/videos/search`) for stock video/pics. Download real clips, wire
   `<video>`/`<img>` with `poster=` frames (videos don't autoplay in a static screenshot).
4. **Render to upload-ready output** (local, not OD): headless Chromium screenshots each
   card → PNG; bundle PNGs into a PDF with PIL. See `scripts/render_carousel.py`.
5. **Write deliverables into OD** via MCP `write_file` so they show in the OD UI.

## Rendering cards → PNG + PDF (the local step)

OD skills produce HTML/CSS, not image files. To get postable assets:
- **Per-card HTML**: extract each `.card` div into its own minimal HTML file (the
  `?card=N` query-param isolation trick FAILS under headless Chrome — it ignores the
  param; you get 8 identical screenshots). Building one file per card is the reliable way.
- **Screenshot**: `chromium --headless --no-sandbox --window-size=1080,1440
  --screenshot=out.png file:///path/card-N.html`. Crop to 1080×1440 if the viewport
  differs.
- **PDF**: `PIL.Image.save(pdf, save_all=True, append_images=[...])` → one page per card.
- **Video cards**: put a `poster=` still (extract with `ffmpeg -ss 2 -i clip.mp4 -frames:v 1`)
  so the static card shows footage; the live `<video>` stays for the HTML deck.
- Gotcha: a "full page" `--screenshot` only captures the first viewport, not the whole
  scrollable deck — screenshot per card, never the whole page.

## Driving other agentic CLIs as sub-agents

Verified on the host (find via `command -v`): `pi`, `kilo`, `kiro`, `antigravity`,
`cursor`, `gemini`, `codex`, `claude`, `qwen` are present; `opencode`/`devin`/`grok`/
`deepseek`/`vela` are NOT. To test one as a sub-agent:
- Run it non-interactively with a `-p`/`exec` prompt; check auth. **Only `pi` returned a
  clean authenticated answer** (`pi -p "..."` → works, has read/bash/edit/write tools).
  `claude`/`gemini` said "not logged in"; `codex` errored on skill YAML; `qwen` hung;
  `antigravity` launched a browser and hung. So **`pi` is the one proven sub-agent**; the
  rest need auth or are broken in this env. Don't claim the others work.
- `pi` can read a repo, analyze code, and propose commands — it successfully diagnosed
  tgforwarder's forward logic and produced the correct (after flag-fix) commands.

## Pitfalls (this user's triggers — avoid)

- **Claiming OD "ran the skill"** — it didn't via start_run; we built from its assets.
- **Per-card screenshot via query param** — produces identical images; build one file per card.
- **fal.ai assumed working** — it was LOCKED (TOP_UP). Use Pexels stock as the fallback.
- **Claiming claude/codex/gemini are usable sub-agents** — only `pi` was verified.
- **"Excuses / it can't be done"** — user mandate is *find a way*. Diagnose, then deliver.

## Verification

- Daemon `HTTP 200` on `/api/health`.
- MCP `tools/list` returns 22 tools.
- Deliverable: open the HTML deck in a browser; confirm 8 distinct PNGs (different
  file sizes = different content) + a multi-page PDF; visually check 1-2 cards.

## Reference files (session-specific detail)
- `references/pexels-fal-media-fallback.md` — exact Pexels search/download calls and the
  fal.ai 403 TOP_UP finding, so a future session doesn't re-discover the lock.
- `references/agent-cli-probe.md` — the non-interactive probe results for each CLI
  (pi works; others need auth/broken).
- `scripts/render_carousel.py` — the Chromium+PIL render script (per-card HTML → PNG → PDF).
