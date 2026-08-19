---
name: manim-video-production
description: "Manim video workflow: git, hardsub, billboard, 0.20.1 fixes."
version: 1.0.0
---

# Manim Video Production — workflow discipline

Use this skill for the *process* of shipping Manim CE videos. For the full mobject/
animation/camera API surface, load the user's `manim-explainer-animations` skill
(installed at ~/.hermes/skills/creative/manim-explainer-animations) — it is richer
and authoritative. This skill captures the operational rules that session work proved
necessary and that the user explicitly demanded.

## 1. Git: commit every verified render (USER EXPLICIT CORRECTION)
The user flagged missing git commits as "very bad engineering." Rule:
- Keep the video project in its OWN git repo (init one in the project dir, not `~`).
- After EACH verified render (visually approved OR pixel-analysis-verified), commit:
  `script.py` + the hardsubbed `.mp4` + the `merged.srt`. One commit per iteration.
- This gives a rollback point and a diffable history to reference in discussion.

## 2. Subtitles: add_subcaption() is NOT visible
`self.add_subcaption(...)` only writes a sidecar `.srt` — no on-screen text.
Burning-in recipe (full detail in references/hardsub.md):
1. Each scene emits a `.srt` beside its `.mp4`.
2. Merge with cumulative offsets into `merged.srt` (scene durations via ffprobe).
3. `ffmpeg -i in.mp4 -vf "subtitles=merged.srt:force_style='FontSize=18,PrimaryColour=&H00FFFF00&,OutlineColour=&H00000000&,BorderStyle=1,Outline=2'" -c:a copy out.mp4`
Deliverable = the hardsubbed mp4.

## 3. 3D text must be billboarded (else slanted "on the floor")
In a `ThreeDScene` with a top-down `phi`, plain `Text`/`Code`/`ImageMobject` placed in
3D space renders edge-on/slanted. Fix: register as fixed-in-frame then remove so it
animates face-on:
```python
self.add_fixed_in_frame_mobjects(mob)
self.remove(mob)
self.play(FadeIn(mob), ...)
```
Class MUST be `ThreeDScene` (not `Scene`) for this method to exist.
Camera: fixed `phi=65*DEGREES, theta=-20*DEGREES` (or -45), no `begin_ambient_camera_rotation`
while objects are near frame edges (it swings them out → clipping).

## 4. 0.20.1 mobject kwarg gotchas
- `Cone(base_radius=..., height=...)` — NOT `radius=` (TypeError).
- `Cylinder(radius=..., height=...)` — `radius=` is fine.
- `Torus(major_radius=..., minor_radius=...)`.
- `Sphere(radius=..., resolution=(u,v))`.
- `Code(code_string=..., language="python", paragraph_config={"font_size":N})`
  (NOT `code=`, NOT `insert_line_no=`, font size goes in paragraph_config).

## 5. See-instead-of-eyes: vision endpoints often dead
`vision_analyze` (aux model) and `browser_vision` (CDP sandbox blocks localhost/file/data)
frequently fail. Substitute: render frames (`ffmpeg -i in.mp4 -ss T -frames:v 1 f.png`),
then PIL pixel analysis — measure content bbox for clipping, edge ratios for upright
text, luminance buckets for visible cube faces. See references/pixel_check.md.

## 6. API truth: inspect the installed build
Repo/NLM digests lie about signatures. Trust
`python -c "import inspect; from manim import X; print(inspect.signature(X.__init__))"`
on the installed `manim` (uv tool at ~/.local/share/uv/tools/manim) over any doc.

## 7. NEVER `rm -rf media` between batch renders (USER EXPLICIT CORRECTION)
A session wiped 21 already-rendered videos because every render started with
`rm -rf media`. Manim writes each scene to its OWN subfolder
(`media/videos/<scene_name>/<quality>/`) — there is NO reason to delete.
- Rule: do NOT delete `media/` (or any render output dir) between renders unless
  the user explicitly asks.
- To re-render a single scene, just re-run manim for that one scene — it only
  overwrites its own folder. Other scenes stay on disk.
- For a batch: loop over scenes in one shell script, logging START/DONE/FAIL per
  scene to a progress log, and never `rm`. Accumulated mp4s stay on disk so a
  crash/later failure loses only the current scene, not the whole batch.
- Verify from disk, not memory: after a batch, `find media -name '*.mp4' -type f
  ! -path '*partial_movie_files*'` and grep the log for `DONE`. Do not claim
  "all N done" until files exist on disk (this exact over/under-statement is
  called out in the dsa-java-gradleqa HANDOFF.md too).

## 8. More 0.20.1 gotchas (caught the hard way)
- `Code.code_lines` is a `Paragraph`, NOT a list. Lines are
  `code.code_lines.submobjects[idx]` (NOT `code.code_lines[idx]` — that raises
  IndexError). Wrap line-highlight math in `len(.submobjects)` checks.
- Complexity curves for `Axes.plot(fn, x_range=...)`:
  * `fn` is called as `fn(x)` (single arg) internally by `ParametricFunction`.
  * A class-level `lambda t: t` works as a lambda, but a class-level `def`
    BECOMES A BOUND METHOD and breaks (`takes 1 positional argument but 2 were
    given` / `'Scene' and 'float'`).
  * SAFEST: define complexity helpers at MODULE level as `def quad(t, *_): return
    t**2` and reference them from the scene as `BF_COMPLEXITY = quad` (a reference
    to a module fn does NOT become a bound method). Or wrap at the call site:
    `graph_axes.plot(lambda x: bf_fn(x), ...)`.
  * Do NOT pass a class attribute that is a `def` to `Axes.plot`.

## 9. Headless render backend: OpenGL hangs, use Cairo
`--renderer=opengl` needs a GPU/display (Xvfb/EGL/GL). In a headless container it
hangs with no process and no output. Use `--renderer=cairo` (CPU-only). On a
local machine with a GPU, OpenGL is far faster — but it will NOT work headless.
- Preview: `manim -ql --renderer=cairo scene.py SceneName`
- Final:   `manim -qh --renderer=cairo scene.py SceneName` (1080p60)
- At high CPU load (load avg >15) a 480p scene can take 10+ min. Be patient;
  let background renders accumulate rather than re-rendering from scratch.

## 10. Storytelling quality: mirror the proven shared-style architecture
User: "your story telling is very poor, see the script in this folder." The
dsa-java-gradleqa scenes (by a prior agent) were judged far better. The winning
pattern, codified in references/dsa_storytelling.md and batch_template.md:
- ONE shared style module (`dsa_style.py`) imported by every scene: palette,
  `make_cube_row` (arrays), `code_panel`, `make_highlight`, `complexity_payoff`.
- Base scene class (e.g. `TrickScene(ThreeDScene)`) implementing the 5 acts:
  cold open (3D data space) → naive (split-screen Code + particle trail + synced
  highlight) → insight beat → idiomatic (same space, different particle path) →
  payoff (2D complexity graph with REAL functions).
- Real code from the source repo, never invented baselines.
- Subclass only implements `run_naive()` / `run_idiomatic()` + class attrs.
Copy that structure; do not hand-roll per-scene helpers.

## References
- references/hardsub.md — full SRT-merge + ffmpeg burn-in recipe.
- references/kwarg_gotchas.md — 0.20.1 constructor signatures that bite.
- references/dsa_storytelling.md — 5-act narrative (cold open → brute force → insight → optimized → payoff) with split-screen Code+3D, synced highlights, particle trails, complexity graphs. Uses manim-dsa-storytelling skill.
- references/animated_mermaid.md — build mermaid diagrams as Manim mobjects (VGroup of nodes/edges) that grow node-by-node via Create/LaggedStart, billboarded via add_fixed_in_frame_mobjects.
- references/batch_template.md — base TrickScene + YAML config + generated scene files pattern for batch-producing many similar explainer videos.
- references/readme_gif.md — GitHub README doesn't render MP4 inline; convert demo MP4 → optimized GIF (ffmpeg palettegen/paletteuse) for inline playback.
- scripts/capability_probe.py — runnable 3D+4D test (shapes, Torus toroid on ThreeDAxes; 4D tesseract double-rotation + hypersphere slice) to validate a fresh Manim install before building.
- scripts/safe_batch_render.sh — batch render loop that NEVER `rm -rf media`, logs START/DONE/FAIL per scene, accumulates mp4s on disk, and prints a disk-verified file list at the end. Use this instead of hand-typed loops that delete between renders.
