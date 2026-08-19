---
name: angular-material-to-spartan
description: Migrate an Angular Material app to SpartAN (shadcn-for-Angular) + Tailwind v4 + Stitch design tokens. Covers the exact failure modes (npm 404 on @spartan-ng/helm, CLI :ui generator hang on installPeerDependencies, Sass stripping @theme, cva variant classes not styling) and the working fixes. Use when converting Material screens to SpartAN or building a SpartAN + Tailwind v4 Angular app from a Stitch design system.
---

# Angular Material → SpartAN + Tailwind v4 (Stitch tokens)

## When to use
- Convert existing Angular Material components to SpartAN Helm components.
- Start a fresh Angular 21 + SpartAN 1.1.x + Tailwind v4 app styled from a Stitch design export.
- User says "use the spartan component" / "adopt spartan" / "stitch designs are the source of truth".

## Golden rule
Use REAL SpartAN Helm components (copied into the project), never hand-rolled Tailwind utilities that re-implement buttons/inputs/cards. The user explicitly rejected hand-rolled Tailwind: "adopt the spartan component, thats the instruction, it is faster and you can easily style them since they are tailwind by default." Match the Stitch PNG/JSON colors/layout 1-to-1.

## Setup (verified working, 2026-07)
1. Angular 21 required — SpartAN 1.1.x needs `peer Angular >= 21`. If on 20, `ng update @angular/core@21 @angular/cli@21` first.
2. Install (use --legacy-peer-deps; SpartAN deps can conflict):
   `npm install -D @spartan-ng/cli @spartan-ng/brain @tailwindcss/postcss tailwindcss postcss`
   `npm install class-variance-authority clsx @ng-icons/core @ng-icons/lucide`
3. Init theme: `npx ng g @spartan-ng/cli:init --theme neutral` (NOT `:info` — that's a dry-run that prints "Nothing to be done").
4. Tailwind config (content must include .ts so utilities scan Helm component source):
   `tailwind.config.js` → `content: ['./src/**/*.{html,ts}']`
   `postcss.config.json` → `{ "plugins": { "@tailwindcss/postcss": {} } }`

## CRITICAL FIXES (these will bite you)

### Fix 1 — @spartan-ng/helm is NOT on npm (404)
There is no published `@spartan-ng/helm` package. The `:ui` generator copies Helm SOURCE into the project; tsconfig must alias it.
- Generator `:ui` HANGS on `installPeerDependencies` (it runs `npm install` and stalls on this host). Workaround: copy the Helm source manually from the CLI package:
  `node_modules/@spartan-ng/cli/src/generators/ui/libs/<component>/files/`
  into `src/app/ui/<component>/`, then rewrite the import alias token (default `@spartan-ng/helm`) to point at your project.
- Add to `tsconfig.json`:
  `"baseUrl": ".", "paths": { "@spartan-ng/helm": ["src/app/ui"], "@spartan-ng/helm/*": ["src/app/ui/*"] }`
- Create `src/app/ui/index.ts` barrel exporting each component's public class (remove any `./icon` export if you didn't copy icons — it 404s).
- See `scripts/helm-copy.mjs` for a re-runnable copier.

### Fix 2 — Sass strips `@theme` / `@apply` in .scss
`@theme inline { ... }` inside a global `.scss` is STRIPPED by the Sass compiler, so no `bg-primary`/`text-foreground` utilities are generated, and `@layer base { @apply border-border }` fails. 
FIX: do NOT rely on `@theme`. Instead:
- Put raw CSS custom properties on `:root` (survive Sass): `--background`, `--foreground`, `--primary`, `--primary-foreground`, `--card`, `--border`, `--muted`, `--muted-foreground`, `--destructive`, `--sidebar`, etc.
- Add an `@layer components` block mapping semantic classes to those vars, e.g.:
  ```scss
  @layer components {
    .bg-background { background-color: var(--background); }
    .text-foreground { color: var(--foreground); }
    .bg-primary { background-color: var(--primary); color: var(--primary-foreground); }
    .border-border { border-color: var(--border); }
    .text-muted-foreground { color: var(--muted-foreground); }
    .bg-card { background-color: var(--card); }
    .bg-sidebar { background-color: var(--sidebar); }
    .bg-muted { background-color: var(--muted); }
  }
  ```
- Stitch palette example (dark): `--background:#051424; --card:#0b1a30; --primary:#5C6BC0; --primary-foreground:#ffffff; --border:#2f3f92; --muted:#111a2e; --muted-foreground:#9aa4bf; --sidebar:#0a1322; --destructive:#ba1a1a;`

### Fix 3 — SpartAN cva variant classes don't style themselves
`hlmBtn variant="default"` renders classes like `spartan-button spartan-button-variant-default spartan-button-size-md` — these are MARKER classes, NOT Tailwind utilities, and the `ui-theme` generator (which would define them) was NOT run. So the button shows unstyled unless you define them. Add to `@layer components`:
```scss
.spartan-button { display:inline-flex; align-items:center; gap:.5rem; border-radius:.75rem; font-weight:600; }
.spartan-button-variant-default { background:var(--primary); color:var(--primary-foreground); }
.spartan-button-variant-outline { border:1px solid var(--border); background:transparent; color:var(--foreground); }
.spartan-button-variant-ghost { background:transparent; color:var(--foreground); }
.spartan-button-variant-ghost:hover { background:var(--muted); }
.spartan-button-size-sm { height:2.25rem; padding:0 1rem; font-size:.875rem; }
.spartan-button-size-md { height:2.5rem; padding:0 1.25rem; }
.spartan-button-size-lg { height:2.75rem; padding:0 2rem; font-size:1rem; }
.spartan-badge-variant-default { background:var(--primary); color:var(--primary-foreground); }
.spartan-badge-variant-secondary { background:var(--muted); color:var(--muted-foreground); }
```
(Keep `inline-flex`, `items-center`, `shrink-0`, `whitespace-nowrap` etc. — those ARE real Tailwind utilities Tailwind generates from scanning `src/app/ui/**/*.ts`.)

### Fix 4 — Material controls with no SpartAN equivalent
Keep these as Material (don't fake them): `mat-paginator`, `mat-select`, `mat-slide-toggle`, `mat-menu`, `mat-datepicker`, `mat-slider`, `mat-expansion-panel`, `mat-nav-list`/`mat-list-item`, `mat-chip`, `quill-editor`, `mat-badge`, `mat-tooltip`. Convert only the chrome around them (cards/buttons/inputs/dividers/icons) to SpartAN. `mat-icon` → `<span class="material-icons">...</span>` (needs Material Icons font, already loaded via index.html).

## Conversion recipe per screen
1. `grep -nE "mat-|MatToolbar|MatCard|MatButton|MatIcon" <comp>.html` to inventory Material usage.
2. Rewrite `.html`: `mat-card`→`<section hlmCard>` (+ `hlmCardHeader`/`hlmCardContent`/`hlmCardTitle`/`hlmCardDescription`/`hlmCardFooter`); `mat-raised-button`/`mat-flat-button`/`mat-stroked-button`/`mat-button`→`<button hlmBtn variant="default|outline|ghost">`; `mat-form-field`+`matInput`→`<input hlmInput>` with `<label hlmLabel>`; `mat-spinner`→`<hlm-spinner>`; `mat-divider`→`<hlm-separator>`; `mat-icon`→`<span class="material-icons">`.
3. Patch `.ts` imports: drop `MatCardModule/MatButtonModule/MatIconModule/MatFormFieldModule/MatInputModule/MatProgressSpinnerModule/MatToolbarModule/MatDividerModule`; add `HlmButtonImports, HlmCardImports, HlmInputImports, HlmLabelImports, HlmBadgeImports, HlmSpinner, HlmSeparator` (import paths `@spartan-ng/helm/button` etc.). Keep `MatMenuModule, MatTooltipModule, MatSelectModule, MatListModule, MatExpansionModule, MatChipsModule, MatCheckboxModule, MatBadgeModule, MatSliderModule, MatDatepickerModule` if used.
4. Build after EACH screen: `npx ng build --configuration development` (expect BUILD=0). The TS path alias resolves at build even if LSP shows TS2304 stale errors.
5. Watch for: duplicate import lines when patching (LSP/tool can add a line twice), and `@if (cond())` wrongly attached to an element attribute (invalid syntax → "Empty expressions") — wrap in a real block instead.

## Verification
- Headless render check (Playwright) per route: assert computed bg of card == Stitch value, submit button bg == `--primary` (#5C6BC0), body bg == `--background`. A Material `mat-raised-button` renders orange (mdc-button) — that's the tell-tale you missed a screen.
- `grep -rE "mat-raised-button|login-button" dist/` after build to catch stragglers.

## Pitfalls observed
- Stale `ng serve` + `.angular/cache` can serve OLD markup after you edit — `rm -rf .angular/cache` and restart the dev server before trusting a render check.
- `fuser -k`/pkill may be blocked; kill via the process tool / `kill <pid>`.
- Header "Sign In" button is often the LAST orange Material element — it lives in `shared/components/header`, not the login page.

See `references/stitch-palette.md` for the full token table and `scripts/helm-copy.mjs` for the manual Helm copier.
