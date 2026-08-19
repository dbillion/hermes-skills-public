from manim import *

BG = "#1C1C1C"; NAIVE = "#FF6B6B"; COUNTER = "#83C167"; MONO = "Menlo"

class TrickExplainer(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=65*DEGREES, theta=-20*DEGREES,
                                     zoom=1.0, frame_center=[0,0,0])

        # TITLE
        title = Text("trick name", font_size=46, color="#58C4DD", font=MONO, weight=BOLD)
        self.play(Write(title), subcaption="Trick N: ...")
        self.wait(1.0)
        self.play(title.animate.move_to([-3.5, 3.6, 0]).scale(0.5))

        # NAIVE branch (objects LEFT, camera fixed)
        code = "..."  # real code from repo
        code_m = Code(code_string=code, language="python",
                      paragraph_config={"font_size": 13}).move_to([-3.0, -0.2, 0])
        self.add_fixed_in_frame_mobjects(code_m); self.remove(code_m)
        cubes = VGroup(*[Square(0.26, fill_color=NAIVE, fill_opacity=0.7)
                         .move_to([-3.6, -1.2+i*0.32, 0]) for i in range(4)])
        self.play(FadeIn(code_m), subcaption="naive: ...")
        self.play(LaggedStart(*[GrowFromCenter(c) for c in cubes], lag_ratio=0.15),
                  subcaption="why it fails")

        # COUNTER branch (objects RIGHT)
        self.play(FadeOut(code_m), FadeOut(cubes))
        code2 = "..."  # strong code
        code2_m = Code(code_string=code2, language="python",
                       paragraph_config={"font_size": 13}).move_to([3.0, -0.2, 0])
        self.add_fixed_in_frame_mobjects(code2_m); self.remove(code2_m)
        self.play(FadeIn(code2_m), subcaption="strong: one pass")

        # ANIMATED diagram (node-by-node, NOT a static PNG)
        self.play(FadeOut(code2_m))
        stream = Text("input", font_size=18, color=WHITE, font=MONO).move_to([0, 2.4, 0])
        dia = SurroundingRectangle(Text("branch?", font_size=16, color=WHITE, font=MONO)).move_to([0,1.2,0])
        arr = Arrow([0,0.7,0], [-2.6,0.9,0], color=NAIVE, stroke_width=3)
        self.add_fixed_in_frame_mobjects(VGroup(stream, dia, arr)); self.remove(VGroup(stream, dia, arr))
        self.play(LaggedStart(Create(arr), FadeIn(stream), FadeIn(dia)), subcaption="flow")

        # WHY: complexity bars (centered, no orbit)
        self.play(FadeOut(stream), FadeOut(dia), FadeOut(arr))
        bar = Prism(dimensions=[1.0,2.2,1.0], fill_color=COUNTER).move_to([0,-0.3,0])
        self.play(GrowFromCenter(bar), subcaption="O(n), one pass")

        # RECAP (billboarded, centered)
        recap = Text("takeaway", font_size=24, color="#83C167", font=MONO).move_to([0,0,0])
        self.add_fixed_in_frame_mobjects(recap); self.remove(recap)
        self.play(Write(recap), subcaption="reach for the stdlib")
        self.wait(2.0)

if __name__ == "__main__":
    pass
# Render: manim -ql script.py TrickExplainer
# Then: ffmpeg burn merged.srt (see scripts/hardsub.sh)
