from manim import Text, Write, FadeOut, Indicate


def title_hook(scene, text, wait_time=0.8, run_time=1.1):
    title = Text(text, font_size=42)
    scene.play(Write(title), run_time=run_time)
    scene.wait(wait_time)
    scene.play(FadeOut(title))
    return title


def emphasize(scene, mobject, color="#FFFF00"):
    scene.play(Indicate(mobject, color=color, scale_factor=1.08))
