# Render Verification Without a Vision Model

`vision_analyze` + `browser_vision` were DEAD this session (404 / sandbox blocks
localhost+file+data URLs). Use ffmpeg + PIL pixel analysis instead.

## Extract frames
```bash
ffmpeg -y -i final_subbed.mp4 -ss 00:00:20 -frames:v 1 _frames/f_20.png
```

## Clip + slant analyzer (Python)
```python
from PIL import Image
import numpy as np
BG = np.array([28,28,28])  # manim bg #1C1C1C
im = Image.open("_frames/f_20.png").convert("RGB"); a=np.array(im)
h,w = a.shape[:2]
m = np.abs(a.astype(int)-BG).sum(2) > 60
ys,xs = np.where(m)
clipped = ys.min()<3 or ys.max()>h-3 or xs.min()<3 or xs.max()>w-3
print(f"content=[{xs.min()},{ys.min()},{xs.max()},{ys.max()}] clipped={clipped}")
# upright-text check: near-white text pixels, mid rows should have many
gray=a.mean(2); bright=gray>180; mid=(ys.min()+ys.max())//2
print("mid-row bright px:", bright[mid-3:mid+4].sum(1).tolist())  # ~0 => slanted
```

## Merge per-scene SRTs with cumulative offsets
Scene durations (example): [6.2, 9.27, 9.27, 10.73, 7.93, 5.53]
Offset each scene's SRT timestamps by the sum of prior durations, concatenate,
write `merged.srt`. Then burn in (see scripts/hardsub.sh).

## What this caught
- Complexity bars CLIPPED during `begin_ambient_camera_rotation` (orbit swung
  them out of frame) -> fixed by centering + dropping orbit.
- Text SLANTED (mid-row bright count ~0) -> fixed by `add_fixed_in_frame_mobjects`.
