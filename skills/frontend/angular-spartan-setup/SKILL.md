---
name: angular-spartan-setup
description: >-
  Scaffold Spartan UI (shadcn-for-Angular: @spartan-ng/brain + @spartan-ng/helm)
  into an Angular project. Covers installing @spartan-ng/cli, the Angular 21
  peer-dependency requirement (Spartan 1.0.0+ needs @angular/cdk >=21, so an
  Angular 20 project must upgrade first), and the non-interactive `ng g
  @spartan-ng/cli:init --theme <name>` flag that avoids the hanging interactive
  prompts. For component usage patterns, see the hub skill angular-best-practices-spartan.
license: MIT
tags: [angular, spartan, tailwind, ui]
---

# Angular Spartan UI Setup

Spartan = shadcn-for-Angular. It brings Tailwind + headless, accessible components
(Brain = behavior, Helm = styling) to Angular. This skill covers *scaffolding it
into a project* — the part that silently fails or hangs. For component usage, see
the hub-installed `angular-best-practices-spartan`.

## PREREQUISITE — Angular version
Spartan `1.0.0`+ requires **Angular >= 21**:
```
npm error peer @angular/cdk@">=21.0.0 <23.0.0" from @spartan-ng/brain@1.1.1
```
If the project is on Angular 20 (e.g. `@angular/cdk@20.2.x`), `npm install` of
`@spartan-ng/brain` will ERESOLVE-fail. Two options:
- **Upgrade Angular 20 → 21** (`ng update @angular/core@21 @angular/cli@21`), THEN
  install Spartan 1.1.1. This is the path that honors "use Spartan".
- Stay on 20 and skip Spartan (build Tailwind UI directly without the component kit).

There is NO Angular-20-compatible Spartan in the current release line.

## Step 1 — install the CLI
```bash
npm install -D @spartan-ng/cli        # ~1.1.1
```
Note: there is no `@clerk/clerk-angular` package (Clerk dropped the Angular SDK);
for Clerk SSO in Angular use `@clerk/clerk-js` directly. Unrelated, but a common
confusion on the same project.

## Step 2 — run init NON-INTERACTIVELY
`ng g @spartan-ng/cli:info` is **informational only** (prints project context as
JSON) — it does NOT scaffold anything ("Nothing to be done"). The real scaffold
is `init`, but it is **interactive** and will hang waiting for input:
```
? Choose which application you want to add the theme to: …
? Choose which theme to apply … (neutral|stone|zinc|gray|slate)
? Path to the styles entry point …
```
Piping newlines does NOT advance the selector cleanly (it beeps / re-prompts).
Pass `--theme` to run non-interactively:
```bash
npx ng g @spartan-ng/cli:init \
  --project knowledge-sharing-app \
  --theme neutral \
  --styles-entry-point src/styles.scss
```
`--theme` (one of neutral|stone|zinc|gray|slate) disables ALL prompts. `neutral`
is the base token set; override the Tailwind theme colors later with your design
tokens (e.g. Stitch colors) in `tailwind.config` + the theme SCSS.

Flags (from `ng g @spartan-ng/cli:init --help`):
- `--project <name>` — app to add the theme to (omit = prompted).
- `--theme <name>` — applies theme AND makes the generator non-interactive.
- `--styles-entry-point <path>` — relative to workspace root (e.g. `src/styles.scss`);
  auto-detected when omitted, but pass it to be safe.
- `--prefix <class>` — prefix for theme class names (e.g. `theme-zinc`); empty = global.

## Step 3 — verify
```bash
ls tailwind.config.js spartan/ src/app/helm/ 2>/dev/null   # scaffolding present
grep -E "spartan|tailwind" package.json                    # deps added
```
If those are absent after init "succeeded", the init silently did nothing —
re-run with the explicit flags above.

## Step 4 — add Helm components (the `:ui` generator)

`ng g @spartan-ng/cli:ui --name=button` copies Helm code into `src/app/ui/<name>/`
and creates `components.json` on first run. BUT on constrained/slow hosts it **HANGS
on the internal `npm install`** (exit 124, no files written — `components.json` + `ui/` absent).

**Fallback — replicate what the generator does (manual copy):**
1. Helm templates live in `node_modules/@spartan-ng/cli/src/generators/ui/libs/<name>/files/`
   as `*.template` files. Copy each `files/` tree → `src/app/ui/<name>/`, strip `.template`,
   and substitute the placeholder `<%- importAlias %>` → `@spartan-ng/helm`.
2. Copy `libs/utils/files/**` → `src/app/ui/utils/` (every component imports `@spartan-ng/helm/utils`).
3. Create `src/app/ui/index.ts` barrel: `export * from './button'; …` for each component
   (DROP `icon` — there is no `icon` template; use `@ng-icons` directly).
4. Create `components.json`: `{ "importAlias": "@spartan-ng/helm", "componentsPath": "src/app/ui" }`.
5. Add tsconfig `paths` (a DIRECTORY, not a file):
   `"@spartan-ng/helm": ["src/app/ui"]` and `"@spartan-ng/helm/*": ["src/app/ui/*"]`.
   (Mapping it to a file like `src/app/ui/index.ts` breaks `@spartan-ng/helm/utils` subpath imports.)
6. `npm install` the runtime deps the copied files import: `@ng-icons/core`, `@ng-icons/lucide`
   (spinner/icon), `class-variance-authority`, `clsx`.
A reusable script for steps 1–5 is at `scripts/bootstrap-spartan.mjs` (see below).

## Step 5 — the `cva` variant theme (mandatory)

Spartan Helm components style via `class-variance-authority`. The `cva` string contains
UTILITY classes (Tailwind emits `inline-flex`, `items-center`…) PLUS custom marker classes
like `spartan-button-variant-default`, `spartan-button-size-sm`. **Tailwind does NOT emit CSS
for those custom marker classes** — they need a theme mapping. The `ui-theme` generator
would create it, but that generator ALSO hangs on npm install. **Define them manually** in
`styles.scss` `@layer components`:

```scss
@layer components {
  .spartan-button-variant-default { background-color: var(--primary); color: var(--primary-foreground); }
  .spartan-button-variant-outline { border: 1px solid var(--primary); color: var(--primary); background: transparent; }
  .spartan-button-variant-secondary { background-color: var(--secondary); color: var(--secondary-foreground); }
  .spartan-button-variant-ghost { background: transparent; color: var(--foreground); }
  .spartan-button-variant-destructive { background-color: var(--destructive); color: var(--destructive-foreground); }
  .spartan-button-variant-link { background: transparent; color: var(--primary); text-decoration: underline; }
  .spartan-button-size-sm { height: 2rem; padding: 0 0.75rem; font-size: 0.875rem; }
  .spartan-button-size-default { height: 2.5rem; padding: 0 1rem; font-size: 0.875rem; }
  .spartan-button-size-lg { height: 2.75rem; padding: 0 2rem; font-size: 1rem; }
}
```
Until this is present, `hlmBtn variant="default"` renders with NO SpartAN background
(often falls back to a stray orange/UA color). Map each `spartan-*` marker you use to your
`:root` palette vars.

## Pitfalls
- Don't run `info` expecting it to set up Tailwind — it only reports.
- Don't pipe `\n` into `init` to bypass prompts; use `--theme`.
- Angular 20 + Spartan 1.x = peer-dep wall → upgrade Angular first.
- Tailwind v4 is required by `@spartan-ng/brain@1.x` (peer `tailwindcss >=4.0.0`).
- `@spartan-ng/helm` is NOT an npm package (404) — it is only the local tsconfig `paths` alias.
- `:ui` generator hangs on npm install on slow hosts → use the manual-copy fallback above.
- `cva` marker classes (`spartan-button-*`) have NO CSS unless you map them in `@layer components`.
- Stale `ng serve` + a headless probe can match the WRONG button (e.g. the header's
  Material `mat-raised-button` "Sign In" instead of the login form's `hlmBtn` submit).
  Select by `type="submit"` / a unique class and assert the expected class string is present
  (`btn.className.includes('spartan-button-variant-default')`), not just the computed color.
- `@theme` is STRIPPED by Sass in Angular's `.scss` global stylesheet — see
  `angular-tailwind-v4-setup` for the manual `@layer components` token fix.
