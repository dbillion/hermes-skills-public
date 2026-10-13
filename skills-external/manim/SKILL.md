---
name: manim
description: Use when creating mathematical/scientific animations with Manim (Community Edition OR ManimGL), building explainer videos, or debugging Manim scenes. Covers CE best-practices, GL best-practices, iart reference patterns, explainer/video pipelines, and the verified Manim 0.20.1 API. Trigger on "manim", "animation", "explainer video", "3blue1brown".
---

# Manim (unified)

Single skill covering **Manim Community Edition (CE)**, **ManimGL**, and the
explainer/video production pipeline. Replaces the previously scattered
`manimce-best-practices`, `manimgl-best-practices`, `iart-manim`,
`yusuke-manim-skill`, `manim-020-api`, `manim-explainer`,
`manim-explainer-video`, `manim-video`, `manim-video-production`.

## Pick the engine
- **ManimCE** (`from manim import *`) — standard, pip-installable, best docs.
  Use for almost everything. Rules: `rules/ce/`, templates `templates/ce/`.
- **ManimGL** (`from manimlib import *`) — Grant Sanderson's engine, shader
  driven, interactive. Use when you need GL-specific features. Rules:
  `rules/gl/`, templates `templates/gl/`.

> The user has stated a preference for **stories (written narrative) over
> rendered videos**, and for the **fastest/cheapest model**. Default to writing
> an explainer as text. Build a video only when explicitly requested.

## CRITICAL — camera/3D pitfalls (from the iart audit)
The single most common failure is wrapping a **2D explainer** in `ThreeDScene`,
which forces a perspective "floor view" and slanted-side props. Read
`references/iart/3d-and-camera.md` before any 3D work. Rules of thumb:
- If content is flat (text, code, diagrams, bars) → use a plain `Scene`.
- Never call `add_fixed_in_frame_mobjects()` on a `Scene` (does not exist; and
  the old pattern `add_fixed_in_frame_mobjects(x); self.remove(x)` deletes the
  object). In a 2D `Scene` mobjects are already screen-space.
- If you do use `ThreeDScene`: center 3D props at `(0,0,0)`, use
  `phi=70°, theta=30°` (NOT a near-head-on `theta=-20°`), and keep props away
  from off-axis `x=±3.6`.

## Directory map
- `rules/ce/` — 23 ManimCE best-practice rules (scenes, shapes, text,
  latex, graphing, 3D, updaters, timing…)
- `rules/gl/` — 18 ManimGL best-practice rules (cli, config, embedding,
  t2c, shaders…)
- `templates/ce/`, `templates/gl/` — ready-to-run scene skeletons
- `references/iart/` — iart-manim patterns (3D/camera, graphs/updaters,
  math/text) + `_iart_skill.md` (original SKILL)
- `references/explainer/` — explainer workflow + video/audio refs
- `references/video/` — full explainer-video production references (mobjects,
  camera/3D, equations, graphs, rendering, production-quality, troubleshooting…)
- `references/api/00-api.md` — verified Manim 0.20.1 API signatures
- `references/yusuke_skill.md` — yusuke-manim-skill overview
- `tools/` — yusuke video_viewer.py + ui.html (preview rendered scenes)
- `scripts/` — frame_verify.py, setup.sh helpers

## Usage
1. Pick engine → read the matching `rules/*` + a template as a starting point.
2. If 3D is involved, read `references/iart/3d-and-camera.md` first.
3. For end-to-end explainer production (storyboard → render → TTS → hardsub),
   read `references/video/` and `references/explainer/`.
4. Verify API calls against `references/api/00-api.md` when unsure of a
   signature/version.

## Notes
- `manimgl-best-practices` and the old `adithya-manimgl-bp` were byte-identical
  duplicates; only one copy is kept here (`rules/gl/`).
- The iart 3D-camera pitfall section was authored during the
  `CollectionsExplainer` floor-view bug fix and is preserved intentionally.
