#!/usr/bin/env node
// bootstrap-spartan.mjs — manual fallback for `ng g @spartan-ng/cli:ui`
// when the generator hangs on `npm install` on a slow/constrained host.
// Run from the Angular app root: `node bootstrap-spartan.mjs`
// Replicates what the SpartAN CLI does internally: copies Helm templates
// into src/app/ui, sets up the @spartan-ng/helm alias, creates components.json.
import fs from 'node:fs';
import path from 'node:path';

const APP = process.cwd();
const CLI_LIBS = path.join(APP, 'node_modules/@spartan-ng/cli/src/generators/ui/libs');
const UI = path.join(APP, 'src/app/ui');
const ALIAS = '@spartan-ng/helm';
const COMPONENTS = ['button', 'card', 'input', 'label', 'field',
  'badge', 'spinner', 'separator', 'sonner', 'typography'];

function* walk(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) yield* walk(p); else yield p;
  }
}
const sub = s => s.split('<%- importAlias %>').join(ALIAS);

fs.mkdirSync(UI, { recursive: true });
for (const name of ['utils', ...COMPONENTS]) {
  const src = path.join(CLI_LIBS, name, 'files');
  if (!fs.existsSync(src)) { console.log('  ! no template for', name); continue; }
  const dst = path.join(UI, name);
  fs.mkdirSync(dst, { recursive: true });
  for (const f of walk(src)) {
    if (!f.endsWith('.template')) continue;
    const rel = path.relative(src, path.dirname(f));
    const outDir = rel ? path.join(dst, rel) : dst;
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(
      path.join(outDir, path.basename(f, '.template')),
      sub(fs.readFileSync(f, 'utf8')));
  }
  console.log('  +', name);
}

// barrel
fs.writeFileSync(UI + '/index.ts',
  COMPONENTS.map(c => `export * from './${c}';`).join('\n') + '\n');

// components.json
fs.writeFileSync(APP + '/components.json',
  JSON.stringify({ importAlias: ALIAS, componentsPath: 'src/app/ui', primitives: COMPONENTS }, null, 2));

// tsconfig paths (directory, not file)
const tc = JSON.parse(fs.readFileSync(APP + '/tsconfig.json', 'utf8'));
tc.compilerOptions.baseUrl = '.';
tc.compilerOptions.paths = {
  '@spartan-ng/helm': ['src/app/ui'],
  '@spartan-ng/helm/*': ['src/app/ui/*'],
};
fs.writeFileSync(APP + '/tsconfig.json', JSON.stringify(tc, null, 2));

console.log('DONE. Now run:');
console.log('  npm install @ng-icons/core @ng-icons/lucide class-variance-authority clsx --legacy-peer-deps');
console.log('Then add the cva variant theme (angular-spartan-setup Step 5) to styles.scss @layer components.');
