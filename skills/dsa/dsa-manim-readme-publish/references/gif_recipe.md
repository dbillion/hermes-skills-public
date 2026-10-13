# GIF generation recipe (480p, git-friendly)

From an mp4 (raw render `scenes/media/videos/<base>/480p15/<SceneClass>.mp4`
OR the renamed final `final_videos/<GifName>.mp4`) → `explainer_videos/gifs/<GifName>.gif`.

ffmpeg palette method (small, smooth, GitHub-renderable). ~15 fps, 854x480.

```python
import os, subprocess
W, H = 854, 480
def make_gif(mp4, gif):
    if os.path.exists(gif): return "skip"
    pal = "/tmp/pal.png"
    subprocess.run(["ffmpeg","-y","-i",mp4,
        "-vf",f"fps=15,scale={W}:{H}:flags=lanczos,palettegen",pal],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    r = subprocess.run(["ffmpeg","-y","-i",mp4,"-i",pal,
        "-lavfi",f"fps=15,scale={W}:{H}:flags=lanczos[x];[x][1:v]paletteuse",gif],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(pal)
    return "ok" if (r.returncode==0 and os.path.exists(gif)) else "FAIL"
```

Run for a batch in the background (13+ gifs exceed the 60s foreground timeout):
```bash
python3 - <<'PY'  # ...loop make_gif over the 13 missing... ; print total
PY
```
Then `ls explainer_videos/gifs/*.gif | wc -l` should reach 83.

## Notes
- 70 of 83 gifs is normal mid-pipeline; the "missing" 13 are usually just
  un-giffed scenes (find their raw mp4 under `scenes/media/`), NOT deleted files.
  Verify on disk before assuming loss.
- GIF sizes: 100K–4M each; 83 ≈ 130M+. Commit via Git LFS (see SKILL.md).
- Phase-2 re-render writes only `final_videos/`; `gifs/` is untouched, so you can
  gif at any time without disturbing the running render.
