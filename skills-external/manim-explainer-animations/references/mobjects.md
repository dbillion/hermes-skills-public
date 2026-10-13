# Mobject Catalog (what can be drawn)

Every class here is `from manim import *`. This is organized by category, matching the CE v0.20 reference manual structure, so you can jump to the right section fast.

## 2D Geometry (`manim.mobject.geometry`)

**Arcs/circles:** `Circle`, `Dot`, `AnnotationDot`, `Ellipse`, `Arc`, `ArcBetweenPoints`, `Annulus`, `AnnularSector`, `Sector`, `CubicBezier`, `CurvedArrow`, `CurvedDoubleArrow`, `ArcPolygon`, `ArcPolygonFromArcs`, `TangentialArc`.

**Lines/vectors:** `Line`, `DashedLine`, `Arrow`, `DoubleArrow`, `Vector`, `TangentLine`, `Elbow`, `RightAngle`, `Angle`.
```python
Line(LEFT, RIGHT, color=BLUE)
Arrow(start=ORIGIN, end=UP + RIGHT, buff=0, color=YELLOW)
Vector([2, 1], color=GREEN)               # arrow from origin, for physics/linalg diagrams
Angle(line1, line2, radius=0.4, color=RED)  # arc showing angle between two Line mobjects
```

**Polygons:** `Polygon`, `Polygram` (multiple disjoint polygons as one mobject), `Rectangle`, `Square`, `RoundedRectangle`, `Triangle`, `RegularPolygon`, `RegularPolygram` (star-polygons like a pentagram), `Star`, `Cutout` (polygon with holes cut from it), `ConvexHull` (wraps a set of 2D points — great for "region satisfying these constraints" explainers).
```python
Star(n=5, outer_radius=2, color=YELLOW, fill_opacity=1)
ConvexHull(*[np.random.uniform(-2, 2, 3) * [1,1,0] for _ in range(12)], color=BLUE)
```

**Boolean ops** (`manim.mobject.geometry.boolean_ops`): `Union`, `Intersection`, `Difference`, `Exclusion` — combine two `VMobject`s set-theoretically. Great for Venn diagrams.
```python
Union(circle_a, circle_b, color=PURPLE)
Intersection(circle_a, circle_b, color=YELLOW, fill_opacity=1)
```

**Labeled geometry** (`manim.mobject.geometry.labeled` — prefer these over manual grouping): `Label`, `LabeledLine`, `LabeledArrow`, `LabeledPolygram`, `LabeledDot`.
```python
LabeledDot(label="A", point=LEFT * 2)
LabeledArrow(start=ORIGIN, end=RIGHT * 3, label="F = ma")
```

**Shape matchers** (auto-sized to another mobject): `SurroundingRectangle`, `BackgroundRectangle`, `Underline`, `Cross`.
```python
SurroundingRectangle(some_text, color=YELLOW, buff=0.15)   # classic "box around this term" highlight
```

**Arrow tips** (customize any `Arrow`/`Line` end): `ArrowTriangleTip` (default), `ArrowTriangleFilledTip`, `ArrowCircleTip`, `ArrowCircleFilledTip`, `ArrowSquareTip`, `ArrowSquareFilledTip`, `StealthTip`.

## 3D Solids (`manim.mobject.three_d`)

`Sphere`, `Cube`, `Cone`, `Cylinder`, `Torus`, `Prism`, `Line3D`, `Arrow3D`, `Dot3D`, `Surface` (parametric surface — the general-purpose 3D plotting primitive), `ThreeDVMobject`.

**Polyhedra** (`manim.mobject.three_d.polyhedra`): `Tetrahedron`, `Octahedron`, `Icosahedron`, `Dodecahedron`, `Polyhedron` (custom), `ConvexHull3D`.
```python
sphere = Sphere(radius=2, resolution=(24, 24), fill_opacity=0.7, checkerboard_colors=[BLUE_D, BLUE_E])
surface = Surface(lambda u, v: np.array([u, v, np.sin(u) * np.cos(v)]),
                   u_range=[-3, 3], v_range=[-3, 3], resolution=(32, 32))
```
Use `Surface` for any "plot z = f(x,y)" explainer — it's the 3D analogue of `ParametricFunction`.

## Text & LaTeX

See `references/text-and-typography.md` for full detail. Quick pointers: `Text` (plain/system fonts), `MarkupText` (Pango markup — inline styling within one mobject), `Tex`/`MathTex` (LaTeX), `Code` (syntax-highlighted code block), `Paragraph`, `BulletedList`, `Title`.

## Numbers & Matrices

`DecimalNumber`, `Integer`, `Variable` (a live-updating labeled numeric display — pair with `ValueTracker`), `Matrix`, `DecimalMatrix`, `IntegerMatrix`, `MobjectMatrix` (matrix whose entries are arbitrary mobjects, not just numbers).
```python
var = Variable(0, "x", num_decimal_places=2)   # auto-updates when var.tracker changes
Matrix([[1, 2], [3, 4]], left_bracket="[", right_bracket="]")
```

## Tables

`Table`, `MathTable` (LaTeX-rendered cells), `DecimalTable`, `IntegerTable`, `MobjectTable` (arbitrary mobjects per cell).
```python
Table([["1", "2"], ["3", "4"]], row_labels=[Text("A"), Text("B")],
      col_labels=[Text("X"), Text("Y")], include_outer_lines=True)
```
Use for the "counting the pattern" beats (vertex/edge/face counts, truth tables, comparison tables).

## Graphs (graph theory — nodes & edges, NOT plots)

`Graph`, `DiGraph` (directed), `GenericGraph`, `LayoutFunction`.
```python
g = Graph(vertices=[1, 2, 3, 4], edges=[(1, 2), (2, 3), (3, 4), (4, 1)],
          layout="spring", labels=True, vertex_config={"radius": 0.3})
```
Layouts: `"spring"`, `"circular"`, `"kamada_kawai"`, `"planar"`, `"random"`, `"partite"`, or a manual dict of positions. Use for graph algorithms, network explainers, trees, state machines.

## Plots / coordinate systems

See `references/plotting-and-graphs.md`. Quick pointers: `Axes`, `NumberPlane`, `PolarPlane`, `ComplexPlane`, `ThreeDAxes`, `NumberLine`/`UnitInterval`, `FunctionGraph`, `ParametricFunction`, `ImplicitFunction`, `BarChart`, `SampleSpace` (probability tree/partition diagrams).

## Vector fields

`ArrowVectorField` (grid of arrows sized/colored by a vector function), `StreamLines` (flowing streamlines, optionally animated with `StreamLines.start_animation()`), base `VectorField`.
```python
field = ArrowVectorField(lambda p: np.array([-p[1], p[0], 0]))  # rotational field
```
Good for physics (E/B fields, fluid flow) and dynamical-systems explainers.

## Images & SVG

`ImageMobject` (raster image, e.g. a photo/screenshot), `SVGMobject` (vector art, e.g. an icon or logo — scales cleanly, unlike `ImageMobject`), `VMobjectFromSVGPath`.
```python
ImageMobject("diagram.png").scale(0.5)
SVGMobject("icon.svg").set_color(BLUE)
```

## Braces & annotations

`Brace`, `BraceLabel`, `BraceText`, `BraceBetweenPoints`, `ArcBrace` — the classic "curly brace under a term with a label" annotation.
```python
Brace(some_mobject, direction=DOWN).get_text("this part")
```

## Grouping & structural types

`VGroup` (group of vector mobjects — nearly always what you want), `VDict` (named/keyed group), `Group` (mixed mobject types, e.g. `VMobject` + `ImageMobject` together), `VectorizedPoint` (invisible anchor point, useful as an animation target).

## Point-cloud types (rare — legacy-ish, prefer VMobject-based shapes for most work)

`PMobject`, `PGroup`, `PointCloudDot`, `Mobject1D`, `Mobject2D`. Mostly superseded by `DotCloud`-style OpenGL-renderer objects; only reach for these for very large scatter-style point sets where per-point `VMobject` overhead would be too slow.
