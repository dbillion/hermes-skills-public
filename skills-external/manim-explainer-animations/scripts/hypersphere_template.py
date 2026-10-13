"""
4D hypersphere (glome) cross-section scene, 3b1b/Veritasium style.
Slicing a 4-ball of radius r at w=c gives an ordinary 3D sphere of
radius sqrt(r^2 - c^2) -- animate c sweeping through the ball.

Render with:
    manim -pql hypersphere_template.py HypersphereSlice
"""
from manim import *
import numpy as np

BG_COLOR = "#0e1116"
PRIMARY_BLUE = "#58C4DD"
ACCENT_YELLOW = "#FFC857"


class HypersphereSlice(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)

        r = 2.0
        c_tracker = ValueTracker(-r)

        axes = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-3, 3])
        self.add(axes)

        title = Text("Slicing a 4D ball with a hyperplane w = c",
                      font_size=30, color="#CCCCCC")
        self.add_fixed_in_frame_mobjects(title)
        title.to_edge(UP)
        self.play(Write(title), run_time=1.2)

        formula = MathTex(r"\text{radius} = \sqrt{r^2 - c^2}",
                           color=ACCENT_YELLOW, font_size=36)
        self.add_fixed_in_frame_mobjects(formula)
        formula.to_edge(DOWN)
        self.play(Write(formula), run_time=1.2)
        self.wait(0.5)

        def make_sphere():
            c = c_tracker.get_value()
            radius = np.sqrt(max(r ** 2 - c ** 2, 1e-4))
            t = (c + r) / (2 * r)  # map [-r, r] -> [0, 1] for color
            color = interpolate_color(ManimColor(PRIMARY_BLUE), ManimColor(ACCENT_YELLOW), t)
            return Sphere(radius=radius, resolution=(24, 24), fill_opacity=0.6,
                          fill_color=color, stroke_color=color, stroke_width=0.5)

        sphere = always_redraw(make_sphere)
        self.play(FadeIn(sphere), run_time=1)
        self.wait(0.5)

        self.begin_ambient_camera_rotation(rate=0.03)
        # sweep the slicing hyperplane all the way through the ball and back
        self.play(c_tracker.animate.set_value(r), run_time=5, rate_func=there_and_back)
        self.stop_ambient_camera_rotation()
        self.wait(1)

        payoff = Text("A sphere that grows then shrinks IS a 4D ball, one slice at a time",
                       font_size=26, color="#CCCCCC")
        self.remove(title, formula)
        self.add_fixed_in_frame_mobjects(payoff)
        payoff.to_edge(UP)
        self.play(Write(payoff), run_time=1.5)
        self.wait(2)
