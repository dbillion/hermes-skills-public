# Serving `next build --output standalone` locally for verification

## Problem
`next build` with `output: 'standalone'` emits `.next/standalone/server.js`. Running `node .next/standalone/server.js` directly serves **404 for `/_next/static/*.css`** → the page renders unstyled (Tailwind utilities don't apply; giant unstyled SVGs, serif fonts, white background). This looks like a broken build but is a **local-serve layout quirk**, not a code bug.

## Cause
The standalone `server.js` expects `.next/static` (and `public`) to sit **next to it**. `next build` puts them in `.next/static`, not inside `.next/standalone/`. The production `Dockerfile` handles this with `COPY --from=builder .next/static ./.next/static`, but a naive local `node .next/standalone/server.js` does not.

## Fix (local verification only)
```bash
rm -rf /tmp/hc_standalone && mkdir -p /tmp/hc_standalone
cp -r .next/standalone/. /tmp/hc_standalone/
cp -r .next/static /tmp/hc_standalone/.next/static
cp -r public /tmp/hc_standalone/public 2>/dev/null
cd /tmp/hc_standalone && PORT=3100 HOSTNAME=127.0.0.1 node server.js
```
Then `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3100/_next/static/css/*.css` should be **200**.

## Fidelity check
Render with headless Chromium and vision-review:
```bash
chromium --headless --no-sandbox --disable-gpu --virtual-time-budget=9000 \
  --window-size=1440,2600 --screenshot=/tmp/shot.png "http://127.0.0.1:3100/<route>"
```
- Missing images when the design uses a CSS `background-image` div: render with an inline `style={{ backgroundImage: url(...) }}` div, NOT `<img>` (Stitch HTML uses background-image divs; `<img>` with the same URL may 404 if the asset is a CSS background).
- Confirm hero copy, palette, and layout match the design; verify ALL routes return 200.
