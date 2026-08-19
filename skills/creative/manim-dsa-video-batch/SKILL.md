---
name: manim-dsa-video-batch
description: Batch-produce DSA Manim explainer videos at scale.
---

# Manim DSA Video Batch — Orchestration

This skill is the **batch production layer** for DSA explainer videos. The
narrative *shape* (5-act brute-vs-optimized vs 4-act single-path) lives in the
companion skills `manim-dsa-storytelling` and `manim-dsa-single-path` — read
those for story structure. This skill covers everything AROUND the scenes:
pulling real data, fanning out generation, rendering at scale, and the
machine-specific pitfalls that brick a batch.

## HARD RULE (user correction — do not violate)
**NEVER use `rm -rf` during generation or rendering of a video batch.** The
user explicitly said: "except when told, dont use rm -rf for this task." A batch
render that wipes `media/` between scenes destroys already-finished videos and
forces re-renders. Instead:
- Render into per-scene output folders and ACCUMULATE.
- To re-render a single scene, let Manim overwrite that scene's own mp4 — do
  not delete the parent `media/` tree.
- If you must clear, target the specific scene subfolder, never `rm -rf media`.
This rule came from a session where repeated `rm -rf media` between renders
wiped 21/23 finished videos. Honor it strictly.

**NEVER TERMINATE A RUNNING RENDER BATCH to free CPU for another task.** A
second hard user correction: I killed the in-flight Python-tricks batch
(proc_59a4e075bf0b) with SIGTERM to give the DSA batch more cores — but the
tricks batch had only rendered 18/23, so 5 finished videos were stranded and
the user had to ask me to recover them. Lessons:
- A completed-on-disk count is NOT "done". A render batch is only done when its
  SUMMARY line shows all targets, or final_videos holds the expected total.
- If two batches compete for CPU, run BOTH at reduced parallelism (e.g. N=2 +
  N=3) rather than killing one. A 4-thread i5 tolerates ~5 concurrent manim
  renders if RAM allows; they just finish a bit slower, with zero lost work.
- Only stop a running batch if the USER explicitly says so, or it is confirmed
  hung (no child for >2x its normal per-scene time). When in doubt, ASK.
- Recovering a killed batch: the finished mp4s are safe on disk (no rm was
  used); just re-render the missing scenes via the resume-safe skip-logic
  (scene present in final_videos -> skipped). See scripts/parallel_render.sh.

## The data-integrity mandate
Every scene must animate the REPO'S REAL tested values, never invented ones.
- Source of truth: `<repo>/src/.../Algorithms.java` (method bodies) and
  `<repo>/src/test/.../AlgorithmsTest.java` (when present, the sample inputs).
- Extract each method body verbatim (balanced-brace scan) and the test's
  `assertEquals(...)` sample data. Feed BOTH to the generator.
- Skipping this produces "plausible but fake" videos — the HANDOFF forbids it.

## Scope the catalog correctly (don't over- or under-generate)
- Start from the repo's method count, subtract what's already in `final_videos/`.
- The skill explicitly says to SKIP trivial one-liners (bit tricks, single-line
  GCD/modPow, count-set-bits, isPowerOfTwo, reverseBits, etc.). Realistic
  remaining count is "somewhat under 68" for a ~96-method repo, not the raw
  method total. Don't force 67 trivial videos.
- Separate into 5-act (genuine brute-vs-optimized split: Two Sum, Kadane,
  KMP/Rabin-Karp, binary-vs-linear search) vs 4-act single-path (sorts,
  traversals, DP, data-structure mechanics). Only ~7 of 55 are true comparisons.

## Generation: fan out to parallel subagents (do NOT hand-write 55 files)
55 scene files is too large to write inline. Use delegate_task batches:
1. Write a `SCENE_CONVENTIONS.md` (read by every subagent) codifying the exact
   conventions of the existing scenes: `ThreeDScene`, `DARK_BG`, `fixed_title`,
   `set_camera_orientation(phi=65*DEGREES, theta=-60*DEGREES)`, `make_cube_row`,
   `code_panel` + `make_highlight` synced via `hl.animate.move_to(code.code_lines[i])`,
   and `add_fixed_in_frame_mobjects(mobj)` BEFORE positioning HUD text (else text
   lies flat on the 3D floor). Provide TWO example scenes (one single-path, one
   comparison) for them to mimic.
2. Extract a per-problem bundle JSON: `{test, source, test_sample, fileprefix,
   scenename, skill, shape}` and split into ~8-problem batches.
3. Dispatch ≤3 subagents concurrently (delegation.max_concurrent_children).
   Each subagent: reads conventions + its batch file, writes the scene files,
   then `ast.parse`-checks every file. Instruct: NO render calls, NO rm, do NOT
   modify shared style modules (dsa_style.py / shapes3d.py / graph_tree_style.py).
4. After all batches: run one consolidated `ast.parse` check across all 55.

## Additive 3D shapes (the "torus" extension)
`shapes3d.py` adds solids the base skill vocabulary declares but never
implemented. User decision was ADDITIVE — use them ONLY where the metaphor
genuinely fits, keep cubes for plain arrays/stacks:
- `make_ring` (Torus) → cycles, circular buffers, ring buffers
- `make_cylinder_queue` (Cylinder) → FIFO queues, stack containers, hash buckets
- `make_cone_pointer` (Cone) → current index / top-of-stack / node marker
- `make_min_heap_tree` (Cones) → heaps (root peak = extreme)
- `make_split_wedge` (prism wedge) → divide-and-conquer / binary-search cut
- `make_prism_grid` (prisms) → 2D DP tables (edit distance, knapsack, LCS)
Verify these at RUNTIME with a test render before the full batch — see
references/python314_bound_method.md.

## CRITICAL RENDERING BUG — Python 3.14 bound-method trap
If a scene passes a complexity function to `Axes.plot` / `complexity_payoff` and
crashes with `TypeError: unsupported operand type(s) for /: '<SceneClass>' and 'float'`,
the cause is: **a plain function assigned as a CLASS attribute becomes a BOUND
method in Python 3.14**. So `self.BF_COMPLEXITY` returns the Scene instance
(`self.BF_COMPLEXITY(5)` → `<SceneClass>`), and Manim does `Scene / float`.
FIX: pass the CLASS-level attribute, not the instance attribute:
    bf = type(self).BF_COMPLEXITY
    opt = type(self).OPT_COMPLEXITY
    complexity_payoff(self, bf, opt, "naive O(n²)", "optimized O(n)")
A module-level `lambda t, *_: t` ALSO binds — `type(self).BF_COMPLEXITY` is the
only robust fix. (This bit a whole batch before being found.) Full recipe in
references/python314_bound_method.md.

## Render at scale — run N parallel, not sequential
A single `manim` render uses ~1 CPU thread at 60%+. On a multi-core box, running
scenes one-at-a-time wastes cores. Use a worker pool:
- Safe parallelism for a 4-thread i5 (e.g. i5-7200U): **N=3** concurrent manim
  processes. N=4 risks thrashing if other heavy processes (Java/gradle, browser,
  IDE) are also running.
- Each worker: render with `python3 -m manim -ql --renderer=cairo
  --disable_caching <file>.py <SceneName>`, then copy the REAL mp4 from
  `scenes/media/videos/<prefix>/480p15/<SceneName>.mp4` into `final_videos/` with
  a clean name. NEVER copy from `partial_movie_files/`.
- Resume-safe: skip any scene whose clean-named mp4 already exists in
  final_videos (size > 1KB). This lets you kill + relaunch without rework.
- Log per-scene `>>> DONE` / `>>> FAIL` + verify exit code 0 AND byte size.
- Template script: scripts/parallel_render.sh. Conventions file:
  templates/scene_conventions.md (copy + adapt per repo).

## Renderer choice on THIS machine (ThinkPad T470, i5-7200U, Intel HD 620)
- OpenGL 4.6 works locally (DISPLAY=:1, Wayland) but on the weak iGPU, Cairo was
  FASTER in timed tests (8.8s vs 15.2s trivial). Use `--renderer=cairo -ql` for
  batches. `-qh` only for a final pass on a stronger machine.
- Foreground renders get killed at the ~600s tool cap — ALWAYS render via
  `terminal(background=true)` for anything multi-minute, and poll the process,
  never block synchronously.

## Verify-before-claiming-done (HANDOFF rule)
Do NOT report "all N done" from memory. After the batch: count real mp4s in
final_videos, confirm each target scene class rendered (exit 0 + file exists on
disk). Report the actual final count.

## "Verified by test" JUnit panel (user-requested, high educational value)
The user explicitly asked to END each video with the algorithm's real JUnit
`@Test` on screen — "not just how the algorithms work but how they are unit
tested." This is now part of the deliverable, not optional.

### Ground-truth via Gradle (don't parse assertions by hand)
- Run `./gradlew test` in the repo. It writes `build/test-results/test/*.xml`
  (per-test name, status PASS/FAIL, failure message). All 96 tests passing is
  the norm; capture the XML so each panel shows REAL expected output, not a
  guess. Running tests is READ-ONLY w.r.t. videos (writes only to gitignored
  `build/`).
- Parse the XML: `testcase` `name` attr is like `A3_quickSort()` — strip the
  trailing `()` to get the method key. Build `testName -> {status, expected}`.
- Derive the "expected output" caption from the assertion body with a
  balanced-brace scan (`assertArrayEquals(new Type[]{...}, x)` ->
  `[1,2,5,8,9]`; `assertEquals(9, x)` -> `9`; `assertTrue(...)` -> `true`).
  This is the REAL verified value — show it big in the panel.

### Panel design (what the user approved)
- A helper `test_panel(scene, test_code, expected_text)` renders: a "Verified
  by test (JUnit)" label, the real `@Test` body as a Code mobject (java,
  add_line_numbers), and a BIG expected-output line: `// -> <expected> (gradle
  test: PASS)`. The user said the raw assertion alone was "not visible enough" —
  so make the OUTPUT prominent (scale ~0.55, BOLD, centered low), not just the
  code.
- Append as the FINAL act, BEFORE the scene's teardown `FadeOut(...)`.
- `test_panel` returns 4 mobjects (label, code, out_label, value) — unpack all
  four and fade all four out at the end. (An earlier 3-mobject version broke
  when the helper signature grew.)

### Bulk-injecting the panel into all N scenes (pitfalls that cost a full session)
Don't hand-edit 83 files. Write ONE injector script, but AVOID these traps:
1. **Anchor indentation strip (silent runtime crash).** Inserting the act at
   `src[:last_match.start()]` (the `s` of `self.play(FadeOut(` ) DROPS the
   anchor line's leading whitespace, pushing it to column 0 -> `NameError: name
   'self' is not defined` at RUNTIME (ast.parse still passes, so a parse-only
   check misses it). FIX: insert at `line_start = src.rfind("\n", 0,
   last.start()) + 1` so the anchor keeps its indentation.
2. **Import-guard false positive.** A guard `if "test_panel" in src: skip
   adding import` fires because the INJECTED CALL `test_panel(self,...)` contains
   the substring -> the import is never added -> `NameError: name 'test_panel'
   is not defined` at runtime. FIX: guard on `re.search(r"test_panel\s*[),]",
   src)` (an import item, not the call) or check for `from dsa_style import
   test_panel`.
3. **Multi-line dsa_style imports.** Some scene files import as
   `from dsa_style import (A, B,\n C, D, test_panel)` (multiline). Adding
   `, test_panel)` to line 1 of that breaks it. FIX: always inject a SEPARATE
   standalone `from dsa_style import test_panel` line right after `from manim
   import *` (works for both single- and multi-line forms).
4. **Pre-existing broken scenes.** Subagents sometimes leave the final
   `self.play(FadeOut(axes)...)` teardown at column 0 (invalid Python). ast.parse
   hides it; runtime crashes. Before injecting, normalize: any column-0 line
   starting with `self.` -> re-indent to 8 spaces. (Do NOT re-indent the module
   docstring `"""` — that corrupts it.) Verify with a CHECK that counts column-0
   `self.` lines (should be 0), not just ast.parse.
5. **Render-test BEFORE the full batch.** Inject, then render 2-3 scenes
   (including one that had a multiline import and one that was originally
   broken) and confirm exit 0 + mp4 exists. Only then launch all 83.

Full injector + Gradle-XML->spec recipe: references/verified_by_test_panel.md.

## Combine all videos into one showcase (brilliance-style)
The user wanted the generated samples combined into ONE video "like the
manim-brilliance-skill" combine. Method:
- Collect only REAL final mp4s (exclude `partial_movie_files/` and `uncached_*`).
- All DSA/scenes renders are 854x480 @ 15fps -> direct `ffmpeg -f concat
  -safe 0 -i list.txt -c copy` (lossless, fast, no re-encode).
- Prepend a 2s title card: `ffmpeg -f lavfi -i "color=c=0x0e0f12:s=854x480:d=2:r=15"
  -vf "drawtext=..."`.
- For an "1080p" deliverable, UPSCALE the combined 480p video with ffmpeg scale
  (native 1080p render of 83 scenes = days on a 4-thread iGPU; upscale is the
  pragmatic path). State this clearly to the user.
- 1080p GIFs of 83 videos balloon a git repo -> use git-lfs or a Release, and
  prefer 480p for commit (user accepted this tradeoff).

## Code-panel fidelity audit (the quicksort trap)
Subagents often "use real code" but quietly render only the PUBLIC WRAPPER and
animate a SIMPLIFIED algorithm — so the video says "quickSort" without showing
`partition()`. This violates the data-integrity mandate and the user WILL catch
it. Mitigate:
1. **Audit every generated scene's `CODE` block BEFORE rendering** with
   `scripts/audit_stubs.py` (flags stub / wrapper-only / truncated code panels).
   It scans all `*.py` in a scenes dir and reports any `CODE = """..."""` that is
   <=2 lines, or a single `public static X f(Y y) { f(y,0,n); }` wrapper. Full
   recipe + the quicksort fix in references/code_panel_fidelity.md.
2. **For comparison/algorithm scenes, the code panel MUST contain the REAL
   recursive/helper bodies**, not just the entry wrapper. If `partition`,
   `merge`, `helper`, `dfs` etc. exist in the source, they must appear.
3. **Animation must match the rendered code AND its final on-screen state must
   match the caption.** Two DISTINCT defects hide here (BOTH happened on
   quicksort in one session):
   - (a) The walkthrough replays a DIFFERENT algorithm than the code panel shows
     (e.g. a simplified pivot-last loop instead of the real Lomuto `partition()`).
   - (b) The animation only runs PART of the algorithm, so the visible elements
     DON'T end in the arrangement the payoff text claims. The first quicksort fix
     showed real code but ran only ONE partition → cubes ended `[5,2,8,1,9]`
     while the caption said `[1,2,5,8,9]`. The user caught it: "i thought the
     final solution will be the arrangement... the animation differs."
   RULE: if the result text states a final arrangement (sorted list, found
   index, computed DP value), the animation MUST run to completion so the visible
   elements actually reach that state. For quicksort that means the FULL
   recursive sort, not one partition. Verify by tracing the animation logic on
   the real sample: the final positions/order must equal the claimed output.
4. After fixing a scene that was ALREADY copied to final_videos, re-render just
   that file and `cp -f` the new mp4 over the old one (the parallel batch's
   skip-logic will NOT re-copy it because the stale file already passes the
   size check).

## References
- references/python314_bound_method.md — full traceback + fix recipe.
- references/extract_real_data.md — balanced-brace Java extraction snippet.
- references/code_panel_fidelity.md — the quicksort trap: stub code panels +
  simplified-animation defect, with the real-source fix recipe.
- references/verified_by_test_panel.md — Gradle-XML ground truth + bulk
  injector with the anchor-indent / import-guard / multiline-import pitfalls.
- scripts/parallel_render.sh — N-parallel render+copy harness.
- scripts/audit_stubs.py — scan scenes for stub/wrapper-only CODE panels
  (run BEFORE the batch; catches the quicksort trap automatically).
- templates/scene_conventions.md — conventions file to drop into a repo.
