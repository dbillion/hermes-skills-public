# Mermaid diagrams via mmdc + Chrome

## Render a mermaid (.mmd) to PNG
`mmdc` (mermaid-cli) needs a headless browser. Point it at the system Chrome:
```bash
PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chrome mmdc -i x.mmd -o x.png
```
Without the env var, `mmdc` fails (no bundled chromium). Dark theme flags
(`-t dark -b "#1C1C1C"`) can also break if Chrome is missing; omit if it errors.

## Embedding in Manim — scaling (head/tail clip pitfall)
The video frame is 16:9. Mermaid flow diagrams are often portrait (e.g. 586x895).
- WRONG: `img.set_width(6.5)` → height becomes ~10 units > 8-unit frame → top/bottom
  CLIPPED (user saw "head and tail cut off").
- RIGHT: `img.set_height(6.0)` (or 6.5) → fits vertically with margin, nothing clipped.
- Place centered: `img.move_to([0, 0.2, 0])` so it never clips.

## Verify no clipping (vision down)
After rendering, extract a frame and run `scripts/frame_verify.py`; confirm the
diagram's content bbox stays inside [3,3,w-3,h-3].
