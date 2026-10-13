---
name: manim-brilliance-explainer
version: 3.2.0
description: General-purpose 3Blue1Brown/Veritasium-style math & science explainer pack for Manim Community Edition -- director/storyboard-writer/coder/QA-reviewer prompt pipeline, technique-selection grammar, camera/angle presets, corpus miner, eval rubric, and a full technique/shot/template library. All example scenes verified against Manim Community v0.20.1. Use for general concept explainers (not DSA/algorithm content -- use manim-dsa-explainer for that).
---

# Skill: Manim Brilliant Explainer (v3.2)

## Purpose

Create math and science animations in the spirit of 3Blue1Brown and Veritasium:
clear, elegant, visual-first, narrative-driven, and mathematically precise.

## Inputs

- topic
- audience level
- target duration
- desired visual style
- core message

## Output

1. Core insight statement
2. Misconception or hook
3. Storyboard with beats
4. Manim scene code using the correct technique from the grammar below
5. Rendering instructions
6. QA checklist

## Creative Rules

1. One idea per shot.
2. Motion must represent meaning.
3. Preserve object identity: transform, never fade-swap.
4. Use a minimal color palette.
5. Use LaTeX for math when appropriate.
6. Labels appear near the object they describe.
7. Camera movement must have a reason.
8. Do not animate more than 3 independent motions at once; stagger the rest.
9. Every scene should have a visible aha moment.
10. The visual should be understandable even with sound off.

## Technique Selection Grammar

Choose the technique by the explanatory job:

- Algebraic manipulation -> TransformMatchingTex (shots/algebra.py)
- Shape morph with same parts -> TransformMatchingShapes
- Same idea in two representations -> TransformFromCopy (shots/linking.py)
- Curve produced by motion -> TracedPath (shots/tracing.py)
- Function plot -> axes.plot, parametric -> plot_parametric_curve
- Naming or grouping -> Brace + label (shots/annotations.py)
- Focus on a term -> SurroundingRectangle (shots/annotations.py)
- Cancellation -> strikethrough Line, never deletion (shots/annotations.py)
- Labels or arrows that follow -> add_updater with become() (shots/followers.py)
- Dynamic graphs that rebuild -> always_redraw + ValueTracker
- Function acting on numbers -> apply_complex_function (shots/complex_maps.py)
- 4 or more elements moving -> lag_ratio cascade (shots/choreography.py)
- Strict sequence in one beat -> Succession (shots/choreography.py)
- One shape becoming another -> Homotopy (shots/deformation.py)
- Limit process -> Transform to a finer version of the same object
- Animated vector fields -> stream.create() (Manim Community)

## Camera and Angle Grammar (style/camera.py, style/angles.py)

- 3D framing: phi about 75 deg, theta about -45 deg, zoom about 0.8
- Ambient orbit about 0.12 rad/s; stop the orbit before the payoff
- 2D zoom in = focus, zoom out = context
- Rotations and phases use rate_func = linear
- Arrivals use ease-out cubic; emphasis uses there_and_back

## Visual Grammar

- Background: near-black
- Primary object: blue
- Important result: yellow
- Error/conflict: red
- Solution/physical analogy: green
- Helper object: grey or dashed

## Production Pipeline Rules

1. Build videos as many small Scene classes, one per beat, not one long scene.
2. Time animations to the narration, not the other way around.
3. Add sound design and narration in post-editing, outside Manim.
4. Preview with -ql, final render with -qh and 60 fps.

## QA Checklist

- Does the animation reveal the core insight?
- Are objects transformed instead of arbitrarily replaced?
- Is the screen uncluttered?
- Are colors meaningful?
- Is the pacing comfortable?
- Are labels readable?
- Is the math correct?
- Does the scene work without narration?
