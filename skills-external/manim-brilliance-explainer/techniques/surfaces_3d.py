# 3D surface with color-by-height, plus 3D field arrows.
# Camera framing follows the standard presets: phi about 70, theta about -40.
# Note: in Manim Community v0.20, set_fill_by_value colorscale pairs are
# (color, value), not (value, color).

import numpy as np
from manim import (
    ThreeDScene, ThreeDAxes, Surface, Arrow3D, VGroup,
    Create, FadeIn, DEGREES, BLUE, YELLOW, RED,
)


class PotentialSurface(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-40 * DEGREES)

        axes = ThreeDAxes(
            x_range=[-3, 3],
            y_range=[-3, 3],
            z_range=[0, 3],
        )

        surf = Surface(
            lambda u, v: [u, v, 1.8 / (np.sqrt(u * u + v * v) + 0.6)],
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(24, 24),
            fill_opacity=0.9,
        )
        # Color by height; pairs are (color, pivot value on z-axis).
        surf.set_fill_by_value(
            axes=axes,
            colorscale=[(BLUE, 0.0), (YELLOW, 1.0), (RED, 2.0)],
        )

        arrows = VGroup()
        for x in (-2, -1, 1, 2):
            for y in (-2, -1, 1, 2):
                r2 = x * x + y * y + 0.3
                arrows.add(Arrow3D(
                    [x, y, 0],
                    [x + 0.6 * x / r2, y + 0.6 * y / r2, 0],
                    stroke_width=1.5,
                ))

        self.play(Create(surf), run_time=2)
        self.play(FadeIn(arrows))
        self.wait(0.5)
