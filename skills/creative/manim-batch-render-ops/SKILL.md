---
name: manim-batch-render-ops
description: Safe parallel batch-rendering of many Manim CE videos.
---

# Manim Batch Render Operations

Class-level operational skill for rendering MANY Manim CE scenes safely and fast.
Complements the content skills (manim-dsa-storytelling 5-act, manim-dsa-single-path
4-act, manim-dsa-video-batch) — this one owns the ORCHESTRATION and SAFETY layer, not
the scene-authoring template.

## When to use
- Rendering >=5 Manim CE scenes in one go (DSA explainers, Python-trick videos, course cuts).
- A batch is slow, looks hung, or you are about to `rm -rf media` and restart.
- You need to free CPU for another task while a render is running.
- A render crashes at a complexity-graph or payoff step with a TypeError mentioning a Scene class.

## Core safety rules (from hard-won corrections)
1. NEVER `rm -rf media` (or any task output) mid-task unless explicitly told. Accumulate
   renders in per-scene folders. Disk is cheap; restarting wastes hours. An agent once deleted
   21 already-rendered trick videos by rm -rf-ing between runs.
2. NEVER kill an in-flight render just to free CPU for another batch. Run BOTH batches at
   REDUCED parallelism (e.g. N=2 and N=3 on a 4-thread box) instead. Killing an incomplete
   render discards real work and violates "do not discard incomplete work." User correction:
   "you shouldnt have killed the python tricks, because it has not completed its rendering."
3. Verify from disk, not from claims. After a batch, run `ls final_videos/*.mp4 | wc -l`
   and check per-file byte sizes. A subagent saying "rendered successfully" is NOT proof — confirm
   the real .mp4 exists (NOT the partial_movie_files/ intermediate).

## Parallel orchestration (the right way to go fast)
Manim renders are single-threaded per scene. On a machine with T threads, run
N = floor(T * 0.75) concurrent renders (leave headroom for OS/other apps). For a 4-thread
i5-7200U: N=3.

Use a Python threading pool inside a bash wrapper (see scripts/parallel_render.sh):
- Reads a JSON map { "<fileprefix>": { "scene": "SceneClass", "final": "CleanName.mp4" } }.
- Per scene: `python3 -m manim -ql --renderer=cairo --disable_caching <file>.py <SceneClass>`.
- Skip if `final_videos/<CleanName>.mp4` already exists (>1KB) -> resume-safe across restarts.
- Copy only the real mp4: `scenes/media/videos/<fileprefix>/480p15/<SceneClass>.mp4`
  (NOT partial_movie_files/).
- Log `>>> DONE/FAIL/SKIP` per scene + a `>>> SUMMARY done=N fail=M total=K` line.

This pattern took a 23-video + 55-video dual batch from one-at-a-time serial to
3+2 concurrent and finished both without deleting anything.

## Python 3.14 plus Manim gotcha (CRITICAL)
In Python 3.14 a function assigned as a class attribute is BOUND when accessed via
`self.X`. So `self.BF_COMPLEXITY` returns the SCENE INSTANCE (not the function), and
`complexity_payoff(self.BF_COMPLEXITY, ...)` dies with:
`TypeError: unsupported operand type(s) for /: 'Trick01NameMangling' and 'float'`.

Fix: pass the unbound function via type(self):
```python
bf = type(self).BF_COMPLEXITY   # unbound -> callable(float)->float
opt = type(self).OPT_COMPLEXITY
self.complexity_payoff(bf, opt, ...)
```
Full detail plus the Cairo/OpenGL benchmark in references/manim_py314_and_renderer.md.

## Renderer choice on weak iGPU (ThinkPad T470 / Intel HD 620)
- Cairo -ql is FASTER than OpenGL on this class of hardware: trivial scene 8.8s (cairo)
  vs 15.2s (opengl) in timed tests. Use `--renderer=cairo -ql` for batch work.
- OpenGL only helps heavy true-3D; it also requires DISPLAY to be set. An earlier "OpenGL
  hangs" was a missing DISPLAY in an automation shell, NOT hardware — OpenGL runs fine when
  DISPLAY is exported. Do not assume OpenGL is broken on this box.
- Do not use -qh for the first pass; reserve high-quality for a final pass elsewhere if needed.

## Identifying a mystery high-RAM process BEFORE killing
When load is high and a render is slow, find what is competing:
```bash
ps -eo pid,ppid,etime,rss,args | grep -i java | grep -v grep   # rss in KB; /1024 ~ GB
```
Then decide safety (full recipe in references/identify_process.md):
- System service? `systemctl list-units --all | grep -i <name>`; package-owned? `pacman -Qo <bin>`.
- Serving anything? `ss -ltnp | grep <port>` -> closed port = idle.
- Parent chain: `ps -p <ppid> -o args`. If launched manually (not a tracked unit),
  `systemctl stop` will not apply; `kill -TERM <pid>` then `kill -KILL` if needed.
- Confirm with the user before stopping a system-level service (shared-state change).
  Example: an idle Elasticsearch (PID 14713, 2.9 GB, port 9200 closed, not the user's project)
  was safe to stop; it freed RAM and dropped load average.

## Pitfalls
- Piping `manim ... 2>&1 | tail -5` makes ps briefly miss the renderer and the process can
  LOOK hung — check partial_movie_files/ for frame growth instead of assuming death.
- pgrep -P <batchpid> can return stale PIDs after the shell wraps; verify the real manim
  child via `pgrep -af "manim.*-ql"`.
- Deriving a scene class name from a filename with shell sed /\U is error-prone (one run
  produced `Trick01NameMangling.Py`). Extract the real class via regex `class (Trick\w+)\(`
  from the file instead.
- A batch script that computes class names inline often fails; use a Python one-liner to read
  the class def from the source file.

## References
- references/manim_py314_and_renderer.md — Py3.14 bound-method fix + Cairo/OpenGL benchmark.
- references/identify_process.md — full recipe to safely ID and stop a high-RAM process.
- scripts/parallel_render.sh — reusable N-way parallel render harness with resume-skip.
