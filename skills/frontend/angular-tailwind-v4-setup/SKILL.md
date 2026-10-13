---
name: angular-tailwind-v4-setup
description: >-
  Wiring Tailwind CSS v4 + a component library (Spartan/ui, or any Tailwind-based UI) into an
  Angular 21 app built with @angular/build. Covers the Angular-version gate, the interactive
  `init` schematic, the TWO config files Tailwind v4 JIT requires under @angular/build, the
  `@theme inline` token pattern, Material+Tailwind Sass ordering, and how to verify the theme
  actually paints (not just BUILD=0). Use when migrating an Angular Material app to Tailwind,
  adding Spartan/ui, or debugging "Tailwind classes do nothing / page renders transparent".
user-invocable: false
allowed-tools:
  - Bash(ng g @spartan-ng/cli:*)
  - Bash(ng update *)
  - Bash(npm install *)
---

# Angular 21 + Tailwind v4 setup (Spartan / any Tailwind UI)

## When this applies
- Adding Spartan/ui (`@spartan-ng/brain` + `@spartan-ng/cli`) to an Angular app.
- Migrating an Angular Material app to Tailwind utility classes.
- Symptom: `ng build` succeeds but `bg-primary` / `bg-background` / `text-foreground` produce NO
  CSS, so the page renders with transparent backgrounds. BUILD=0 lies.

## Version gate
Spartan 1.1.x needs Angular >= 21 (`@angular/core ">=21.0.0 <23.0.0"`). On Angular 20 the install
ERESOLVEs. Upgrade FIRST on an isolated branch:
```bash
git checkout -b tailwind-spartan
ng update @angular/core@21 @angular/cli@21 @angular/cdk@21 @angular/material@21
# commit before ng update (it refuses a dirty tree); run `npm install` first if it complains about
# extraneous babel packages (reconciles node_modules).
npm install @spartan-ng/brain@^1.1.1 @spartan-ng/cli@^1.1.1 \
  tailwindcss @tailwindcss/postcss postcss autoprefixer --legacy-peer-deps
```
There is NO `@spartan-ng/helm` npm package in the 1.1.x line (404) — Helm is copied in by the CLI.

## init is interactive — pass flags
`ng g @spartan-ng/cli:init` hangs in a non-TTY (prompts app/theme/styles). Run:
```bash
ng g @spartan-ng/cli:init --project <app> --theme neutral --styles-entry-point src/styles.scss
```
`ng g @spartan-ng/cli:info` is READ-ONLY (prints context, scaffolds nothing).

## THE critical fix: Tailwind v4 JIT needs TWO config files
`@import 'tailwindcss/...'` in styles.scss alone gives reset/utilities CSS but does NOT scan
templates — so component classes never generate. `@angular/build` (Angular 21) enables Tailwind only
when it detects a PostCSS config.

Create BOTH:
- `tailwind.config.js` with `content: ['./src/**/*.{html,ts}']`
- `postcss.config.json` → `{ "plugins": { "@tailwindcss/postcss": {} } }`

Without `postcss.config.json` the build errors: "trying to use tailwindcss directly as a PostCSS
plugin ... install @tailwindcss/postcss".

## Custom palette — `@theme inline` is STRIPPED by Sass (use manual mapping)

The `@theme inline` pattern below is the documented approach, but in Angular's
`.scss` global stylesheet the **Sass compiler drops the entire `@theme` at-rule**
before PostCSS/Tailwind processes it. Symptom: built CSS has your `:root` vars
but ZERO `.bg-*` / `.text-*` rules, and `bg-primary` is "NOT FOUND" — so the
page renders transparent even though `ng build` returns 0.

```scss
/* DOES NOT WORK under Angular's SCSS pipeline — Sass eats @theme: */
@theme inline {
  --color-background: #051424; --color-primary: #5C6BC0; /* … */
}
```

**The fix: define the semantic utilities MANUALLY in `@layer components`** (Sass-safe),
mapping to `:root` CSS vars that DO survive:

```scss
:root {
  --background: #051424; --foreground: #f8f9fa;
  --primary: #5C6BC0; --primary-foreground: #ffffff;
  --card: #0b1a30; --muted-foreground: #bac3ff;
  --border: #2f3f92; --ring: #5C6BC0;
  --destructive: #ba1a1a; /* …rest of palette… */
}
@layer components {
  .bg-background { background-color: var(--background); }
  .text-foreground { color: var(--foreground); }
  .bg-primary { background-color: var(--primary); }
  .text-primary { color: var(--primary); }
  .text-primary-foreground { color: var(--primary-foreground); }
  .bg-card { background-color: var(--card); }
  .bg-muted { background-color: var(--muted); }
  .text-muted-foreground { color: var(--muted-foreground); }
  .border-border { border-color: var(--border); }
  .bg-destructive { background-color: var(--destructive); }
  .text-destructive { color: var(--destructive); }
  /* opacity variants (Tailwind's /opacity needs @theme, so hand-roll): */
  .bg-primary\/10 { background-color: color-mix(in srgb, var(--primary) 10%, transparent); }
  .border-primary\/40 { border-color: color-mix(in srgb, var(--primary) 40%, transparent); }
}
```
Verify the rule is present in `dist/**/styles.css` via `grep` for
`.bg-primary { background-color: var(--primary) }` — NOT just BUILD=0.

## Material + Tailwind ordering
Sass requires `@use` before `@import`/`@layer`. Put `@use '@angular/material' as mat;` at the top
of styles.scss, before the `tailwindcss` `@import`s.

## Verify it PAINTS (BUILD=0 is not enough)
Headless render check (Playwright Chromium cached at ~/.cache/ms-playwright; module at
~/node_modules/playwright). Expect `rgb(5, 20, 36)` for a `#051424` bg, NOT `rgba(0,0,0,0)`.
If transparent → `@theme inline` or PostCSS config missing.

## Stale dev-server trap
Multiple `ng serve` on :4200 (one via detached `(... &)` subshell not tracked by the process mgr)
serve OLD bundles; DOM shows Material `mdc-button` + empty `--color-primary` even after edits.
Ensure a single server on the port before any render check.

See `references/angular21-tailwind-v4.md` for full configs + the exact render-check script.
For the SpartAN `cva` variant-class theme (`.spartan-button-variant-default` etc. have
NO CSS until you map them), see `angular-spartan-setup` Step 5.
