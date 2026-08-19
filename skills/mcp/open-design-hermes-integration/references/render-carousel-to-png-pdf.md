# Render an Open Design carousel → upload-ready PNGs + PDF

Proven method used to turn OD's `card-xiaohongshu` (swipeable multi-card
carousel, 1080×1440, 3:4) into standalone picture files + a Facebook-ready PDF.
This is the **working** deliverable path — do NOT rely on OD `start_run` (see
SKILL.md pitfall); build the HTML from the skill's assets, then render locally.

## Why not `start_run`?
OD `start_run` accepts the run (HTTP 202) but ends `status: failed` headlessly
(adapter/agent-execution handoff is broken in this setup). We instead read the
skill's `SKILL.md` + `example.html` assets directly and assemble the artifact
ourselves, then render. Same output, no dependency on the broken pipeline.

## Prereqs (on this machine)
- Chromium/Chrome: `/usr/bin/chromium`, `/usr/local/bin/google-chrome` ✓
- PIL: `python3 -c "import PIL"` ✓ (no `img2pdf`/`wkhtmltopdf` needed — PIL builds PDF)
- ffmpeg: `/usr/bin/ffmpeg` ✓ (to extract poster frames from video clips)

## Step 1 — Build the carousel HTML
Author a vertical deck of `.card` divs (1080px wide, `aspect-ratio:3/4` → 1440px
tall, `border-radius:32px`). Use Tailwind CDN (`<script src="https://cdn.tailwindcss.com">`)
exactly like the `card-xiaohongshu` template. Reserve `<video>` slots for footage.

## Step 2 — Video cards need a POSTER still (static platforms)
A playing `<video>` does NOT render in a headless screenshot. Extract a frame:
```bash
ffmpeg -y -ss 00:00:02 -i clip.mp4 -frames:v 1 -q:v 2 poster.jpg
```
Then set `poster="poster.jpg"` on the `<video>` tag (keep the `<source>` too).

## Step 3 — Render each card to its own PNG (CRITICAL detail)
**Do NOT screenshot the whole page and crop.** Chrome `--screenshot` only captures
the first viewport (one card), so a full-page crop yields 8 identical images
(verified: all 8 PNGs had the same MD5). Instead, emit **one standalone HTML per
card** (extract each `.card` div into its own `<body>`), then screenshot each file:

```python
import re, subprocess, os
from PIL import Image
html = open("index.html").read()
style = re.search(r'<style>.*?</style>', html, re.DOTALL).group(0)
cards = re.findall(r'(<div class="card [^"]*">.*?</div>\s*</div>)', html, re.DOTALL)
for i, c in enumerate(cards, 1):
    doc = f"<!DOCTYPE html><html><head><meta charset='UTF-8'>\
<script src='https://cdn.tailwindcss.com'></script>{style}</head>\
<body style='margin:0;background:#f3eee5;'><div class='deck'>{c}</div></body></html>"
    open(f"card-{i:02d}.html","w").write(doc)
```
Then for each `card-NN.html`:
```bash
chromium --headless --no-sandbox --hide-scrollbars \
  --window-size=1080,1440 --default-background-color=00000000 \
  --screenshot=card-NN.png "file://$(pwd)/card-NN.html"
```
Center-crop to exact 1080×1440 if Chrome added any chrome. Verify uniqueness:
`md5sum card-*.png` — 8 distinct hashes confirms success.

## Step 4 — Bundle into a PDF (Facebook document post)
```python
from PIL import Image
import os
imgs = [Image.open(f"card-{i:02d}.png").convert("RGB") for i in range(1,9)]
imgs[0].save("travel-carousel.pdf", save_all=True, append_images=imgs[1:], resolution=96.0)
```

## Step 5 — Push into OD via MCP (the build path the user wants)
Create the project, then `write_file` each asset (base64). `write_file` requires an
existing project — call `create_project` first or it returns
`no project matches "..."`:
```jsonc
// tools/call create_project  {"name":"travel-carousel","kind":"deck"}
// tools/call write_file      {"project":"travel-carousel","path":"pictures/card-01.png",
//                              "content":"<base64>","encoding":"base64"}
```
This makes the deliverable visible in the OD UI (project id e.g. `travel-carousel-36df`)
and lives in OD's artifact store, not just local disk.

## Verification
- `md5sum pictures/card-*.png` → 8 unique hashes (catches the "all identical" bug).
- `vision_analyze` 1-2 cards to confirm text is readable + video cards show poster.
- Confirm OD project exists via `list_projects` (MCP) or the OD web UI.
