"""
Algebra-step derivation, 3b1b-style: each equation morphs into the next
via TransformMatchingTex, so matching terms glide into place instead of
cross-fading. This pattern generalizes to any multi-step derivation.

Render with:
    manim -pql algebra_steps_template.py QuadraticDerivation
"""
from manim import *

BG_COLOR = "#0e1116"
ACCENT_YELLOW = "#FFC857"


class QuadraticDerivation(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        title = Text("Completing the square", font_size=36, color="#CCCCCC").to_edge(UP)
        self.play(Write(title), run_time=1)

        steps = [
            MathTex("x^2", "+", "6x", "+", "5", "=", "0"),
            MathTex("x^2", "+", "6x", "=", "-5"),
            MathTex("x^2", "+", "6x", "+", "9", "=", "-5", "+", "9"),
            MathTex("(x", "+", "3)^2", "=", "4"),
            MathTex("x", "+", "3", "=", r"\pm 2"),
            MathTex("x", "=", "-3", r"\pm 2"),
        ]
        for step in steps:
            step.move_to(ORIGIN)

        current = steps[0]
        self.play(Write(current), run_time=1.2)
        self.wait(1)

        for nxt in steps[1:]:
            self.play(TransformMatchingTex(current, nxt), run_time=1.5)
            self.wait(1)
            current = nxt

        self.play(Circumscribe(current, color=ACCENT_YELLOW, fade_out=True), run_time=1.5)
        self.wait(1)
