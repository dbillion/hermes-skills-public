from manim import MathTex, Axes, Write, Create, Indicate, UP, YELLOW


def equation_to_graph(scene, latex, func, x_range=None):
    equation = MathTex(latex, font_size=44)
    axes = Axes(
        x_range=[-3, 3, 1],
        y_range=[-2, 4, 1],
        axis_config={
            "color": "#BBBBBB",
            "stroke_width": 3,
            "include_ticks": False,
        },
        tips=False,
    )

    if x_range is None:
        curve = axes.plot(func, color="#58C4DD")
    else:
        curve = axes.plot(func, x_range=x_range, color="#58C4DD")

    scene.play(Write(equation))
    scene.wait(0.6)
    scene.play(equation.animate.to_edge(UP))
    scene.play(Create(axes), run_time=1.0)
    scene.play(Create(curve), run_time=1.4)
    scene.play(Indicate(equation, color=YELLOW), Indicate(curve, color=YELLOW))
    scene.wait(0.7)

    return equation, axes, curve
