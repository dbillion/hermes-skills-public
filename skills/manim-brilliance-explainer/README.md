# Manim Brilliance Skill v3.2 (Complete Pack)

A reusable skill pack for creating 3Blue1Brown / Veritasium-inspired Manim
animations: skill definition, camera director, angle laws, topic scenes, and
a full gallery of the signature animation techniques.

ALL 21 SCENES VERIFIED on Manim Community v0.20.1 (Python 3.14).

## Pack layers

1. Skill definition: SKILL.md + prompts/ + eval/ + storyboard/
2. Style system: style/ (palette, timing, camera director, angle laws, labels)
3. Reusable shots: shots/ (hook, algebra morph, linking, tracing, annotations,
   followers, complex maps, choreography, deformation)
4. Templates: templates/ (explainer, mystery, cinematic)
5. Topic scenes: examples/topics/ (Fourier, eigenvectors, neural net, calculus, EM)
6. Technique gallery: techniques/ (the 10 signature moves, one scene each)
7. Corpus miner: corpus/ (pattern extraction from public Manim repos)

## Technique gallery

Each technique has a runnable scene in techniques/ and a reusable helper in shots/:

- matching_transforms.py    TransformMatchingTex, TransformMatchingShapes
- transform_from_copy.py    linking representations with copy-flights
- traced_path.py            a point draws its own curve
- annotations_demo.py       braces, boxes, strikethrough cancellation
- updaters.py               follower labels and tangent-tracking arrows
- rate_functions_gallery.py easing comparison (linear, ease-out, there_and_back)
- complex_mapping.py        complex plane warp z to z squared
- surfaces_3d.py            3D surface with color-by-height and 3D arrows
- choreography.py           lag_ratio cascades, AnimationGroup, Succession
- homotopy.py               continuous shape deformation

## Quickstart

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Or with uv:

    uv venv
    uv pip install -r requirements.txt

Render one technique:

    uv run manim -qm techniques/matching_transforms.py MatchingTransforms

Render one topic:

    uv run manim -qm examples/topics/fourier_epicycles.py FourierEpicycles

Render everything at low quality:

    uv run scripts/render_all.py

Output videos land in:

    media/videos/<script_name>/<quality>/<SceneName>.mp4

## Camera director presets (style/camera.py)

- 3D framing: phi about 75 deg, theta about -45 deg, zoom about 0.8
- Ambient orbit rate about 0.12 rad/s; stop the orbit before the payoff
- 2D: focus_2d zooms in on an idea, reset_2d restores context
- Lock titles in 3D with lock_to_screen

## Angle laws (style/angles.py)

- rotating_angle(t, omega, phase): theta = omega * t + phase
- fourier_angles(t, harmonics): theta_n = n * omega * t
- eigen_rotation(eigval): complex eigenvalue gives rotation angle and scale
- tangent_angle(axes, x, graph): slope as an angle

## Known harmless warnings

- pydub SyntaxWarning on Python 3.12+: dependency regex style, safe to ignore.
- 3D surfaces render slowly (minutes) even at low quality. This is normal.

## Notes

- Examples use Manim Community syntax (from manim import *).
- Manim also needs ffmpeg and LaTeX installed on your system.
- Inspired by public explanatory techniques; not a copy of proprietary assets.
- Check licenses before redistributing code or assets from external repos.
