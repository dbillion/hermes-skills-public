# Complex-plane warps: show a function acting on every number at once.
# Points move according to f(z); the grid is the object that transforms.

from manim import Scene, ComplexPlane, MathTex, Create, Write, BLUE, UL


class ComplexMappingDemo(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"

        plane = ComplexPlane(
            axis_config={"include_numbers": False, "stroke_width": 1.5}
        )
        label = MathTex(r"z \to z^2", font_size=40, color=BLUE).to_corner(UL)

        self.play(Create(plane), Write(label))
        self.wait(0.4)

        self.play(
            plane.animate.apply_complex_function(lambda z: z ** 2),
            run_time=3,
        )
        self.wait(0.5)
