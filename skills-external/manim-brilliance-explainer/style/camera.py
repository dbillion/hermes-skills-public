# Camera director: the 3B1B cinematography as reusable functions.
#
# 3D semantics:
#   phi   = tilt from straight above (0 = top-down, 90 = side). Use 70-80.
#   theta = azimuth around the z-axis. Use -30 to -60.
#   zoom  = overall scale. About 0.8.
#
# 2D semantics (MovingCameraScene):
#   zoom in  = focus on one idea
#   zoom out = restore context

from manim import ORIGIN, DEGREES

DEFAULT_PHI = 75 * DEGREES
DEFAULT_THETA = -45 * DEGREES
DEFAULT_ZOOM = 0.8
DEFAULT_2D_WIDTH = 14.2


def set_standard_3d_view(scene, phi=None, theta=None, zoom=None):
    scene.set_camera_orientation(
        phi=DEFAULT_PHI if phi is None else phi,
        theta=DEFAULT_THETA if theta is None else theta,
        zoom=DEFAULT_ZOOM if zoom is None else zoom,
    )


def dolly(scene, phi=None, theta=None, zoom=None, frame_center=None, run_time=2.0):
    kwargs = {"run_time": run_time}
    if phi is not None:
        kwargs["phi"] = phi
    if theta is not None:
        kwargs["theta"] = theta
    if zoom is not None:
        kwargs["zoom"] = zoom
    if frame_center is not None:
        kwargs["frame_center"] = frame_center
    scene.move_camera(**kwargs)


def orbit(scene, rate=0.12):
    scene.begin_ambient_camera_rotation(rate=rate)


def stop_orbit(scene):
    scene.stop_ambient_camera_rotation()


def lock_to_screen(scene, *mobjects):
    # Keep titles/labels screen-fixed while the 3D world rotates.
    scene.add_fixed_in_frame_mobjects(*mobjects)


def focus_2d(scene, mobject, width_factor=1.6, run_time=0.8):
    frame = scene.camera.frame
    target_width = max(mobject.width, mobject.height, 0.5) * width_factor
    scene.play(
        frame.animate.set(width=target_width).move_to(mobject),
        run_time=run_time,
    )


def reset_2d(scene, width=None, run_time=0.8):
    frame = scene.camera.frame
    scene.play(
        frame.animate.set(
            width=DEFAULT_2D_WIDTH if width is None else width
        ).move_to(ORIGIN),
        run_time=run_time,
    )
