"""
Shared helpers for the single-path (non-comparison) DSA videos, built on the
manim-dsa-single-path skill. Adds graph/tree node-and-edge helpers on top of
dsa_style's array (cube-row) helpers, which this module also re-exports.
"""
from manim import *
from dsa_style import (DARK_BG, CUBE_COLOR, ACCENT, GOOD, SCENE_SHIFT,
                        make_cube_row, fixed_title, code_panel, make_highlight)

NODE_COLOR = "#3a3f4b"


def make_graph(axes, positions, edges):
    """positions: {node_id: (x, y, z)}. edges: [(a, b), ...]. Returns (nodes dict, lines VGroup)."""
    nodes = {}
    for nid, pos in positions.items():
        dot = Sphere(radius=0.18, fill_color=NODE_COLOR, fill_opacity=0.95, resolution=(8, 8))
        dot.move_to(axes.c2p(*pos))
        lbl = Text(str(nid), color=WHITE).scale(0.32)
        lbl.rotate(90 * DEGREES, axis=RIGHT)
        lbl.move_to(axes.c2p(*pos) + OUT * 0.35)
        nodes[nid] = VGroup(dot, lbl)
    lines = VGroup()
    for a, b in edges:
        line = Line3D(nodes[a][0].get_center(), nodes[b][0].get_center(),
                      color=WHITE, thickness=0.01)
        lines.add(line)
    return nodes, lines


def make_tree(axes, tree_positions, edges):
    """tree_positions: {node_id: (x, y, z)} laid out with root at top (highest y)."""
    return make_graph(axes, tree_positions, edges)


def make_vertical_stack(axes, values, cube_size=0.5):
    """Cube row oriented vertically -- a stack, bottom to top."""
    cubes = VGroup()
    labels = VGroup()
    for i, v in enumerate(values):
        c = Cube(side_length=cube_size, fill_color=CUBE_COLOR, fill_opacity=0.9, stroke_color=WHITE)
        c.move_to(axes.c2p(0, i, 0))
        lbl = Text(str(v), color=WHITE).scale(0.3)
        lbl.rotate(90 * DEGREES, axis=RIGHT)
        lbl.next_to(c, RIGHT, buff=0.15)
        cubes.add(c)
        labels.add(lbl)
    return cubes, labels
