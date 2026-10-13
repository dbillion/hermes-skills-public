# Link two representations: a copy of the source flies to the target while
# the original stays. Then a dashed line keeps them visually connected.

from manim import TransformFromCopy, DashedLine, Create, GREY_B


def link_term_to_target(scene, term, target, keep_link=True):
    scene.play(TransformFromCopy(term, target), run_time=1.4)
    if keep_link:
        link = DashedLine(
            term.get_bottom(), target.get_top(),
            stroke_width=1.5, color=GREY_B,
        )
        scene.play(Create(link), run_time=0.6)
        return link
    return None
