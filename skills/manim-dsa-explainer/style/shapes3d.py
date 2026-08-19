"""
Extended 3D vocabulary for the manim-dsa-storytelling / manim-dsa-single-path
skills. dsa_style.py and graph_tree_style.py only ever used Cube (arrays,
stacks) and Sphere (graph nodes). This module adds the shapes those skills
declared but never implemented: Cylinder, Torus, Cone, and prism-based grids
-- each mapped to a DS metaphor where the shape actually carries meaning
(not decoration for its own sake).

Import alongside dsa_style / graph_tree_style; nothing here replaces those,
it extends them.
"""
from manim import *
from dsa_style import CUBE_COLOR, ACCENT, GOOD

CYL_COLOR = "#4a7fb5"    # queues / hash buckets
RING_COLOR = "#b56a4a"   # circular structures
CONE_COLOR = "#c94f6d"   # pointers / heap peaks


def make_cylinder_queue(axes, values, spacing=1.0, radius=0.28, height_scale=0.25, min_height=0.3):
    """FIFO queue / hash bucket -> row of upright cylinders (front-to-back).
    Cylinders read as 'containers you push into / pop from the ends' -- a
    clearer FIFO cue than cubes, which the array/stack helpers already own."""
    cyls, labels = VGroup(), VGroup()
    for i, v in enumerate(values):
        h = max(abs(v) * height_scale, min_height)
        cyl = Cylinder(radius=radius, height=h, fill_color=CYL_COLOR,
                        fill_opacity=0.9, stroke_color=WHITE, resolution=(12, 12))
        cyl.move_to(axes.c2p(i * spacing + 0.5, 0, 0))
        cyl.shift(UP * h / 2)
        lbl = Text(str(v), color=WHITE).scale(0.32)
        lbl.rotate(90 * DEGREES, axis=RIGHT)
        lbl.next_to(cyl, DOWN, buff=0.12)
        cyls.add(cyl)
        labels.add(lbl)
    return cyls, labels


def make_ring(axes, node_values, ring_radius=1.6, tube_radius=0.05, node_radius=0.16):
    """Circular queue / cycle-in-a-linked-list / ring buffer -> Torus track
    with dots seated on it. The closed loop *is* the concept (wrap-around,
    a detected cycle) in a way a straight cube row can't show."""
    ring = Torus(major_radius=ring_radius, minor_radius=tube_radius,
                  checkerboard_colors=False, fill_color=RING_COLOR,
                  fill_opacity=0.5, resolution=(24, 12))
    ring.move_to(axes.c2p(0, 0, 0))
    nodes = VGroup()
    labels = VGroup()
    n = max(len(node_values), 1)
    for i, v in enumerate(node_values):
        theta = i * TAU / n
        pos = axes.c2p(ring_radius * np.cos(theta), ring_radius * np.sin(theta), 0)
        dot = Sphere(radius=node_radius, fill_color=CUBE_COLOR, fill_opacity=0.95, resolution=(8, 8))
        dot.move_to(pos)
        lbl = Text(str(v), color=WHITE).scale(0.3)
        lbl.rotate(90 * DEGREES, axis=RIGHT)
        lbl.move_to(pos + OUT * 0.3)
        nodes.add(dot)
        labels.add(lbl)
    return ring, nodes, labels


def make_cone_pointer(location, color=CONE_COLOR, size=0.22, direction=DOWN):
    """A pointer/cursor marker: 'current node', 'top of stack', 'i / j index',
    heap root. Cones read as arrows in a way cubes/spheres don't -- use for
    anything that moves through a structure across the animation."""
    cone = Cone(base_radius=size, height=size * 1.8, direction=direction,
                fill_color=color, fill_opacity=0.95, stroke_color=WHITE, resolution=8)
    cone.move_to(location)
    return cone


def make_min_heap_tree(axes, values, x_spread=1.4, y_step=1.1):
    """Binary (min-)heap -> tree of cones, root at top pointing up, sized by
    value. The 'peak' shape reinforces heap-property intuition (root is the
    extreme) better than a uniform cube/sphere tree."""
    n = len(values)
    cones, labels, positions = VGroup(), VGroup(), {}
    for i, v in enumerate(values):
        depth = int(np.floor(np.log2(i + 1)))
        idx_in_row = i - (2 ** depth - 1)
        row_count = 2 ** depth
        x = (idx_in_row - (row_count - 1) / 2) * (x_spread / row_count) * 2
        y = -depth * y_step
        pos = axes.c2p(x, y, 0)
        positions[i] = pos
        size = max(0.14, min(0.32, abs(v) * 0.02 + 0.16))
        cone = Cone(base_radius=size, height=size * 1.8, direction=UP,
                    fill_color=CONE_COLOR, fill_opacity=0.9, stroke_color=WHITE, resolution=8)
        cone.move_to(pos)
        lbl = Text(str(v), color=WHITE).scale(0.3)
        lbl.rotate(90 * DEGREES, axis=RIGHT)
        lbl.next_to(cone, DOWN, buff=0.15)
        cones.add(cone)
        labels.add(lbl)
    edges = VGroup()
    for i in range(n):
        for child in (2 * i + 1, 2 * i + 2):
            if child < n:
                edges.add(Line3D(positions[i], positions[child], color=WHITE, thickness=0.008))
    return cones, labels, edges


def make_split_wedge(axes, x_pos, y_height=1.2, depth=0.5, color=ACCENT):
    """Triangular prism 'wedge' driven through an array to show a
    divide-and-conquer split point (merge sort midpoint, quickselect
    partition, binary search elimination). No cube/sphere/cone reads as
    'a cut' the way a wedge does."""
    apex = axes.c2p(x_pos, y_height, depth / 2)
    base_l = axes.c2p(x_pos - 0.35, 0, depth / 2)
    base_r = axes.c2p(x_pos + 0.35, 0, depth / 2)
    apex_b = axes.c2p(x_pos, y_height, -depth / 2)
    base_l_b = axes.c2p(x_pos - 0.35, 0, -depth / 2)
    base_r_b = axes.c2p(x_pos + 0.35, 0, -depth / 2)
    wedge = Polyhedron(
        vertex_coords=[apex, base_l, base_r, apex_b, base_l_b, base_r_b],
        faces_list=[[0, 1, 2], [3, 4, 5], [0, 1, 4, 3], [1, 2, 5, 4], [2, 0, 3, 5]],
    )
    wedge.set_fill(color, opacity=0.75)
    wedge.set_stroke(WHITE, width=1)
    return wedge


def make_prism_grid(axes, rows, cols, cell_values=None, cell_size=0.4, gap=0.06):
    """2D DP table (edit distance, knapsack, LCS) as a grid of thin
    rectangular prisms lying flat, height encoding cell value -- a literal
    'grid you fill in' rather than a row of cubes standing for an array."""
    step = cell_size + gap
    prisms, labels = VGroup(), VGroup()
    for r in range(rows):
        for c in range(cols):
            v = 0 if cell_values is None else cell_values[r][c]
            h = max(0.05, min(0.6, abs(v) * 0.04 + 0.06))
            prism = Cube(side_length=cell_size, fill_color=CUBE_COLOR,
                        fill_opacity=0.85, stroke_color=WHITE, stroke_width=0.5)
            prism.stretch_to_fit_height(h)
            pos = axes.c2p(c * step, -r * step, 0)
            prism.move_to(pos)
            prism.shift(OUT * h / 2)
            if cell_values is not None:
                lbl = Text(str(v), color=WHITE).scale(0.22)
                lbl.rotate(90 * DEGREES, axis=RIGHT)
                lbl.move_to(pos + OUT * (h + 0.15))
                labels.add(lbl)
            prisms.add(prism)
    return prisms, labels
