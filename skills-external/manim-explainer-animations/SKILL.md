---
name: manim-explainer-animations
description: Build complete Manim Community Edition (v0.20.x) animations and explainer videos — any mobject (2D/3D geometry, text, LaTeX, graphs, tables, matrices, vector fields, SVG/images), any animation (creation, transforms, indication, movement, updaters), camera work, and full-scene assembly — in the polished style of 3Blue1Brown and Veritasium. Use this whenever the user asks for a "manim animation/scene/video," "math/physics/CS explainer," code walkthroughs animated on screen, animated diagrams, animated graphs/plots, or wants Python code for any 2D/3D visualization intended to look produced rather than default-styled. Covers the full library surface (not just 3D/4D shapes) — text writing effects, LaTeX, transforms, camera moves, plotting, tables, and more. Use even if the user only mentions "make this concept visual" without naming Manim explicitly, and use it for any follow-up work on a Manim scene already in the conversation.
---

# Manim Explainer Animations (Manim Community Edition, latest stable v0.20.x)

## What this skill produces

A produced-feeling explainer sequence, not just technically-correct code: a hook, a build-up, a visual payoff, a release — using the right mobject/animation combination for the idea, not just the first one that works. Treat camera work, color, pacing, and text choices as part of the deliverable.

**Always use Manim Community Edition** (`pip install manim`, import as `from manim import *`), not `manimlib` (Grant Sanderson's personal fork), unless the user explicitly asks for exact 3b1b source parity. CE is what's documented, pip-installable, and actively maintained.

## Setup

```bash
pip install manim --break-system-packages
apt-get install -y libcairo2-dev libpango1.0-dev ffmpeg 2>/dev/null || true
python3 -c "import manim; print(manim.__version__)"   # confirm before building anything nontrivial
```

Optional but high-value plugins (check if the task needs them before installing):
```bash
pip install manim-voiceover --break-system-packages   # narration-synced timing, TTS or recorded audio
pip install manim-physics --break-system-packages     # rigid body / fluid / pendulum simulations
```

## Workflow

1. **Identify the idea's shape before picking mobjects.** Is this a transformation (Transform-family), a process over time (updaters/ValueTracker), a relationship (Graph/graph theory), a function (Axes/ParametricFunction), a proof/derivation (MathTex + TransformMatchingTex), or a spatial object (3D mobjects)? The category determines which reference file to read.
2. **Storyboard in beats** (5-8 beats, ~5-20s each): hook → build-up → core demonstration → payoff. Comment each beat in the `construct()` method so timing can be adjusted independently later.
3. **Read the relevant reference file(s) below before writing code** — don't guess class names or signatures from memory; the API surface is large and easy to misremember (e.g. `ShowCreation` was renamed `Create` in CE; `TexMobject`/`TextMobject` were renamed `MathTex`/`Tex`).
4. **Render low-quality first**, iterate on timing, then final-render:
   ```bash
   manim -pql scene.py SceneName    # quick preview, 480p15
   manim -pqh scene.py SceneName    # 1080p60 final
   manim -pqk scene.py SceneName    # 4K60, only if actually needed
   ```
5. **Apply the style-guide conventions** (color, camera, pacing) from `references/style-guide.md` — don't leave default Manim styling (pure black background, default primary colors) unless the user asked for a plain/utilitarian look.

## Reference files — read the ones relevant to the task

- `references/mobjects.md` — full catalog of drawable objects: 2D geometry, 3D solids, text/LaTeX, tables, matrices, graphs (graph-theory), plots/axes, vector fields, SVG/images, braces/labels. Start here to find "what class do I even use."
- `references/animations.md` — full catalog of animations: creation, transforms (incl. `TransformMatchingTex`/`TransformMatchingShapes` for algebra-step and diagram-morph explainers), fading/growing, indication (`Circumscribe`, `Indicate`, `Wiggle`, `Flash`, `FocusOn`), movement (`MoveAlongPath`, `Homotopy`), rotation, composition (`AnimationGroup`, `LaggedStart`, `Succession`), and `ChangeSpeed`.
- `references/text-and-typography.md` — `Text` vs `MarkupText` vs `Tex`/`MathTex` vs `Code`, fonts, LaTeX templates, writing/typing effects (`Write`, `AddTextLetterByLetter`, `TypeWithCursor`), bullet lists, and common LaTeX gotchas.
- `references/camera-and-scenes.md` — all Scene subclasses (`Scene`, `ThreeDScene`, `MovingCameraScene`, `ZoomedScene`, `LinearTransformationScene`), camera moves, multiple scenes/sections, and interactive/embedded use.
- `references/plotting-and-graphs.md` — `Axes`/`NumberPlane`/`PolarPlane`/`ComplexPlane`, `ParametricFunction`/`ImplicitFunction`, `Graph`/`DiGraph` (graph theory, not plots), `BarChart`, vector fields and `StreamLines`.
- `references/advanced-techniques.md` — updaters (the single most powerful CE feature for "live" animations), interactive `ValueTracker`-driven scenes, sound, `manim-voiceover` narration sync, rendering config/performance, plugin ecosystem, and OpenGL vs Cairo renderer tradeoffs.
- `references/4d-math.md` and `references/style-guide.md` — kept from the earlier 4D-focused version of this skill: 4D rotation/projection math and the 3b1b/Veritasium visual-language conventions (color palette, camera pacing, narration-beat structure). Read `style-guide.md` for ANY explainer video, not just 4D ones.
- `scripts/` — runnable full templates: `tesseract_template.py`, `hypersphere_template.py` (4D), `cheatsheet_scene.py` (fires through a wide sample of mobjects/animations in one file — good starting point to copy-modify from), `graphing_template.py`, `algebra_steps_template.py` (TransformMatchingTex derivation).

## Version-specific things worth knowing (CE v0.19–v0.20)

- `ConvexHull` / `ConvexHull3D` are recent additions for wrapping a point set in 2D/3D — useful for "here's the region defined by these constraints" explainers.
- `Label`, `LabeledLine`, `LabeledArrow`, `LabeledPolygram`, `LabeledDot` give first-class labeled-geometry mobjects — prefer these over manually grouping a shape + a `Text`/`MathTex` and positioning it.
- `SpiralIn` (growing family) and `TypeWithCursor`/`UntypeWithCursor` (creation family) are newer, more "produced-feeling" reveal/text effects than the older `FadeIn`/`Write` defaults — reach for them when the plain versions feel flat.
- `ChangeSpeed` lets you speed up/slow down a sub-animation without hand-rewriting its `run_time` — useful for a "let's fast-forward through the boring part" beat.
- CE now ships a Cairo (default, stable, universally installable) and an OpenGL renderer (`--renderer=opengl`, faster, supports true interactivity via `self.interactive_embed()`) — default to Cairo unless the task specifically needs live interactivity or heavy 3D performance; see `references/advanced-techniques.md`.

## Common pitfalls

- **Using old ManimGL/3b1b names.** `ShowCreation`→`Create`, `TextMobject`/`TexMobject`→`Text`/`Tex`/`MathTex`, `CONFIG` dict pattern → constructor kwargs. If code looks like a 3b1b tutorial from before ~2021, verify every class name against the reference files before using it.
- **Forgetting `self.wait()` after a reveal.** Every `play()` that introduces a new idea needs a following pause or the pacing reads as rushed — see `style-guide.md`.
- **Building animations without updaters when the object should track something live** (a moving point, a value changing over time, a graph that redraws). Reach for `always_redraw`/`add_updater` — see `references/advanced-techniques.md` — rather than manually re-creating objects frame by frame.
- **Pure-black background / default primary colors.** Reads as an unstyled default. Apply the palette in `style-guide.md`.
- **Raw `Text` for math.** Always `MathTex`/`Tex` for actual formulas — `Text` doesn't do LaTeX layout or spacing correctly for math.
- **Not checking `manim --version` before assuming an API exists.** The library moves between versions; if unsure, note it and verify rather than confidently guessing.
