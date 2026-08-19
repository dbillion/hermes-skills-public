from manim import Scene, Text, Write, FadeOut, MathTex, Axes, Create, Indicate, UP, YELLOW


class ThreeMinuteExplainer(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"

        title = Text("Core Question", font_size=42)
        self.play(Write(title))
        self.wait(0.8)
        self.play(FadeOut(title))

        equation = MathTex("f(x) = x^2", font_size=44)
        axes = Axes(
            x_range=[-2, 2, 1],
            y_range=[-1, 4, 1],
            axis_config={"color": "#BBBBBB", "stroke_width": 3},
            tips=False,
        )
        curve = axes.plot(lambda x: x ** 2, color="#58C4DD")

        self.play(Write(equation))
        self.play(equation.animate.to_edge(UP))
        self.play(Create(axes))
        self.play(Create(curve))
        self.play(Indicate(equation, color=YELLOW), Indicate(curve, color=YELLOW))
        self.wait(1.0)
