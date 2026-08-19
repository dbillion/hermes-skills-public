"""
Plotting/calculus template: function plot, tangent line sliding along the
curve, and a Riemann-sum sweep converging toward the area under the curve.

Render with:
    manim -pql graphing_template.py CalculusExplainer
"""
from manim import *

BG_COLOR = "#0e1116"
PRIMARY_BLUE = "#58C4DD"
ACCENT_YELLOW = "#FFC857"


class CalculusExplainer(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        axes = Axes(x_range=[-1, 4, 1], y_range=[-1, 9, 2], x_length=8, y_length=5,
                    axis_config={"include_tip": True})
        graph = axes.plot(lambda x: x ** 2, color=PRIMARY_BLUE, x_range=[0, 3])
        label = axes.get_graph_label(graph, label="x^2", x_val=2.7, direction=UP)

        self.play(Create(axes), run_time=1.5)
        self.play(Create(graph), Write(label), run_time=1.5)
        self.wait(1)

        # tangent line sliding along the curve
        x_tracker = ValueTracker(0.3)
        tangent = always_redraw(lambda: axes.get_secant_slope_group(
            x=x_tracker.get_value(), graph=graph, dx=0.01,
            secant_line_color=ACCENT_YELLOW, secant_line_length=4,
        ))
        self.play(FadeIn(tangent))
        self.play(x_tracker.animate.set_value(2.8), run_time=4, rate_func=linear)
        self.play(FadeOut(tangent))
        self.wait(0.5)

        # Riemann sum sweeping to finer rectangles -> area under curve
        dx_tracker = ValueTracker(0.5)
        rects = always_redraw(lambda: axes.get_riemann_rectangles(
            graph, x_range=[0, 3], dx=dx_tracker.get_value(),
            color=PRIMARY_BLUE, fill_opacity=0.6, stroke_width=0.5,
        ))
        self.play(FadeIn(rects))
        self.play(dx_tracker.animate.set_value(0.02), run_time=4, rate_func=smooth)
        self.wait(1)

        integral = MathTex(r"\int_0^3 x^2\,dx = 9", color=ACCENT_YELLOW).to_edge(DOWN)
        self.play(Write(integral), run_time=1.2)
        self.wait(2)
