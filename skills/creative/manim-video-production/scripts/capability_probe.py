"""
Capability probe: single-frame validation of Manim CE v0.20.1 install.
Renders one still of each major category — embed these tests in a fresh
env to confirm shapes/camera/4D before building full videos.

Usage: manim -ql -s capability_probe.py Probe3D
       manim -ql -s capability_probe.py Probe4DTesseract
       manim -ql -s capability_probe.py Probe4DHypersphere

Each renders a single frame (fast even on slow CPUs — the combined
full-video render times out on cloud runners).  Verify with PIL pixel
analysis or visual inspection of the output PNG.

Generated frames go to media/images/capability_probe/<SceneName>_ManimCE_v0.20.1.png.
Validate with:
    from PIL import Image; import numpy as np
    im = Image.open("frame.png").convert("RGB"); a = np.array(im)
    BG = np.array([14, 17, 22])
    content = (np.abs(a.astype(int) - BG.astype(int)).sum(2) > 40).sum()
    print(f"{content} content pixels (expect >5000 for 3D, >8000 for tesseract)")
"""
from manim import *
import numpy as np

BG = "#0e1116"
PRI = "#58C4DD"
ACC = "#FFC857"


class Probe3D(ThreeDScene):
    """3D shapes (sphere, cube, cone, cylinder, TORUS toroid) on Cartesian axes — single frame."""
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        axes = ThreeDAxes(x_range=[-4, 4], y_range=[-4, 4], z_range=[-3, 3])
        self.add(axes)
        sphere = Sphere(radius=0.8, fill_color=PRI, fill_opacity=0.7).move_to([-2.5, 2.5, 0])
        cube = Cube(side_length=1.3, fill_color=ACC, fill_opacity=0.7).move_to([2.5, 2.5, 0])
        cone = Cone(base_radius=0.8, height=1.6, fill_color="#FF6B6B", fill_opacity=0.7).move_to([-2.5, -2.5, 0])
        cyl = Cylinder(radius=0.6, height=1.6, fill_color="#83C167", fill_opacity=0.7).move_to([2.5, -2.5, 0])
        torus = Torus(major_radius=1.0, minor_radius=0.35, fill_color=ACC, fill_opacity=0.8).move_to([0, 0, 0])
        self.add(sphere, cube, cone, cyl, torus)


def rotation_matrix_4d(plane, angle):
    idx = {'x': 0, 'y': 1, 'z': 2, 'w': 3}
    i, j = idx[plane[0]], idx[plane[1]]
    m = np.eye(4)
    c, s = np.cos(angle), np.sin(angle)
    m[i, i], m[j, j], m[i, j], m[j, i] = c, c, -s, s
    return m


def project_4d_to_3d(v4, viewer_distance=3.0):
    x, y, z, w = v4
    denom = viewer_distance - w
    k = viewer_distance / denom if abs(denom) > 1e-6 else 1e6
    return np.array([x * k, y * k, z * k])


def tesseract_vertices():
    return np.array([[x, y, z, w] for x in (-1, 1) for y in (-1, 1)
                     for z in (-1, 1) for w in (-1, 1)], dtype=float)


def tesseract_edges(v):
    return [(i, j) for i in range(16) for j in range(i + 1, 16)
            if np.sum(v[i] != v[j]) == 1]


class Probe4DTesseract(ThreeDScene):
    """Double-rotation tesseract projection (single still at angle=pi/4)."""
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        verts = tesseract_vertices()
        edges = tesseract_edges(verts)
        a = np.pi / 4
        lines = VGroup()
        for i, j in edges:
            r1 = rotation_matrix_4d('xw', a)
            r2 = rotation_matrix_4d('yz', a * 0.61803)
            p1 = project_4d_to_3d(r1 @ r2 @ verts[i])
            p2 = project_4d_to_3d(r1 @ r2 @ verts[j])
            w_avg = (verts[i][3] + verts[j][3]) / 2
            t = (w_avg + 1) / 2
            col = interpolate_color(ManimColor(PRI), ManimColor(ACC), t)
            lines.add(Line3D(p1, p2, color=col, thickness=0.02))
        self.add(lines)


class Probe4DHypersphere(ThreeDScene):
    """Hypersphere cross-section at w=0 (mid-slice) — single frame."""
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        r = 2.0
        c = 0.0  # mid-slice
        radius = np.sqrt(max(r ** 2 - c ** 2, 1e-4))
        sphere = Sphere(radius=radius, resolution=(24, 24), fill_opacity=0.6,
                        fill_color=PRI, stroke_color=ACC, stroke_width=0.5)
        self.add(sphere)