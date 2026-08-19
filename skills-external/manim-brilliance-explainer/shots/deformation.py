# Continuous deformation: one shape becomes another without cutting.
# The homotopy function maps (x, y, z, t) -> (x, y, z).

from manim import Homotopy


def deform(scene, mobject, homotopy_fn, run_time=2):
    scene.play(Homotopy(homotopy_fn, mobject), run_time=run_time)
    return mobject
