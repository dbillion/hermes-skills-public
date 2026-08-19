# Angular 21 + Tailwind v4 + SpartAN — working config & verification

Condensed from a real session that hit every pitfall. The project was an Angular 21
CLI app (was 20, upgraded), migrating from Angular Material to Tailwind v4 + SpartAN
Helm components, themed to a Stitch "Momentum" dark palette.

## The THREE things that silently break (and the fixes)

### 1. Tailwind v4 JIT needs TWO config files (BUILD=0 but no utilities)
Under `@angular/build` (Angular 21), Tailwind only activates when it finds a
PostCSS config. `@import 'tailwindcss'` in styles.scss alone gives reset + SOME
utilities but does NOT scan templates.

- `tailwind.config.js`: `{ content: ['./src/**/*.{html,ts}'] }`
- `postcss.config.json`: `{ "plugins": { "@tailwindcss/postcss": {} } }`

Without `postcss.config.json` the build errors:
`trying to use tailwindcss directly as a PostCSS plugin … install @tailwindcss/postcss`.

### 2. `@theme` is STRIPPED by Sass (the big one)
In Angular's `.scss` global stylesheet the Sass compiler **drops the `@theme`
at-rule entirely** before PostCSS/Tailwind sees it. Result: `:root` vars survive
but ZERO `.bg-*`/`.text-*` rules are generated → page renders transparent,
yet `ng build` returns 0.

Diagnose (definitive):
```bash
python3 - <<'EOF'
css = open('dist/knowledge-sharing-app/browser/styles.css').read()
import re
print('@theme present:', '@theme' in css)          # False
print('bg-primary rule:', bool(re.search(r'\.bg-primary\{', css)))  # False
print('--background var:', '--background:' in css)   # True (survives in :root)
EOF
```

Fix — manual `@layer components` mapping to `:root` vars (Sass-safe):
```scss
:root {
  color-scheme: dark;
  --background: #051424;  --foreground: #f8f9fa;
  --card: #0b1a30;       --card-foreground: #f8f9fa;
  --primary: #5C6BC0;     --primary-foreground: #ffffff;
  --secondary: #2f3f92;    --secondary-foreground: #f8f9fa;
  --muted: #12243f;       --muted-foreground: #bac3ff;
  --accent: #2f3f92;      --accent-foreground: #f8f9fa;
  --success: #43A047;      --success-foreground: #ffffff;
  --destructive: #ba1a1a;  --destructive-foreground: #ffdad6;
  --border: #2f3f92;      --input: #2f3f92;  --ring: #5C6BC0;
  --sidebar: #00105b;       --sidebar-foreground: #f8f9fa;
  --sidebar-primary: #5C6BC0; --sidebar-primary-foreground: #ffffff;
}
@layer base {
  * { border-color: var(--border);
      outline-color: color-mix(in srgb, var(--ring) 50%, transparent); }
  body { background-color: var(--background);
         color: var(--foreground);
         font-family: "Inter", system-ui, sans-serif; }
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
  .bg-secondary { background-color: var(--secondary); }
  .bg-accent { background-color: var(--accent); }
  .bg-success { background-color: var(--success); }
  .text-success { color: var(--success); }
  .bg-destructive { background-color: var(--destructive); }
  .text-destructive { color: var(--destructive); }
  .border-border { border-color: var(--border); }
  .border-primary { border-color: var(--primary); }
  .bg-sidebar { background-color: var(--sidebar); }
  .text-sidebar-foreground { color: var(--sidebar-foreground); }
  /* opacity variants (Tailwind /opacity needs @theme, so hand-roll with color-mix) */
  .bg-primary\/10 { background-color: color-mix(in srgb, var(--primary) 10%, transparent); }
  .bg-primary\/15 { background-color: color-mix(in srgb, var(--primary) 15%, transparent); }
  .bg-primary\/20 { background-color: color-mix(in srgb, var(--primary) 20%, transparent); }
  .border-primary\/40 { border-color: color-mix(in srgb, var(--primary) 40%, transparent); }
  .shadow-primary\/20 { --tw-shadow-color: color-mix(in srgb, var(--primary) 20%, transparent);
                       box-shadow: 0 10px 30px color-mix(in srgb, var(--primary) 20%, transparent); }
}
```

### 3. SpartAN `cva` marker classes have NO CSS
`hlmBtn variant="default"` emits `spartan-button spartan-button-variant-default
spartan-button-size-default` + utility classes. Tailwind emits the utilities
(`inline-flex`, `items-center`…) but NOT the custom `spartan-*` marker classes.
The `ui-theme` generator would create them but it hangs on npm install too.
Map them manually (full set in `angular-spartan-setup` Step 5).

## styles.scss HEAD (correct order — @use before @import/@layer)
```scss
@use '@angular/material' as mat;

@layer theme, base, components, utilities;
@import 'tailwindcss/theme.css' layer(theme);
@import 'tailwindcss/preflight.css' layer(base);
@import 'tailwindcss/utilities.css';

@import "@spartan-ng/brain/hlm-tailwind-preset.css";

html {
  @include mat.theme((
    color: ( primary: mat.$azure-palette, tertiary: mat.$blue-palette ),
    typography: Roboto, density: 0,
  ));
}
```

## Render-check recipe (Playwright Chromium — cached, no install)
Chromium is cached at `~/.cache/ms-playwright`; the module is at
`~/node_modules/playwright`. Point the import at the absolute module path.

```js
// /tmp/render-check.mjs
import { chromium } from '/home/deeone/node_modules/playwright/index.mjs';
const b = await chromium.launch();
const p = await b.newPage();
await p.goto('http://localhost:4200/auth/login', { waitUntil: 'networkidle', timeout: 40000 });
await p.waitForTimeout(1500);
const r = await p.evaluate(() => {
  const cs = el => el ? getComputedStyle(el) : null;
  const submit = [...document.querySelectorAll('button')].find(x => x.getAttribute('type') === 'submit');
  const card = document.querySelector('.login-card');
  return {
    submitHasVariant: submit?.className.includes('spartan-button-variant-default') ?? false,
    submitBg: submit ? cs(submit).backgroundColor : '(none)',   // expect rgb(92, 107, 192)
    cardBg: cs(card).backgroundColor,                                          // expect rgb(11, 26, 48)
    bodyBg: cs(document.body).backgroundColor,                                 // expect rgb(5, 20, 36)
  };
});
console.log(JSON.stringify(r, null, 2));
await b.close();
```
Run: `node /tmp/render-check.mjs`. **Assert the class string is present, not just
the color** — a stale server can serve an old bundle that happens to show the
right color from a different state.

## Bootstrap-Spartan script (manual `:ui` copy fallback)
When `ng g @spartan-ng/cli:ui` hangs on npm install, this replicates the copy:
`scripts/bootstrap-spartan.mjs` (run from the Angular app root):
```js
#!/usr/bin/env node
// Copies SpartAN Helm templates into src/app/ui, sets up the @spartan-ng/helm alias.
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const APP = process.cwd();
const CLI_LIBS = path.join(APP, 'node_modules/@spartan-ng/cli/src/generators/ui/libs');
const UI = path.join(APP, 'src/app/ui');
const ALIAS = '@spartan-ng/helm';
const COMPONENTS = ['button','card','input','label','field','badge','spinner','separator','sonner','typography'];
const sub = s => s.replaceAll('<%- importAlias %>', ALIAS);
for (const name of ['utils', ...COMPONENTS]) {
  const src = path.join(CLI_LIBS, name, 'files');
  if (!fs.existsSync(src)) { console.log('  ! skip', name); continue; }
  const dst = path.join(UI, name);
  fs.mkdirSync(dst, { recursive: true });
  for (const f of walk(src)) {
    if (!f.endsWith('.template')) continue;
    const rel = path.relative(src, path.dirname(f));
    const outDir = rel ? path.join(dst, rel) : dst;
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(path.join(outDir, path.basename(f, '.template')),
                    sub(fs.readFileSync(f, 'utf8')));
  }
  console.log('  +', name);
}
// barrel
fs.writeFileSync(path.join(UI, 'index.ts'),
  COMPONENTS.map(c => `export * from './${c}';`).join('\n') + '\n');
// components.json
fs.writeFileSync(path.join(APP, 'components.json'),
  JSON.stringify({ importAlias: ALIAS, componentsPath: 'src/app/ui', primitives: COMPONENTS }, null, 2));
// tsconfig paths
const tc = JSON.parse(fs.readFileSync(path.join(APP, 'tsconfig.json'), 'utf8'));
tc.compilerOptions.baseUrl = '.';
tc.compilerOptions.paths = { '@spartan-ng/helm': ['src/app/ui'], '@spartan-ng/helm/*': ['src/app/ui/*'] };
fs.writeFileSync(path.join(APP, 'tsconfig.json'), JSON.stringify(tc, null, 2));
console.log('DONE — now: npm i @ng-icons/core @ng-icons/lucide class-variance-authority clsx --legacy-peer-deps');
function* walk(dir) { for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
  const p = path.join(dir, e.name);
  if (e.isDirectory()) yield* walk(p); else yield p; } }
```
Then `npm install @ng-icons/core @ng-icons/lucide class-variance-authority clsx --legacy-peer-deps`.

## Version gate reminder
SpartAN 1.1.x requires Angular >= 21. On Angular 20 the install ERESOLVEs.
Upgrade first on an isolated branch (`ng update @angular/core@21 @angular/cli@21 @angular/cdk@21 @angular/material@21`), commit, then install.
