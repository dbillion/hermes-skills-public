---
name: premium-webapp-build
description: Build premium interactive web apps with Next.js + shadcn.
version: 1
author: hermes-agent
license: MIT
metadata:
  hermes:
    tags: [frontend, nextjs, shadcn, tailwind, 21st-dev, open-design, netlify, premium-ui]
    related_skills: [static-site-premium-ui, design-taste-frontend]
---

# Premium Webapp Build (Next.js + shadcn + 21st.dev / OpenDesign)

## When to Use (and when NOT)
Use this skill as the DEFAULT for premium UI work when ANY of these is true:
- The user says "something better than plain text", wants animated cards, media-rich pages, or a real product UI.
- The user names **Next.js / React / shadcn / Tailwind components / a real app**.
- The page needs interactivity beyond CSS (client state, modals with dynamic data, visualizers, quizzes, routed pages).
- The user already has 21st.dev `magic` or OpenDesign wired and wants to USE them.

Use `static-site-premium-ui` ONLY as a fallback when: the deploy must be zero-build static files, OR the user explicitly says "no framework / just HTML". Do not reach for static by default for a premium brief — it forfeits shadcn components and real routing, and the user (dbillion) has explicitly rejected static-first for premium work.

Load order:
1. `design-taste-frontend` — dials, locks, AI-tells, pre-flight matrix (mandatory; applies unchanged to React).
2. `static-site-premium-ui` — for the CSS token system and em-dash ban if hand-rolling any CSS.
3. This skill — framework scaffolding, shadcn, 21st.dev/OpenDesign wiring, Netlify Next deploy.

## Design Read (declare before coding)
"Reading this as: a learning hub / product page for the audience, with a premium dark-tech language, leaning toward Next.js App Router + Tailwind v4 + shadcn/ui, a single locked emerald accent, and motivated motion via motion/react."

Enforce the taste-skill locks: ONE accent (we use emerald `#34d399` / `#0f9d6b`), dark+light theme lock via CSS tokens, shape consistency, ZERO em-dashes in all source, reduced-motion support.

## Scaffold a Next.js app (verified path)
```bash
export PATH="/home/deeone/.bun/bin:$PATH"
rm -rf myapp
npx --yes create-next-app@latest myapp --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --no-turbopack
```
Tailwind v4 + App Router + `src/`. Then install the shadcn primitive stack:
```bash
npm install clsx tailwind-merge class-variance-authority lucide-react \
  @radix-ui/react-slot @radix-ui/react-dialog @radix-ui/react-tabs mermaid
```

### npm install scripts gate (CRITICAL, non-obvious)
On this box npm blocks postinstall scripts with `EALLOWSCRIPTS` ("--allow-scripts is not allowed in project-scoped installs"). Fix per-project: add to the project's `package.json`:
```json
"allowScripts": { "esbuild": true, "sharp": true, "@tailwindcss/oxide": true, "core-js": true }
```
(The `--allow-scripts` CLI flag is REJECTED by the project policy; only the package.json field works.) Then `npm install` succeeds. (unrs-resolver's postinstall stays unapproved with a harmless warning — ignore it.)

## shadcn components (hand-build, standard)
`@latest shadcn` generator can hang; hand-write the small standard components instead — see `templates/shadcn-basics.tsx` for `cn`, `Button`, `Card`, `Badge`, `Dialog`, `Tabs`. They are thin wrappers over Radix + cva. Copy into `src/components/ui/`.

## 21st.dev magic + OpenDesign (the user's stated utilities)
The user wants these USED, not replaced. Wiring + calling them:
- **Wire `magic-21st` into `~/.hermes/config.yaml`** as a SEPARATE mcp_servers entry (never overwrite existing servers). Command `npx -y @21st-dev/magic@latest`, env `API_KEY`. CRITICAL: put the key in a SHELL ENV VAR and reference it as `${TWENTY_FIRST_DEV_KEY}` in config — never paste the literal key into config.yaml (consent gate + secret hygiene). See reference `references/magic-mcp-cli.md`.
- **Call it via scoped `mcp-cli`** (never bare): `mcp-cli -c /tmp/magic-scope.json call magic-21st/search '{"query":"..."}'`. `search` and `get_component` are the free/quota steps; `generate` (returns a build URL, not inline code) is PAYWALLED on the free tier (`generation_limit_reached`). Spend retrieval quota on real component code (e.g. Hero Animated id 1788) and port the design DNA into the app.
- **OpenDesign** (`od` MCP, daemon on :7456) has 162 skills (card-xiaohongshu, frontend-slides, etc.) when a full page generation is wanted.

## Media: prefer MP4 over GIF for large archives
For 80+ walkthrough assets, GIFs are ~2x the size of the 1080p MP4 source (189MB GIF vs 88MB MP4 in our run). Use `<video autoPlay loop muted playsInline>` with the MP4s in `public/videos/`. Copy the source MP4s, not the GIFs.

## Netlify deploy (Next.js runtime) — VERIFIED
```bash
# netlify at ~/.bun/bin/netlify, team dbillion, authed as Oludayo/dayozoe
cat > netlify.toml <<'TOML'
[build]
  command = "npm run build"
  publish = ".next"
[dev]
  command = "npm run dev"
  port = 3000
[[plugins]]
  package = "@netlify/plugin-nextjs"
TOML
npm install -D @netlify/plugin-nextjs
netlify deploy --build --prod --create-site --team dbillion
```
`--auth` requires a token VALUE (not a flag alone) — omit it when the CLI is already authed. The build uses Turbopack; a transient "Error while running build" on first try cleared on re-run. After deploy, VERIFY with `curl -s -o /dev/null -w "%{http_code}" <url>/` and grep for hero copy; also check a `/videos/*.mp4` returns 200 video/mp4.

## Verify before claiming done
- `npm run build` passes (TS + static generation of all routes).
- `git push` (88MB videos is fine; 189MB GIFs timed out at 180s — another reason to use MP4).
- Live HTTP 200 on `/`, a routed page, and a media asset.

## User preference (dbillion / Oludayo Adeoye)
Expects PREMIUM, MEDIA-RICH, INTERACTIVE UIs, never plain text, for edtech/DSA brand work. Wants real frameworks (Next.js + shadcn) over static HTML. New MCP utilities (21st-dev magic, notebooklm-v2, OpenDesign) are SEPARATE servers, never replacements. Secrets go in env vars, never pasted into config files.
