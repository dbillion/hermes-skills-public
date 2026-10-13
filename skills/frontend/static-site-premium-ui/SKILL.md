---
name: static-site-premium-ui
description: Premium animated static hub on Netlify, no React build.
version: 1
author: hermes-agent
license: MIT
metadata:
  hermes:
    tags: [frontend, static-site, netlify, dsa, ui, tailwind-alternative]
    related_skills: [design-taste-frontend, premium-webapp-build]
---

## When to Use
- The deploy target MUST be static files (Netlify, GitHub Pages, S3), NOT a React or Next build.
- User explicitly says "no framework / just HTML", or zero-build is a hard requirement.
- User wants a premium, media-rich, animated learning hub, landing page, or gallery AND a framework is not wanted.

**DEFAULT-CHANGED (dbillion correction):** For premium/interactive/edtech UI work, do NOT reach for static first. The user (Oludayo Adeoye / dbillion) explicitly rejected a static HTML build in favor of a real framework: "why cant it be a nextjs app that can benefit from all the codes in shadcn since you have that skill and also od skills for great web design?" When the user wants React/shadcn/Next, interactivity, or names a framework, use **`premium-webapp-build`** instead. Static HTML is now a FALLBACK, not the default.

- Pair with `design-taste-frontend` for the dials, locks, AI-tells, and pre-flight checklist.

# Static Site Premium UI (vanilla HTML/CSS/JS)

Use when: the user wants a premium, media-rich, animated hub or landing page that
deploys as static files (Netlify, GitHub Pages, S3). The companion skill
`design-taste-frontend` owns the React/Tailwind defaults and the full pre-flight
matrix; this skill translates those into vanilla CSS plus JS and adds the
static-host-specific gotchas the taste skill does not cover.

## Load order
1. `design-taste-frontend` (the dials, locks, AI-tells, pre-flight checklist).
2. This skill (static translation plus deploy mechanics).

## Design Read (declare before coding)
"Reading this as: a learning hub or landing page for the audience, with a premium
dark-tech educational language, leaning toward native CSS plus a display font,
a single locked accent, glassmorphism, and motivated motion."

Baseline dials: DESIGN_VARIANCE 8, MOTION_INTENSITY 6, VISUAL_DENSITY 4.

## CSS token system (replaces Tailwind dark variant plus design systems)
Define once in `:root`, override under `[data-theme="light"]`:

```css
:root {
  --bg:#070b0a; --surface:rgba(255,255,255,.04); --border:rgba(255,255,255,.09);
  --text:#eaf2ee; --muted:#93a39c;
  --accent:#34d399;        /* ONE locked accent, used identically everywhere */
  --accent-ink:#04150f;    /* high-contrast text ON accent fills */
  --radius-card:18px; --radius-btn:999px; --radius-input:14px;  /* SHAPE lock */
}
[data-theme="light"]{ --bg:#f4f7f5; --text:#0c1714; --accent:#0f9d6b; /* ... */ }
```

- Color Consistency Lock: one `--accent`; never a second hue mid-page.
- Shape Consistency Lock: reuse the three radius vars; no ad-hoc px per component.
- Page Theme Lock: ship BOTH dark and light as real themes. Topbar toggle sets
  `document.documentElement.dataset.theme`, persists to `localStorage`, and
  re-inits Mermaid (`mermaid.initialize({theme: t==='dark'?'dark':'neutral'})`).

## Em-dash ban covers ALL source files
Pre-flight checks visible copy, but em-dashes also leak into code comments and
get flagged in PR reviews. Before shipping:
`grep -rln "—\|–" . --include="*.js" --include="*.css" --include="*.html" --include="*.md"`
Replace with a hyphen (or restructure). ZERO em-dashes anywhere, ever.

## Motivated motion only (vanilla)
- Entry reveal: `@keyframes card-in { to { opacity:1; transform:none } }` on cards,
  `animation-delay` staggered by index (cap ~360ms).
- Hover: `transform: translateY(-4px)` plus border-color to accent.
- Modal: short `modal-in` fade or scale.
- Gate under `@media (prefers-reduced-motion: reduce) { .card{animation:none;opacity:1;transform:none} }`.
- Animate ONLY `transform` and `opacity`.

## Real assets, not fake screenshots
Use actual media (for example 83 algorithm GIFs in `gifs/`). Never div-based fake
previews. Copy assets locally; reference `gifs/<name>.gif`. For more than 5 items
use a grid, tabs, or filter chips, not a long `<ul>` with `divide-y`.

## GIF payload performance (critical)
Eighty-three 1080p-origin GIFs were about 186MB. `mogrify -layers optimize` on that
many files is FAR too slow (12+ minutes, killed). Fast parallel resize instead:
`ls gifs/*.gif | parallel -j4 "mogrify -strip -resize 360x {}"` (4-core box).
`gifsicle` is NOT installed by default; `parallel` IS. Keep width ~360px for grid
thumbnails. Verify final `du -sh gifs` before deploy.

## Verify a static site locally
`python3 -m http.server 8099` MUST launch with `background=true`; in a SEPARATE call
poll the server, sleep 1 to 2 seconds, then `curl -s -o /dev/null -w "%{http_code}"
http://127.0.0.1:8099/`. A foreground curl before the server is up returns `000`
(not a real failure). Assert 200 for index, css, js, and one asset.

## Deploy
- GitHub: `gh repo create <name> --private --source=. --remote=origin`, commit, `git push -u origin main`.
- Netlify: `~/.bun/bin/netlify deploy --create-site <site> --prod --dir .`
  (non-interactive `--create-site` avoids the top-level-await crash under Node25 plus
  bun interactive prompt). Use the bun-installed netlify at `~/.bun/bin/netlify`.
- `.gitignore`: exclude `.netlify/`, `.DS_Store`.

## User preference (dbillion / Oludayo Adeoye)
He expects PREMIUM, MEDIA-RICH, ANIMATED UIs (GIFs, mermaid, animated cards), never
plain text, for edtech and DSA brand work. **For premium/interactive work he now
expects a real framework (Next.js + shadcn), not static HTML** — see the correction
in "When to Use". Always load `design-taste-frontend` on UI tasks. New MCP utilities
(21st-dev magic, notebooklm-v2) go in as SEPARATE servers, never replacing existing ones.
If a framework is wanted, use `premium-webapp-build`.
