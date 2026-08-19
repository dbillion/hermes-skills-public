from manim import Text, UR, GREY_B


def make_label(text, target, direction=UR, buff=0.2, font_size=28):
    label = Text(text, font_size=font_size, color=GREY_B)
    label.next_to(target, direction, buff=buff)
    return label
