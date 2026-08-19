# Manim 0.20.1 constructor gotchas (verified via inspect on installed build)

These caused real TypeErrors this session. Always prefer
`inspect.signature(X.__init__)` on the installed `manim` over docs/repo digests.

| Class | WRONG | CORRECT |
|---|---|---|
| `Cone` | `Cone(radius=0.8, height=1.6)` | `Cone(base_radius=0.8, height=1.6)` |
| `Cylinder` | — | `Cylinder(radius=0.6, height=1.6)` (radius OK) |
| `Torus` | `Torus(radius=...)` | `Torus(major_radius=1.0, minor_radius=0.35)` |
| `Sphere` | — | `Sphere(radius=0.8, resolution=(24,24))` |
| `Code` | `Code(code=..., font_size=18, insert_line_no=False)` | `Code(code_string=..., language="python", paragraph_config={"font_size":18})` |
| `ThreeDScene` text | placed in 3D -> slanted | billboard: `add_fixed_in_frame_mobjects(m); remove(m)` |
| camera pan | `self.camera.frame.animate.shift(...)` | `self.move_camera(frame_center=[x,y,z])` (ThreeDScene) |

## 4D math (from manim-explainer-animations/references/4d-math.md)
- 4D has 6 rotation planes: xy,xz,xw,yz,yw,zw.
- Project 4D->3D perspective: `k = dist/(dist - w)`; keep `dist > max|w|`.
- Double rotation (e.g. xw + yz*0.618) = signature 4D tumble; ratio != 1 avoids resync.
- Hypersphere slice at w=c -> 3D sphere radius sqrt(r^2 - c^2).
