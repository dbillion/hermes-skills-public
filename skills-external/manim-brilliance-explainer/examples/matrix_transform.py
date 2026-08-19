from manim import Scene, NumberPlane, Vector, MathTex, Create, Write, ApplyMethod, Indicate, YELLOW, GREEN, UL


BG_COLOR = "#0f0f0f"


class MatrixTransform(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        plane = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-3, 3, 1],
            background_line_style={"stroke_opacity": 0.4},
        )

        vector = Vector([1, 1], color=YELLOW)
        matrix_tex = MathTex(
            r"\begin{bmatrix}2 & 1 \\ 1 & 2\end{bmatrix}",
            font_size=42,
        ).to_corner(UL)

        matrix_values = [[2, 1], [1, 2]]

        self.play(Create(plane), Create(vector))
        self.wait(0.5)
        self.play(Write(matrix_tex))
        self.wait(0.5)

        self.play(
            ApplyMethod(plane.apply_matrix, matrix_values),
            ApplyMethod(vector.apply_matrix, matrix_values),
            run_time=2.0,
        )

        self.play(Indicate(vector, color=GREEN))
        self.wait(1.0)
