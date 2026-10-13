# Algebraic manipulation: pieces of the equation morph into the next form.
# Split MathTex into comma-separated parts so matching works piece by piece.

from manim import TransformMatchingTex, PI


def morph_equation(scene, eq_from, eq_to, path_arc=PI / 4, run_time=1.5):
    scene.play(
        TransformMatchingTex(eq_from, eq_to, path_arc=path_arc),
        run_time=run_time,
    )
    return eq_to
