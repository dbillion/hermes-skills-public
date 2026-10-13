# Electromagnetism: EM wave in 3D with orbiting camera, and magnetic
# streamlines around a wire.
# Note: Manim Community animates vector fields with stream.create();
# Grant's manimlib start_animation/end_animation API does not exist here.

import numpy as np
from manim import (
    ThreeDScene, Scene, Text, Arrow, Line, Dot, VGroup, ValueTracker,
    always_redraw, StreamLines, DEGREES, GREY_B, YELLOW, BLUE, DOWN, UP,
    LEFT, RIGHT, linear,
)


class EMWave(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=75 * DEGREES, theta=-50 * DEGREES, zoom=0.75)

        axis = Line(5 * LEFT, 5 * RIGHT, color=GREY_B, stroke_width=1)
        phase = ValueTracker(0)

        def field_arrows():
            g, p = VGroup(), phase.get_value()
            for x in np.arange(-5, 5.01, 0.5):
                amp = 1.2 * np.cos(x - p)
                if abs(amp) > 0.06:
                    g.add(Arrow([x, 0, 0], [x, amp, 0], buff=0,
                                stroke_width=1.5, color=YELLOW))
                    g.add(Arrow([x, 0, 0], [x, 0, amp], buff=0,
                                stroke_width=1.5, color=BLUE))
            return g

        title = Text("E and B, perpendicular, traveling together", font_size=28)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)

        self.add(axis, always_redraw(field_arrows))
        self.begin_ambient_camera_rotation(rate=0.12)
        self.play(phase.animate.set_value(4 * np.pi), run_time=8, rate_func=linear)
        self.stop_ambient_camera_rotation()
        self.wait(0.5)


class WireField(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"

        def B(p):
            x, y, _ = p
            return np.array([-y, x, 0]) / (x * x + y * y + 1e-6)

        stream = StreamLines(
            B,
            x_range=[-6, 6, 0.5],
            y_range=[-4, 4, 0.5],
            padding=0.2,
            stroke_width=2,
        )
        wire = Dot([0, 0, 0], radius=0.12, color=YELLOW)
        lab = Text("current out of screen", font_size=24).next_to(wire, DOWN)

        self.add(stream, wire, lab)
        self.play(stream.create(), run_time=3)
        self.wait(2)
