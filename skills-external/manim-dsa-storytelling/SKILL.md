---
name: manim-dsa-storytelling
description: Build narrative-driven Manim explainer videos that compare a brute-force algorithm against its optimized counterpart, using a 3D cartesian "data space" (solids as data-structure metaphors), particle systems for data flow, and complexity graphs for payoff. Layers on top of the manim-explainer-animations skill — read that skill's references first for mobject/animation API, then use this file for the story structure, the brute-vs-optimized visual grammar, and the 3D-solid vocabulary. Use whenever the user wants a DSA/algorithm comparison video, a "why is this faster" explainer, or a code-repo walkthrough turned into an animated story.
---

# Manim DSA Storytelling (brute-force vs optimized)

## Relationship to manim-explainer-animations

This is a companion skill, not a replacement. Before writing any scene:
1. Read `manim-explainer-animations/SKILL.md` and its `references/` — it owns the API surface
   (mobjects, animations, camera, plotting, text, advanced techniques).
2. Use this file for the **story shape**: how a brute-vs-optimized comparison should be beat-by-beat,
   which 3D solids map to which data-structure ideas, and how to stage particle-based data flow so it
   reads as "the algorithm thinking," not decoration.

## The narrative shape (5 acts, ~45-90s total)

A DSA comparison video is a small argument, not a code dump. Every beat exists to answer one
question: why does the optimized version win, and what is it doing differently?

1. Cold open — the problem, spatially. State the problem as a shape in 3D space before any code
   appears (e.g. an array as a row of glowing cubes on an axis, a graph as a torus/mesh of nodes).
   No numbers yet — just "here is the space we're searching."

## Code-and-visual duality (non-optional)

The point of this format is that someone can watch it and then go reproduce the algorithm — not
just enjoy an abstract animation. Every beat that demonstrates brute-force or optimized behavior
MUST show the real source alongside the visualization, not describe it in prose:

- Use a `Code` mobject (see manim-explainer-animations/references/text-and-typography.md) loaded
  with the actual source — `code_string=` copy-pasted from the real file, not a paraphrase. If the
  brute-force version doesn't exist in the source repo, write a standard, idiomatic baseline and
  say so in an on-screen or narration note — never invent an unfaithful "optimized" version either.
- Split-screen layout: `Code` panel fixed in frame on one side (e.g. left third/half via
  `add_fixed_in_frame_mobjects` + `to_edge(LEFT)`), the 3D data-space visualization occupying the
  other side. Shift the 3D group (axes + solids) toward the free side so neither overlaps the code.
- Sync a highlight, don't just display static code: keep a `SurroundingRectangle` (or similar) over
  `code_obj.code_lines[i]` and move it to track whichever line the animation is currently acting out
  — the comparison line during a brute-force hop, the update line when a running value changes. The
  highlight is the bridge between "watching a shape move" and "understanding what the code just did."
- Swap panels between brute-force and optimized beats (`FadeOut` old `Code`, `FadeIn` new `Code`) —
  don't try to `Transform` between two different algorithms' source, it reads as morphing nonsense.
- If the code is too long to read in the time budget, trim to the relevant function only (still the
  real function body, not a summary) rather than shrinking font past legibility.
2. Brute force — show the search, don't just say it's slow. Animate the brute-force approach as
   an exhaustive particle sweep: a particle (or swarm) visiting every candidate — every pair, every
   subarray, every path — using nested loop-driven animations so the O(n^2) or O(n^3) cost is felt
   as visibly more particle-trips, not just stated in a caption.
3. The insight. A single beat, usually text + a highlighted subset of the 3D space, naming the
   one fact the optimized algorithm exploits (a running sum, a seen-set, a monotonic property). This
   is the hinge of the whole video — give it a full breath, don't rush past it.
4. Optimized — show the shortcut, same space. Re-run the same problem in the same 3D space, but
   the particle path is short, direct, and often single-pass. Reuse camera angle and axes from beat 1
   so the contrast is legible as "same space, different path" rather than "different scene."
5. Payoff — the complexity graph. Cut to a 2D plot of both curves (O(n^2) vs O(n), or whatever
   applies) as input size grows. Let the optimized curve visibly separate from the brute-force curve
   — this is the "receipts" beat. End on the gap, held.

Keep acts 2 and 4 visually parallel (same camera, same solid, same color for "the answer") so the
video reads as one A/B comparison, not two unrelated animations.

## 3D solid vocabulary (data-structure metaphors)

Pick the solid for what it visually implies, not for novelty — a solid used inconsistently across
beats reads as decoration, not explanation.

| Solid | Use for | Why it reads correctly |
|---|---|---|
| Cube/Prism row along an Axes x-axis | Arrays, sequences | Discrete, ordered, indexable — matches how viewers already picture an array |
| Torus / torus knot | Cyclic structures — circular buffers, graphs with cycles, hash-ring structures | The loop is the point; don't use a torus for a linear structure, it implies wraparound |
| Sphere cluster in 3D axes | Unordered sets / hash sets (the "seen" set in two-sum, visited-nodes in BFS/DFS) | No implied order — spheres floating in space read as "membership," not "sequence" |
| Cone/pyramid stack | Trees, heaps, recursion depth | Vertical taper reads as "levels" without extra labeling |
| Surface/mesh grid over a 2D domain | DP tables, 2D grid problems (matrix chain, LCS, grid paths) | Height can encode the DP value directly — literally plot the table |

Keep the Dark Studio-style palette from manim-explainer-animations/references/style-guide.md
consistent across both the brute-force and optimized run — only the color of the "active/moving"
particle should stand out (one accent color, reused every beat it appears).

## Particle systems for data flow

Use always_redraw + a ValueTracker (see manim-explainer-animations/references/advanced-techniques.md)
to drive a Dot/small Sphere along a path — this is "the particle" that stands in for the algorithm's
current pointer/cursor/comparison. Patterns:

- Sweep (brute force): nested loop -> nested Succession/LaggedStart of short particle hops, one hop
  per comparison. Let the trail (TracedPath) accumulate visibly — a dense tangle of trails by the
  end of the brute-force beat is the point, it visualizes the wasted work.
- Single pass (optimized): one continuous MoveAlongPath or ValueTracker-driven sweep, left to right,
  no backtracking. The trail should look like a straight, calm line next to the brute-force tangle.
- State callouts: attach a small always_redraw'd label near the particle showing the live variable
  it's tracking (running sum, current max, seen-set membership) so the "why" stays on screen, not
  just the "what."

Don't animate every single comparison in a large input at full speed — for anything beyond ~8-10
elements, either subsample (animate the real pattern on a small n, then cut to the complexity graph
for large n) or use ChangeSpeed/run_time scaling to compress repetitive middle sections.

## Workflow for this skill

1. Identify the brute-force/optimized pair from the target source (read the actual code — don't
   invent the algorithm; if the repo only contains the optimized version, write the brute-force
   baseline yourself but say so, and keep it faithful to the standard textbook version).
2. Pick one 3D solid from the vocabulary table above for the whole video — don't mix metaphors.
3. Storyboard the 5 acts as scene-file comments before writing any self.play() calls.
4. Build brute-force and optimized beats as two methods/sections sharing camera setup and solid
   construction, so visual parity isn't accidentally lost between them.
5. Render -pql first (480p15) to check pacing and camera, then -pqh for final export.
6. Confirm the complexity-graph payoff beat actually reflects the real Big-O of both approaches —
   don't eyeball the curve shapes, plot the true functions with Axes.plot.

## Common pitfalls specific to this comparison format

- Telling instead of showing the cost. A caption that says "O(n^2)" without a visibly denser
  particle trail than the optimized beat is a missed beat, not a finished one.
- Different camera/axes between the two runs. Breaks the A/B read — always reuse the exact
  Axes/camera object (or an identical clone) for both beats.
- Skipping the insight beat. Jumping straight from brute force to optimized without naming what
  changed leaves the "why" implicit — the insight beat is not optional.
- Losing the metaphor. If a torus was "the graph" in beat 1, it must still be recognizably the
  same torus in beat 4 — re-derive positions from the same data, don't rebuild the mobject from
  scratch with new coordinates.
- Text lying flat on the "floor." This format lives in ThreeDScene with a tilted camera
  (phi != 0), so it hits this pitfall constantly: any Text/MathTex added without
  add_fixed_in_frame_mobjects() is embedded in the scene's xy-plane and reads as lying on the
  ground once the camera tilts. Fix, depending on what the text is for:
    - HUD text (titles, act labels, captions, complexity-graph tags): call
      self.add_fixed_in_frame_mobjects(mobj) BEFORE positioning it (to_edge/to_corner), so it
      renders as a screen-space overlay. See manim-explainer-animations/references/camera-and-scenes.md.
    - Text spatially anchored to a 3D object (e.g. a value label under an array cube, that
      should visually stay attached to that object): don't fix it in frame — instead rotate it
      out of the xy-plane, e.g. label.rotate(90 * DEGREES, axis=RIGHT), so it stands upright and
      faces the camera instead of lying flat.
  Test this specifically by rendering -pql and eyeballing a frame partway through any tilted-camera
  beat (ffmpeg -ss 00:00:0X -update 1 -frames:v 1 out.png on the rendered file) before trusting the
  full render — this bug is invisible in the code and only shows up on screen.
