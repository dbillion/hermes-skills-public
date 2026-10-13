# Fourier series as rotating vectors.
# The angle law is the whole trick: theta_n(t) = n * omega * t.
# Radius of term n for a square wave: 4 / (pi * n), odd n only.

import numpy as np
from manim import (
    Scene, ValueTracker, always_redraw, Circle, Arrow, Axes, Dot, DashedLine,
    VGroup, LEFT, RIGHT, ORIGIN, GREY_B, BLUE_B, YELLOW, PI, Create, linear,
)


class FourierEpicycles(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"

        OMEGA = 1.0
        CENTER = 4.5 * LEFT
        TERMS = [(n, 4 / (PI * n)) for n in (1, 3, 5, 7, 9, 11)]

        t = ValueTracker(0)

        axes = Axes(
            x_range=[0, 4 * PI, PI],
            y_range=[-2, 2, 1],
            x_length=7.5,
            y_length=3.5,
            axis_config={"include_ticks": False, "color": GREY_B},
            tips=False,
        ).to_edge(RIGHT)

        def partial_sum(time):
            return sum(r * np.sin(n * OMEGA * time) for n, r in TERMS)

        graph = axes.plot(partial_sum, color=YELLOW, stroke_width=2)

        def epicycles():
            group = VGroup()
            tip = CENTER
            for n, r in TERMS:
                group.add(Circle(radius=r, stroke_width=1, color=GREY_B).move_to(tip))
                angle = n * OMEGA * t.get_value()   # angle law
                new_tip = tip + r * np.array([np.cos(angle), np.sin(angle), 0])
                group.add(Arrow(tip, new_tip, buff=0, stroke_width=2, color=BLUE_B))
                tip = new_tip
            return group, tip

        chain = always_redraw(lambda: epicycles()[0])
        tipdot = always_redraw(lambda: Dot(epicycles()[1], radius=0.05, color=YELLOW))
        gdot = always_redraw(
            lambda: Dot(
                axes.c2p(t.get_value(), partial_sum(t.get_value())),
                radius=0.05,
                color=YELLOW,
            )
        )
        link = always_redraw(
            lambda: DashedLine(
                epicycles()[1],
                axes.c2p(t.get_value(), partial_sum(t.get_value())),
                stroke_width=1,
                color=GREY_B,
            )
        )

        self.play(Create(axes), Create(graph), run_time=1.5)
        self.add(chain, tipdot, gdot, link)
        self.play(t.animate.set_value(4 * PI), run_time=15, rate_func=linear)
