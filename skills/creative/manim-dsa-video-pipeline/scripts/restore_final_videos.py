#!/usr/bin/env python3
"""Restore final_videos/ from scenes/media raw renders (Phase 2 path-bug recovery).

The Phase-2 loop looked for the produced mp4 by FINAL name but Manim writes it by
SCENE CLASS name, so it marked every scene FAIL and (with an os.remove-first pattern)
wiped final_videos. This copies the real renders back with correct final names.

Usage: python3 restore_final_videos.py [EXPLAINER_DIR]
Default EXPLAINER_DIR = /home/deeone/dsa-java-gradleqa/explainer_videos
"""
import json, os, glob, shutil, sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "/home/deeone/dsa-java-gradleqa/explainer_videos"
rmap = json.load(open(os.path.join(BASE, "_render_map_full.json")))
finaldir = os.path.join(BASE, "final_videos")
os.makedirs(finaldir, exist_ok=True)

restored = 0
missing = []
for base, info in rmap.items():
    scene, final = info["scene"], info["final"]
    prod = glob.glob(os.path.join(BASE, "scenes/media/videos", base, "480p15", scene + ".mp4"))
    if not prod:
        prod = glob.glob(os.path.join(BASE, "scenes/media/videos", base, "480p15", final[:-4] + ".mp4"))
    dst = os.path.join(finaldir, final)
    if prod:
        if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(prod[0]):
            shutil.copy(prod[0], dst)
        restored += 1
    else:
        missing.append((base, scene, final))

print(f"restored: {restored}")
print(f"missing:  {missing}")
print(f"final_videos count: {len(glob.glob(os.path.join(finaldir, '*.mp4')))}")
