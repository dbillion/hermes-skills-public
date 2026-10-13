# Annotations: box for focus, brace for grouping, strikethrough for
# cancellation. Cancelled terms are struck, never deleted.

from manim import (
    Scene, MathTex, SurroundingRectangle, Brace, Line,
    Write, Create, GrowFromCenter, YELLOW, RED, DOWN,
)


class AnnotationsDemo(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"

        eq = MathTex("E", "=", "m", "c^2", font_size=52)
        self.play(Write(eq))
        self.wait(0.3)

        # Focus box around one term.
        box = SurroundingRectangle(eq[3], color=YELLOW, buff=0.1)
        self.play(Create(box))
        self.wait(0.3)

        # Brace grouping several terms.
        brace = Brace(eq[2:], DOWN)
        blabel = brace.get_text("mass-energy part")
        self.play(GrowFromCenter(brace), Write(blabel))
        self.wait(0.3)

        # Cancellation: strike, do not delete.
        strike = Line(eq[2].get_left(), eq[3].get_right(), color=RED, stroke_width=4)
        self.play(Create(strike))
        self.wait(0.6)
