# Scene Authoring Conventions — DSA Explainer Batch (MUST FOLLOW)

You are generating Manim CE 0.20.1 scene files for a DSA explainer video project.
Existing scenes set the style — your new scenes MUST match them exactly.

## Files you work with (in the scenes/ dir)
- `dsa_style.py` — import: DARK_BG, CUBE_COLOR, ACCENT, GOOD, SCENE_SHIFT,
  make_cube_row, fixed_title, code_panel, make_highlight, complexity_payoff.
- `graph_tree_style.py` — make_graph, make_tree, make_vertical_stack (Cube/Sphere).
- `shapes3d.py` — NEW additive shapes: make_cylinder_queue, make_ring (Torus),
  make_cone_pointer, make_min_heap_tree, make_split_wedge, make_prism_grid.

## STUDY THESE EXISTING SCENES FIRST
- Single-path: `s02_merge_sort.py` (ThreeDScene, 4-act walkthrough).
- Comparison: `q03_two_sum.py` (ThreeDScene, 5-act brute-vs-optimized, uses
  `complexity_payoff(self, bf_fn, opt_fn, "brute O(n²)", "opt O(n)")` with plain
  functions — NOT lambdas bound via self).

## Exact conventions
1. `from manim import *` then `from dsa_style import ...` (only what you use).
2. Module-level constants for the SAMPLE INPUT from AlgorithmsTest.java (real values).
3. Scene extends `ThreeDScene`; `self.camera.background_color = DARK_BG`.
4. `fixed_title(self, "Name")` + `self.play(Write(title))`.
5. `self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)`.
6. `axes = ThreeDAxes(...)`; `axes.shift(SCENE_SHIFT)`.
7. SHOW REAL SOURCE: `code_panel(self, CODE, "label", GOOD, scale=0.45)` →
   `(label, code)`. `make_highlight(self, code, line_index, color)` for the
   SurroundingRectangle; animate `hl.animate.move_to(code.code_lines[i])`.
   CODE = real method body (verbatim, trimmed to the relevant function).
8. HUD text (titles, insight, payoff, complexity tags): ALWAYS
   `self.add_fixed_in_frame_mobjects(mobj)` BEFORE positioning (`to_edge(DOWN)`).
   Value labels attached to 3D objects: `lbl.rotate(90*DEGREES, axis=RIGHT)`.
9. Arrays: `make_cube_row(axes, arr, height_scale=...)`. Additive new shapes ONLY
   where metaphor fits (torus=cycles, cylinder=queues/stacks, cone=heap/pointer,
   prism grid=DP table, wedge=search-cut). Cubes for plain arrays.
10. Comparison (5-act): cold-open, brute sweep (dense TracedPath), insight, optimized
    (short trail), payoff via `complexity_payoff(self, type(self).BF_COMPLEXITY,
    type(self).OPT_COMPLEXITY, "brute O(..)", "opt O(..)")` — pass CLASS-level attrs!
11. Single-path (4-act): cold-open, walkthrough, key property, payoff.

## OUTPUT REQUIREMENTS
- Write to `scenes/<prefix>_<name>.py`; class `<PrefixName>Walkthrough` (single)
  or `<PrefixName>BruteVsOptimized` (comparison). Render:
  `python3 -m manim -ql file.py ClassName`.
- After writing ALL assigned files, syntax-check each:
  `python3 -c "import ast; ast.parse(open('<file>').read())"`.
- Do NOT render. Do NOT use rm. Do NOT modify dsa_style/graph_tree_style/shapes3d.
