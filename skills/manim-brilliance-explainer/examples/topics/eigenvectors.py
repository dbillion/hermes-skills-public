# Eigenvectors: transform the whole plane, show which vectors stay on their span.

import numpy as np
from manim import (
    Scene, NumberPlane, Vector, DashedLine, MathTex, Create, Write,
    ApplyMethod, Indicate, GrowArrow, YELLOW, GREEN, RED, UL, DL,
)


class Eigenvectors(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"

        M = [[2, 1], [1, 2]]   # eigenvalues 3 and 1

        plane = NumberPlane(background_line_style={"stroke_opacity": 0.4})

        d1 = np.array([1, 1, 0]) / np.sqrt(2)
        d2 = np.array([1, -1, 0]) / np.sqrt(2)
        span1 = DashedLine(-3.5 * d1, 3.5 * d1, color=YELLOW)
        span2 = DashedLine(-3.5 * d2, 3.5 * d2, color=GREEN)

        v1 = Vector([1, 1], color=YELLOW)     # eigenvector, eigenvalue 3
        v2 = Vector([1, -1], color=GREEN)     # eigenvector, eigenvalue 1
        v3 = Vector([1.5, 0], color=RED)      # normal vector, for contrast

        self.play(Create(plane), GrowArrow(v1), GrowArrow(v2), GrowArrow(v3))
        self.play(Create(span1), Create(span2))
        self.wait(0.5)

        self.play(
            ApplyMethod(plane.apply_matrix, M),
            ApplyMethod(v1.apply_matrix, M),
            ApplyMethod(v2.apply_matrix, M),
            ApplyMethod(v3.apply_matrix, M),
            ApplyMethod(span1.apply_matrix, M),
            ApplyMethod(span2.apply_matrix, M),
            run_time=2,
        )
        self.wait(0.5)

        self.play(Indicate(v1, color=YELLOW), Indicate(v2, color=GREEN))
        self.play(
            Write(MathTex(r"A v_1 = 3\,v_1", color=YELLOW).to_corner(UL)),
            Write(MathTex(r"A v_2 = 1\,v_2", color=GREEN).to_corner(DL)),
        )
        self.wait()
