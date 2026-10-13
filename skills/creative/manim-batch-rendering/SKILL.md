---
name: manim-batch-rendering
description: Render Manim video batches without the classic time-sinks.
---

# Manim Batch Rendering — avoiding the time-sinks

This skill captures the non-obvious pitfalls that turned a "render 23 videos" task into
a multi-hour debug loop, and the exact discipline that fixed it. It is renderer- and
skill-agnostic: works whether you drive scenes by hand, by the manim-dsa-storytelling
skill, or by any other Manim story format.

## NON-NEGOTIABLE: never `rm -rf media` between renders

The single biggest time-waster observed: wiping the media folder as a "clean start"
before each scene deletes every finished mp4, so the whole batch re-renders from
scratch repeatedly. Manim writes each scene to `media/videos/<scene_name>/480p15/`
(by default) — outputs ACCUMULATE per folder. Let them. The correct batch pattern:

- Each scene renders to its own folder; do not delete between scenes.
- Run the batch as a BACKGROUND process; check a progress log periodically.
- Do NOT use a foreground command with a short timeout — a 9-minute render gets
  killed at the 60s/600s cap and leaves no mp4.

## Pitfall 1 — Python 3.14 bound-method crash in complexity-graph payoff beats

Symptom: a scene that worked through Acts 1-4 crashes at the Act-5 complexity graph
with `TypeError: unsupported operand type(s) for /: '<SceneClass>' and 'float'`.

Root cause: In Python 3.14 a plain function assigned as a CLASS attribute
(`BF_COMPLEXITY = lin`, `OPT_COMPLEXITY = quad`) becomes a BOUND METHOD when accessed
on an instance. So `self.BF_COMPLEXITY` receives `self` (the Scene) as its first arg,
and Manim's `Axes.plot` evaluates `Scene / float` → crash. It is invisible until the
payoff beat actually plots, because Acts 1-4 never call the complexity function.

Also note: `lambda t: t` assigned at class level is STILL bound the same way, so
"make it a lambda" does NOT fix it.

FIX — pass the UNBOUND class attribute:
```python
bf = type(self).BF_COMPLEXITY    # unbound function (module fn), not self.BF_COMPLEXITY
opt = type(self).OPT_COMPLEXITY
complexity_payoff(self, bf, opt, "naive O(n^2)", "idiomatic O(n)")
```
Verify once (see references/python314-bound-method-complexity.md for the full repro
recipe): a debug scene should print `type(self).BF_COMPLEXITY is lin` → True and
`type(self).BF_COMPLEXITY(5)` → 5 (not the Scene).

## Pitfall 2 — wrong scene-class name from filename mangling

Symptom: the batch runs for minutes but writes no mp4 (or writes a junk one), and the
log shows manim invoked with a name like `Trick01NameMangling.Py` (note the `.Py`).

Root cause: deriving the scene class name by string-mangling the filename
(`basename`, `sed 's/_\([a-z]\)/\U\1/g'`, etc.) produces `.Py` / spacing artifacts.
Manim cannot find a class `Trick01NameMangling.Py`, so it renders nothing useful.

FIX — extract the class name FROM THE FILE, never from the filename:
```bash
cls=$(python -c "
import re, sys
src = open(sys.argv[1]).read()
m = re.search(r'class\s+(Trick\w+)\s*\(', src)
print(m.group(1) if m else 'TrickUNKNOWN')
" "$f")
```
Each scene file defines exactly one `class Trick...`, so this is robust.

## Pitfall 3 — migration of old scene files silently breaks

If you bulk-regenerate scene files (e.g. from a YAML/template), watch for:
- Old files importing a different base module (`from template import TrickScene`) than
  your current base (`from dsa_style import TrickScene`) — they won't get your fixes.
- Old files defining the wrong method names (`_run_naive` / `_run_optimized`) when the
  base class calls `run_naive` / `run_idiomatic` — the method is never invoked.
- Old files using `@staticmethod def bf_complexity(t): return t` instead of a module-level
  complexity helper — the staticmethod is exactly the bound-method bug from Pitfall 1.

A migrator that reads each old file's class attributes and rewrites a clean file (see
`scripts/migrate_scenes.py`) solves all three at once. After migrating, syntax-check
AND import-check every file before batching (see references/validation-checklist.md).

## Render command by hardware (see references/render-command-by-hardware.md)

- Local machine WITH a display (DISPLAY / WAYLAND_DISPLAY set): both Cairo and OpenGL
  work. On a weak iGPU (Intel HD 620), Cairo `-ql` was FASTER than OpenGL `-ql` in
  timed tests (less per-frame window-swap overhead), so prefer Cairo for batch work.
- Headless / automation shell with NO display env: OpenGL hangs or fails — use Cairo.
- `-ql` (480p15) is the right tier for a 2-core CPU. Reserve `-qh` for a final pass.

## Safe batch driver (scripts/safe_batch_render.sh)

Use the provided `scripts/safe_batch_render.sh`: derives class names from files, logs
`>>> DONE` / `>>> FAIL` per scene, continues on failure, accumulates mp4s. Run it
backgrounded. It is the antidote to every pitfall above.
