# Animation Catalog (how mobjects move/appear/change)

All used as `self.play(AnimationName(mobject, ...), run_time=..., rate_func=...)`.

## Creation (`manim.animation.creation`)

`Create` (draw the outline progressively — the CE replacement for old `ShowCreation`), `Uncreate` (reverse), `DrawBorderThenFill` (outline first, then fill — good for logos/icons), `Write` (for `Text`/`Tex` — draws each "stroke" like handwriting), `Unwrite`, `AddTextLetterByLetter`, `RemoveTextLetterByLetter`, `AddTextWordByWord`, `TypeWithCursor`/`UntypeWithCursor` (typewriter effect with a blinking cursor — more "produced" than plain `Write` for code/terminal-style reveals), `ShowIncreasingSubsets` (reveal a VGroup's submobjects one at a time, e.g. a scatter plot appearing point by point), `ShowSubmobjectsOneByOne` (show only one submobject at a time, replacing the last), `SpiralIn` (newer, spiral-inward reveal — nice alternative to `FadeIn`/`GrowFromCenter` when you want more visual energy), `ShowPartial` (base class).
```python
self.play(Create(circle), run_time=1.5)
self.play(Write(formula), run_time=2)
self.play(TypeWithCursor(code_block), run_time=3)
```

## Fading & Growing

`FadeIn`, `FadeOut` (support `shift=`, `scale=` kwargs for directional/scaling fades). `GrowFromCenter`, `GrowFromPoint`, `GrowFromEdge`, `GrowArrow`, `SpinInFromNothing` (grows while spinning — good for emphasis on a new element).
```python
self.play(FadeIn(text, shift=UP))
self.play(GrowArrow(vector))
```

## Indication (draw attention without changing the object permanently)

`Indicate` (brief scale+color pulse), `Circumscribe` (draw a temporary shape around it, e.g. a rectangle or circle), `Flash` (radiating lines from a point), `FocusOn` (shrinking ring drawing the eye to a point), `Wiggle` (small rotation wiggle), `ApplyWave` (wave distortion), `Blink`, `ShowPassingFlash` (a moving highlight travels along a path once), `ShowPassingFlashWithThinningStrokeWidth`.
```python
self.play(Circumscribe(key_term, color=YELLOW, fade_out=True))
self.play(Indicate(formula_part))
```
These are the primary "look here" tools — much better than manually recoloring and reverting.

## Transform family (`manim.animation.transform`)

`Transform` (morphs mobject A into the shape of B, keeping A's identity — B stays hidden/unused after), `ReplacementTransform` (A is replaced by B in the scene; prefer this when you'll keep manipulating B afterward), `TransformFromCopy` (leaves the original in place, morphs a copy onto the target), `FadeTransform`/`FadeTransformPieces` (cross-fade while moving — better than `Transform` when shapes are very different), `ClockwiseTransform`/`CounterclockwiseTransform` (control rotation direction during the morph), `CyclicReplace` (swap positions of a cycle of mobjects), `Swap` (2-mobject shortcut), `MoveToTarget` (animate to a `.target` you set beforehand via `mob.generate_target()`), `ApplyMethod` (animate calling a method), `ApplyFunction`/`ApplyPointwiseFunction`/`ApplyPointwiseFunctionToCenter` (apply an arbitrary spatial function to every point — for warping/distortion effects), `ApplyMatrix` (linear-transform every point — the standard "here's what a matrix does to the plane" animation), `ApplyComplexFunction` (complex-plane warps, e.g. visualizing `z -> z^2`), `Restore` (return to a saved `.save_state()`), `ScaleInPlace`, `ShrinkToCenter`.
```python
self.play(ApplyMatrix([[2, 1], [0, 1]], plane))          # shear transform of a NumberPlane
self.play(ApplyComplexFunction(lambda z: z**2, plane))    # z -> z^2 visualized
mob.generate_target(); mob.target.shift(RIGHT).scale(2)
self.play(MoveToTarget(mob))
```

### Matching transforms (algebra-step / diagram-morph explainers — very high value for math videos)

`TransformMatchingTex` — morphs one `MathTex`/`Tex` into another, automatically matching identical LaTeX substrings so they glide into their new position instead of the whole formula cross-fading. **This is the single most important animation for "watch the equation rearrange" beats.**
```python
eq1 = MathTex("a", "+", "b", "=", "c")
eq2 = MathTex("a", "=", "c", "-", "b")
self.play(TransformMatchingTex(eq1, eq2))
```
`TransformMatchingShapes` — same idea but for arbitrary `VMobject`s matched by shape rather than LaTeX string, e.g. morphing one diagram into a related diagram.

## Movement

`MoveAlongPath` (move a mobject along an arbitrary `VMobject` path), `Homotopy`/`SmoothedVectorizedHomotopy` (deform points via a time-varying function — general-purpose "flow" animation), `ComplexHomotopy`, `PhaseFlow` (move points along a vector field's flow — pairs with `ArrowVectorField`).
```python
self.play(MoveAlongPath(dot, circle_path), run_time=3, rate_func=linear)
```

## Rotation

`Rotate` (one-shot rotation by an angle), `Rotating` (continuous rotation, typically used with `run_time` + `rate_func=linear` for a steady spin).

## Numbers

`ChangeDecimalToValue`, `ChangingDecimal` — animate a `DecimalNumber`/`Integer` counting up/down. Pairs naturally with a `ValueTracker` for a "counter" display.

## Specialized

`Broadcast` (expanding concentric-circle pulse from a point — radar/signal effect).

## Composition (combine multiple animations)

`AnimationGroup` (play several animations together, optionally staggered via `lag_ratio`), `LaggedStart` (same idea, simpler API — most common for "reveal N similar things in sequence"), `LaggedStartMap` (apply one animation type across a VGroup's submobjects, staggered — shortcut over manually building a list), `Succession` (play animations one after another in a single `play()` call, useful for chaining without extra `wait()`s).
```python
self.play(LaggedStart(*[FadeIn(m) for m in dots], lag_ratio=0.05), run_time=2)
self.play(LaggedStartMap(Create, edges_vgroup, lag_ratio=0.03))
```

## Speed control

`ChangeSpeed` — wraps another animation and speeds it up/slows it down over its duration without manually recomputing `run_time`; useful for a "fast-forward through the repetitive part, slow down for the interesting part" beat within a single animation call.

## Rate functions (`manim.utils.rate_functions`, used via `rate_func=` on any `play()`)

Common ones: `linear`, `smooth` (default — ease in/out), `rush_into`, `rush_from`, `slow_into`, `there_and_back`, `there_and_back_with_pause`, `wiggle`, `ease_in_sine`/`ease_out_sine`/`ease_in_out_sine` (and cubic/quad/expo/bounce/elastic/back variants). Use `there_and_back` for anything that should return to its start (great for cross-section sweeps), `linear` for anything meant to feel mechanical/constant (ambient rotation, counting), `smooth` as the default for everything else.
