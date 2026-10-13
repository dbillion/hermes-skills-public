# Angular Spartan — Detailed Workaround Code Blocks

Companion to SKILL.md. Copy-paste-ready snippets verified during the Angular 21 + Spartan 1.1.1 +
Tailwind v4 migration (July 2026).

## tsconfig.json path mapping
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@spartan-ng/helm": ["src/app/ui"],
      "@spartan-ng/helm/*": ["src/app/ui/*"]
    }
  }
}
```

## styles.scss — :root palette + @layer components (the fix for GOTCHA 3)
```scss
:root {
  --background: 222 41% 11%;        /* #051424 */
  --foreground: 220 14% 96%;        /* #f8f9fa */
  --card: 222 47% 11%;              /* #0b1a30 */
  --primary: 232 25% 35%;           /* #5C6BC0 */
  --primary-foreground: 220 14% 96%;
  --secondary: 232 30% 28%;         /* #4858ab */
  --muted-foreground: 220 9% 46%;   /* #767683 */
  --border: 222 14% 22%;            /* #2a3a5c */
  --destructive: 0 72% 51%;         /* #ba1a1a */
  --success: 142 71% 45%;           /* #43A047 */
}

@layer base {
  body { background-color: hsl(var(--background)); color: hsl(var(--foreground)); }
}

@layer components {
  .bg-primary { background-color: hsl(var(--primary)); }
  .bg-background { background-color: hsl(var(--background)); }
  .bg-card { background-color: hsl(var(--card)); }
  .text-foreground { color: hsl(var(--foreground)); }
  .text-muted-foreground { color: hsl(var(--muted-foreground)); }
  .bg-border { background-color: hsl(var(--border)); }
  .border-border { border-color: hsl(var(--border)); }
  .text-primary { color: hsl(var(--primary)); }
  .shadow-primary\/20 { box-shadow: 0 10px 15px -3px hsl(var(--primary) / 0.2); }

  .spartan-button-variant-default { background-color: hsl(var(--primary)); color: hsl(var(--primary-foreground)); }
  .spartan-button-variant-outline { border: 1px solid hsl(var(--primary)); color: hsl(var(--primary)); }
  .spartan-button-variant-secondary { background-color: hsl(var(--secondary)); color: hsl(var(--primary-foreground)); }
  .spartan-button-variant-ghost { background-color: transparent; }
  .spartan-button-variant-destructive { background-color: hsl(var(--destructive)); color: white; }
  .spartan-button-variant-link { color: hsl(var(--primary)); text-decoration: underline; }
  .spartan-button-size-sm { height: 2rem; padding: 0 0.75rem; }
  .spartan-button-size-md { height: 2.5rem; padding: 0 1rem; }
  .spartan-button-size-lg { height: 2.75rem; padding: 0 1.5rem; }

  .spartan-badge-variant-default { background-color: hsl(var(--primary)); color: hsl(var(--primary-foreground)); }
  .spartan-badge-variant-secondary { background-color: hsl(var(--secondary)); color: hsl(var(--primary-foreground)); }
  .spartan-badge-variant-destructive { background-color: hsl(var(--destructive)); color: white; }
  .spartan-badge-variant-outline { border: 1px solid hsl(var(--border)); color: hsl(var(--foreground)); }
}
```

## Helm copy script (run from project root — the GOTCHA 1 workaround)
```python
# ks-bootstrap-spartan.py — copies Helm component sources from the CLI package into src/app/ui
import os, shutil, pathlib

CLI_LIBS = pathlib.Path("node_modules/@spartan-ng/cli/src/generators/ui/libs")
DEST = pathlib.Path("src/app/ui")
COMPONENTS = ["utils","button","card","input","label","field","badge","spinner","separator","sonner","typography"]

for c in COMPONENTS:
    src = CLI_LIBS / c / "files"
    if not src.exists():
        print("SKIP", c, "(no files/)"); continue
    dst = DEST / c
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print("COPIED", c)

# write components.json + barrel index.ts (importAlias @spartan-ng/helm)
```
Then install peers: `npm install class-variance-authority clsx @ng-icons/core @ng-icons/lucide --legacy-peer-deps`

## AG-UI SSE client (verified working)
```ts
runAgent(name: string, query: string): Observable<string> {
  const subject = new Subject<string>();
  const url = `${API_CONFIG.baseUrl}/agents/${name}/run`;
  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages: [{ role: 'user', content: query }] }),
  }).then(res => {
    const reader = res.body!.getReader();
    const dec = new TextDecoder();
    let buf = '', acc = '';
    const read = (): Promise<void> => reader.read().then(({ value, done }) => {
      if (done) { subject.next(acc); subject.complete(); return; }
      buf += dec.decode(value, { stream: true });
      for (const block of buf.split('\n\n')) {
        const line = block.trim();
        if (!line.startsWith('data:')) continue;
        try {
          const ev = JSON.parse(line.slice(5).trim());
          if (ev.type === 'TEXT_MESSAGE_CONTENT') { acc += ev.delta; subject.next(acc); }
        } catch { /* ignore malformed */ }
      }
      return read();
    });
    return read();
  }).catch(e => subject.error(e));
  return subject.asObservable();
}
```

## angular.json budget fix
```json
"budgets": [
  { "type": "initial", "maximumWarning": "1MB", "maximumError": "2MB" },
  { "type": "anyComponentStyle", "maximumWarning": "10kB", "maximumError": "20kB" }
]
```

## Headless verification snippet (Playwright)
```js
const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
console.assert(bg === 'rgb(5, 20, 36)', 'dark bg missing: ' + bg);
const h1 = await page.locator('h1').first().innerText();
console.assert(h1.length > 0, 'no h1 — blank screen');
```
