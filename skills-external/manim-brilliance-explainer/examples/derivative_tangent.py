from manim import Scene, Axes, Text, Dot, ValueTracker, always_redraw, Write, Create, FadeIn, FadeOut, smooth, UR, DOWN


BG_COLOR = "#0f0f0f"
COLOR_PRIMARY = "#58C4DD"
COLOR_ACCENT = "#FFFF00"
COLOR_ERROR = "#FC6255"


class DerivativeInsight(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        title = Text("What is a derivative?", font_size=42)
        self.play(Write(title), run_time=1.2)
        self.wait(0.8)
        self.play(FadeOut(title))

        axes = Axes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-1, 4, 1],
            axis_config={
                "color": "#BBBBBB",
                "stroke_width": 3,
                "include_ticks": False,
            },
            tips=False,
        )

        curve = axes.plot(
            lambda x: x ** 2,
            x_range=[-2, 2],
            color=COLOR_PRIMARY,
            stroke_width=5,
        )

        self.play(Create(axes), run_time=1.0)
        self.play(Create(curve), run_time=1.5)
        self.wait(0.5)

        x = ValueTracker(1.0)

        point = always_redraw(
            lambda: Dot(
                axes.c2p(x.get_value(), x.get_value() ** 2),
                color=COLOR_ACCENT,
                radius=0.07,
            )
        )

        tangent = always_redraw(
            lambda: axes.plot(
                lambda t: 2 * x.get_value() * t - x.get_value() ** 2,
                x_range=[x.get_value() - 1.2, x.get_value() + 1.2],
                color=COLOR_ERROR,
                stroke_width=4,
            )
        )

        slope_label = always_redraw(
            lambda: Text(
                f"slope = {2 * x.get_value():.2f}",
                font_size=32,
                color=COLOR_ERROR,
            ).to_corner(UR)
        )

        self.play(FadeIn(point), run_time=0.7)
        self.play(Create(tangent), FadeIn(slope_label), run_time=1.2)
        self.wait(0.6)

        self.play(x.animate.set_value(-1.5), run_time=2.5, rate_func=smooth)
        self.wait(0.6)

        self.play(x.animate.set_value(2.0), run_time=2.5, rate_func=smooth)
        self.wait(0.6)

        insight = Text(
            "Derivative = instantaneous slope",
            font_size=34,
            color=COLOR_ACCENT,
        ).to_edge(DOWN)

        self.play(Write(insight), run_time=1.2)
        self.wait(1.2)
