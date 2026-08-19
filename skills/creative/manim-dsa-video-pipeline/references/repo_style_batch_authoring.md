# Authoring a batch of scenes against a REPO's own style module

Some projects (e.g. `dsa-java-gradleqa/explainer_videos/`) already ship their own
`dsa_style.py` / `shapes3d.py` / `graph_tree_style.py` plus a
`SCENE_CONVENTIONS.md`. In that case do NOT use this skill's `base_template.py`
— generate plain scene files that import the repo's helpers. The 5-act /
4-act structure still applies; only the plumbing differs.

## Workflow that worked (7 scenes, one pass, zero syntax failures)

1. Read the repo's `SCENE_CONVENTIONS.md` **and** the two example scenes it
   names (one single-path, one comparison) **and** every style module, in ONE
   batched set of `read_file` calls. The examples are the spec; the doc is the
   summary.
2. Read the batch spec file listing each problem's filename prefix, class name,
   act shape, assigned 3D shape, real source, and real test values.
3. Write scenes 2-3 at a time in batched `write_file` calls.
4. Run the index audit script (below), fix, then `ast.parse` every file.

## Pitfall: code_lines index must be < the CODE string's line count

The single most common defect. `make_highlight(self, code, i, color)` and
`hl.animate.move_to(code.code_lines[i])` index into the CODE panel. If you
first draft a long CODE block, then trim it down to the verbatim snippet the
batch file actually specifies, every index you wrote silently goes out of
range — and `ast.parse` will NOT catch it. It only blows up at render time.

Fix: after any CODE-block edit, re-derive the indices. Run
`scripts/check_code_line_indices.py` over the scene directory.

## Pitfall: trimming code panels vs. inventing helper bodies

When a batch file's "REAL SOURCE" block contains only the public wrapper
(e.g. `subsets()` calling `backtrackSubsets(...)` whose body is not given),
keep the panel strictly verbatim to that block. Do NOT write a plausible
helper body to have more lines to highlight — that violates the "real code,
never invent" rule. Drive the animation from the visual structure (recursion
tree, board, interval tree) instead, and point the highlight at the wrapper's
few real lines.

## Pitfall: `make_cube_row` on string/char data

`dsa_style.make_cube_row` computes `max(abs(v) * height_scale, min_height)`,
so `abs()` is called on every value — passing a list of characters raises
`TypeError`. For string problems (KMP, Rabin-Karp) pass codepoints and render
the char via `label_fn`:

```python
cubes, labels = make_cube_row(axes, [ord(c) for c in text],
                              height_scale=0.0, min_height=0.4,
                              label_fn=lambda v: chr(v))
```

`height_scale=0.0` + a `min_height` gives a flat, uniform char row, which is
what a text-scan animation wants.

## Pitfall: comparison scenes need module-level plain functions

`complexity_payoff(scene, bf_fn, opt_fn, ...)` — define `def bf(x): ...` and
`def opt(x): ...` at module level and pass them by name. Do not pass bound
methods (`self.bf`); do not define them as class attributes (they become
bound methods and receive `self` as the first arg).

## Noise to ignore

Pyright / LSP reporting `Import "manim" could not be resolved` and a cascade
of `"Write" is not defined` for every star-imported name is editor-environment
noise when manim isn't in the LSP's interpreter. It is not a code defect.
Judge the files by `ast.parse` plus the index audit, and say so explicitly in
the report rather than "fixing" the star import.

## Reporting shape the user wanted

A table of file / class / act shape / syntax status, then a short
"conventions followed" list, then an explicit "notes / issues" section calling
out any deviation (e.g. verbatim-source trimming, the `ord()` workaround) and
any tool noise. Do not bury a deviation in prose.
