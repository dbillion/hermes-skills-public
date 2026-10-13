---
name: 21st-dev-magic
description: Premium shadcn UI via 21st.dev magic MCP. Free-tier limits.
category: frontend
version: 1
author: hermes-agent
license: MIT
hermes:
  tags: [frontend, ui, 21st-dev, shadcn, mcp, nextjs, netlify]
  related_skills: [design-taste-frontend, open-design-hermes-integration]
---

# 21st.dev magic MCP

21st.dev's "magic" MCP (server id `magic-21st`, package `@21st-dev/magic`) generates and serves shadcn/ui React components. It is the right tool when the user wants a premium, animated, on-brand UI and a 21st.dev API key is available.

## When to Use
- User wants premium, animated, on-brand UI and mentions 21st.dev, magic, "beautiful cards", "better designs", or "use mcp-cli to call 21st".
- A 21st.dev API key is available or the user says to use one.
- This is the class-level skill for 21st.dev magic MCP usage; do not invent a narrower one-off skill.

## When to reach for it
- User asks for "beautiful/animated cards", "better designs", "premium UI", or explicitly says "use 21st" / "use magic" / "call 21st via mcp-cli".
- User has provided a 21st.dev API key (looks like `21st_sk_...`).
- Pair with the taste skill for design discipline (single accent lock, dark+light theme lock, no em-dashes). The taste skill is USER-WNED — do not edit it; apply its rules yourself.

## CRITICAL: free-tier reality (verify with get_usage)
- `generate` is **PAID**. On the free tier it returns `locked: true, reason: "generation_limit_reached"`. It does NOT consume the daily retrieval quota. There is no retry workaround without upgrading (https://21st.dev/pricing).
- `get_component` (returns actual component **code**) is free but limited to **2 retrievals/day** (`freeRetrievalsPerDay: 2`).
- `search` (returns metadata only, free, effectively unlimited) → use it to find a component id, then spend ONE `get_component` retrieval on the best match.
- Reliable free flow: **search → get_component (code) → port by hand into your app.** Do not promise `generate` output on a free key.

## Call the tool — do not conclude it won't work
When the user says "use mcp-cli to call 21st", actually invoke it. The earlier mistake was reasoning about why it might fail instead of running it. It works; only `generate` is gated.

## Wiring the key (env var, never literal)
The key must live in a shell env var, referenced from config — never embed the literal key in `~/.hermes/config.yaml` (consent-gated + secret-leak risk).
- Export in shell profiles so Hermes expands it at MCP launch: `export TWENTY_FIRST_DEV_KEY="21st_sk_..."` in `~/.bashrc`/`~/.zshrc`/`~/.profile`.
- Hermes `config.yaml` server block: `env: { API_KEY: "${TWENTY_FIRST_DEV_KEY}" }`. (Setting the literal via an approved terminal edit is possible but env-var is preferred.)
- MCP servers added to config only become callable after an **external Hermes restart** (cannot restart from a gateway-connected session).

## Calling via mcp-cli (scoped, per policy)
Always scope `mcp-cli` with a temp config; pass the key as an env var to the `mcp-cli` process (never literally on the command line). Exact commands in `references/mcp-cli-recipes.md`.

## What each tool returns
- `search {query, framework}` → metadata list (id, name, previewUrl, installCommand). Free.
- `get_component {id}` → `componentCode` (tsx, copy-paste ready) + `demoCode` + `previewUrl`. Free (counts against 2/day). Port `componentCode`.
- `generate {prompt, mode:"code"|"sketch", variantCount, directions}` → on free tier returns `locked:true`. On paid: `structuredContent.url` to watch it build in a browser (does NOT return code inline). `mode:"sketch"` = self-contained HTML/Tailwind you can copy anywhere.
- `get_usage {}` → current tier + remaining retrievals.

## Porting into Next.js (App Router) + shadcn
Returned components are React/shadcn. To use in a Next.js app:
- Place under `src/components/ui/` (e.g. `bento-grid.tsx`); they import `@/lib/utils` (`cn`) and `lucide-react` — ensure installed (`clsx tailwind-merge class-variance-authority lucide-react`, plus `@radix-ui/react-*` for interactive primitives like Dialog/Tabs).
- Re-theme to the user's locked accent: replace hardcoded icon/text colors (`text-blue-500`, `text-purple-500`) with `text-primary` and the hover radial with the accent color.
- Keep taste-skill discipline: one accent, dark+light CSS-variable tokens, no em-dashes.

## Deploy (Next.js → Netlify Next runtime)
Build the app, then deploy. Pitfalls in `references/netlify-next-deploy.md`:
- npm's project-scoped `allowScripts` gate blocks `create-next-app`/`npm install` → fix by adding `allowScripts` to the project `package.json` (NOT the `--allow-scripts` flag, which is also blocked).
- Netlify: first create with `--create-site --team <team>`; **redeploy an existing linked site with `netlify deploy --prod` and NO `--team`** (`--team` only valid alongside `--create-site`).
- Prefer MP4 over GIF for animations: 88MB vs 189MB for the same 83 clips; browsers autoplay `<video muted loop playsInline>`.

## Verification
After deploy: `curl -s -o /dev/null -w "%{http_code}" <url>/<route>` should be 200; grep served HTML for expected markers (hero copy, bento labels). Push large media to GitHub in the background (can exceed a 300s foreground timeout).
