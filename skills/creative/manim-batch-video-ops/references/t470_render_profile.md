# Render profile — ThinkPad T470 (weak laptop iGPU)

## Hardware (from inxi -Fxz)
- CPU: Intel i5-7200U, 2 cores / 4 threads, 2.5–3.1 GHz.
- RAM: 32 GiB.
- GPU: Intel HD Graphics 620 (Kaby Lake), Mesa iris driver.
- OpenGL: 4.6, direct render = YES (renderer "Mesa Intel HD 620").
- Display: Wayland (KDE Plasma); DISPLAY=:1, WAYLAND_DISPLAY=wayland-0.
- Disk: NVMe SSD (fast I/O).
- OS: EndeavourOS / Arch.

## Measured render timings (same trivial scene)
- Cairo -ql:   ~8.8 s
- OpenGL -ql:  ~15.2 s   (slower! per-frame window-swap overhead on weak iGPU)

## Guidance
- Batch default: `manim --renderer=cairo -ql FILE.py ClassName`
- For heavy 3D scenes (axes + cubes + particles + two Code panels) Cairo is
  comparable or faster than OpenGL on this GPU. Use Cairo for automated/batch.
- OpenGL 4.6 works in an INTERACTIVE terminal (DISPLAY inherited). A background
  / headless automation shell without DISPLAY will hang or fail — that is an
  environment issue, NOT a hardware limit.
- `-ql` (480p15) for the full batch. Reserve `-qh` (1080p60) for a final pass
  on a stronger machine or when you have GPU time locally.
- If a render seems stuck for >2x its normal time, check `pgrep -P <batchpid>`
  for a live `manim`/`python` child; a silent class-name mismatch
  (e.g. `Trick01NameMangling.Py`) makes Manim find no scene and exit fast with
  no useful output — always verify the class name is correct.
