# A moving point draws its own curve. Use this when the curve is PRODUCED
# by motion (epicycles, orbits), not when it is a static function plot.
# Note: min_distance_to_new_point exists only in Grant's manimlib, not in
# Manim Community, so it is intentionally not used here.

from manim import TracedPath, YELLOW


def trace_motion(scene, moving_mobject, color=YELLOW, stroke_width=3):
    trace = TracedPath(
        moving_mobject.get_center,
        stroke_width=stroke_width,
        stroke_color=color,
    )
    scene.add(trace)
    return trace
