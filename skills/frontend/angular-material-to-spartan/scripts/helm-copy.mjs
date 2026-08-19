// helm-copy.mjs — manual copier for SpartAN Helm components.
// The `ng g @spartan-ng/cli:ui` generator HANGS on installPeerDependencies on some hosts.
// This copies Helm SOURCE from the installed CLI package into src/app/ui/<name> and
// rewrites the import-alias token (default @spartan-ng/helm) to the project alias.
//
// Usage: node helm-copy.mjs
// Requires: @spartan-ng/cli installed in node_modules.

import { cpSync, mkdirSync, readdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = process.cwd();
const cliLibs = join(root, 'node_modules/@spartan-ng/cli/src/generators/ui/libs');
const destUi = join(root, 'src/app/ui');
const importAlias = '@spartan-ng/helm'; // matches tsconfig paths "@spartan-ng/helm" -> src/app/ui

// Components known to copy cleanly from the CLI libs tree.
const components = [
  'utils', 'button', 'card', 'input', 'label', 'field',
  'badge', 'spinner', 'separator', 'sonner', 'typography',
];

mkdirSync(destUi, { recursive: true });

for (const c of components) {
  const src = join(cliLibs, c, 'files');
  if (!existsSync(src)) {
    console.warn(`! skip ${c}: no files at ${src}`);
    continue;
  }
  const dst = join(destUi, c);
  mkdirSync(dst, { recursive: true });
  cpSync(src, dst, { recursive: true });

  // Rewrite the import-alias token inside copied .ts templates (e.g. @spartan-ng/helm/utils).
  for (const f of readdirSync(dst)) {
    if (!f.endsWith('.ts')) continue;
    const p = join(dst, f);
    const txt = readFileSync(p, 'utf8');
    const next = txt.replace(new RegExp(importAlias, 'g'), importAlias);
    if (next !== txt) writeFileSync(p, next);
  }
  console.log(`+ copied ${c}`);
}

// Build a barrel index.ts (drop ./icon if not copied).
const barrel = components
  .filter((c) => c !== 'utils')
  .map((c) => `export * from './${c}';`)
  .join('\n') + '\n';
writeFileSync(join(destUi, 'index.ts'), barrel);
console.log('wrote src/app/ui/index.ts');

// Reminder:
console.log('\nNEXT: ensure tsconfig.json has:');
console.log('  "baseUrl": ".",');
console.log('  "paths": { "@spartan-ng/helm": ["src/app/ui"], "@spartan-ng/helm/*": ["src/app/ui/*"] }');
