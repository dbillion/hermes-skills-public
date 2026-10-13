# Plotting & Graphs

## Coordinate systems (`manim.mobject.graphing.coordinate_systems`)

`Axes` (general 2D x/y axes), `NumberPlane` (Axes + full grid, good background for linear-algebra/complex-analysis scenes), `PolarPlane` (r/θ grid), `ComplexPlane` (NumberPlane labeled for complex numbers, supports `n2p`/`p2n` — number-to-point and point-to-number conversion), `ThreeDAxes` (3D version), `CoordinateSystem` (shared base — most methods below exist on all of them).

```python
axes = Axes(x_range=[-5, 5, 1], y_range=[-3, 3, 1], axis_config={"include_tip": True})
plane = NumberPlane(x_range=[-7, 7], y_range=[-4, 4], background_line_style={"stroke_opacity": 0.4})
```

### Plotting a function on an Axes

```python
graph = axes.plot(lambda x: x**2, color=YELLOW, x_range=[-2, 2])
label = axes.get_graph_label(graph, label="x^2")
self.play(Create(axes), Create(graph), Write(label))
```
`axes.plot` returns a `ParametricFunction`/`FunctionGraph` under the hood — you can `self.play(Create(graph))` to draw it progressively, which reads much better than a static `FadeIn` for "here's the function."

### Area under a curve, tangent lines, and other calculus visuals

```python
area = axes.get_area(graph, x_range=[0, 2], color=BLUE, opacity=0.3)
tangent = axes.get_secant_slope_group(x=1, graph=graph, dx=0.01, secant_line_color=RED)
riemann = axes.get_riemann_rectangles(graph, x_range=[0, 2], dx=0.2, color=BLUE)
```
These are exactly the 3b1b-style calculus visuals (Riemann sum sweeping to become an integral, tangent line sliding along a curve) — check `Axes` methods before hand-building any of this from scratch, most calculus visuals are already a method call.

### Parametric & implicit functions

```python
ParametricFunction(lambda t: np.array([np.cos(t), np.sin(2*t), 0]), t_range=[0, TAU], color=PURPLE)
ImplicitFunction(lambda x, y: x**3 + y**3 - 3*x*y, color=GREEN)   # e.g. a folium/implicit curve
```

### Number lines

`NumberLine`, `UnitInterval` (a `NumberLine` pre-configured for `[0, 1]`) — for 1D visuals (real number line, probability on `[0,1]`, timeline).

## Graph theory (nodes/edges — different from the plotting `Graph` name collision, see mobjects.md)

Already covered in `mobjects.md` — `Graph`/`DiGraph`. Cross-referenced here because it's easy to confuse "plot a graph of a function" with "draw a graph-theory graph"; Manim's own naming does collide (`axes.plot()` for functions vs the `Graph` class for nodes/edges) — be explicit in comments about which one code is using.

## Bar charts & probability

```python
BarChart(values=[3, 7, 5, 9], bar_names=["A", "B", "C", "D"], y_range=[0, 10, 2])
SampleSpace(...)   # partitioned rectangle for probability-tree/conditional-probability explainers
```

## Vector fields & flow (see also `mobjects.md`)

```python
field = ArrowVectorField(lambda p: np.array([-p[1], p[0], 0]), x_range=[-4,4], y_range=[-4,4])
stream = StreamLines(lambda p: np.array([-p[1], p[0], 0]), stroke_width=2, max_anim_run_time=8)
self.add(stream)
stream.start_animation(warm_up=True, flow_speed=1.2)
self.wait(8)
```
`StreamLines.start_animation` gives continuously-flowing lines (needs `self.wait()` for the duration you want it to play, since it's a persistent animation, not a one-shot `play()` call).

## Scaling axes non-linearly

Pass `x_axis_config={"scaling": LogBase(10)}` (or `y_axis_config`) to any `CoordinateSystem` for log-scale axes — useful for exponential-growth / decibel / pH-style explainers where linear axes would be unreadable.
