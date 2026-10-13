---
name: manim-explainer-video
description: "Manim 0.20.1 API + video workflow. Use on Manim errors."
version: 1.0.0
---

# Manim CE 0.20.1 — Explainer-Video Workflow

Playbook from a long run building 3Blue1Brown-style DSA videos (naive-vs-trick).
Carries inspect-verified API + the discipline that made output teach.

## 0. GOLDEN RULES (user-enforced)

1. **COMMIT EACH VERIFIED RENDER TO GIT.** User called missing commits "very bad
   engineering." After every correct render, commit script + output for rollback.
   Do NOT leave the good version uncommitted.
2. **TRUST `inspect.signature()` on the INSTALLED manim, NOT repo/NLM digests.**
   NotebookLM + repomix returned a WRONG `Code` signature (divergent version).
   The installed binary is truth.
3. **Text must face the viewer.** In `ThreeDScene`, `Text`/`Code`/`Image` in 3D
   space renders SLANTED (floor-plane) under top-down cam. Billboard (§3).
4. **Manim does NOT render visible subtitles.** `add_subcaption()` -> `.srt`
   sidecar only. Burn in with ffmpeg (§5).

## 1. Key API signatures (inspect-verified)

- `Code(code_string=..., language="python", add_line_numbers=False,
   paragraph_config={"font_size": 18})` — NOT `code=`, `font_size=`,
   `insert_line_no=`, `background_stroke_color=`.
- `Cube(side_length=2.0)`, `Prism(dimensions=(1,2,1))`, `Square(side_length=0.5)`.
- `ImageMobject(fn)`; prefer `set_height(h)` for tall images (set_width clips).
- `Arrow(start,end,color=,stroke_width=)`, `SurroundingRectangle`,
   `Create`, `GrowFromCenter`, `LaggedStart`, `Write`, `FadeIn`, `FadeOut`.

## 2. ThreeDScene camera

- Class MUST be `ThreeDScene` (not `Scene`) for billboarding to exist.
- FIXED 3/4: `set_camera_orientation(phi=65*DEGREES, theta=-20*DEGREES,
   zoom=1.0, frame_center=[0,0,0])`.
- Do NOT pan cam (`move_camera(frame_center=...)`) to separate branches — distorts
   angle. Keep cam fixed, SHIFT OBJECTS.
- No `begin_ambient_camera_rotation` near edges (orbits clip objects).
- `self.camera.frame.animate` -> AttributeError on ThreeDCamera. Use
   `move_camera(...)` or `MovingCameraScene`.

## 3. Billboard (fixes slanted floor text)

```python
txt = Text("label", font_size=20)
self.add_fixed_in_frame_mobjects(txt)
self.remove(txt)
self.play(FadeIn(txt))   # animates while staying face-on
```
Apply to EVERY text/code/image/label in 3D. Skipping = #1 cause of "lying on
floor" text.

## 4. Continuous 3B1B structure

- One `ThreeDScene`, object-shift drifts between beats (not hard cuts).
- Arc: **Wrong -> Less Wrong -> Right** (from `manim-composer` skill).
- Typed code via `Write()`, not `FadeIn`.
- Animated diagrams: build from mobjects, reveal node-by-node (LaggedStart/Create),
   not a static PNG. See `templates/video_script.py`.

## 5. Hardsub pipeline

1. Each scene -> `<Scene>.srt`.
2. Merge with cumulative offsets (`references/render_verify.md`).
3. `ffmpeg -i in.mp4 -vf "subtitles=merged.srt:force_style='FontSize=18,...'" -c:a copy out_subbed.mp4`
   (`scripts/hardsub.sh` does it.)

## 6. Verify without vision (endpoints were 404/sandbox-blocked)

ffmpeg-extract frames + PIL analysis: content bbox (clip), edge ratio (upright
text). `references/render_verify.md` has the analyzer. Caught clipped bars +
slanted text.

## Files
- `references/api_signatures.md` — full inspect dump.
- `references/render_verify.md` — frame extract + PIL analyzer.
- `scripts/hardsub.sh` — merge + burn-in.
- `templates/video_script.py` — known-good scaffold.
