"""
Shared style + helpers for the dsa-java-gradleqa brute-vs-optimized explainer
videos, built on the manim-dsa-storytelling skill (5-act structure, real code
panels with synced highlight, particle sweeps, complexity-graph payoff).

Import this from every scene file to keep the ten videos visually consistent
(same palette, same camera language, same code-panel + particle idioms).
"""
from manim import *

DARK_BG = "#0e0f12"
CUBE_COLOR = "#3a3f4b"
ACCENT = "#f2a154"   # brute-force accent
GOOD = "#5ad1a6"     # optimized accent
PANEL_BG = "#17181c"

SCENE_SHIFT = RIGHT * 3.0


def make_cube_row(axes, values, height_scale=0.25, min_height=0.25, label_fn=str):
    """Array/sequence -> row of cubes along the x-axis (skill's array metaphor)."""
    cubes = VGroup()
    labels = VGroup()
    for i, v in enumerate(values):
        h = max(abs(v) * height_scale, min_height)
        c = Cube(side_length=0.5, fill_color=CUBE_COLOR, fill_opacity=0.9, stroke_color=WHITE)
        c.stretch_to_fit_height(h)
        c.move_to(axes.c2p(i + 0.5, 0, 0))
        c.shift(UP * h / 2)
        lbl = Text(label_fn(v), color=WHITE).scale(0.32)
        lbl.rotate(90 * DEGREES, axis=RIGHT)
        lbl.next_to(c, DOWN, buff=0.12)
        cubes.add(c)
        labels.add(lbl)
    return cubes, labels


def fixed_title(scene, text, color=WHITE, scale=0.6, edge=UP):
    t = Text(text, color=color).scale(scale)
    scene.add_fixed_in_frame_mobjects(t)
    t.to_edge(edge)
    return t


def code_panel(scene, code_str, label_text, label_color, scale=0.55, y_shift=-0.3):
    """Split-screen Code mobject + corner label, fixed-in-frame (ThreeDScene-safe)."""
    label = Text(label_text, color=label_color).scale(0.45)
    scene.add_fixed_in_frame_mobjects(label)
    label.to_corner(UL).shift(DOWN * 0.7)

    code = Code(code_string=code_str, language="java", formatter_style="native",
                background="window", add_line_numbers=True,
                paragraph_config={"font_size": 16})
    scene.add_fixed_in_frame_mobjects(code)
    code.scale(scale).to_edge(LEFT, buff=0.3).shift(UP * y_shift)
    return label, code


def make_highlight(scene, code, line_idx, color):
    hl = SurroundingRectangle(code.code_lines[line_idx], color=color, buff=0.05)
    scene.add_fixed_in_frame_mobjects(hl)
    return hl


def test_panel(scene, test_code, expected_text, label="Verified by test (JUnit)"):
    """Act 5b: show the REAL @Test that proves correctness, with the expected
    output and a green check. Returns (label, code, check) mobjects."""
    label = Text(label, color=GOOD).scale(0.4)
    scene.add_fixed_in_frame_mobjects(label)
    label.to_corner(UL).shift(DOWN * 0.7)
    code = Code(code_string=test_code, language="java", formatter_style="native",
                background="window", add_line_numbers=True,
                paragraph_config={"font_size": 15})
    scene.add_fixed_in_frame_mobjects(code)
    code.scale(0.4).to_edge(LEFT, buff=0.3).shift(UP * 0.1)
    check = Text("✓ " + expected_text, color=GOOD).scale(0.4)
    scene.add_fixed_in_frame_mobjects(check)
    check.to_edge(DOWN, buff=0.3)
    return label, code, check


def complexity_payoff(scene, bf_fn, opt_fn, bf_tag_text, opt_tag_text,
                       x_range=(0, 10, 2), y_range=(0, 100, 20)):
    """Act 5: cut to 2D complexity graph, brute vs optimized curve."""
    graph_axes = Axes(x_range=list(x_range), y_range=list(y_range),
                       x_length=7, y_length=4,
                       axis_config={"color": WHITE}).to_edge(DOWN, buff=0.8)
    x_label = graph_axes.get_x_axis_label("n").scale(0.6)
    y_label = graph_axes.get_y_axis_label("work").scale(0.6)

    bf_curve = graph_axes.plot(bf_fn, x_range=[x_range[0], x_range[1]], color=ACCENT)
    opt_curve = graph_axes.plot(opt_fn, x_range=[x_range[0], x_range[1]], color=GOOD)

    bf_tag = Text(bf_tag_text, color=ACCENT).scale(0.4).next_to(bf_curve, UR, buff=0.1)
    opt_tag = Text(opt_tag_text, color=GOOD).scale(0.4).next_to(opt_curve.get_end(), UP, buff=0.15)

    scene.play(Create(graph_axes), Write(x_label), Write(y_label))
    scene.play(Create(bf_curve), Write(bf_tag), run_time=1.2)
    scene.play(Create(opt_curve), Write(opt_tag), run_time=1.2)
    scene.wait(1.2)
