# Neural network: activations as fill opacity, weights as stroke, forward pass
# as light pulses along edges.
# Note: ShowPassingFlash already sets remover=True internally, so do not pass it.

import numpy as np
from manim import (
    Scene, VGroup, Circle, Line, FadeIn, ShowPassingFlash, BLUE_B, RED_B,
    YELLOW, WHITE,
)


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


class NeuralNetwork(Scene):
    def construct(self):
        self.camera.background_color = "#0f0f0f"
        rng = np.random.default_rng(7)
        sizes = [3, 4, 4, 2]
        X, Y = 2.4, 0.95

        layers = VGroup()
        for i, n in enumerate(sizes):
            x = (i - (len(sizes) - 1) / 2) * X
            layers.add(VGroup(*[
                Circle(
                    radius=0.25,
                    stroke_color=WHITE,
                    stroke_width=1.5,
                    fill_color=WHITE,
                    fill_opacity=0.1,
                ).move_to([x, (j - (n - 1) / 2) * Y, 0])
                for j in range(n)
            ]))

        W = [rng.normal(0, 1, (sizes[i], sizes[i + 1])) for i in range(len(sizes) - 1)]
        acts = [rng.random(sizes[0])]
        for i in range(len(sizes) - 1):
            acts.append(sigmoid(W[i].T @ acts[i]))

        edge_groups = VGroup()
        for i in range(len(sizes) - 1):
            g = VGroup()
            for a, src in enumerate(layers[i]):
                for b, dst in enumerate(layers[i + 1]):
                    w = W[i][a, b]
                    g.add(Line(
                        src.get_right(),
                        dst.get_left(),
                        stroke_width=1 + 2 * min(1, abs(w)),
                        stroke_opacity=min(1, abs(w)),
                        color=BLUE_B if w > 0 else RED_B,
                    ))
            edge_groups.add(g)

        self.play(FadeIn(edge_groups), FadeIn(layers))
        layers[0].set_fill(opacity=1)

        for i in range(len(sizes) - 1):
            self.play(*[
                ShowPassingFlash(
                    e.copy().set_stroke(YELLOW, 2),
                    run_time=0.9,
                )
                for e in edge_groups[i]
            ])
            self.play(*[
                n.animate.set_fill(opacity=acts[i + 1][j])
                for j, n in enumerate(layers[i + 1])
            ], run_time=0.5)
        self.wait()
