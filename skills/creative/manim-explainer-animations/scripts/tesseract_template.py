"""
Tesseract rotation + cross-section scene, 3b1b/Veritasium style.

Render with:
    manim -pql tesseract_template.py TesseractExplainer      # quick preview
    manim -pqh tesseract_template.py TesseractExplainer      # final quality
"""
from manim import *
import numpy as np

BG_COLOR = "#0e1116"
PRIMARY_BLUE = "#58C4DD"
ACCENT_YELLOW = "#FFC857"


def rotation_matrix_4d(plane: str, angle: float) -> np.ndarray:
    idx = {'x': 0, 'y': 1, 'z': 2, 'w': 3}
    i, j = idx[plane[0]], idx[plane[1]]
    m = np.eye(4)
    c, s = np.cos(angle), np.sin(angle)
    m[i, i], m[j, j] = c, c
    m[i, j], m[j, i] = -s, s
    return m


def project_4d_to_3d(v4, viewer_distance=3.0):
    x, y, z, w = v4
    denom = viewer_distance - w
    k = viewer_distance / denom if abs(denom) > 1e-6 else 1e6
    return np.array([x * k, y * k, z * k])


def tesseract_vertices():
    return np.array([[x, y, z, w]
                      for x in (-1, 1) for y in (-1, 1)
                      for z in (-1, 1) for w in (-1, 1)], dtype=float)


def tesseract_edges(verts):
    return [(i, j) for i in range(16) for j in range(i + 1, 16)
            if np.sum(verts[i] != verts[j]) == 1]


class TesseractExplainer(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)

        verts4d = tesseract_vertices()
        edges = tesseract_edges(verts4d)

        # BEAT 1: static cube first (w=... collapsed), orient the viewer
        title = Text("A tesseract is a cube extruded through a 4th axis",
                      font_size=32, color="#CCCCCC")
        self.add_fixed_in_frame_mobjects(title)
        title.to_edge(UP)
        self.play(Write(title), run_time=1.5)
        self.wait(1)

        angle = ValueTracker(0.0)

        def project(v4):
            a = angle.get_value()
            r1 = rotation_matrix_4d('xw', a)
            r2 = rotation_matrix_4d('yz', a * 0.61803)  # golden-ratio offset, never resyncs
            rotated = r1 @ r2 @ v4
            return project_4d_to_3d(rotated)

        lines = VGroup()
        for i, j in edges:
            p1, p2 = project(verts4d[i]), project(verts4d[j])
            w_avg = (verts4d[i][3] + verts4d[j][3]) / 2
            t = (w_avg + 1) / 2  # map [-1,1] -> [0,1]
            color = interpolate_color(ManimColor(PRIMARY_BLUE), ManimColor(ACCENT_YELLOW), t)
            lines.add(Line3D(p1, p2, color=color, thickness=0.015))

        # BEAT 2: sweep-reveal the wireframe being "drawn"
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.03), run_time=3)
        self.wait(1)

        def updater(group):
            for (i, j), line in zip(edges, group):
                p1, p2 = project(verts4d[i]), project(verts4d[j])
                line.put_start_and_end_on(p1, p2)

        lines.add_updater(updater)

        # BEAT 3: rotate through the two orthogonal planes together (true 4D tumble)
        self.begin_ambient_camera_rotation(rate=0.04)
        self.play(angle.animate.set_value(TAU), run_time=10, rate_func=linear)
        self.stop_ambient_camera_rotation()
        lines.remove_updater(updater)
        self.wait(1)

        # BEAT 4: payoff line
        payoff = Text("Its shadow morphs because the 4th axis is passing through our view",
                       font_size=28, color="#CCCCCC")
        self.add_fixed_in_frame_mobjects(payoff)
        payoff.to_edge(DOWN)
        self.play(Write(payoff), run_time=1.5)
        self.wait(2)
