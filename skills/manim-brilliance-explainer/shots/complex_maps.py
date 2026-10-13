# Complex-plane warps: show a function acting on all numbers at once.

def warp_plane(scene, plane, fn, run_time=3):
    scene.play(plane.animate.apply_complex_function(fn), run_time=run_time)
    return plane
