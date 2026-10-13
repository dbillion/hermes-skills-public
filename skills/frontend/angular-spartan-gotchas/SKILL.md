---
name: angular-spartan-gotchas
description: >-
  Angular + Spartan UI (shadcn-for-Angular) + Tailwind v4 migration and build gotchas. Covers the
  non-obvious failure modes from installing Spartan 1.1.1 on Angular 21: the @spartan-ng/helm npm 404
  workaround (manual copy + tsconfig paths), the @spartan-ng/cli:ui generator hang, the @theme inline
  Sass-stripping bug that kills Tailwind colors, production build-budget errors, and headless
  verification patterns. Use when scaffolding, migrating, or debugging a SpartAN + Tailwind Angular app.
license: MIT
tags: [angular, spartan, tailwind, migration, troubleshooting]
globs:
  - "**/styles.scss"
  - "**/angular.json"
  - "**/tsconfig.json"
  - "**/*.component.ts"
---

# Angular + Spartan UI + Tailwind v4 — Gotchas & Verified Workarounds

Condensed from a real Angular 21 + Spartan 1.1.1 + Tailwind v4 migration (July 2026). Each item below
is a failure mode that actually happened and the fix that worked.

## Install (Angular 21 + Spartan 1.1.1 + Tailwind v4)
1. `npm install -D @spartan-ng/cli` then `ng g @spartan-ng/cli:init --theme neutral`.
2. If init fails on peer/Angular-version, upgrade Angular first (`ng update`). **Spartan 1.1.1 requires Angular >= 21.**
3. After init, `styles.scss` has duplicated `@use` imports + an `@theme inline` block — clean it (see GOTCHA 3).

## GOTCHA 1 — `@spartan-ng/helm` is NOT on npm (404)
Published packages: `@spartan-ng/brain` and `@spartan-ng/cli`. Helm sources ship INSIDE the CLI at
`node_modules/@spartan-ng/cli/src/generators/ui/libs/<component>/files/`.
**Workaround — manual copy + tsconfig path mapping:**
- Copy each component dir from CLI `libs/<c>/files/` into `src/app/ui/<c>`
  (button, card, input, label, field, badge, spinner, separator, sonner, typography, utils).
- `tsconfig.json`: `"baseUrl": "."`, `"paths": { "@spartan-ng/helm": ["src/app/ui"], "@spartan-ng/helm/*": ["src/app/ui/*"] }`
- `npm install class-variance-authority clsx @ng-icons/core @ng-icons/lucide --legacy-peer-deps`
- Clean the barrel `src/app/ui/index.ts` (remove exports for uncopied modules like `./icon`).

## GOTCHA 2 — `ng g @spartan-ng/cli:ui` generator HANGS
It runs `installPeerDependencies` (npm install) and hangs on constrained hosts. Do NOT use the
generator; use the manual copy from GOTCHA 1. The `ui-theme` generator also hangs for the same reason
(the variant theme layer it would emit must be hand-written — see GOTCHA 3).

## GOTCHA 3 — `@theme inline` in `.scss` is STRIPPED by Sass
Tailwind v4 + Sass strips `@theme inline { }` from `.scss`, so NO color utilities are generated.
Symptom: transparent backgrounds, unstyled (orange Material) buttons, dist CSS has no `.bg-primary`.
**Fix — do NOT use `@theme` inside `.scss`:**
1. Raw palette as CSS custom properties under `:root` (e.g. `--background: 222 41% 11%;` for #051424).
2. `@layer components { .bg-primary { background-color: hsl(var(--primary)); } .bg-background { ... } .text-foreground { ... } .text-muted-foreground { ... } .bg-border { ... } .border-border { ... } .text-primary { ... } }`
3. Map SpartAN `cva` variant marker classes (CUSTOM classes, not utilities) in the same `@layer components`:
   `.spartan-button-variant-default { background-color: hsl(var(--primary)); color: hsl(var(--primary-foreground)); }`
   plus `-outline`/`-secondary`/`-ghost`/`-destructive`/`-link` and sizes `-sm`/`-md`/`-lg`;
   `.spartan-badge-variant-default/secondary/destructive/outline` similarly.
   NOTE: `spartan-button` marker class will NOT appear as a selector in dist CSS — EXPECTED. Verify by
   grepping dist for `.bg-primary { background-color: hsl(var(--primary)); }`.

## Verification (headless — Playwright at /home/deeone/node_modules/playwright)
- `npx ng serve --port 4200` as a BACKGROUND process. If "Port 4200 in use", a STALE `ng serve` from a
  prior session is running — `ss -tlnp | grep 4200` → `kill -9 <pid>` → start fresh. A stale server
  serving an OLD build is the #1 cause of "blank screen / broken styles" false alarms.
- Assert computed colors, not just "no errors": `getComputedStyle(document.body).backgroundColor`
  → expect `rgb(5, 20, 36)` for #051424 dark theme.
- LSP tsc errors for `@spartan-ng/helm/*` are often STALE; trust `npx ng build` (respects tsconfig paths).

## Production build-budget pitfall
`npx ng build` (no --configuration) enforces budgets. Legacy Material `*.scss` exceeds default 8kB
component-style error and 500kB initial error → BUILD=1. Fix `angular.json`: `anyComponentStyle` error
→ 20kB, `initial` error → 2MB. Dev build (`--configuration development`) skips budgets.

## Angular control-flow & binding pitfalls
- `@for` `track` must be UNIQUE. Duplicate data → NG0955; use `track $index`.
- `(keydown.enter)="$event.shiftKey ..."` fails ($event typed Event). Use `onEnter($event: KeyboardEvent)` + `onEnter($any($event))`.
- Parent rendering child via `<router-outlet>` must NOT import the child (e.g. SearchPage must not import SearchInterface) → NG8113.

## API calls from Angular (absolute base URL)
- `api.config.ts` holds ABSOLUTE base URL (http://localhost:3000/api). Dev server does NOT proxy /api.
  Relative `/api/...` fetch hits :4200 → 404. Always use `API_CONFIG.baseUrl`.
- CORS on NestJS agent controller is `Access-Control-Allow-Origin: *` → cross-origin fetch works.
- AG-UI SSE: POST `{messages:[{role:'user',content}]}` → `res.body.getReader()` → split on `\n\n` →
  parse `data: {json}` → accumulate `TEXT_MESSAGE_CONTENT.delta` into a Subject<string>.

## Stitch 1-to-1 workflow (user mandate pattern)
- Use REAL copied Helm components (hlmBtn/hlmCard/hlmInput/hlmLabel/hlmBadge/hlmSpinner/hlmSeparator),
  do NOT hand-roll Tailwind buttons. Stitch PNGs/JSON are SOURCE OF TRUTH for colors/type.
- For controls with no SpartAN equivalent (mat-select, mat-slide-toggle, mat-menu, mat-autocomplete,
  mat-chip, quill, mat-tab-group, mat-snack-bar, mat-dialog, mat-paginator, mat-nav-list/mat-expansion):
  RETAIN the Material module as functional control, convert visible chrome to SpartAN. Hybrid is accepted.

See `references/workflow-gotchas.md` for the full copy-paste code blocks and the verified SSE snippet.
