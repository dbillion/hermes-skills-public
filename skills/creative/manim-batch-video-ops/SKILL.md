---
name: manim-batch-video-ops
description: Batch Manim CE scene generation and rendering mechanics.
---

# Manim Batch Video Ops

The narrative *format* (5-act brute-vs-optimized, 4-act single-path, 3D-solid
vocabulary, code-duality) lives in `manim-dsa-storytelling` /
`manim-dsa-single-path`. This skill covers the **operational mechanics** that
break batch jobs: deletion of good work, class-name mismatches, the Python 3.14
bound-method crash, and renderer/machine mismatch. Read those skills for story
shape; read this for the plumbing.

## 0. The no-delete rule (user correction — HARD)
Never run `rm -rf media` (or any bulk delete of the render tree) as part of a
batch loop or "to start fresh." Each scene renders into its own folder and
**accumulates**; deleting wipes finished videos and forces re-renders
(9+ min each on a weak laptop). The user explicitly called this out:
"why do you run rm -rf? you delete everything and restart again, wasting time."
- Render scripts: NO `rm`. Accumulate. Log per scene.
- If you must clear a single scene's partial state, target that scene's folder
  only, never the whole tree, and never while other renders depend on it.

## 1. Batch render scaffold (safe)
A correct batch loop looks like this (see `references/batch_render_template.sh`):
- No `rm -rf`.
- Derive the scene **class name from the file**, not from a sed/guess:
  `re.search(r'class\s+(Trick\w+|[A-Z]\w+Walkthrough\w*)\s*\(', src)`.
  Never compute it from the filename stem — that produced
  `Trick01NameMangling.Py` (with the `.Py` suffix) which Manim can't find,
  containing a broken class name and silently yielding invalid renders.
- `manim --renderer=cairo -ql FILE.py ClassName >> LOG 2>&1`
- Check `rc==0` AND that `media/videos/<stem>/480p15/<ClassName>.mp4` exists
  (NOT `partial_movie_files/`) before declaring DONE.
- Echo `>>> DONE <file> rc=.. size=..` / `>>> FAIL` lines so the run is
  auditable from the log.

## 2. Python 3.14 bound-method bug (the #1 silent crash)
**Symptom**: `TypeError: unsupported operand type(s) for /: 'MyScene' and 'float'`
thrown deep in `scale.py:123 return value / self.scale_factor` during an
`Axes.plot(...)` / complexity-graph payoff — usually at the LAST act.
**Root cause**: a plain function assigned as a class attribute becomes a
**bound method** when accessed on an instance in Python 3.14. If a base-class
helper does `complexity_payoff(self, self.BF_COMPLEXITY, ...)`, then
`self.BF_COMPLEXITY` is a bound method — calling it as `function(t)` actually
invokes `lin(self, t)`, returning the Scene, which then flows into arithmetic.
Confirm with: `type(self).BF_COMPLEXITY is s.lin` → **False** when broken
(instance access wraps it); `type(self).BF_COMPLEXITY` is the raw function.
**Fix**: pass the **class-level** (unbound) attribute:
`bf = type(self).BF_COMPLEXITY; opt = type(self).OPT_COMPLEXITY` then call
`complexity_payoff(self, bf, opt, ...)`.
Also: `Axes.plot(func, x_range=...)` calls `func(t)` with exactly ONE arg, so
the helper must accept a single positional arg (e.g. `def quad(t, *_): return t**2`
— the `*_` absorbs the stray 2nd arg some Manim versions pass). See
`references/python314_bound_method_bug.md` for the full repro + verification.

## 3. Renderer choice on a weak laptop iGPU
On a ThinkPad T470 (i5-7200U, 2c/4t, Intel HD 620, 32GB RAM, Wayland,
`DISPLAY=:1`):
- `manim --renderer=cairo -ql` is the batch default. Measured: Cairo 8.8s vs
  OpenGL 15.2s for a trivial scene; for our 3D scenes (axes + cubes + particles
  + two Code panels) Cairo is comparable or faster because the HD 620 pays
  per-frame window-swap overhead on OpenGL.
- OpenGL 4.6 direct-render WORKS in an **interactive terminal** (DISPLAY set),
  but a headless automation/background shell that doesn't inherit DISPLAY will
  hang/fail. So OpenGL is fine for manual `-pqh` final passes in your terminal,
  not for automated batch runs.
- `-ql` (480p15) for the whole batch; reserve `-qh` for a final pass on a
  stronger machine or locally when you have GPU time.
See `references/t470_render_profile.md`.

## 4. Parallel generation via subagents (large N)
For 30+ scenes, don't hand-write them in the main session — token cost explodes.
1. Extract REAL source + REAL test samples from the source repo
   (`grep`/`ast`-style extraction; never invent sample values — the HANDOFF for
   dsa-java-gradleqa mandates pulling sample inputs from the test file).
2. Write a `SCENE_CONVENTIONS.md` capturing the exact style (palette, camera
   `phi=65*DEGREES theta=-60*DEGREES`, `make_cube_row`, `code_panel`,
   `make_highlight`, `add_fixed_in_frame_mobjects` for HUD text, the 5-act vs
   4-act shape). Subagents MUST read the existing example scenes first.
3. Chunk into batches of ~8; each chunk ≤3 concurrent `delegate_task` leaf
   subagents. Each gets its problems' real source/samples + the conventions file
   + the rule: write files, syntax-check with `ast.parse`, **do NOT render**,
   **do NOT rm**, **do NOT modify shared modules**.
4. After all subagents return, you syntax-check the union, then batch-render
   (see §1).

## 5. Migrating old scene files to a new base class
When a base class changes method names / complexity-helper style, an
auto-migrator is far safer than hand-edits. Pattern:
- Extract each old file's class attributes via `ast` (TITLE, INPUT_DATA,
  INSIGHT_TEXT, NAIVE_CODE, IDIOMATIC_CODE, and `@staticmethod bf_complexity`).
- Rewrite with correct imports (`from dsa_style import TrickScene, lin, quad,
  cubic, const_mult`), correct method names (`run_naive`/`run_idiomatic`, NOT
  `_run_naive`/`_run_optimized`), and module-level complexity helpers
  (`BF_COMPLEXITY = lin`, NOT a `@staticmethod` or a class-level `lambda` — see §2).
- Write to a `.new` temp, `ast.parse` it, then `os.replace`. Skip files that
  fail to parse. Map `@staticmethod bf_complexity` bodies to helpers:
  `return t`→`lin`, `return t**2`→`quad`, `return t*N`→`const_mult(N)`.
- Verify ALL migrated files import cleanly (`importlib.import_module` each,
  confirm the scene class is exposed) before rendering.

## 6. Pitfalls checklist
- [ ] No `rm -rf media` anywhere in the loop.
- [ ] Scene class name derived from `class (X)` in the file, not the filename.
- [ ] Complexity helpers passed as `type(self).ATTR` (unbound), not `self.ATTR`.
- [ ] Complexity helper accepts one positional arg (`def f(t, *_)`).
- [ ] HUD text wrapped in `add_fixed_in_frame_mobjects` BEFORE positioning;
     value labels on 3D objects rotated upright instead.
- [ ] Final `.mp4` taken from `media/videos/<stem>/480p15/`, not
      `partial_movie_files/`.
- [ ] Verify exit codes + file existence on disk before claiming "all done"
      (the dsa-java HANDOFF calls out under/over-stated completion reports).
