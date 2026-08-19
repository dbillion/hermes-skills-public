---
name: spartan-angular-integration
description: >-
  Integrating spartan/ui (Helm styled components) into Angular projects when the
  official @spartan-ng/cli generators are unreliable — manual Helm copy, tsconfig
  paths, Tailwind v4 theming pitfalls, and headless verification. Use when the
  `ng g @spartan-ng/cli:ui` generator hangs, @spartan-ng/helm 404s from npm, the
  dark theme renders transparent/unstyled, or you need to convert Material screens
  to SpartAN without hand-rolling Tailwind.
user-invocable: false
---

# spartan/ui integration — the reliable path when the CLI generator fails

The upstream `@spartan-ng/cli:ui` generator is the happy path, but on Angular 21 hosts it
commonly HANGS on `installPeerDependencies` (an internal `npm install` that never returns) and
`@spartan-ng/helm` is NOT published to npm (install → 404). When that happens, do NOT wait on the
generator — copy the Helm source manually. This skill records the deterministic workaround plus
the two theming pitfalls that otherwise eat hours.

## When to use this instead of the `spartan` skill

Use the `spartan` skill for normal component APIs/composition. Use THIS skill when you are
*setting up* SpartAN in a project and hit: generator hang, helm 404, transparent theme, or
`spartan-button` classes with no color. It complements (does not replace) `spartan`.

## Manual Helm copy (the working setup)

1. `npm install -D @spartan-ng/cli @spartan-ng/brain` (brain IS on npm; helm is not).
2. `ng g @spartan-ng/cli:init --theme <neutral|...>` to scaffold Tailwind v4 + preset
   (init works; only `:ui` hangs). If init is interactive, pass `--theme`.
3. Copy Helm templates from the installed CLI package:
   ```bash
   ls node_modules/@spartan-ng/cli/src/generators/ui/libs/<component>/files/
   ```
   For each component: copy `files/` → `src/app/ui/<component>/`.
4. In the copied `.ts`, the templates reference an `importAlias` (default `@spartan-ng/helm`).
   Keep it (or substitute your prefix consistently).
5. Add `tsconfig.json` `paths` so the alias resolves to the copied dir:
   ```json
   "compilerOptions": { "baseUrl": ".",
     "paths": { "@spartan-ng/helm": ["src/app/ui"], "@spartan-ng/helm/*": ["src/app/ui/*"] } }
   ```
6. Install runtime deps the templates import:
   `npm install class-variance-authority clsx @ng-icons/core @ng-icons/lucide --legacy-peer-deps`
7. Create `src/app/ui/index.ts` barrel: `export * from './button';` etc. Do NOT export `./icon`
   unless you copied an icon component (the barrel must match real dirs or the build fails).
8. `components.json` with `"importAlias": "@spartan-ng/helm"` (the CLI would write this; create
   it by hand so future `:ui` runs, if they ever work, stay consistent).

A deterministic copy script beats the interactive generator: iterate `libs/*/files`, copy to
`src/app/ui/<name>`, string-replace the importAlias, then write `components.json` + the barrel.

## Theming pitfall #1 — `@theme inline` in `.scss` is stripped by Sass

Putting `:root { --primary: ... }` + `@theme inline { ... }` in a global `.scss` makes Sass drop
`@theme` at compile time. Result: `bg-primary`, `text-foreground` etc. NEVER appear in built CSS;
your dark theme silently falls back to transparent / leftover Material colors. **Verify** by
grepping the built `styles.css` for `.bg-primary` — if count is 0, this is why.

Fix: do NOT use `@theme inline` from SCSS. Use an explicit `@layer components` block mapping
semantic classes to `:root` CSS vars (vars survive Sass):

```scss
:root { --background:#051424; --foreground:#f8f9fa; --primary:#5C6BC0; --primary-foreground:#fff;
        --border:#2f3f92; --muted-foreground:#c6c5d3; --destructive:#ba1a1a; }
@layer base { body { background-color: var(--background); color: var(--foreground); } }
@layer components {
  .bg-primary { background-color: var(--primary); }
  .bg-background { background-color: var(--background); }
  .text-foreground { color: var(--foreground); }
  .text-muted-foreground { color: var(--muted-foreground); }
  .border-border { border-color: var(--border); }
  .text-destructive { color: var(--destructive); }
}
```

## Theming pitfall #2 — SpartAN `cva` marker classes are NOT utilities

`spartan-button`, `spartan-button-variant-default`, `spartan-badge-variant-secondary` are custom
marker classes from the copied Helm `cva()` defs. If you grep built CSS and `spartan-button` count
is 0, that is EXPECTED (markers, not selectors). The actual color comes from your `@layer
components` rules above + the cva variant classes. To color variants, ADD explicit rules:

```scss
.spartan-button-variant-default { background-color: var(--primary); color: var(--primary-foreground); }
.spartan-button-variant-destructive { background-color: var(--destructive); color: #fff; }
.spartan-badge-variant-secondary { background-color: var(--border); color: var(--foreground); }
```
(The `ui-theme` generator would emit these but it also hangs — add by hand.)

## Verification red herring — the orange `mat-raised-button`

After converting a screen, headless-render and check the button color. Seeing ORANGE does NOT mean
SpartAN failed — it's often a DIFFERENT component's leftover Material button (e.g. the header's
"Sign In" `mat-raised-button`, class `login-button`), not the form's submit. Target the real
submit: `document.querySelector('button[type=submit]')` → computed `background-color`. A correctly
themed `hlmBtn` submit is indigo (#5C6BC0) once pitfalls #1/#2 are fixed.

## Tailwind must scan copied Helm `.ts`

`tailwind.config.js` content globs must include `./src/**/*.{html,ts}` — the copied Helm components
live in `src/app/ui/**/*.ts` and carry Tailwind utilities inside cva variant strings. Glob-only-
`.html` purges them.

## User preference (this project)

User directive: "adopt the spartan component, that's the instruction — it is faster and you can
easily style them since they are Tailwind by default." Meaning: PREFER copied Helm components over
hand-written Tailwind markup for every screen; do not re-implement buttons/cards/inputs by hand.
Stitch-generated screen designs are the source of truth for layout/colors; implement them with
real Helm components 1-to-1.

## Verify before declaring done

- `npx ng build` → BUILD=0.
- Headless render each converted route: body bg = intended dark hex, submit button = indigo,
  no `mat-raised-button` orange remaining (except intentional header SSO, which should also be
  converted). Grep built CSS: `.bg-primary` count > 0.
