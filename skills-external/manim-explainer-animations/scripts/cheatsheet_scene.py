"""
Cheat-sheet scene: fires through a broad sample of mobjects, text effects,
transforms, indication, and camera moves in one file. Not meant to be a
finished video -- meant to be copy-modified from: delete the beats you
don't need, keep the patterns for the ones you do.

Render with:
    manim -pql cheatsheet_scene.py CheatSheet
"""
from manim import *

BG_COLOR = "#0e1116"
PRIMARY_BLUE = "#58C4DD"
ACCENT_YELLOW = "#FFC857"


class CheatSheet(MovingCameraScene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        # BEAT 1: title text
        title = Text("Manim capability tour", font_size=44, color="#CCCCCC")
        self.play(Write(title), run_time=1.2)
        self.wait(0.5)
        self.play(title.animate.to_edge(UP), run_time=0.8)

        # BEAT 2: geometry + indication
        circle = Circle(radius=1.2, color=PRIMARY_BLUE).shift(LEFT * 3)
        square = Square(side_length=2, color=ACCENT_YELLOW).shift(RIGHT * 3)
        self.play(Create(circle), Create(square), run_time=1.5)
        self.play(Indicate(circle), Circumscribe(square, color=ACCENT_YELLOW))
        self.wait(0.5)

        # BEAT 3: transform between shapes (ReplacementTransform)
        triangle = Triangle(color=PRIMARY_BLUE).move_to(circle)
        self.play(ReplacementTransform(circle, triangle), run_time=1.2)
        self.wait(0.5)

        # BEAT 4: MathTex with TransformMatchingTex (algebra-step morph)
        self.play(FadeOut(triangle), FadeOut(square))
        eq1 = MathTex("a", "+", "b", "=", "c")
        eq2 = MathTex("a", "=", "c", "-", "b")
        eq1.move_to(ORIGIN)
        self.play(Write(eq1), run_time=1.2)
        self.wait(0.5)
        self.play(TransformMatchingTex(eq1, eq2), run_time=1.5)
        self.wait(0.5)
        self.play(FadeOut(eq2))

        # BEAT 5: plotting a function with area-under-curve
        axes = Axes(x_range=[-3, 3, 1], y_range=[-1, 5, 1], x_length=6, y_length=4)
        graph = axes.plot(lambda x: x ** 2, color=ACCENT_YELLOW, x_range=[-2, 2])
        area = axes.get_area(graph, x_range=[0, 2], color=PRIMARY_BLUE, opacity=0.4)
        self.play(Create(axes), run_time=1)
        self.play(Create(graph), run_time=1.2)
        self.play(FadeIn(area), run_time=1)
        self.wait(0.5)
        self.play(FadeOut(VGroup(axes, graph, area)))

        # BEAT 6: updater-driven counter synced to a moving dot
        tracker = ValueTracker(0)
        counter = always_redraw(lambda: DecimalNumber(tracker.get_value(),
                                                         num_decimal_places=1,
                                                         color=ACCENT_YELLOW).to_edge(DOWN))
        dot = Dot(color=PRIMARY_BLUE).move_to(LEFT * 3)
        dot.add_updater(lambda m: m.move_to(LEFT * 3 + RIGHT * tracker.get_value()))
        self.add(counter, dot)
        self.play(tracker.animate.set_value(6), run_time=2, rate_func=linear)
        dot.clear_updaters()
        self.wait(0.5)
        self.play(FadeOut(VGroup(counter, dot)))

        # BEAT 7: camera push-in (MovingCameraScene)
        label = Text("Zoom demo", font_size=32).shift(DOWN * 0.5)
        self.play(FadeIn(label))
        self.play(self.camera.frame.animate.scale(0.5).move_to(label), run_time=1.5)
        self.wait(0.5)
        self.play(self.camera.frame.animate.scale(2).move_to(ORIGIN), run_time=1.5)

        self.play(FadeOut(title), FadeOut(label))
        self.wait(1)
