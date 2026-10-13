"""
A2: Merge Sort -- single-path walkthrough (manim-dsa-single-path skill).
Source: dsa-java-gradleqa/Algorithms.java mergeSort()/mergeSorted() (real, verbatim).
Sample test: [5,2,8,1,9] -> [1,2,5,8,9]  (AlgorithmsTest.A2_mergeSort)
"""
from manim import *
from dsa_style import DARK_BG, CUBE_COLOR, ACCENT, GOOD, SCENE_SHIFT, make_cube_row, fixed_title, code_panel, make_highlight, test_panel

arr = [5, 2, 8, 1, 9]

CODE = """public static int[] mergeSort(int[] a) {
    if (a.length < 2) return a;
    int mid = a.length / 2;
    int[] left = mergeSort(Arrays.copyOfRange(a, 0, mid));
    int[] right = mergeSort(Arrays.copyOfRange(a, mid, a.length));
    return mergeSorted(left, right);
}
private static int[] mergeSorted(int[] l, int[] r) {
    int[] out = new int[l.length + r.length]; int i=0, j=0, k=0;
    while (i < l.length && j < r.length) out[k++] = l[i] <= r[j] ? l[i++] : r[j++];
    while (i < l.length) out[k++] = l[i++];
    while (j < r.length) out[k++] = r[j++];
    return out;
}"""


class MergeSortWalkthrough(ThreeDScene):
    def construct(self):
        self.camera.background_color = DARK_BG
        title = fixed_title(self, "Merge Sort")
        self.play(Write(title))
        self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)

        axes = ThreeDAxes(x_range=[0, len(arr), 1], y_range=[0, 10, 2],
                           z_range=[-4, 4, 1], x_length=6.5, y_length=4, z_length=3)
        axes.shift(SCENE_SHIFT)
        cubes, labels = make_cube_row(axes, arr, height_scale=0.4)

        self.play(Create(axes), run_time=1)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in cubes], lag_ratio=0.1))
        self.play(LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.1))
        self.wait(0.3)

        # Act 2 -- the walkthrough
        label, code = code_panel(self, CODE, "mergeSort()", GOOD, scale=0.45)
        self.play(FadeIn(label), FadeIn(code))
        hl = make_highlight(self, code, 3, GOOD)
        self.play(Create(hl))

        # visualize split: separate halves vertically to show recursion, then merge back sorted
        n = len(arr)
        mid = n // 2
        self.play(hl.animate.move_to(code.code_lines[3]),
                   *[cubes[i].animate.shift(UP * 0.6) for i in range(mid)],
                   *[cubes[i].animate.shift(DOWN * 0.6) for i in range(mid, n)], run_time=0.6)
        self.wait(0.3)

        def merge_sort(indices):
            if len(indices) < 2:
                return indices
            m = len(indices) // 2
            left = merge_sort(indices[:m])
            right = merge_sort(indices[m:])
            self.play(hl.animate.move_to(code.code_lines[9]), run_time=0.15)
            merged = sorted(left + right, key=lambda i: arr[i])
            anims = []
            for pos, idx in enumerate(merged):
                anims.append(cubes[idx].animate.move_to(axes.c2p(pos + 0.5, 0, 0)).shift(
                    UP * max(abs(arr[idx]) * 0.4, 0.4) / 2))
            self.play(*anims, run_time=0.5)
            return merged

        merge_sort(list(range(n)))
        self.play(hl.animate.move_to(code.code_lines[0]).set_color(ACCENT), run_time=0.2)

        self.wait(0.3)
        self.play(FadeOut(label), FadeOut(code), FadeOut(hl))

        # Act 3 -- key property
        insight = Text("Key property: merging two already-sorted halves takes one linear pass",
                        color=WHITE).scale(0.38)
        self.add_fixed_in_frame_mobjects(insight)
        insight.to_edge(DOWN)
        self.play(Write(insight))
        self.wait(1.0)
        self.play(FadeOut(insight))

        # Act 4 -- payoff
        result = Text("sorted  --  O(n log n)", color=ACCENT).scale(0.5)
        self.add_fixed_in_frame_mobjects(result)
        result.to_edge(DOWN)
        self.play(Write(result))
        self.wait(1.0)

        # Act 5 -- Verified by test (real JUnit @Test)
        tcode = ("@Test void A2_mergeSort() {\n"
                 "    assertArrayEquals(new int[]{1,2,5,8,9},\n"
                 "        Algorithms.mergeSort(new int[]{5,2,8,1,9}));\n"
                 "}")
        tl, tc, tk = test_panel(self, tcode, "input [5,2,8,1,9] -> [1,2,5,8,9]")
        self.play(FadeIn(tl), FadeIn(tc), FadeIn(tk))
        self.wait(1.6)
        self.play(FadeOut(tl), FadeOut(tc), FadeOut(tk))

        self.play(FadeOut(axes), FadeOut(cubes), FadeOut(labels), FadeOut(title), FadeOut(result))
