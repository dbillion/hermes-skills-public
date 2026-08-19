# Next.js → Netlify (Next runtime) deploy pitfalls

## Pitfall 1: npm allowScripts gate blocks install
`create-next-app` / `npm install` fail with `EALLOWSCRIPTS` under npm 11+ project-scoped policy.
The `--allow-scripts` CLI flag is ALSO blocked.
Fix: add the `allowScripts` field to the **project** `package.json` (not the flag):
```json
"allowScripts": { "esbuild": true, "sharp": true, "@tailwindcss/oxide": true, "core-js": true }
```
Then `npm install` succeeds.

## Pitfall 2: Netlify --team only with --create-site
- First deploy (new site): `netlify deploy --build --prod --create-site --team <team>`
- Redeploy an EXISTING linked site: `netlify deploy --prod` — **omit `--team`**,
  otherwise it errors: `--team flag can only be used with --create-site flag`.
- Netlify CLI lives at `/home/deeone/.bun/bin/netlify` (bun PATH, not bash default);
  prepend `export PATH="/home/deeone/.bun/bin:$PATH"`.

## Pitfall 3: media payload
- 83 GIFs = 189MB; same content as 1080p MP4 = 88MB. Prefer MP4:
  `<video src=... muted loop autoPlay playsInline>` autoplays in browsers.
- Copy into `public/videos/`. `git push` of ~88MB can exceed a 300s foreground
  timeout → run `git push` in background (`background=true, notify_on_complete=true`).

## netlify.toml (Next runtime)
```toml
[build]
  command = "npm run build"
  publish = ".next"
[dev]
  command = "npm run dev"
  port = 3000
[[plugins]]
  package = "@netlify/plugin-nextjs"
```
Install the plugin first: `npm install -D @netlify/plugin-nextjs`.

## Verify after deploy
```bash
curl -s -o /dev/null -w "%{http_code}\n" <url>/
curl -s <url>/algorithms | grep -oE "Open category|walkthroughs"
```
