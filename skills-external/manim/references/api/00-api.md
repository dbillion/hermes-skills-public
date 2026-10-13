---
name: manim-020-api
description: "Verified Manim 0.20.1 API signatures from source."
version: 1.0.0
---

# Manim CE 0.20.1 — Verified API Signatures

These signatures were extracted from the actual ManimCommunity/manim source
(repomix pack → NLM query) on 2026-08-05. Use them instead of guessing. The
agent repeatedly mis-guessed `Code` args; the REAL signatures are below.

## Code mobject — INSTALLED manim 0.20.1 (ground truth via inspect)
```python
# ground truth from `inspect.signature(Code.__init__)` on the installed build:
Code(
    code_file=None,            # load from file
    code_string=None,          # THE STRING — param is `code_string` (NOT `code`!)
    language=None,             # "python", etc.
    formatter_style="vim",     # syntax theme
    tab_width=4,
    add_line_numbers=True,     # bool toggle (NOT `insert_line_no`)
    line_numbers_from=1,
    background="rectangle",    # "rectangle" | "window"
    background_config=None,
    paragraph_config=None,     # font size lives HERE: paragraph_config={"font_size": 18}
)
# NO `font=`, NO `font_size=` (top-level), NO `background_stroke_color`.
# Correct usage:
Code(code_string=code, language="python", paragraph_config={"font_size": 18})
```
**Common failures:**
- `Code(code=...)` → TypeError (param is `code_string`)
- `Code(..., font_size=18)` → TypeError (must be in paragraph_config)
- `Code(..., insert_line_no=False)` → TypeError (param is `add_line_numbers`)
- `Code(..., background_stroke_color=...)` → TypeError (not a param)
**ALWAYS verify against the INSTALLED package:** `python -c "import inspect; from manim import Code; print(inspect.signature(Code.__init__))"` — the cloned GitHub repo may differ from the installed version. NLM digests of the repo gave a wrong signature here; trust `inspect` on the live build.

## 3D primitives (manim/mobject/three_d/three_dimensions.py)
```python
Cube(side_length=2.0, **kwargs)                 # inherits Prism
Prism(dimensions=(3, 2, 1), **kwargs)          # dimensions is an iterable (x,y,z)
```
Note: `Prism` is a `VGroup`. Color via `fill_color=` / `fill_opacity=` /
`stroke_color=` (standard mobject kwargs). `Cube(side_length=1, fill_color=...,
fill_opacity=0.6, stroke_color=...)`.

## ImageMobject (manim/mobject/types/image_mobject.py)
```python
ImageMobject(filename_or_array, scale_to_resolution=1080, invert=False,
             image_mode="RGBA", **kwargs)
```
Pass a path string. `.set_width(w)` to scale.

## ThreeDScene camera movement (CRITICAL)
`ThreeDScene` uses `self.move_camera(...)`, NOT `self.camera.frame.animate...`
(the `frame` attribute exists only on `MovingCameraScene`).
```python
self.move_camera(phi=65*DEGREES, theta=-20*DEGREES, zoom=1.0, run_time=2.0)
self.move_camera(frame_center=[-2.5, 0, 0], run_time=2.0)   # pan/drift
self.begin_ambient_camera_rotation(rate=0.12)
self.stop_ambient_camera_rotation()
```
**Common failure:** `self.camera.frame.animate.shift(...)` →
`AttributeError: 'ThreeDCamera' object has no attribute 'frame'`.
Use `move_camera(frame_center=..., run_time=...)` for drifts, or
`MovingCameraScene` if you need `.frame.animate`.

## 3B1B-style camera orientation (from user feedback)
- Use a FIXED 3/4 angle: `self.set_camera_orientation(phi=70*DEGREES, theta=30*DEGREES, zoom=1.05, frame_center=[0,0,0])`.
- Do NOT pan the camera (`move_camera(frame_center=...)`) to separate branches — it
  distorts the angle per scene and feels "wrongly oriented". Instead KEEP the camera
  fixed and SHIFT the objects left/right to create branch separation.
- Do NOT run `begin_ambient_camera_rotation` while objects are near frame edges —
  the orbit swings them out of frame (clipping). Either center objects at ORIGIN with
  margin, or skip the orbit. Verify with frame pixel analysis: content bbox must stay
  inside [3, 3, w-3, h-3].
- Keep diagrams/recap CENTERED (`move_to([0,0,0])`) so they never clip.

`background_color` (Scene.camera.background_color).

## Text / MathTex
`Text("...", font_size=30, color=..., font="Menlo", weight=BOLD)`.
`MathTex(r"\frac{1}{2}")` — raw string required. `add_subcaption("text",
duration=N)` per animation for narration.

## Verification loop (do NOT skip)
1. Render `-ql` first (854x480, 15fps) — fast, catches API errors.
2. If TypeError on a constructor, query the SOURCE (repomix the manim repo,
   NLM) rather than guessing from memory.
3. Only render `-qh` (1080p60) for final output.

## Repomix+NLM digest recipe (when API is unsure)
```
git clone --depth 1 https://github.com/ManimCommunity/manim /tmp/manim-src
cd /tmp/manim-src
repomix --style markdown --include "manim/mobject/text/code_mobject.py,manim/mobject/three_d/three_dimensions.py,manim/scene/three_d_scene.py" -o /tmp/api.md
nlm notebook create "Manim API"
NB=$(nlm notebook list --json | python3 -c "import sys,json;print([n['id'] for n in json.load(sys.stdin) if 'Manim' in n['title']][0])")
nlm source add "$NB" --file /tmp/api.md --title "manim key API" --wait
nlm notebook query "$NB" "exact __init__ signature of Code from source, quote lines"
```
