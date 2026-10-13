# Choreography: cascades with lag_ratio, mixed AnimationGroup, strict
# Succession. Never move 4+ elements all at once.

from manim import (
    Scene, VGroup, Square, Circle, Text, SurroundingRectangle,
    FadeIn, Create, Write, AnimationGroup, Succession,
    UP, DOWN, RIGHT, YELLOW, GREEN, RED, PI,
)


class ChoreographyDemo(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"

        squares = VGroup(*[
            Square(side_length=0.8).shift(RIGHT * i * 1.6)
            for i in range(-2, 3)
        ])

        # Cascade: each starts 15% after the previous.
        self.play(*[FadeIn(s, shift=UP) for s in squares], lag_ratio=0.15)

        # Mixed concurrent actions with stagger.
        self.play(AnimationGroup(
            squares[0].animate.set_color(YELLOW),
            squares[2].animate.shift(UP),
            squares[4].animate.rotate(PI / 4),
            lag_ratio=0.3,
        ))

        # Strict sequence inside one beat.
        circ = Circle(radius=0.4, color=GREEN)
        lab = Text("sequence", font_size=24)
        box = SurroundingRectangle(lab, color=RED)
        grp = VGroup(circ, lab, box).arrange(DOWN, buff=0.4).to_edge(DOWN)
        circ.move_to(grp[0].get_center())
        lab.move_to(grp[1].get_center())
        box.move_to(grp[2].get_center())

        self.play(Succession(Create(circ), Write(lab), Create(box)))
        self.wait(0.5)
