from manim import Scene, Text, Write, FadeOut, Rectangle, Arrow, DOWN, RIGHT, YELLOW, RED


class VeritasiumMystery(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"

        hook = Text("This should not happen...", font_size=42)
        self.play(Write(hook))
        self.wait(0.9)
        self.play(FadeOut(hook))

        box = Rectangle(width=2.5, height=1.5, color=RED)
        expected = Text("Expected", font_size=28).next_to(box, DOWN)
        actual = Arrow(start=box.get_right(), end=box.get_right() + 2 * RIGHT, color=YELLOW)
        actual_label = Text("Actual", font_size=28).next_to(actual, DOWN)

        self.play(Create(box), Write(expected))
        self.wait(0.5)
        self.play(Create(actual), Write(actual_label))
        self.wait(1.0)
