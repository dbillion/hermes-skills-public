#!/usr/bin/env bash
# Reusable N-way parallel Manim batch render with resume-skip.
# Renders each scene in $RMAP (JSON: {"<fileprefix>": {"scene": "SceneClass", "final": "Clean.mp4"}}),
# copies the REAL mp4 (not partial_movie_files/) to $FINAL, skips if already present.
# NO rm. Verifies exit code + byte size per scene.
# Usage: N=3 SCENES=/path/to/scenes FINAL=/path/to/final_videos RMAP=/path/to/map.json bash parallel_render.sh
set -u
SCENES="${SCENES:-.}"
FINAL="${FINAL:-./final_videos}"
RMAP="${RMAP:-./_render_map.json}"
N="${N:-3}"
LOG="${LOG:-./render_parallel.log}"
: > "$LOG"

/home/deeone/.local/share/uv/tools/manim/bin/python - "$SCENES" "$FINAL" "$RMAP" "$LOG" "$N" <<'PY'
import json, os, sys, subprocess, shutil, threading, time
scenes, final, rmap, log, N = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
rmap = json.load(open(rmap))
lock = threading.Lock()
done = fail = skipped = 0

def worker(fp, scene, finalname):
    global done, fail, skipped
    fpath = os.path.join(scenes, fp + ".py")
    dst = os.path.join(final, finalname)
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        with lock:
            open(log,"a").write(f">>> SKIP {fp} -> {finalname}\n"); skipped += 1
        return
    if not os.path.exists(fpath):
        with lock:
            open(log,"a").write(f">>> MISSING {fp}\n"); fail += 1
        return
    with lock:
        open(log,"a").write(f">>> RENDER {fp} :: {scene}\n"); lock.acquire(); logf=open(log,"a")
    r = subprocess.run(["python3","-m","manim","-ql","--renderer=cairo","--disable_caching",
                        os.path.join(scenes, fp+".py"), scene], cwd=scenes,
                       capture_output=True, text=True)
    if r.returncode != 0:
        with lock:
            open(log,"a").write(f">>> FAIL {fp} rc={r.returncode}\n"+r.stderr[-600:]+"\n"); fail += 1
        return
    cand = os.path.join(scenes,"media","videos",fp,"480p15",scene+".mp4")
    if os.path.exists(cand):
        shutil.copy(cand, dst)
        with lock:
            open(log,"a").write(f">>> DONE {fp} -> {finalname} ({os.path.getsize(dst)} bytes)\n"); done += 1
    else:
        with lock:
            open(log,"a").write(f">>> FAIL {fp}: mp4 not found at {cand}\n"); fail += 1

threads = []
for fp, info in rmap.items():
    while threading.active_count() - 1 >= N:
        time.sleep(1)
    t = threading.Thread(target=worker, args=(fp, info["scene"], info["final"]))
    t.start(); threads.append(t)
for t in threads: t.join()
with open(log,"a") as L:
    L.write(f">>> SUMMARY done={done} fail={fail} skipped={skipped} total={len(rmap)}\n")
print(f"PARALLEL RENDER DONE: done={done} fail={fail} skipped={skipped} total={len(rmap)}")
PY
echo "=== finished $(date) ===" >> "$LOG"
