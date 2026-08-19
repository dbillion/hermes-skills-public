# Advanced Techniques

## Updaters — the most powerful CE feature for "live" animation

An updater is a function called every frame to recompute a mobject's state. Use this instead of manually creating new objects frame-by-frame whenever something needs to *track* something else (a moving point, a changing value, a graph redrawing as its function changes).

### `always_redraw` — rebuild a mobject from scratch every frame

Best when the shape/topology of the mobject genuinely changes (e.g. a `Line` whose length changes, a `Sphere` whose radius changes).
```python
radius = ValueTracker(1.0)
circle = always_redraw(lambda: Circle(radius=radius.get_value(), color=BLUE))
self.add(circle)
self.play(radius.animate.set_value(3), run_time=2)
```

### `mobject.add_updater(func)` — mutate an existing mobject in place every frame

Best for cheap, incremental changes (repositioning, following another mobject) where full rebuild is wasteful.
```python
label = Text("dot")
label.add_updater(lambda m: m.next_to(dot, UP))   # label follows dot every frame
self.add(dot, label)
self.play(dot.animate.shift(RIGHT * 3))
...
label.remove_updater(...)   # remove before the object needs to stop tracking (e.g. before a Transform)
```
**Always remove updaters before a `Transform`/`ReplacementTransform` on the same mobject** — an active updater fighting the transform animation produces glitchy results. Also remove ambient updaters before `self.wait()`-only "let it settle" beats if precise final position matters.

### `ValueTracker` / `ComplexValueTracker`

An invisible mobject holding a single number (or complex number), meant purely as an animation driver — `.animate.set_value(x)` on it inside `self.play()` is the standard way to smoothly drive any updater-based animation (rotation angle, radius, slider position, counter value).

### `UpdateFromFunc` / `UpdateFromAlphaFunc`

Animation-class versions of updaters, for one-shot custom animations that don't fit any built-in `Animation` subclass — `UpdateFromAlphaFunc` gives you the interpolation alpha (0→1) directly, useful for hand-writing a custom easing/behavior in a single `play()` call instead of a full custom `Animation` subclass.

### `MaintainPositionRelativeTo`

Keeps one mobject's position locked relative to another's, for the animation's duration — a scoped alternative to a manual `add_updater` when you only need it for one `play()` call.

## Sound

```python
self.add_sound("click.wav", time_offset=0)   # play a sound effect at a specific point in the scene
```
For full narration: prefer the `manim-voiceover` plugin (below) over hand-timing `self.wait()` calls against a separately-recorded voiceover — it keeps animation timing and narration audio in sync automatically and re-times on edits.

## `manim-voiceover` (narration-synced timing — install separately: `pip install manim-voiceover`)

```python
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService  # or recorded audio / other TTS services

class MyScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService())
        with self.voiceover(text="This is a tesseract, a four-dimensional cube.") as tracker:
            self.play(Create(tesseract), run_time=tracker.duration)
```
`tracker.duration` gives you the actual spoken-audio length so the animation's `run_time` matches the narration exactly — this is the correct way to build narration-synced explainers, rather than guessing `run_time` values and hoping they line up with a voiceover added later.

## `manim-physics` (rigid body / fluid / pendulum simulations — install separately)

Adds `Rigidbody`/`SpaceScene` and related classes for simple 2D physics (gravity, collisions, pendulums) rendered directly through Manim — useful for physics explainers where hand-coding the kinematics via updaters would be tedious.

## Rendering config & performance

- `config.background_color`, `config.frame_rate`, `config.pixel_height/width` can be set at the top of a file (or via CLI flags) instead of per-Scene — use for project-wide defaults.
- 3D scenes with many `Surface`/`Sphere` objects at high resolution are the main render-time cost — keep `resolution=(24,24)`-ish while iterating, raise it only for the final render.
- `--renderer=opengl` is faster for complex 3D scenes and enables `interactive_embed()`, but has less consistent cross-platform behavior than the default Cairo renderer — default to Cairo unless a specific need (live interactivity, heavy 3D) justifies switching, and mention the tradeoff to the user if you do switch.
- Use `self.next_section(...)` + `--save_sections` (see `camera-and-scenes.md`) to avoid re-rendering the whole video while iterating on one beat.

## Plugin ecosystem

Check `manim plugins -l` (lists installed plugins) or the community plugin list before hand-building something that's already a well-tested plugin — `manim-voiceover` and `manim-physics` above are the two most broadly useful; others exist for chemistry (`manim-chemistry`), circuit diagrams, and DSP/signal-processing visuals. If the user's domain matches one of these, mention the plugin option before building the equivalent from primitives.
