# Homotopy: continuous deformation from one shape to another.
# The homotopy function maps (x, y, z, t) -> (x, y, z), with t in [0, 1].

import numpy as np
from manim import Scene, Circle, Homotopy, interpolate, Create, BLUE, YELLOW


class HomotopyDemo(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"

        def circle_to_square(x, y, z, t):
            theta = np.arctan2(y, x)
            circle_pt = np.array([np.cos(theta), np.sin(theta), 0.0])
            m = max(abs(np.cos(theta)), abs(np.sin(theta)))
            square_pt = circle_pt / m
            return tuple(interpolate(circle_pt, square_pt, t))

        mob = Circle(radius=1.5, color=BLUE, stroke_width=4)
        self.play(Create(mob))
        self.wait(0.3)
        self.play(Homotopy(circle_to_square, mob), run_time=2)
        self.play(mob.animate.set_stroke(color=YELLOW))
        self.wait(0.4)
