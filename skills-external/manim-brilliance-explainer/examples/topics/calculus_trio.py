# Three calculus classics: Riemann limit, circle unroll, tangent angle.

import numpy as np
from manim import (
    Scene, Axes, Circle, Line, Polygon, Dot, Arc, Text, MathTex, VGroup,
    ValueTracker, always_redraw, Create, Write, FadeIn, Transform,
    BLUE, GREEN, YELLOW, RED, UP, DOWN, LEFT, RIGHT, DR, PI, smooth,
)


class RiemannToIntegral(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"
        axes = Axes(
            x_range=[0, 4, 1],
            y_range=[0, 8, 2],
            axis_config={"include_ticks": False},
        )
        graph = axes.plot(lambda x: 0.5 * x ** 2, color=BLUE)
        self.play(Create(axes), Create(graph))

        rects = axes.get_riemann_rectangles(
            graph, x_range=(0, 3), dx=1.0,
            fill_opacity=0.4, color=BLUE, stroke_width=1,
        )
        self.play(FadeIn(rects))

        for dx in (0.25, 0.08):
            finer = axes.get_riemann_rectangles(
                graph, x_range=(0, 3), dx=dx,
                fill_opacity=0.4, color=BLUE, stroke_width=0.5,
            )
            self.play(Transform(rects, finer), run_time=1.5)

        area = axes.get_area(graph, x_range=(0, 3), color=GREEN, opacity=0.4)
        self.play(Transform(rects, area))
        self.wait(0.5)


class CircleToTriangle(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"
        R, dr, S = 2.0, 0.12, 0.6
        radii = np.arange(dr, R + 1e-9, dr)
        OFF = 3.5 * RIGHT

        rings = VGroup(*[
            Circle(radius=r * S, stroke_width=2).move_to(3.5 * LEFT)
            for r in radii
        ])
        rings.set_color_by_gradient(BLUE, GREEN)

        lines = VGroup(*[
            Line(LEFT * PI * r * S, RIGHT * PI * r * S, stroke_width=2)
            .move_to(OFF + UP * r * S)
            for r in radii
        ])
        lines.set_color_by_gradient(BLUE, GREEN)

        self.play(Create(rings))
        self.wait(0.5)
        self.play(*[Transform(r, l) for r, l in zip(rings, lines)], run_time=2.5)

        tri = Polygon(
            OFF,
            OFF + UP * R * S + LEFT * PI * R * S,
            OFF + UP * R * S + RIGHT * PI * R * S,
            color=YELLOW,
        )
        self.play(Create(tri))
        self.play(Write(
            MathTex(r"A = \tfrac12 (2\pi R) R = \pi R^2", color=YELLOW).to_edge(DOWN)
        ))
        self.wait()


class TangentAngle(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"
        axes = Axes(
            x_range=[-3, 3],
            y_range=[-1, 5],
            axis_config={"include_ticks": False},
        )
        f = lambda x: 0.5 * x ** 2 + 0.5
        graph = axes.plot(f, color=BLUE)
        a = ValueTracker(0.6)

        def build():
            x0 = a.get_value()
            ang = axes.angle_of_tangent(x0, graph)
            pt = axes.i2gp(x0, graph)
            tangent = axes.plot(
                lambda x: np.tan(ang) * (x - x0) + f(x0),
                color=RED,
                stroke_width=3,
            )
            arc = Arc(radius=0.5, start_angle=0, angle=ang, arc_center=pt, color=YELLOW)
            label = Text(
                f"{np.degrees(ang):.0f}" + chr(176),
                font_size=24,
                color=YELLOW,
            ).next_to(pt, DR)
            return VGroup(tangent, Dot(pt, color=YELLOW), arc, label)

        stuff = always_redraw(build)

        self.play(Create(axes), Create(graph))
        self.add(stuff)
        self.play(a.animate.set_value(2.2), run_time=3, rate_func=smooth)
        self.wait(0.5)
