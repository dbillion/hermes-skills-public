#!/usr/bin/env python3
"""Generate 480p GIFs for dsa-java-gradleqa scenes from scenes/media raw renders.

Handles the two real-world quirks:
  - GIF final names are INCONSISTENT (Q03_TwoSum, A04_HeapSort, FloodFill, Astar).
    Always map scene base -> gif name via _render_map_full.json `final`, never guess.
  - Manim output is named by SCENE CLASS, not final name.

Usage: python3 make_gifs_from_media.py [EXPLAINER_DIR]
Default EXPLAINER_DIR = /home/deeone/dsa-java-gradleqa/explainer_videos
Two-pass ffmpeg palette @480p15 keeps files GitHub-LFS-friendly.
"""
import json, os, glob, subprocess, sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "/home/deeone/dsa-java-gradleqa/explainer_videos"
rmap = json.load(open(os.path.join(BASE, "_render_map_full.json")))
W, H = 854, 480

made = skipped = missing = 0
for base, info in rmap.items():
    scene, final = info["scene"], info["final"]
    gifbase = final[:-4]
    gif = os.path.join(BASE, "gifs", gifbase + ".gif")
    if os.path.exists(gif):
        skipped += 1
        continue
    prod = glob.glob(os.path.join(BASE, "scenes/media/videos", base, "480p15", scene + ".mp4"))
    if not prod:
        prod = glob.glob(os.path.join(BASE, "scenes/media/videos", base, "480p15", gifbase + ".mp4"))
    if not prod:
        missing += 1
        continue
    mp4 = prod[0]
    pal = f"/tmp/pal_{gifbase}.png"
    subprocess.run(["ffmpeg", "-y", "-i", mp4, "-vf",
                    f"fps=15,scale={W}:{H}:flags=lanczos,palettegen", pal],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    r = subprocess.run(["ffmpeg", "-y", "-i", mp4, "-i", pal, "-lavfi",
                        f"fps=15,scale={W}:{H}:flags=lanczos[x];[x][1:v]paletteuse", gif],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(pal):
        os.remove(pal)
    made += 1 if (r.returncode == 0 and os.path.exists(gif)) else 0

print(f"made: {made}  skipped(exists): {skipped}  missing_source: {missing}")
print(f"total gifs: {len(glob.glob(os.path.join(BASE, 'gifs', '*.gif')))}")
