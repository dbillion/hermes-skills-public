# Pacing constants and the easing grammar.

from manim import linear, smooth, rate_functions

FAST = 0.6
NORMAL = 1.0
SLOW = 1.8

PAUSE_SHORT = 0.5
PAUSE_MEDIUM = 0.8
PAUSE_LONG = 1.3

ORBIT_RATE = 0.12   # ambient 3D camera rotation, rad/s

# Easing grammar:
ROTATION = linear                          # spins, phases, traveling waves
ARRIVAL = rate_functions.ease_out_cubic    # objects arriving at a position
EMPHASIS = rate_functions.there_and_back   # pulses and attention bumps
DEFAULT_MOTION = smooth                    # general movement
