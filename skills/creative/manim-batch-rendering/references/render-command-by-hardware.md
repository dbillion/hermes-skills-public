# Render command by hardware

## How to check your environment
```
echo "DISPLAY=$DISPLAY"
echo "WAYLAND_DISPLAY=$WAYLAND_DISPLAY"
inxi -Fxz     # CPU, GPU, OpenGL version, driver
nproc         # core count
docker ps     # running containers = transient load that inflates render time
```

## Local machine WITH a display (DISPLAY / WAYLAND_DISPLAY set)
Both Cairo and OpenGL work. Timed comparison on a ThinkPad T470 (i5-7200U, 2c/4t,
Intel HD 620 iGPU, OpenGL 4.6 direct-render via iris driver):
- Trivial scene: Cairo `-ql` = 8.8s, OpenGL `-ql` = 15.2s → CAIRO FASTER.
- Reason: OpenGL pays per-frame window-swap/context overhead that only pays off on
  heavy 3D, and a weak iGPU can't amortize it.
- Recommendation for batch work: `manim --renderer=cairo -ql <file> <Scene>`.

## Headless / automation shell with NO display env
OpenGL hangs or fails (no Xvfb/EGL in the sandbox). Use Cairo:
`manim --renderer=cairo -ql <file> <Scene>`.
NOTE: the earlier "OpenGL doesn't work here" was a DISPLAY-env issue in the automation
shell, NOT missing hardware — same machine renders OpenGL fine from an interactive
terminal that has DISPLAY set.

## Quality tier
- `-ql` (480p15): right tier for a 2-core CPU and for iterating/verifying a batch.
- `-qh` (1080p60): reserve for a FINAL pass on already-verified scenes. On a 2-core
  iGPU each `-qh` frame is minutes; a 23-video batch at `-qh` is many hours.

## Proven safe batch command
```
cd /path/to/scenes
bash safe_batch_render.sh        # background it; it logs >>> DONE/FAIL per scene
```
The script accumulates mp4s per-scene folder and never deletes between renders.
