# Follower objects via add_updater. Unlike always_redraw, the follower is
# MUTATED in place, so it keeps its identity for later transforms.
# Prefer m.become(new) over deprecated methods like set_text.
# Remember to call follower.clear_updaters() when the following is over.

from manim import UP


def follow(scene, follower, target, direction=UP, buff=0.15):
    def update(m):
        if direction is None:
            m.move_to(target.get_center())
        else:
            m.next_to(target, direction, buff=buff)
    follower.add_updater(update)
    scene.add(follower)
    return follower


def connect_between(scene, arrow, start_mob, end_mob):
    def update(m):
        m.put_start_and_end_on(start_mob.get_center(), end_mob.get_center())
    arrow.add_updater(update)
    scene.add(arrow)
    return arrow
