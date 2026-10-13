---
name: manim-api-patterns
description: Manim CE v0.20.x patterns for explainer videos.
---

# Manim API Patterns (CE v0.20.x)

This skill captures reusable patterns discovered while building DSA explainer videos with Manim CE v0.20.x. It complements the `manim-explainer-animations` and `manim-dsa-storytelling` skills with battle-tested implementation patterns.

## 1. Code Mobject — `code_lines` is a Paragraph

```python
from manim import Code

code = Code(code_string="def foo():\n    return 1", language="python")
# code.code_lines is a Paragraph object
# Actual lines are in code.code_lines.submobjects (list of VGroups)
lines = code.code_lines.submobjects
# lines[0] = first line VGroup, lines[1] = second line, etc.
```

**Error if treated as list**: `IndexError: list index out of range` or `AttributeError`.

## 2. Class-level lambdas become bound methods

```python
class MyScene(Scene):
    BF_COMPLEXITY = lambda x: x  # WRONG - becomes bound method, gets (self, x)
    
    @staticmethod
    def bf_complexity(t):  # CORRECT
        return t
```

When defined as class attributes, lambdas receive `self` as first argument. Use `@staticmethod` or module-level functions.

## 3. ThreeDScene — Text billboarding

**HUD text (titles, labels, captions)**: Must call `add_fixed_in_frame_mobjects()` BEFORE positioning.

```python
title = Text("My Title")
self.add_fixed_in_frame_mobjects(title)  # FIRST
title.to_edge(UP)  # THEN position
```

**Text anchored to 3D objects**: Don't fix in frame. Rotate upright instead.

```python
label = Text("value")
label.rotate(90 * DEGREES, axis=RIGHT)  # Stand upright, face camera
label.next_to(cube, DOWN, buff=0.1)
```

## 4. Camera orientation conventions

```python
# Standard explainer 3D view
self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)

# For 2D complexity graph (top-down)
self.move_camera(phi=0, theta=-90 * DEGREES, run_time=0.5)
```

## 5. Axes.plot expects Callable[[float], float]

```python
# WRONG: lambda takes wrong args
bf_curve = graph_axes.plot(self.BF_COMPLEXITY, x_range=[0, 20])

# CORRECT: wrapper with single float arg
bf_curve = graph_axes.plot(lambda t: self.bf_complexity(t), x_range=[0, 20])
```

## 6. Performance on CPU-constrained environments

- `-ql` (480p15): ~3-5 min per video on load avg 35+ (2-4 vCPU)
- `-qh` (1080p60): ~15-30 min per video
- Use `-s` for single-frame validation before full render
- Background renders without `rm -rf media` between scenes to preserve previous outputs

## 7. Scene generation pattern (reusable 5-act DSA template)

```python
# Template: trick_XX_name.py
class TrickXXName(TrickScene):
    TITLE = "Title"
    SOLID_TYPE = "cubes|spheres|cones|torus|surface"
    INPUT_DATA = [...]
    INSIGHT_TEXT = "One-sentence hinge fact"
    
    NAIVE_CODE = """..."""
    IDIOMATIC_CODE = """..."""
    
    @staticmethod
    def bf_complexity(t): return ...
    @staticmethod
    def opt_complexity(t): return ...
    
    def _run_naive(self):
        lines = self.bf_code.code_lines.submobjects
        for i in range(min(len(lines), N)):  # Safe iteration
            self.play(self.bf_hl.animate.move_to(lines[i]), run_time=0.3)
    
    def _run_optimized(self):
        lines = self.opt_code.code_lines.submobjects
        for i in range(min(len(lines), N)):
            self.play(self.opt_hl.animate.move_to(lines[i]), run_time=0.3)
```

## 8. Background rendering without cleanup

```bash
# DON'T rm -rf media between scenes
for f in trick_*.py; do
    manim -ql $f ClassName  # preserves previous media/
done
```

## 9. 5-Act DSA Storytelling Structure

| Act | Purpose | Key Elements |
|-----|---------|--------------|
| 1. Cold Open | Problem as spatial 3D shape | `ThreeDAxes` + solids (cubes/spheres/cones) |
| 2. Brute Force | Exhaustive particle sweep | Split-screen Code + `SurroundingRectangle` highlight + `TracedPath` particle |
| 3. Insight | One hinge fact | Text beat, highlighted subset of 3D space |
| 4. Optimized | Same space, direct path | Swap Code panel, clean `TracedPath` |
| 5. Payoff | Complexity graph | `Axes.plot` with true functions, visible separation |

## 10. 3D Solid Vocabulary

| Solid | Use For | Why |
|-------|---------|-----|
| Cube/Prism row | Arrays, sequences | Discrete, ordered, indexable |
| Torus / torus knot | Cyclic structures | Loop implies wraparound |
| Sphere cluster | Unordered sets / hash sets | No implied order |
| Cone/pyramid stack | Trees, heaps, recursion | Vertical taper = levels |
| Surface/mesh grid | DP tables, 2D grids | Height encodes DP value |

## References

- `manim-explainer-animations` skill: `references/mobjects.md`, `references/camera-and-scenes.md`, `references/text-and-typography.md`
- `manim-dsa-storytelling` skill: 5-act structure, 3D solid vocabulary, particle system patterns