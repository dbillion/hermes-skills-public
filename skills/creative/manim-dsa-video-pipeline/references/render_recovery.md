# Phase 2 render recovery (dsa-java-gradleqa)

## Symptom
A render loop reports `SUMMARY done=0 fail=83 skip=0` but the animations visibly ran to
100% in the log, and `scenes/media/videos/<base>/480p15/` contains a real `.mp4` per scene.
`final_videos/` is nearly empty (only 1 file, or 0) — i.e. the originals got wiped.

## Root cause
The loop computes the expected output path as:
```
produced = scenes/media/videos/<base>/480p15/<FINALNAME>.mp4
```
but Manim writes the file named after the SCENE CLASS, not the final name:
```
scenes/media/videos/q03_two_sum/480p15/TwoSumBruteVsOptimized.mp4   # class name
# NOT Q03_TwoSum.mp4
```
So `os.path.exists(produced)` is always False → every scene is marked FAIL. If the loop did
`os.remove(dst)` BEFORE rendering (to "always refresh"), it deleted the old final and never
copied the new one → `final_videos/` wiped.

## Recovery (no re-render needed)
Copy from `scenes/media` to `final_videos` with the correct FINAL name:
```python
import json, os, glob, shutil
BASE="explainer_videos"; rmap=json.load(open(f"{BASE}/_render_map_full.json"))
for base,info in rmap.items():
    scene, final = info["scene"], info["final"]
    prod = glob.glob(f"{BASE}/scenes/media/videos/{base}/480p15/{scene}.mp4")
    if not prod:
        prod = glob.glob(f"{BASE}/scenes/media/videos/{base}/480p15/{final[:-4]}.mp4")
    if prod:
        shutil.copy(prod[0], f"{BASE}/final_videos/{final}")
```
This restores all 83 mp4s. Run `scripts/restore_final_videos.py` for the ready-made version.

## Prevention (fix the loop)
Look up the produced file by SCENE CLASS name, not final name:
```python
produced = os.path.join(scenes, "media", "videos", base, "480p15", scene + ".mp4")
```
And do NOT `os.remove(dst)` up front — copy then replace, or only remove after a successful
copy. Also treat `rc=0` + missing file as a path bug to investigate, not a silent FAIL.

## Note on the readability fix
`dsa_style.test_panel()` scales were bumped (code font 14→18 / scale 0.34→0.46; expected
output scale 0.55→0.95). That fix only lands in renders produced AFTER the edit. If you
restore from old `scenes/media`, the GIFs reflect the OLD small panel. To get the readable
panel uniformly, do ONE clean full re-render pass after the path bug is fixed.
