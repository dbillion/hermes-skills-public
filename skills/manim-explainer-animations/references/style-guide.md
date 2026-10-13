# Style Guide: 3Blue1Brown / Veritasium conventions

Use this to make Manim output look like a produced explainer, not a default-theme demo.

## Color palette

Avoid Manim's default pure `BLACK`/`WHITE`/saturated primaries — they read as "unstyled."

```python
BG_COLOR       = "#0e1116"   # near-black background, slight blue tint
PRIMARY_BLUE   = "#58C4DD"   # 3b1b's signature "Manim blue" (BLUE_C-ish)
ACCENT_YELLOW  = "#FFC857"   # highlight / "pay attention here" color
ACCENT_RED     = "#FC6255"   # contrast/warning/error highlight, use sparingly
SOFT_GREEN     = "#83C167"   # secondary positive highlight
GREY_TEXT      = "#CCCCCC"   # body text, not pure white (softer on video)
```

Rules of thumb:
- One shape/idea = one consistent color throughout the whole video. Don't recolor the tesseract mid-video without a narrative reason (e.g. color = w-depth is fine and expected).
- Reserve `ACCENT_YELLOW` exclusively for the thing the viewer should look at *right now* — if everything is highlighted, nothing is.
- When color encodes the 4th dimension (the w-axis proxy), use a smooth gradient (e.g. `color_gradient([BLUE_E, PRIMARY_BLUE, ACCENT_YELLOW], ...)`) mapped to w-value — this is the single most common way both channels visualize an unshowable axis.

## Camera conventions

- Default resting angle for 3D scenes: `phi=65*DEGREES, theta=-45*DEGREES` — close to 3b1b's default "three-quarter" view, avoids a flat/dead-on look.
- Ambient rotation during "explaining" beats: slow, `rate=0.03`–`0.08` via `begin_ambient_camera_rotation`. Never spin fast enough to be dizzying — the camera motion should be barely-consciously-noticed, giving a sense of "real 3D object" without distracting from narration.
- Stop ambient rotation (`self.stop_ambient_camera_rotation()`) during any beat where precise reading of a diagram matters (e.g. counting vertices) — motion competes with careful looking.
- Punch-in (`self.move_camera(zoom=1.5, run_time=1.5)`) for the "reveal" moment; Veritasium in particular uses a fast push-in right at the emotional payoff line.
- Cut back out (zoom=1, wider phi) at the start of a new beat to "reset" the viewer's sense of scale.

## Pacing / timing

- Default `run_time` for a single concept animation: **1.5–3 seconds**. Faster reads as rushed; slower drags.
- Always `self.wait(1)` (or more) after a `play()` that introduces a new idea, before moving on — give the idea a beat to land. This is one of the most consistently under-used calls by people imitating this style; the "let it breathe" pause is a huge part of why the pacing feels right.
- For a full explainer scene, budget roughly:
  - 5–10% hook / cold open
  - 20–30% build-up (dimensional analogy, setting up notation)
  - 40–50% core demonstration (the actual 4D object, rotation, cross-section)
  - 10–20% payoff / reframe ("...and that's why a shadow of a rotating tesseract looks like it's turning inside out")
- Use `LaggedStart` for revealing multiple similar objects (e.g. all 16 tesseract vertices appearing) rather than `FadeIn` on a `VGroup` all at once — staggering reads as more intentional/directed.

## Text and LaTeX conventions

- Formulas via `MathTex`, never raw `Text` for actual math.
- Keep on-screen text minimal — narration (or narration-timed captions) carries the explanation; on-screen text is for labels, key formulas, and the occasional short reinforcing phrase, not paragraphs.
- Font: Manim's default (Computer Modern via LaTeX) is correct and expected for this style — don't override to a sans-serif unless doing a deliberately "modern/casual" Veritasium-style caption overlay, in which case a clean sans (e.g. a `Text(..., font="Helvetica")` alternative) is fine for *captions* while formulas stay LaTeX.
- Label axes with the actual variable, not generic "Axis 1/2/3/4" — e.g. `MathTex("w")` in the accent color, placed near wherever the w-gradient is explained.

## Narration-synced structure (for when audio/voiceover will be added later)

Structure the Scene's `construct()` method as a sequence of clearly-commented beats so a human (or TTS pass) can attach narration lines 1:1:

```python
def construct(self):
    # BEAT 1: Hook — show the finished tesseract rotating, no explanation yet
    ...
    self.wait(2)

    # BEAT 2: Build up — point to line to square to cube
    ...

    # BEAT 3: Reveal — "…so what happens when we do this one more time?"
    ...
```

This also makes it trivial to re-time beats independently later without re-deriving the whole animation.

## Borrowed techniques, attributed by name

- **"3b1b sweep-reveal":** use `Create()` with `rate_func=smooth` on wireframe edges rather than `FadeIn`, so structure appears to be "drawn" — reinforces that it's a precise mathematical object, not a picture.
- **"Veritasium real-world anchor":** before or after the abstract 4D sequence, cut to (or describe, if no footage) a tangible real-world analogy — e.g. a shadow of a rotating 3D wireframe cube on a table, explicitly drawn as the 3D analogy of what a tesseract's 3D "shadow" is doing. Both channels ground abstraction in something the eye already trusts.
- **"Predict then reveal":** pause on a pattern (e.g. the vertex-count table) with the last row blanked out or covered, held for at least 1 full second, before revealing — gives the audience a chance to guess, which measurably increases engagement with the payoff.
