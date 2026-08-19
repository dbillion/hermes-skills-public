# TracedPath: a moving point draws its own curve. Use when the curve is
# PRODUCED by motion, not when it is a static function plot.
# Note: min_distance_to_new_point is manimlib-only; not available in Community.

import numpy as np
from manim import Scene, Dot, ValueTracker, TracedPath, always_redraw, YELLOW, PI, linear


class TracedPathDemo(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"

        t = ValueTracker(0)

        # Spirograph motion: a small circle rolling around a bigger one.
        def tip_pos():
            time = t.get_value()
            center = np.array([2 * np.cos(0.5 * time), 2 * np.sin(0.5 * time), 0])
            return center + np.array([np.cos(3 * time), np.sin(3 * time), 0])

        tip = always_redraw(lambda: Dot(tip_pos(), radius=0.06, color=YELLOW))
        trace = TracedPath(
            tip.get_center,
            stroke_width=3,
            stroke_color=YELLOW,
        )

        self.add(trace, tip)
        self.play(t.animate.set_value(4 * PI), run_time=10, rate_func=linear)
        self.wait(0.5)
