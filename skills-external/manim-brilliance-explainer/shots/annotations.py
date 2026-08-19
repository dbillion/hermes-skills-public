# Live labeling: boxes for focus, braces for grouping, strikethrough for
# cancellation. Cancelled terms are struck, never deleted.

from manim import (
    SurroundingRectangle, Brace, Line,
    Create, GrowFromCenter, Write, YELLOW, RED, DOWN,
)


def box_term(scene, term, color=YELLOW, buff=0.08):
    box = SurroundingRectangle(term, color=color, buff=buff)
    scene.play(Create(box))
    return box


def brace_group(scene, group, label_text, direction=DOWN):
    brace = Brace(group, direction)
    label = brace.get_text(label_text)
    scene.play(GrowFromCenter(brace), Write(label))
    return brace, label


def strike_term(scene, term, color=RED):
    strike = Line(term.get_left(), term.get_right(), color=color, stroke_width=4)
    scene.play(Create(strike))
    return strike
