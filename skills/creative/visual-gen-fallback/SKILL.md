---
name: visual-gen-fallback
description: "Infographic fallback when renderer or vision is unavailable."
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
---

# Visual Asset Generation Without a Renderer (Fallback)

Use this when a user wants a generated visual (infographic, social graphic, image with a
brand character) but the agent has **no `image_generate` tool**, **no local diffusion
backend** (ComfyUI absent, no GPU), and/or **`vision_analyze` is unavailable**. Do NOT hang
or fabricate output. Take the available path and report blockers as actionable asks.

## Decision: can I render at all?

- `image_generate` in toolset? → use it (see `baoyu-infographic` / `comfyui` skills).
- Local ComfyUI on `:8188` + `comfy` CLI + GPU? → `comfyui` skill (best for exact brand
  match via Flux/SDXL img2img with the reference image).
- Comfy Cloud API key + paid tier? → `comfyui` skill against `https://cloud.comfy.org`
  (also good for exact match).
- **None of the above** → use the NotebookLM fallback below.

## Step 1 — Characterize the reference image WITHOUT vision (PIL fallback)

`vision_analyze` may fail with `404` (file:// not readable by the vision backend) or `429`
(rate-limited). Don't assume blindness — read pixels directly for the facts a generator
needs (transparency, dominant palette):

```python
from PIL import Image
from collections import Counter
im = Image.open("character.png").convert("RGBA")   # force alpha
w,h = im.size; px = im.load()
cnt = Counter()
for y in range(0,h,2):
    for x in range(0,w,2):
        r,g,b,a = px[x,y]
        if a > 40:                                  # skip transparent pixels
            cnt[(r//24*24, g//24*24, b//24*24)] += 1
print("mode:", im.mode, "size:", im.size)          # RGBA => transparent background
print("alpha extrema:", im.split()[-1].getextrema())
for (r,g,b),n in cnt.most_common(10):
    print(f"  #{r:02X}{g:02X}{b:02X}  freq={n}")
```

This yields the factual palette + alpha info to brief any generator. (Example: a warm
dark owl came out RGBA 360x360, transparent bg, maroon/rust/black dominant.)

## Step 2 — Upload brief + reference image to NotebookLM, then generate

`nlm source add --file` accepts BOTH a `.md`/`.txt` brief and a `.png`/`.jpg` reference
(the image source `type` becomes `image`). Create a notebook, add both, generate:

```bash
NL=/home/deeone/.local/bin/nlm
NBID=$($NL notebook create "Infographic Pack" --json \
       | grep -o '"notebook_id": *"[^"]*"' | sed 's/.*"notebook_id": *"//;s/"//')
$NL source add "$NBID" --file /path/to/brief.md --title "Brief" --wait
$NL source add "$NBID" --file /path/to/character.png --title "Brand Character (reference)" --wait
$NL infographic create "$NBID" --orientation portrait --style professional \
   --focus "Hand-drawn doodle style, warm cozy colors, include the character pointing to tips" --confirm
```

(See `nlm-productivity` skill for the full `nlm` command surface, download-by-id, and rate
limits. Requires `nlm` CLI + auth.)

**Caveat — fidelity:** NotebookLM infographic generation produces layout/structure but will
NOT pixel-match a brand character the way Flux/SDXL img2img would. If an *exact* visual match
matters, you need a diffusion backend (Comfy Cloud key + img2img with the reference).

## Step 3 — Report blockers as actionable asks (never a dead end)

When fully blocked, the user expects TWO things: (a) take the available path (e.g. upload to
NotebookLM), AND (b) itemize each blocker with the exact unblock. Template:

- **Vision 404 (file://):** deliver the image as a MEDIA attachment the runtime decodes, or
  configure the vision backend to read local paths. (PIL fallback above avoids needing it.)
- **Vision 429:** wait out the cooldown, or use a vision-capable model/provider with quota.
- **No image-generation backend:** local ComfyUI absent on this host; Comfy Cloud needs a
  paid API key (best for exact match via Flux/SDXL img2img). Or any image-gen endpoint key
  (OpenAI/DALL·E, etc.).

## Pitfalls

- PIL characterization must `convert("RGBA")` before reading alpha; transparent pixels have
  `a` near 0 — skip them (`a > 40`) or the histogram is dominated by the bg color.
- `vision_analyze` 404 on `file://` is NOT "image missing" — the file often exists; the
  vision backend just can't reach the local FS. Verify with `search_files`/file stat first.
- NotebookLM infographic ≈ layout generator, not a character renderer. Don't promise brand
  fidelity from it.
- `nlm` extraction with `grep ... | python3` can trip a security scanner (pipe-to-interpreter).
  Prefer `grep -o` + `sed` to pull the ID without piping JSON into an interpreter.

## See Also

- `nlm-productivity` — full NotebookLM CLI surface (user-owned; recommend `hermes curator adopt`
  if you want to fold this in).
- `comfyui` — local/cloud diffusion when a renderer IS available (best for pixel-matching a
  brand character via img2img).
- `baoyu-infographic` — layout×style infographic planner that assumes `image_generate` exists
  (bundled; protected).
