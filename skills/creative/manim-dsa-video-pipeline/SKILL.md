---
name: manim-dsa-video-pipeline
description: Batch-produce Manim DSA videos via 5-act template and YAML.
---

# Manim DSA Video Production Pipeline

## Overview

Production pipeline for creating Manim Community Edition (v0.20.x) explainer videos that compare naive vs idiomatic Python patterns using the narrative structure from `manim-dsa-storytelling`. Handles reusable template, automated scene generation from YAML, safe code highlighting, complexity graphs, and batch rendering.

## Relationship to Other Skills

- **Requires**: `manim-explainer-animations` (base Manim CE API, camera, mobjects, animations)
- **Requires**: `manim-dsa-storytelling` (5-act narrative structure, 3D solid vocabulary, code-and-visual duality)
- **Extends**: Both skills with production-grade tooling for batch video creation

## Pipeline Components

### 1. Base Template (`templates/base_template.py`)

`TrickScene(ThreeDScene)` with all 5 acts pre-implemented:

```python
class TrickScene(ThreeDScene):
    # Subclasses define these:
    NAIVE_CODE = ""
    IDIOMATIC_CODE = ""
    INPUT_DATA = []
    SOLID_TYPE = "cubes"  # cubes, spheres, cones, surface, torus
    TITLE = ""
    INSIGHT_TEXT = ""
    
    @staticmethod
    def bf_complexity(t): return t ** 2
    @staticmethod
    def opt_complexity(t): return t
    
    def _run_naive(self): ...      # override with naive animation
    def _run_optimized(self): ...  # override with optimized animation
```

**Key methods:**
- `play_act1_cold_open()` — builds 3D data space (axes + solids + labels)
- `play_act2_brute()` — naive code panel + particle + synced highlight
- `play_act3_insight()` — hinge text beat
- `play_act4_optimized()` — idiomatic code panel + clean trail
- `play_act5_payoff()` — 2D complexity graph with true curves

### 2. Scene Generator (`scripts/generate_scenes.py`)

Reads `references/tricks.yaml` and generates all scene files with:
- Correct class structure inheriting `TrickScene`
- Safe code line iteration using `.code_lines.submobjects`
- Static methods for complexity functions (avoids bound-method bug)
- Bounded line highlighting with `min(n, max_lines)`

### 3. Config Format (`references/tricks.yaml`)

```yaml
tricks:
  - id: "01"
    name: "Name Mangling"
    title: "Python Name Mangling"
    solid_type: "spheres"
    input_data: ["_internal", "__mangled", "public"]
    insight_text: "Double underscore mangles to _ClassName__attr..."
    naive_code: "..."
    idiomatic_code: "..."
    bf_complexity: "lambda t: t"
    opt_complexity: "lambda t: t"
    naive_lines: 8
    opt_lines: 8
```

## dsa-java-gradleqa variant (83-scene Java DSA pipeline)

This skill's Python-tricks batch is one consumer; the repo `dbillion/dsa-java-gradleqa`
(40 interview questions + 20+ algorithms = 83 scenes) is another. The 83-scene pipeline
has its OWN `dsa_style.py` (NOT `base_template.py`) and a different failure profile.
Load-bearing USER WORKFLOW RULES for that repo:

1. **NEVER unilaterally stop/restart a running background render.** User: "don't stop anything."
   Let a run finish, then do a separate pass. Ask before killing a render.
2. **Test for conflict before push:** `git fetch` + `git rev-list --left-right --count <b>...origin/<b>`
   → `(0 0)` = fast-forward, safe. Confirm BEFORE commit/push.
3. **Push only on explicit "push"** (verbal "yes push" / "commit and pish"). No auto-push.
4. **Build with placeholders, then prove:** emit a "🎬 GIF pending" row, validate (0 broken
   links, balanced HTML), THEN fill. Don't block the deliverable on stragglers.
5. **Missing ≠ deleted:** a short count (e.g. "only 70 gifs") is a *generation gap*, not a
   deletion. Re-render writes only `final_videos/`, never `gifs/` — it cannot remove GIFs.
   Verify on disk + `scenes/media` before assuming loss.
6. **Separate-folder re-render:** write re-renders to `final_videos_v2/` so originals survive
   unless the user explicitly accepts overwrite.

FAILURE MODE A — batch prints `done=0 fail=83` but animations ran to 100%: the loop checks
for the produced mp4 by the FINAL name (`final_videos/Q03_TwoSum.mp4`) but Manim writes it by
the SCENE CLASS name (`scenes/media/videos/q03_two_sum/480p15/TwoSumBruteVsOptimized.mp4`).
File-check fails → FAIL, and an `os.remove(dst)`-first loop WIPES final_videos. Recover with
`scripts/restore_final_videos.py` (see `references/render_recovery.md`).

FAILURE MODE B — "83" is the SCENE count, not the GIF count. GIFs are built in batches;
missing ones were never giffed (name-match gaps), not deleted. Generate from
`scenes/media/.../<SceneClass>.mp4` via `scripts/make_gifs_from_media.py`. GIF names are
INCONSISTENT (`Q03_TwoSum`, `A04_HeapSort`, `FloodFill`, `Astar`) — map via
`_render_map_full.json` `final`, never guess.

README embed (GitHub constraint): markdown tables can't hold fenced code or a full-width
image, so each question is an HTML table — Row1 Topic|Diagram|Question; Row2 Function
(`<pre><code>`) | Unit test (`<pre><code>` colspan=2); Row3 `<img colspan=3 width=100%>`.
Mermaid doesn't render in cells — use existing `docs/diagrams/*.png` (S/graph-extras have
NONE → render `—`). Validate 0 broken gif/diagram refs, balanced tags. See
`references/readme_explainer_tables.md`.

## When the repo has its OWN style module

If the target project already ships `dsa_style.py` / `shapes3d.py` /
`graph_tree_style.py` and a `SCENE_CONVENTIONS.md`, do NOT use
`templates/base_template.py` — write plain scene files importing the repo's
helpers, and follow the repo's conventions exactly. See
`references/repo_style_batch_authoring.md` for the full workflow and its
pitfalls (out-of-range `code_lines[]` after trimming a CODE block, `abs()` in
`make_cube_row` breaking on char data, verbatim-source trimming rules, LSP
star-import noise, and the reporting shape).

Verification: run `scripts/check_code_line_indices.py <scenes_dir>` after ANY
edit to a CODE string, then `ast.parse` each file. `ast.parse` alone does not
catch a highlight index that points past the end of the code panel.

## Critical Debugging Fixes (Embedded in Template)

### 1. Code Mobject Line Access
**Problem**: `Code.code_lines` is a `Paragraph`, not a list. Lines are in `.code_lines.submobjects`.
**Fix**: Always use `self.bf_code.code_lines.submobjects` for iteration.

### 2. Lambda as Class Attribute → Bound Method
**Problem**: `BF_COMPLEXITY = lambda x: x` becomes a bound method receiving `self` as first arg.
**Fix**: Use `@staticmethod`:
```python
@staticmethod
def bf_complexity(t): return t ** 2
```

### 3. Axes.plot Function Signature
**Problem**: `Axes.plot(fn)` calls `fn(t)` with parameter `t`, not `x`.
**Fix**: Wrap complexity functions:
```python
lambda t: self.bf_complexity(t)
```

### 4. Safe Code Highlighting
**Problem**: IndexError when highlighting beyond available lines.
**Fix**: Bounded iteration:
```python
lines = self.bf_code.code_lines.submobjects
n = len(lines)
for i in range(min(n, max_lines)):
    self.play(self.bf_hl.animate.move_to(lines[i]), run_time=0.3)
```

### 5. Non-Numeric Data in 3D Axes
**Problem**: `max(abs(min(data)))` fails on string data.
**Fix**: Try/except fallback in `make_data_space()`:
```python
try:
    numeric_data = [float(d) for d in data]
    y_min, y_max = min(numeric_data)*1.2, max(numeric_data)*1.2
except (ValueError, TypeError):
    y_min, y_max = -2, 2
```

## Rendering Workflow

```bash
# Preview (480p15, fast)
manim -pql trick_XX_name.py TrickXXName

# Final (1080p60)
manim -pqh trick_XX_name.py TrickXXName

# Burn subtitles (reuse existing pipeline)
./burn_subs.sh out/TrickXX.mp4 out_sub/TrickXX.mp4
```

## File Structure

```
manim-dsa-video-pipeline/
├── SKILL.md
├── templates/
│   └── base_template.py          # TrickScene base class
├── scripts/
│   ├── generate_scenes.py        # Auto-generates all scene files
│   └── render_batch.sh           # Batch rendering script (TODO)
├── references/
│   ├── tricks.yaml               # All 23 trick configurations
│   ├── debugging_fixes.md        # This section expanded
│   └── solid_vocabulary.md       # 3D solid → data structure mapping
└── examples/
    └── trick_01_name_mangling.py # Example generated scene
```

## Quality Gates (Per manim-dsa-storytelling)

- [ ] Every `Text` in `ThreeDScene` uses `add_fixed_in_frame_mobjects()` BEFORE positioning
- [ ] Labels on 3D cubes use `rotate(90*DEGREES, axis=RIGHT)` to stand upright
- [ ] Camera/axes REUSED exactly between naive and optimized beats
- [ ] Insight beat NOT skipped
- [ ] Complexity graph uses TRUE functions (not hand-drawn curves)
- [ ] Code panels show REAL source (trimmed, not paraphrased)
- [ ] Synced `SurroundingRectangle` highlights track live line numbers

## Known Limitations

- Rendering on CPU-constrained environments (load avg 35+) takes 5-10 min/video at 480p15
- GPU machine recommended for 1080p60 final renders
- `torus` and `surface` solid types in `make_data_space()` not fully implemented
- Subtitle burning requires separate `burn_subs.sh` pipeline

## Example: Adding a New Trick

1. Add entry to `references/tricks.yaml`
2. Run `python scripts/generate_scenes.py`
3. Preview: `manim -pql trick_XX_new.py TrickXXNew`
4. Final: `manim -pqh trick_XX_new.py TrickXXNew`
5. Burn subs and deliver