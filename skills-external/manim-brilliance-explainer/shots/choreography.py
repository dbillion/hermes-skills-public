# Staggered group motion: never move 4+ elements all at once.

def cascade(scene, mobjects, anim_factory, lag_ratio=0.15):
    scene.play(*[anim_factory(m) for m in mobjects], lag_ratio=lag_ratio)
