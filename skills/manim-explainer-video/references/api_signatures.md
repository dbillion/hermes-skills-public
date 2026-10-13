# Manim CE 0.20.1 — Inspect-Verified Signatures

Dumped via:
`/home/deeone/.local/share/uv/tools/manim/bin/python -c "import inspect; from manim import Code; print(inspect.signature(Code.__init__))"`

DO NOT trust NotebookLM/repomix digests of the GitHub repo — they quoted a
divergent version with wrong param names.

## Code
```
Code(code_file=None, code_string=None, language=None, formatter_style=None,
     tab_width=4, add_line_numbers=False, line_numbers_from=1, background=None,
     background_config=None, paragraph_config=None)
```
- Use `code_string=` (NOT `code=`).
- Font sizing lives in `paragraph_config={"font_size": 18}` (NOT top-level `font_size=`).
- `add_line_numbers=` (NOT `insert_line_no=`).
- No `font=`, `background_stroke_color=`, `insert_line_no=` params exist.

## 3D primitives
- `Cube(side_length=2.0)`
- `Prism(dimensions=(1, 2, 1))`
- `Square(side_length=0.5)`

## Image
- `ImageMobject(filename_or_array)`; `.set_height(h)` preferred for tall PNGs
  (`.set_width` on a 586x895 portrait overflows 16:9 and clips head/tail).

## Arrows / shapes
- `Arrow(start, end, color=, stroke_width=, buff=)`
- `SurroundingRectangle(mobject, color=, buff=)`
- `Create`, `GrowFromCenter`, `LaggedStart`, `Write`, `FadeIn`, `FadeOut`

## Text
- `Text(t, font_size=, color=, font="Menlo", weight=BOLD)`

## ThreeDScene camera
- `self.set_camera_orientation(phi=, theta=, gamma=, zoom=, frame_center=)`
- `self.move_camera(phi=, theta=, frame_center=, run_time=)`  # NOT self.camera.frame.animate
- `self.add_fixed_in_frame_mobjects(*mobs)` + `self.remove(*mobs)`  # billboard
- `self.begin_ambient_camera_rotation(rate=)` / `self.stop_ambient_camera_rotation()`
