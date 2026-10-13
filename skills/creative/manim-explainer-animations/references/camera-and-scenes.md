# Camera & Scenes

## Scene subclasses — pick based on what the camera needs to do

| Class | Use when | Key methods/attrs |
|---|---|---|
| `Scene` | Default; static 2D camera, no pan/zoom needed | `self.play`, `self.add`, `self.wait` |
| `ThreeDScene` | Any 3D content | `set_camera_orientation(phi=, theta=, zoom=)`, `begin_ambient_camera_rotation(rate=)`, `move_camera(...)`, `add_fixed_in_frame_mobjects(...)` for UI/text that shouldn't rotate with the 3D scene |
| `MovingCameraScene` | 2D scene that needs to pan/zoom (frame the important part, pull back to reveal) | `self.camera.frame` is itself a mobject — animate it: `self.play(self.camera.frame.animate.scale(0.5).move_to(target))` |
| `ZoomedScene` | Need a persistent inset "magnifying glass" view of part of the scene while the main view keeps playing | `self.zoomed_camera`, `self.activate_zooming()` |
| `LinearTransformationScene` | Specifically for "watch a matrix transform the plane" linear-algebra explainers | Auto-sets up a `NumberPlane` + basis vectors; `self.apply_matrix(m)` |
| `VectorScene` | Vector-diagram-heavy content (base class `LinearTransformationScene` builds on) | Helper methods for adding/labeling vectors |

## ThreeDScene camera cookbook

```python
class MyScene(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES, zoom=1)
        self.begin_ambient_camera_rotation(rate=0.05)   # slow orbit, "alive" feel
        self.play(...)
        self.stop_ambient_camera_rotation()              # stop before anything needs careful reading
        self.move_camera(phi=80 * DEGREES, theta=30 * DEGREES, zoom=1.5, run_time=2)  # deliberate reframe

        # Text/UI that must NOT rotate with the 3D scene:
        label = Text("Fixed HUD text")
        self.add_fixed_in_frame_mobjects(label)
        label.to_corner(UL)
```
`phi` = angle from the z-axis (0 = looking straight down; 90° = looking from the side). `theta` = azimuthal angle around z. Default resting view for explainer-style 3D: `phi=65*DEGREES, theta=-45*DEGREES` (see style-guide.md).

## MovingCameraScene cookbook (2D pan/zoom)

```python
class MyScene(MovingCameraScene):
    def construct(self):
        big_diagram = ...  # some VGroup
        self.add(big_diagram)
        self.play(self.camera.frame.animate.scale(0.4).move_to(big_diagram[3]))  # push in on one part
        self.wait()
        self.play(self.camera.frame.animate.scale(2.5).move_to(ORIGIN))          # pull back out
```
This is the standard "zoom into the interesting detail, then pull back to show the whole picture" move.

## Multiple scenes / sections

- Each `Scene` subclass renders to its own video file; a full video is typically several `Scene` classes concatenated in post (or with `\section` markers via `self.next_section("name")` and rendering with `--save_sections` for finer-grained caching/re-render during iteration).
- Use `self.next_section("beat_name")` at each storyboard beat boundary during development — lets you re-render just the section you're iterating on instead of the whole scene (`manim render --save_sections`), which massively speeds up the iterate-on-timing workflow.

## Interactive / embedded use

- `self.interactive_embed()` inside `construct()` (OpenGL renderer, `--renderer=opengl`) drops into an IPython shell with the live scene, letting you nudge mobjects and see results immediately — useful for exploring camera angles or layout before committing to code, not for final output.
- Jupyter: `%%manim -ql SceneName` cell magic renders inline in a notebook — good for rapid iteration on a single scene without repeated CLI calls.

## Rendering flags worth knowing (used from the command line, not in code)

```bash
manim -pql file.py Scene       # preview, low quality (fast iteration)
manim -pqh file.py Scene       # high quality (1080p60) final render
manim -pqk file.py Scene       # 4K60
manim -s file.py Scene         # save last frame only (skip full render) — great for checking a static layout
manim --format=gif file.py Scene   # export as GIF instead of mp4
manim -a file.py                # render ALL Scene classes in the file
```
Always iterate with `-ql -s` (or just `-ql`) — never iterate on timing/layout at final quality, it multiplies render time for no benefit until the storyboard is locked.
