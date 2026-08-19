# Uses the camera director + angle laws from style/.
# This file fixes its own import path, so it runs from any directory.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (
    ThreeDScene, Text, Arrow, ValueTracker, always_redraw,
    ORIGIN, UP, YELLOW, PI, linear,
)
from style.camera import set_standard_3d_view, orbit, stop_orbit, lock_to_screen
from style.angles import rotating_angle, unit_vector


class CinematicTemplate(ThreeDScene):
    def construct(self):
        set_standard_3d_view(self)   # phi=75 deg, theta=-45 deg, zoom=0.8

        title = Text("Standard 3B1B framing", font_size=30)
        title.to_edge(UP)
        lock_to_screen(self, title)

        t = ValueTracker(0)
        arrow = always_redraw(
            lambda: Arrow(
                ORIGIN,
                2 * unit_vector(rotating_angle(t.get_value(), omega=1.5)),
                buff=0,
                color=YELLOW,
            )
        )

        self.add(title, arrow)
        orbit(self, rate=0.12)
        self.play(t.animate.set_value(2 * PI), run_time=4, rate_func=linear)
        stop_orbit(self)
        self.wait(0.5)
