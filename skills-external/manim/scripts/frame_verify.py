#!/usr/bin/env python3
"""Verify Manim frames: detect clipping + upright text without a vision model.
Usage: python frame_verify.py  (run from the video dir; expects _frames/<name>.png)
Or: python frame_verify.py path/to/frame.png
"""
import sys, os
from PIL import Image
import numpy as np

BG = np.array([28, 28, 28])  # #1C1C1C manim default


def analyze(path):
    im = Image.open(path).convert("RGB")
    a = np.array(im)
    h, w = a.shape[:2]
    diff = np.abs(a.astype(int) - BG).sum(2)
    mask = diff > 60
    ys, xs = np.where(mask)
    if len(ys) == 0:
        print(f"{os.path.basename(path)}: EMPTY frame"); return
    top, bot, left, right = ys.min(), ys.max(), xs.min(), xs.max()
    clipped = (top < 3) or (bot > h - 3) or (left < 3) or (right > w - 3)
    gray = a.mean(2)
    gx = np.abs(np.diff(gray.astype(int), axis=1))
    gy = np.abs(np.diff(gray.astype(int), axis=0))
    v_edges = (gx > 40).sum()
    h_edges = (gy > 40).sum()
    ratio = v_edges / max(h_edges, 1)
    print(f"{os.path.basename(path)}: {w}x{h} content=[{left},{top},{right},{bot}] "
          f"clipped={clipped} v/h_edge={ratio:.2f} "
          f"{'(upright-text-likely)' if ratio > 0.6 else '(low-text)'}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for p in sys.argv[1:]:
            analyze(p)
    else:
        d = "_frames"
        for f in sorted(os.listdir(d)):
            if f.endswith(".png"):
                analyze(os.path.join(d, f))
