# Angle laws: every rotation in these animations is angle = f(t).
# Use rate_func=linear when driving these with ValueTracker.

import numpy as np
from manim import PI


def rotating_angle(t, omega=1.0, phase=0.0):
    # Uniform rotation: theta(t) = omega * t + phase
    return omega * t + phase


def fourier_angles(t, harmonics, omega=1.0):
    # Epicycle angle for each harmonic: theta_n(t) = n * omega * t
    return [n * omega * t for n in harmonics]


def unit_vector(angle):
    return np.array([np.cos(angle), np.sin(angle), 0.0])


def eigen_rotation(eigval):
    # Complex eigenvalue -> (rotation angle, scale factor).
    # Example: eigval = 1 + 1j gives 45 degrees and sqrt(2).
    return float(np.angle(eigval)), float(np.abs(eigval))


def tangent_angle(axes, x, graph):
    # Slope of a graph expressed as an angle (radians).
    return axes.angle_of_tangent(x, graph)


def deg(rad):
    return float(rad * 180.0 / PI)
