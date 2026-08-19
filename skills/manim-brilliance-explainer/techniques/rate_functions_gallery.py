# Rate functions: the same motion under different easing laws, side by side.
# Grammar: rotations = linear, arrivals = ease-out, emphasis = there_and_back.

from manim import (
    Scene, Dot, Text, VGroup, LEFT, RIGHT, DOWN, UP,
    linear, smooth, rate_functions,
)


class RateFunctionsDemo(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"

        runs = [
            ("linear", linear),
            ("smooth", smooth),
            ("rush_into", rate_functions.rush_into),
            ("there_and_back", rate_functions.there_and_back),
            ("ease_in_out_sine", rate_functions.ease_in_out_sine),
        ]

        rows = VGroup()
        for i, (name, rf) in enumerate(runs):
            label = Text(name, font_size=22).move_to(LEFT * 4 + DOWN * i * 0.9)
            dot = Dot().next_to(label, RIGHT, buff=0.5)
            rows.add(label, dot)
        self.add(rows)

        dots = [m for m in rows if isinstance(m, Dot)]

        # Each dot runs the same shift with its own rate function.
        self.play(*[
            dot.animate(rate_func=rf, run_time=2).shift(RIGHT * 4.5)
            for dot, (_, rf) in zip(dots, runs)
        ])
        self.wait(0.4)

        # Custom easing: ease-out cubic for a soft arrival.
        extra = Dot().move_to(LEFT * 4 + DOWN * 0.5)
        self.play(
            extra.animate.shift(UP * 0 + RIGHT * 4.5),
            run_time=1.5,
            rate_func=lambda t: 1 - (1 - t) ** 3,
        )
        self.wait(0.4)
