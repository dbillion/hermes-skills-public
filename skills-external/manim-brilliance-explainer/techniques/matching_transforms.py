# TransformMatchingTex: pieces of the equation morph into the next form.
# Split MathTex into comma-separated parts so matching works piece by piece.

from manim import (
    Scene, MathTex, Square, Circle, Write, FadeOut, Create,
    TransformMatchingTex, TransformMatchingShapes, PI, BLUE, YELLOW,
)


class MatchingTransforms(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"

        eq1 = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=48)
        eq2 = MathTex("c", "=", "\\sqrt{", "a^2", "+", "b^2", "}", font_size=48)

        self.play(Write(eq1))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq1, eq2, path_arc=PI / 4), run_time=2)
        self.wait(0.5)

        self.play(FadeOut(eq2))

        # Shapes variant: morph one shape into another while keeping parts.
        sq = Square(side_length=1.6, color=BLUE)
        ci = Circle(radius=0.9, color=YELLOW)
        self.play(Create(sq))
        self.wait(0.3)
        self.play(TransformMatchingShapes(sq, ci), run_time=1.5)
        self.wait(0.5)
