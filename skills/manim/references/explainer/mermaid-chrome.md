# Render Mermaid diagrams via mmdc using system Chrome

`mmdc` (mermaid-cli) needs a headless browser. On this box Chrome is at
`/usr/local/bin/chrome` (NOT the puppeteer default cache), so mmdc fails with
"Could not find Chrome" unless you point at it.

## Command
```bash
PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chrome \
  mmdc -i diagram.mmd -o diagram.png -b "#1C1C1C" -t dark
```
- `-b` background hex (match Manim BG, e.g. `#1C1C1C`).
- `-t dark` for dark theme.
- If Chrome path differs, find it: `which chrome chromium chromium-browser google-chrome 2>/dev/null` or `ls /usr/local/bin/*chrome*`.

## Why not the repo's PNG?
Auto-generated repo diagrams (e.g. `tricks_10.png` = 108x184px class-tree) are
too small/blurry for video and show structure, not flow. Generate a purpose-built
flow/sequence diagram per video so you can animate the winning path.

## Authoring the .mmd
Use `flowchart TD` with `style` fills for naive (red `#FF6B6B`) vs correct
(green `#83C167`) branches. Keep nodes short; Manim will narrate them.
