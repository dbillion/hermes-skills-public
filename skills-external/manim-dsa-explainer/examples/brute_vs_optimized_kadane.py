"""
Test render v2 for manim-dsa-storytelling skill: code-and-visual duality.
Source: Q1 maxSumSubarray (Kadane) from dsa-java-gradleqa/Algorithms.java.
Brute-force baseline is a standard idiomatic version (not present in the repo).
Real code is shown split-screen with a synced line highlight, so the
video teaches something someone could go implement.
"""
from manim import *

DARK_BG = "#0e0f12"
CUBE_COLOR = "#3a3f4b"
ACCENT = "#f2a154"
GOOD = "#5ad1a6"
PANEL_BG = "#17181c"

nums = [-2, 3, 4, -1, 2, -5, 6]

BRUTE_CODE = """static int bruteForceMaxSubarray(int[] nums) {
    int best = nums[0];
    for (int i = 0; i < nums.length; i++) {
        int sum = 0;
        for (int j = i; j < nums.length; j++) {
            sum += nums[j];
            best = Math.max(best, sum);
        }
    }
    return best;
}"""

KADANE_CODE = """public static SubarrayResult maxSumSubarray(int[] nums) {
    int bestSum = nums[0], currentSum = nums[0];
    int bestStart = 0, bestEnd = 0, currentStart = 0;
    for (int i = 1; i < nums.length; i++) {
        if (currentSum < 0) {
            currentSum = nums[i];
            currentStart = i;
        } else {
            currentSum += nums[i];
        }
        if (currentSum > bestSum) {
            bestSum = currentSum;
            bestStart = currentStart;
            bestEnd = i;
        }
    }
    return new SubarrayResult(bestSum, ...);
}"""

class BruteVsOptimizedV2(ThreeDScene):
    def construct(self):
        self.camera.background_color = DARK_BG

        # code panel lives on the LEFT as a fixed-in-frame HUD (see pitfall notes
        # in manim-dsa-storytelling/SKILL.md: text in ThreeDScene must be fixed
        # in frame or it lies flat on the xy "floor" once the camera tilts).
        # the 3D data space is shifted RIGHT so it doesn't collide with the panel.
        SCENE_SHIFT = RIGHT * 3.0

        title = Text("Maximum Subarray Sum", color=WHITE).scale(0.6)
        self.add_fixed_in_frame_mobjects(title)
        title.to_edge(UP)
        self.play(Write(title))

        self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)

        axes = ThreeDAxes(x_range=[0, len(nums), 1], y_range=[-6, 8, 2],
                           z_range=[-4, 4, 1], x_length=6.5, y_length=4, z_length=3)
        axes.shift(SCENE_SHIFT)

        cubes = VGroup()
        labels = VGroup()
        for i, n in enumerate(nums):
            h = max(abs(n) * 0.25, 0.25)
            c = Cube(side_length=0.5, fill_color=CUBE_COLOR, fill_opacity=0.9, stroke_color=WHITE)
            c.stretch_to_fit_height(h)
            c.move_to(axes.c2p(i + 0.5, 0, 0))
            c.shift(UP * h / 2)
            lbl = Text(str(n), color=WHITE).scale(0.35)
            lbl.rotate(90 * DEGREES, axis=RIGHT)
            lbl.next_to(c, DOWN, buff=0.12)
            cubes.add(c)
            labels.add(lbl)

        self.play(Create(axes), run_time=1)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in cubes], lag_ratio=0.1))
        self.play(LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.1))
        self.wait(0.3)

        # ACT 2 -- brute force: real code panel + synced line highlight
        bf_label = Text("Brute force  O(n\u00b2)", color=ACCENT).scale(0.45)
        self.add_fixed_in_frame_mobjects(bf_label)
        bf_label.to_corner(UL).shift(DOWN * 0.7)

        bf_code = Code(code_string=BRUTE_CODE, language="java",
                        formatter_style="native", background="window",
                        add_line_numbers=True, paragraph_config={"font_size": 16})
        self.add_fixed_in_frame_mobjects(bf_code)
        bf_code.scale(0.55).to_edge(LEFT, buff=0.3).shift(DOWN * 0.3)

        self.play(FadeIn(bf_label), FadeIn(bf_code))

        bf_hl = SurroundingRectangle(bf_code.code_lines[5], color=ACCENT, buff=0.05)
        self.add_fixed_in_frame_mobjects(bf_hl)
        self.play(Create(bf_hl))

        particle = Dot3D(radius=0.07, color=ACCENT)
        particle.move_to(cubes[0].get_top())
        trail = TracedPath(particle.get_center, stroke_color=ACCENT,
                            stroke_width=1.5, stroke_opacity=0.5)
        self.add(trail, particle)

        best = nums[0]
        for i in range(len(nums)):
            self.play(bf_hl.animate.move_to(bf_code.code_lines[4]), run_time=0.15)
            s = 0
            for j in range(i, len(nums)):
                s += nums[j]
                mid = (cubes[i].get_top() + cubes[j].get_top()) / 2 + UP * 0.35
                self.play(
                    particle.animate.move_to(mid),
                    bf_hl.animate.move_to(bf_code.code_lines[5]),
                    run_time=0.05, rate_func=linear,
                )
                self.play(particle.animate.move_to(cubes[j].get_top()),
                           run_time=0.05, rate_func=linear)
                if s > best:
                    best = s
                    self.play(bf_hl.animate.move_to(bf_code.code_lines[6]).set_color(GOOD),
                               run_time=0.08)
                    bf_hl.set_color(ACCENT)

        self.wait(0.2)
        self.play(FadeOut(bf_label), FadeOut(bf_code), FadeOut(bf_hl),
                   FadeOut(trail), FadeOut(particle))

        # ACT 3 -- the insight
        insight = Text("Insight: a negative running sum never helps what comes next",
                        color=WHITE).scale(0.4)
        self.add_fixed_in_frame_mobjects(insight)
        insight.to_edge(DOWN)
        self.play(Write(insight))
        self.wait(1.0)
        self.play(FadeOut(insight))

        # ACT 4 -- optimized: Kadane's real code panel + synced highlight
        opt_label = Text("Optimized: Kadane's algorithm  O(n)", color=GOOD).scale(0.45)
        self.add_fixed_in_frame_mobjects(opt_label)
        opt_label.to_corner(UL).shift(DOWN * 0.7)

        opt_code = Code(code_string=KADANE_CODE, language="java",
                         formatter_style="native", background="window",
                         add_line_numbers=True, paragraph_config={"font_size": 16})
        self.add_fixed_in_frame_mobjects(opt_code)
        opt_code.scale(0.5).to_edge(LEFT, buff=0.3).shift(DOWN * 0.2)

        self.play(FadeIn(opt_label), FadeIn(opt_code))

        opt_hl = SurroundingRectangle(opt_code.code_lines[1], color=GOOD, buff=0.05)
        self.add_fixed_in_frame_mobjects(opt_hl)
        self.play(Create(opt_hl))

        particle2 = Dot3D(radius=0.07, color=GOOD)
        particle2.move_to(cubes[0].get_top())
        trail2 = TracedPath(particle2.get_center, stroke_color=GOOD,
                             stroke_width=3, stroke_opacity=0.9)
        self.add(trail2, particle2)

        current_sum = nums[0]
        best_sum = nums[0]
        for i in range(1, len(nums)):
            self.play(particle2.animate.move_to(cubes[i].get_top()),
                       opt_hl.animate.move_to(opt_code.code_lines[4]),
                       run_time=0.3, rate_func=smooth)
            if current_sum < 0:
                current_sum = nums[i]
                self.play(opt_hl.animate.move_to(opt_code.code_lines[5]), run_time=0.2)
            else:
                current_sum += nums[i]
                self.play(opt_hl.animate.move_to(opt_code.code_lines[8]), run_time=0.2)
            self.play(opt_hl.animate.move_to(opt_code.code_lines[10]), run_time=0.15)
            if current_sum > best_sum:
                best_sum = current_sum
                self.play(opt_hl.animate.move_to(opt_code.code_lines[11]).set_color(ACCENT),
                           run_time=0.2)
                opt_hl.set_color(GOOD)

        self.wait(0.3)
        self.play(FadeOut(opt_label), FadeOut(opt_code), FadeOut(opt_hl),
                   FadeOut(trail2), FadeOut(particle2))

        # ACT 5 -- payoff: the complexity graph
        self.move_camera(phi=0, theta=-90 * DEGREES, run_time=0.5)
        self.play(FadeOut(axes), FadeOut(cubes), FadeOut(labels), FadeOut(title))

        graph_axes = Axes(x_range=[0, 10, 2], y_range=[0, 100, 20],
                           x_length=7, y_length=4,
                           axis_config={"color": WHITE}).to_edge(DOWN, buff=0.8)
        x_label = graph_axes.get_x_axis_label("n").scale(0.6)
        y_label = graph_axes.get_y_axis_label("work").scale(0.6)

        bf_curve = graph_axes.plot(lambda x: x ** 2, x_range=[0, 10], color=ACCENT)
        opt_curve = graph_axes.plot(lambda x: x * 8, x_range=[0, 10], color=GOOD)

        bf_tag = Text("brute force O(n\u00b2)", color=ACCENT).scale(0.4).next_to(bf_curve, UR, buff=0.1)
        opt_tag = Text("Kadane O(n)", color=GOOD).scale(0.4).next_to(opt_curve.get_end(), UP, buff=0.15)

        self.play(Create(graph_axes), Write(x_label), Write(y_label))
        self.play(Create(bf_curve), Write(bf_tag), run_time=1.2)
        self.play(Create(opt_curve), Write(opt_tag), run_time=1.2)
        self.wait(1.2)
