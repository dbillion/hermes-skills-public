---
name: manim-video-render-ops
description: "Manim pitfalls: bound-fn crash, rm-rf trap, cairo vs opengl."
---

# Manim Video Render Ops

This skill is about the *operational* layer of producing Manim videos — the part
that quietly eats entire sessions if you get it wrong. The animation/API knowledge
lives in manim-explainer-animations and manim-dsa-storytelling; this skill is the
"don't shoot yourself in the foot while rendering 20 scenes" checklist.

## 1. The #1 time-sink: `rm -rf media` between renders

Manim writes each scene to its OWN folder:
`media/videos/<scene_file_stem>/<quality>/<SceneName>.mp4`
(e.g. `media/videos/trick_01_name_mangling/480p15/Trick01NameMangling.mp4`).
Renders accumulate safely — there is NO need to clear anything between scenes.

Running `rm -rf media` (or `rm -rf media/videos`) before each render WIPES every
finished video, so you re-render everything and never accumulate. This has burned
real sessions where only 2 of 23 videos survived because each new render deleted the
previous 21.

RULE: never `rm -rf media`. To re-render ONE scene, run `manim` for just that file —
its folder is overwritten in place, siblings are untouched. If you must clear, target
`media/videos/<that_one_scene>/` only.

## 2. Foreground timeout kills mid-render — background your batches

A 480p15 scene on a 2–4 core laptop takes ~5–10 min. The foreground tool
`timeout` is 600s and KILLS the render process mid-way, leaving no final mp4 (only
`partial_movie_files/`). Symptoms: a render "ran" for 600s then vanished.

RULE: launch multi-minute renders as a BACKGROUND process (notify_on_complete=true)
and poll a log file. Verify completion from DISK, not from a "I ran it" memory:
`find media -name '*.mp4' ! -path '*partial_movie_files*' | sort`

A safe batch driver (no rm, accumulates, continues on failure, logs per scene):
```bash
#!/usr/bin/env bash
cd /home/deeone/manim-dsa/videos/tricks/redo   # adapt to your dir
LOG=batch_progress.log; : > "$LOG"
for f in trick_*.py; do
  cls=$(python3 -c "import re,sys; s=sys.argv[1]; m=re.match(r'trick_(\d+)_(.+)',s); \
    print('Trick'+m.group(1)+re.sub(r'_',' ',m.group(2)).title().replace(' ',''))" "$f")
  t0=$(date +%s)
  manim --renderer=cairo -ql "$f" "$cls" >> "$LOG" 2>&1
  rc=$?; t1=$(date +%s)
  if [ $rc -eq 0 ] && [ -f "media/videos/${f%.py}/480p15/${cls}.mp4" ]; then
    echo ">>> DONE $f ($cls) rc=$rc elapsed=$((t1-t0))s" | tee -a "$LOG"
  else
    echo ">>> FAIL $f ($cls) rc=$rc elapsed=$((t1-t0))s" | tee -a "$LOG"
  fi
done
echo ">>> ALL DONE" | tee -a "$LOG"
```

## 3. Renderer choice: Cairo vs OpenGL + the display-context trap

- `--renderer=opengl` needs a live display: `$DISPLAY` (X11) or `$WAYLAND_DISPLAY`
  must be set in the shell running manim. In a headless automation shell those are
  often UNSET, so OpenGL hangs or errors even on a machine with a real GPU.
  FIX: run from an interactive shell that has the display vars, or fall back to Cairo.
- `--renderer=cairo` ALWAYS works (CPU rasterization). On a weak iGPU (Intel HD 620
  class) Cairo is frequently FASTER than OpenGL for these scenes because OpenGL pays
  per-frame window-swap/context overhead that only pays off on heavy 3D or strong GPUs.
- Quality: `-ql` (480p15) is correct for a 2–4 core CPU. `-qh`/`-pqh` (1080p60) is
  minutes-per-frame here — reserve it for a final pass on a stronger machine, or for
  small scenes.

Detect display quickly:
```bash
echo "DISPLAY=$DISPLAY WAYLAND_DISPLAY=$WAYLAND_DISPLAY"
which inxi >/dev/null && inxi -Fxz   # real CPU/GPU/RAM/display facts
```
Verify OpenGL actually works locally before committing to it:
```bash
cat > /tmp/smoke.py <<'EOF'
from manim import *
class Smoke(Scene):
    def construct(self):
        self.add(Circle().set_color(RED)); self.wait(0.2)
EOF
manim --renderer=opengl -ql /tmp/smoke.py Smoke 2>&1 | tail -3
ls -lh /tmp/media/videos/smoke/480p15/Smoke.mp4 2>/dev/null && echo OPENGL_OK
```

## 4. Python 3.14 pitfall: class-attribute function binding crashes Axes.plot

`Axes.plot(fn, x_range=...)` calls `fn(x)` with ONE argument. But if `fn` is stored
as a CLASS ATTRIBUTE and you pass the INSTANCE attribute, Python 3.14 binds it as a
method → `fn(x)` actually runs `fn(self, x)` and RETURNS THE SCENE INSTANCE. manim
then does `Scene / float` and dies at the complexity-graph payoff beat:

```
TypeError: unsupported operand type(s) for /: 'MyScene' and 'float'
  ... number_line.py:391 in number_to_point
  ... scale.py:123 in inverse_function -> return value / self.scale_factor
```

This is invisible until the LAST beat (the graph), so a scene that "looks fine" through
acts 1–4 crashes right at the end. Both forms bind:
```python
class MyScene(TrickScene):
    BF_COMPLEXITY = lambda t: t ** 2          # lambda -> bound method on instance
    BF_COMPLEXITY = lin                         # module-level def -> ALSO bound via self.BF_COMPLEXITY
    # self.BF_COMPLEXITY(5)  -> returns self (the Scene), not 25
```

FIX — pass the UNBOUND class attribute, not the instance attribute:
```python
# in the base-class payoff method:
bf = type(self).BF_COMPLEXITY      # unbound function via class-dict lookup
opt = type(self).OPT_COMPLEXITY
complexity_payoff(self, bf, opt, "naive O(n^2)", "idiomatic O(n)")
```
Alternative: wrap with a fresh closure (a new function object is not bound to the
Scene): `complexity_payoff(self, lambda x: self.BF_COMPLEXITY(x), ...)`.

Cheap pre-render verification (no full render needed):
```python
import dsa_style as s
print(type(self).BF_COMPLEXITY is s.lin)   # expect True
print(type(self).BF_COMPLEXITY(5))          # expect 25, NOT the Scene class
```
If the second line prints the Scene name, you have the bug.

## 5. Code.code_lines is a Paragraph — index .submobjects

`Code(code_string=..., add_line_numbers=True).code_lines` is a `manim Paragraph`
object, NOT a list. `code.code_lines[i]` raises `IndexError`. Index the submobjects:
```python
hl = SurroundingRectangle(code.code_lines.submobjects[line_idx], color=..., buff=0.05)
self.play(hl.animate.move_to(code.code_lines.submobjects[i]))
```
Guard with `code.code_lines.submobjects[min(idx, len(code.code_lines.submobjects)-1)]`
when line counts are uncertain.

## 6. Bulk-migrate scene files with ast, don't hand-edit

When you must change a base class API across 20+ scene files (rename `_run_naive`
-> `run_naive`, swap `from template` -> `from dsa_style`, replace `@staticmethod
bf_complexity` with module-level `lin`), write a one-shot migrator instead of editing
each file:
```python
import ast, os, re
for f in sorted(glob.glob('trick_*.py')):
    tree = ast.parse(open(f).read())
    # extract class attrs (ast.literal_eval Constant/List/Dict/Tuple; skip lambdas)
    # re-emit a clean file; write to .new, ast.parse it, then os.replace if OK
```
Pitfalls when regenerating: (a) don't wrap code strings in triple-quotes if the code
contains `"""` — use `{code!r}` (repr) for the assignment; (b) strip the `.py` suffix
BEFORE deriving the class name or you get `Trick01NameMangling.Py`; (c) after, run a
syntax+grep audit: `from template import` gone, no `_run_naive`, no `BF_COMPLEXITY =
lambda`, then `importlib.import_module` each file to confirm the scene class loads.

## Pre-flight checklist for a batch render
1. No `rm -rf media` anywhere in the driver.
2. Driver runs in background; logs DONE/FAIL per scene; continues on failure.
3. `find media -name '*.mp4' ! -path '*partial_movie_files*'` to verify, not memory.
4. If using a complexity graph: `type(self).BF_COMPLEXITY(5)` returns a number, not the Scene.
5. `Code` highlights use `.code_lines.submobjects[i]`.
6. Renderer: Cairo if no display context; `-ql` on 2–4 cores.
