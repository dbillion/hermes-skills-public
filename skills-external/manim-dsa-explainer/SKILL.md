---
name: manim-dsa-explainer
version: 1.0.0
description: Consolidated skill for building narrative-driven Manim explainer videos for DSA/algorithm content -- covers both single-path walkthroughs (one algorithm, no brute-force baseline) and brute-vs-optimized comparisons, plus a technique-selection grammar, camera/angle presets, and a mandatory "verified by test" beat so every rendered video is traceable to a passing unit test. Supersedes manim-dsa-storytelling + manim-dsa-single-path as the single entry point for DSA video work; still layers on top of manim-explainer-animations, which owns the base mobject/animation API surface.
---

# Manim DSA Explainer (single-path + comparison, unified)

## Relationship to the other skill

Read `manim-explainer-animations/SKILL.md` and its `references/` first -- it owns
the mobject/animation API surface (mobjects, animations, camera, plotting, text,
advanced techniques). This skill owns the **narrative shape** for DSA content
specifically: which of the two formats to use, the 3D-solid vocabulary, the
technique-selection grammar, camera/angle presets, and the mandatory
verified-by-test closing beat.

## Step 0 -- pick the format

- **Comparison (5 acts)**: use when a genuine brute-force baseline exists AND
  the complexity gap is real and instructive (e.g. two-sum brute O(n^2) vs
  hash-set O(n), LIS O(n^2) vs O(n log n)).
- **Single-path (4 acts)**: use for everything else -- sorts, traversals,
  searches, tree/graph operations, single-pass or single-table DP, data
  structure mechanics, bit tricks. This is the default; most of a DSA catalog
  has no real brute/optimized pair, so don't force one.

Both formats close with the same **Act 6: verified by test** (below) -- that
part is not optional and does not vary by format.

## Comparison format -- 5 acts (~45-90s)

1. Cold open -- state the problem as a shape in 3D space, no numbers yet.
2. Brute force -- animate an exhaustive particle sweep (nested loops felt as
   many particle-trips, not a caption saying "O(n^2)").
3. The insight -- one beat naming the single fact the optimized version
   exploits. Give it a full breath.
4. Optimized -- same 3D space, same camera/axes as act 1, short direct path.
5. Payoff -- complexity explained by symbol + text + flow (see rule #5):
   two stacked lanes (Time, Space), each a morphing MathTex with a one-clause
   WHY beneath it and a cost-volume bar that collapses on the optimized morph.
   Both curves plotted from the true Big-O (Axes.plot, not eyeballed shapes),
   optimized curve visibly separating.

## Single-path format -- 4 acts (~30-50s)

1. Cold open -- build the data structure/space with the matching solid before
   any code appears.
2. The walkthrough -- real source in a `Code` mobject with a synced
   `SurroundingRectangle` highlight tracking the active line, while a
   particle/marker performs the algorithm in the 3D structure. Largest act.
3. The key property -- why this approach works (loop invariant, structural
   guarantee, base case). Real breath (Write + wait), not skipped just
   because there's no brute-force to contrast against.
4. Payoff -- final state held (sorted array, traced path, returned value).
   Complexity explained by symbol + text + flow (rule #5): Time AND Space
   lanes, each morphing with a one-clause WHY and a collapsing cost-volume.

## Act 6 -- verified by test (mandatory, both formats)

Every scene must close by showing the actual passing JUnit `@Test` (or
equivalent in the target language) that proves the algorithm animated is
correct -- not a paraphrase, the real `@Test` method body, pulled from the
project's own test file. Use `test_replay()` from the shared style module, which
shows BOTH the test source statically (a `Code` panel) AND the test's *executed*
result dynamically (it runs the real `@Test` via Gradle and animates the captured
input->output + a green check). This exists specifically because it was
implemented once, in a `dsa_style.py` helper, then only used in 3 of 83 scenes
in an early batch and silently dropped for the rest even though the helper stayed
available and imported -- treat "no test_replay call" as a rendering bug, same
severity as a missing highlight sync, not an optional polish pass.

## Code display is mandatory -- static AND dynamic (non-negotiable)

Showing the real source code is one of the highest-value parts of these videos.
It must appear in BOTH forms, never only one:

- **Static code:** the verbatim algorithm source as a `Code` mobject
  (`code_panel()`), shown during the walkthrough. Brute force AND optimized
  versions each get their own panel with a title (e.g. "Brute force O(n^2)" /
  "Optimized: HashMap O(n)"). The source is real and pulled from the project,
  never paraphrased.
- **Dynamic code:** a `SurroundingRectangle` highlight (`make_highlight()`)
  that tracks the active line in lockstep with the animation -- as the particle /
  marker steps through the structure, the highlight moves line-by-line through
  the `Code` panel. This is what makes the code *alive*, not a frozen block.

Treat a scene missing either the static `Code` panel or the dynamic line-sync
highlight as a rendering bug, same severity as a missing test payoff. When
upgrading a scene, never drop the `code_panel`/`make_highlight` calls to make
room for the complexity or test beats -- they coexist.

Rules:
- Pull the sample input/output directly from the test file, never invent
  values -- if the walkthrough already used a specific input in act 1/2 (the
  single-path case) it must be the *same* input the test asserts on, so the
  video and the test are visibly the same claim.
- If no test exists yet for the algorithm being animated, do not skip the
  act -- write the missing test first (in the target project's real test
  file, following its existing conventions), confirm it passes, then animate
  it. A video for untested code is not "done."
- Keep this act short (label + code + check, ~1.5-2s hold) -- it is a
  provenance stamp, not a second walkthrough.

## 3D solid vocabulary (data-structure metaphors)

Pick the solid for what it visually implies, not for novelty -- an inconsistent
solid across beats reads as decoration, not explanation. Keep the same solid
for the whole video once chosen.

| Solid | Use for |
|---|---|
| Cube/Prism row along an Axes x-axis | Arrays, sequences, in-place sorts |
| Torus / torus knot | Cyclic structures -- circular buffers, graphs with cycles |
| Sphere cluster in 3D axes | Unordered sets / hash sets (the "seen" set) |
| Cone/pyramid stack, tree layout | Trees, heaps, recursion depth |
| Surface/mesh grid over a 2D domain | DP tables, 2D grid problems |
| Dot/Sphere nodes + Line/Arrow edges | Graphs (BFS/DFS/Dijkstra/MST/bipartite) |
| Cylinder (queue) | FIFO queues / hash buckets |
| Ring (torus + seated dots) | Circular queues, cycle-in-list, ring buffers |
| Cone pointer | Cursor marker -- current index, top-of-stack, current node |
| Min-heap tree (cones, root at top) | Heap-specific structures |
| Split wedge (triangular prism) | Divide & conquer cut point (merge-sort mid,
  quickselect partition, binary-search elimination) |
| Prism grid (flat rectangular-prism grid) | 2D DP tables (edit distance,
  knapsack, LCS) |

## Technique-selection grammar

Choose the Manim technique by the explanatory job, not habit:

| Job | Technique |
|---|---|
| Algebraic manipulation | `TransformMatchingTex` |
| Shape morph, same parts | `TransformMatchingShapes` |
| Same idea, two representations | `TransformFromCopy` |
| Curve produced by motion | `TracedPath` |
| Function plot | `axes.plot` / `plot_parametric_curve` |
| Naming or grouping | `Brace` + label |
| Focus on a term | `SurroundingRectangle` |
| Cancellation | strikethrough `Line`, never deletion |
| Labels/arrows that follow a moving object | `add_updater` |
| Dynamic graph that rebuilds | `always_redraw` + `ValueTracker` |
| 4+ elements moving together | `lag_ratio` cascade |
| Strict sequence in one beat | `Succession` |
| One shape becoming another (no shared parts) | `Homotopy` |
| Code line tracking during execution | `Code` mobject + synced
  `SurroundingRectangle`, see Act 6 rules above |

## Camera and angle grammar

- 3D framing: `phi` about 65-75deg, `theta` about -45 to -60deg.
- Ambient orbit about 0.12 rad/s if used at all; stop the orbit before the
  payoff/verified-by-test beats -- both need to be read as still frames.
- 2D zoom in = focus on one idea, zoom out = restore context.
- Rotations/phases use `rate_func=linear`; arrivals use ease-out cubic;
  emphasis uses `there_and_back`.
- HUD text (titles, act labels, the verified-by-test panel) must go through
  `add_fixed_in_frame_mobjects()` BEFORE positioning (`to_edge`/`to_corner`),
  or it renders lying flat on the xy-plane once the camera tilts. Text
  spatially anchored to a 3D object instead gets rotated out of-plane
  (`label.rotate(90 * DEGREES, axis=RIGHT)`), not fixed in frame. Verify this
  on a real render, not by reading the code -- render `-pql`, then
  `ffmpeg -ss 00:00:0X -update 1 -frames:v 1 out.png` on a mid-tilt frame and
  eyeball it, before trusting the full render.

## Visual grammar

- Background: near-black (Dark Studio palette from
  `manim-explainer-animations/references/style-guide.md`).
- Primary object: blue. Important result / active particle: one consistent
  accent color, reused every beat it appears. Error/conflict: red.
  Solution/analogy: green. Helper object: grey or dashed.
- One idea per shot. Motion represents meaning -- don't animate a swap that
  didn't happen in the real code.
- Preserve object identity: transform, don't fade-swap, when the underlying
  data is the same object across a beat.
- Don't animate more than ~3 independent motions at once; stagger the rest
  with `lag_ratio`.

## Shared style layer (transferred from manim-brilliance-explainer)

The following creative rules, color grammar, and QA checklist are ported from the
general-purpose brilliance explainer so DSA scenes share one visual language.
Treat them as mandatory, not optional polish — they are the difference between a
video that decorates an algorithm and one that teaches it. The base mobject/animation
API still lives in `manim-explainer-animations`; these rules govern *how* to use it.

### 10 creative rules (DSA-adapted)
1. One idea per shot.
2. Motion must represent meaning — animate a swap only if the real code swaps.
3. Preserve object identity: `Transform`, never fade-swap, when the underlying
   data is the same object across a beat (an array element sliding to a new
   index must be the *same* mobject, not a `FadeOut`+`FadeIn`).
4. Minimal color palette (see grammar below).
5. Complexity is explained by **symbol + text + flow**, never a bare caption:
   - Show it as a **mathematical symbol** (`O(n^2)`, `O(n \\log n)`, `O(n)`,
     `O(1)`) via `MathTex`, and **morph** between brute and optimized
     (`TransformMatchingTex`) so the complexity drop is the aha (rule from the
     brilliance layer).
   - **Both TIME and SPACE must be shown.** Naive-vs-optimized almost always
     trades time for space (e.g. Two-Sum: `Time O(n^2)->O(n)`,
     `Space O(1)->O(n)`). Render two stacked lanes, each morphing.
   - Under each symbol, a **one-clause Text stating WHY** (e.g. "every pair
     checked" / "one hash lookup per element"). The *why* is mandatory — it is
     the part that teaches, not the symbol alone.
   - Convey the cost as a **FLOW of work**: a cost-volume bar that grows with
     the bound (tall for `n^2`, short for `n`) and collapses on the optimized
     morph, so the viewer *feels* the complexity shrink rather than reading it.
   Use `complexity_v2()` from the shared style module (isolated prototype) which
   implements all four of these.
6. Labels appear near the object they describe — invariant labels sit next to
   the pointer/value they track.
7. Camera movement must have a reason; stop orbits before payoff/test beats.
8. At most 3 independent motions at once; stagger the rest with `lag_ratio`.
9. Every scene has a visible aha moment (the single realization the algorithm
   hinges on — give it a full breath).
10. The visual is understandable with sound off (persistent invariant labels).

### Color grammar (additive to the existing ACCENT/GOOD pair)
- Background: near-black (`#0e0f12`).
- Primary object / **active element**: BLUE (`#4aa3ff`) — the thing currently moving.
- Important result / the answer found: YELLOW (`#ffd166`).
- Error / failed comparison: RED (`#ff5d5d`).
- Solution / chosen path / optimized: GREEN (`#5ad1a6`).
- Helper object: GREY or dashed.
The existing `ACCENT` (brute) / `GOOD` (optimized) pair stays for the
brute-vs-optimized framing; BLUE / RED / YELLOW layer on top for *intra-act*
emphasis (which element is active, which comparison just failed, which value is
the result). Do not introduce further colors — a 5-color max keeps it readable.

### Legibility rules (non-negotiable — a real regression was caught where
text wrote on top of itself and fonts were too small to read at 480p)
- **Every text line owns its own vertical lane.** A title goes `to_edge(UP)`;
  any secondary line (subtitle, `nums = [...]`, status) goes to a DISTINCT band
  BELOW it (e.g. `UP * 2.4` via the `subtitle()` helper), never `to_edge(UP)` +
  a tiny `shift(DOWN * 0.2)`. Two texts at the same `UP` edge overwrite each
  other — that is the "text over itself" bug. The hook opener (`hook_opening`)
  also uses the subtitle band, NOT the title edge.
- **Fonts are LARGE by default.** Under a tilted 3D camera at 480p, body text
  must be >= ~0.5 and titles >= ~0.9 (manim `scale` units). Treat anything
  smaller as a bug. Pin one sans (`TeXGyreHeros-Bold`) for all `Text` so weights
  stay consistent; use `MathTex` for math. The shared `improved_dsa_style.py`
  constants `TITLE_SIZE=0.9 / LABEL_SIZE=0.55 / EXPECTED_SIZE=0.85` are the floor.
- **Fade or `ReplacementTransform` between text states, never `Write` onto an
  already-visible mobject.** If a line must change (title -> result), fade the
  old one out (or `ReplacementTransform` it) before/while the new one appears.
- **Keep text upright and fixed-in-frame** (`add_fixed_in_frame_mobjects`) in 3D
  scenes so it never lies flat on the floor or foreshortens into an unreadable
  sliver.

### QA checklist (extended)
- Does the animation reveal the core insight / key property?
- Are objects transformed instead of arbitrarily replaced (identity kept)?
- Is the code real and verbatim, highlight synced to the line executing?
- Is the screen uncluttered; are colors meaningful, not decorative?
- Are labels readable, and upright under a tilted 3D camera?
- **Is the complexity beat animated (morph `O(n^2)` -> `O(n \log n)`), not just
  two static curves drawn side by side?**
- **Does the scene open with a hook (the wrong intuition) before the solution?**
- **Are invariant labels persistent so it works without sound?**
- **Does the `test_panel` text render at a readable size (~20pt after scale)?**
- Does the scene end with Act 6 (real passing `@Test`) for the exact input
  animated?
- Does the scene work without narration/sound?

## Numerical & state encoding grammar (color = what the data IS doing)

The creative rules above cover *which* element and *which* outcome gets a color.
This section covers the harder gap: using color/shade/geometry to encode the
**numerical state and function** of the data — filled vs empty, in motion vs at
rest, magnitude, and the matrix/vector shape of the computation. Evidence base:
the sequential/diverging/qualitative colormap taxonomy and perceptual-uniformity
requirement (Matplotlib colormaps guide; CMasher/arXiv:2003.01069; ColorCET;
Crameri scientific colormaps; Golden Software color-mapping guide; Dev3lop
perception-based mapping), plus the *educational* findings of Stasko et al.
"Designing Educationally Effective Algorithm Visualizations" (Auburn/HalVis) and
PyTorch "Inside the Matrix" for matrix geometricization.

### 1. Fill / empty / capacity state of a solid
A solid's *fill level* is data, so show it, don't hide it:
- Empty/uncommitted: GREY (`#9aa0a6`), low opacity.
- Partially filled / active: BLUE (`#4aa3ff`), full opacity.
- Full / at-capacity (queue full, bucket saturated, heap maxed): the structure's
  accent at full saturation, optionally with a thin YELLOW rim to read "full".
- Overflow / rejection: flash RED (`#ff5d5d`) on the boundary that rejected it.
Encodes the capacity invariant without a caption. (HalVis: state changes must be
visible at the micro level, not just implied.)

### 2. Data movement along flow lines
When data travels between the data tray and a structure (or between structures),
the flow line itself carries the state (this is the "which structure, when"
visual made literal):
- In transit: BLUE.
- Accepted into the structure: GREEN (`#5ad1a6`).
- Rejected / evicted / cycled out: RED.
Keep a flow line to ONE primary motion per beat (the "max 3 motions" rule) and
let the line color tell the viewer the data's fate without a label.

### 3. Vectors = magnitude, not decoration
A numeric value that has a direction/basis (running sum, pointer offset, gradient)
is drawn as an `Arrow` from the relevant origin whose **length = |value|** and
whose **direction = sign/axis**. Drive it with `always_redraw` + `ValueTracker`
so it swings live as the algorithm runs (e.g. Kadane's `currentSum` vector dips
negative then snaps up — the algorithm, made visible). A vector that doesn't
encode a real metric is banned by rule #2 (motion represents meaning).

### 4. Matrices / DP tables = heatmap, not just grid
A 2D computation (DP, adjacency, matrix multiply) is a `prism_grid` whose **cell
fill encodes the numeric value** via a perceptually-uniform ramp:
- Sequential magnitude: dark -> bright (one hue family).
- Value relative to a midpoint (deviation, residual): DIVERGING ramp
  (blue -> white -> red), mid = neutral — do NOT use rainbow/"jet", which the
  CMasher and Matplotlib sources show distorts magnitude and fails grayscale.
- Categorical structure (which structure owns which cell): QUALITATIVE distinct
  hues.
Animate the **fill sweep in dependency order** (PyTorch "Inside the Matrix":
spatially coherent mental model) so the viewer reads *how* the table is built,
not just the final numbers.

### 5. Oscillating numbers (the HUD)
Live numeric readouts (currentSum, heap size, in-flight count, inversions) live
in the fixed-in-frame HUD as `MathTex`/`Text` driven by `ValueTracker`. Jitter
the displayed digit by a tiny `sin` modulation on change so the eye catches the
update — magnitude of jitter = size of the change (meaningful, not screensaver).

### 6. Accessibility (non-negotiable)
Per the color-vision-deficiency sources: any sequential/diverging ramp must stay
distinguishable **after grayscale conversion** and avoid red/green-only pairing.
Prefer blue/yellow + luminance steps over red/green. The base palette here
(BLUE/YELLOW/RED/GREEN/GREY on near-black) already leans blue/yellow; keep RED
for *transient* error flashes, not as a steady-state category, to protect
deuteranopic viewers.

## API correctness (verified against manim 0.20.1 via Context7)

These are the version-correct call patterns. Get them wrong and the scene
crashes at render time (not at import), so always render `-pql` before calling a
scene done.

- **`Scene.play` takes only `Animation` objects.** Passing a bare `Mobject`
  (e.g. a helper that returns `self`) raises `TypeError: Unexpected argument
  <Mobject>`. To change a mobject's color/stroke without animating it, call the
  mutator as a plain statement (`obj.set_color(GREEN)`), not inside `play()`. To
  *animate* a color/state change, use `obj.animate.set_color(GREEN)` or
  `self.play(obj.animate.set_stroke(...))`.
- **`add_fixed_in_frame_mobjects` is a `ThreeDScene` method** (camera keeps the
  mobject screen-fixed under camera moves). A plain `Scene` does NOT have it — so
  any scene using `fixed_title` / invariant labels / HUD text must subclass
  `ThreeDScene`, even for "2D-looking" videos.
- **`Transform(mobject, target)` keeps a reference to `mobject`** (mutates it
  in place; `target` is not added). Use **`ReplacementTransform(mobject, target)`**
  when the intent is to *swap* one object for another (e.g. a title becoming the
  result text). For LaTeX label changes use `TransformMatchingTex` (with
  `isolate=` / `key_map=` to refine matching, e.g. the `O(n^2)` -> `O(n \log n)`
  complexity morph).
- **Live geometry: `always_redraw(lambda: ...)` + `ValueTracker`.** The lambda
  rebuilds the mobject each frame from `tracker.get_value()` (e.g. a magnitude
  `Arrow` whose length = |value|, or an `Arc` whose angle tracks time). Animate
  the tracker with `self.play(tracker.animate.set_value(x))` — never
  `self.play(tracker, ...)`.
- **Staggered simultaneous motion: `LaggedStart(*[anim for ...], lag_ratio=...)`
  capped at ~3 independent motions** (skill rule). For curved transform paths
  pass `path_arc` to `Transform`/`ReplacementTransform`.
- **Code panels are two separate `Code`/`Text` mobjects swapped by `FadeOut` +
  `FadeIn`** (not `Transform`ed into each other) — see Workflow step 4.
- Syntax-check before every render: `python3 -c "import ast;
  ast.parse(open('X.py').read())"` -- but note this catches typos, not
  runtime `play()` arg errors, so the `-pql` render is still the real gate.

## Workflow

1. Read the real source and its real test file -- never invent behavior or
   sample values; pull both from the repo (see Act 6 rules if a test is
   missing).
2. Pick format (Step 0), then pick one solid from the vocabulary table for
   the whole video.
3. Storyboard the acts as comments before writing any `self.play()` calls.
4. Build the code panel(s) with the real, verbatim source -- one panel for
   single-path, two (swapped, not `Transform`ed into each other) for
   comparison.
5. Syntax-check first: `python3 -c "import ast; ast.parse(open('X.py').read())"`
   -- cheap, catches typos before a slow render.
6. Render `-pql` (480p15) first, check pacing, camera, and the flat-text
   pitfall; then `-pqh` for final export.
7. Confirm any complexity-graph beat reflects the real Big-O -- plot the true
   functions, don't eyeball curve shapes.
8. Verify exit code 0 and that the output `.mp4` actually exists on disk
   (not just `partial_movie_files/`) before marking a scene done or reporting
   progress -- re-verify from disk, not from memory of a prior turn.

## QA checklist (run before calling a scene finished)

- Does the animation reveal the core insight / key property?
- Are objects transformed instead of arbitrarily replaced?
- Is the code shown real and verbatim, with the highlight synced to the
  line actually executing?
- Is the screen uncluttered, and are colors meaningful (not decorative)?
- Is the pacing comfortable -- not racing through the largest act, not
  padding a trivial one-liner into a full 4-act video?
- Are labels readable and, under a tilted 3D camera, upright (not lying on
  the floor)?
- **Does the scene end with Act 6 -- a real, passing `@Test` shown on
  screen for the exact input animated?** If not, the scene is not finished,
  regardless of everything else on this checklist.
- Does the scene work without narration/sound?

## Common pitfalls

- Forcing a fake "brute force" comparison when there's no instructive worse
  baseline -- use the single-path format instead.
- Padding a trivial algorithm (bit tricks, one-line GCD) into a full video --
  compress the walkthrough act, spend the time on the key-property beat.
- Graphs without a stable layout -- fix node positions once, don't let them
  jump between acts.
- Losing the metaphor -- if a torus was "the graph" in act 1, it must still
  be recognizably the same torus at the payoff; re-derive positions from the
  same data, don't rebuild from scratch with new coordinates.
- **Dropping Act 6.** This happened for 80 of 83 scenes in the source
  project despite the helper (`test_panel`) already existing and being
  imported -- the fix isn't a new helper, it's calling the one that's already
  there, every time.
