#!/usr/bin/env bash
# Parallel render of a batch of Manim scenes (cairo -ql, NO rm).
# Runs up to N concurrent manim renders (N=3 safe for a 4-thread i5).
# Copies REAL mp4 (not partial_movie_files) to final_videos/ with clean names.
# Resume-safe: skips scenes whose clean-named mp4 already exists.
#
# Usage: bash parallel_render.sh
# Requires _render_map.json in the same dir: { fileprefix: {scene, final} }
set -u
SCENES=/home/deeone/dsa-java-gradleqa/explainer_videos/scenes
FINAL=/home/deeone/dsa-java-gradleqa/explainer_videos/final_videos
N=3
LOG=/home/deeone/dsa-java-gradleqa/explainer_videos/render_new_parallel.log
rmap=/home/deeone/dsa-java-gradleqa/explainer_videos/_render_map.json
: > "$LOG"

/home/deeone/.local/share/uv/tools/manim/bin/python - "$SCENES" "$FINAL" "$rmap" "$LOG" <<'PY'
import json, os, sys, subprocess, shutil, threading, time

scenes, final, rmap, log = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
rmap = json.load(open(rmap))
N = 3
lock = threading.Lock()
done = 0; fail = 0

def worker(fp, scene, finalname):
    global done, fail
    dst = os.path.join(final, finalname)
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        with lock:
            open(log,"a").write(f">>> SKIP {fp} -> {finalname} (present)\n"); done += 1
        return
    with lock:
        open(log,"a").write(f">>> RENDER {fp} :: {scene}\n"); log_f = open(log,"a"); log_f.flush()
    cmd = ["python3","-m","manim","-ql","--renderer=cairo","--disable_caching",
           os.path.join(scenes, fp+".py"), scene]
    r = subprocess.run(cmd, cwd=scenes, capture_output=True, text=True)
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
            open(log,"a").write(f">>> FAIL {fp}: mp4 not at {cand}\n"); fail += 1

threads = []
for fp, info in rmap.items():
    while threading.active_count() - 1 >= N:
        time.sleep(1)
    t = threading.Thread(target=worker, args=(fp, info["scene"], info["final"]))
    t.start(); threads.append(t)
for t in threads: t.join()
open(log,"a").write(f">>> SUMMARY done={done} fail={fail} total={len(rmap)}\n")
print(f"PARALLEL RENDER DONE: done={done} fail={fail} total={len(rmap)}")
PY
echo "=== finished $(date) ===" >> "$LOG"
