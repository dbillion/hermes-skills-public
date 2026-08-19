# TransformFromCopy: a COPY of the source flies to the target representation
# while the original stays. The dashed line keeps them connected.

from manim import (
    Scene, MathTex, Axes, Dot, DashedLine, Write, Create,
    TransformFromCopy, UP, BLUE, YELLOW, GREY_B,
)


class TransformFromCopyDemo(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"

        eq = MathTex("f(x)", "=", "x^2", font_size=44).to_edge(UP)
        axes = Axes(
            x_range=[-2, 2],
            y_range=[-1, 4],
            axis_config={"include_ticks": False},
            tips=False,
        )
        graph = axes.plot(lambda x: x ** 2, color=BLUE)
        dot = Dot(axes.i2gp(1.5, graph), color=YELLOW)

        self.play(Write(eq), Create(axes), Create(graph))
        self.wait(0.4)

        # The term x^2 flies down to become its point on the curve.
        self.play(TransformFromCopy(eq[2], dot), run_time=1.5)

        link = DashedLine(eq[2].get_bottom(), dot.get_top(),
                          stroke_width=1.5, color=GREY_B)
        self.play(Create(link))
        self.wait(0.5)
