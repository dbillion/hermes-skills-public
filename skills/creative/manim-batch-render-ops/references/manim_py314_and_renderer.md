# Manim + Python 3.14 gotcha and renderer benchmark

## The bound-method crash
On Python 3.14, a function stored as a class attribute is BOUND when read via `self`:
```python
class Trick01NameMangling(ThreeDScene):
    BF_COMPLEXITY = lambda n: n            # module-level intent: callable
    def construct(self):
        self.complexity_payoff(self.BF_COMPLEXITY, ...)   # self.BF_COMPLEXITY -> the Scene!
```
`self.BF_COMPLEXITY` returns the *instance* (because Py3.14 binds class-level functions),
so `payoff(self.BF_COMPLEXITY, x)` raises:
`TypeError: unsupported operand type(s) for /: 'Trick01NameMangling' and 'float'`

### Fix
Pass the unbound function through `type(self)`:
```python
bf = type(self).BF_COMPLEXITY
opt = type(self).OPT_COMPLEXITY
self.complexity_payoff(bf, opt, ...)
```
Verified: debug scene printed `PAYOFF OK`, call result `5`. Applies to any base-class
complexity helper (e.g. `dsa_style.play_act5_payoff`).

## Renderer benchmark (ThinkPad T470, i5-7200U, Intel HD 620 iGPU)
Timed on a trivial scene, `-ql` tier:
- Cairo: ~8.8 s
- OpenGL: ~15.2 s

Conclusion: on this weak iGPU, **use `--renderer=cairo -ql`** for batch work. OpenGL was
~1.7x slower here.

### Why OpenGL "hung" before
Earlier an OpenGL render appeared to hang. Root cause: the automation shell had no `DISPLAY`
exported. OpenGL backend needs `DISPLAY=:1` (or WAYLAND_DISPLAY). With DISPLAY set,
`manim --renderer=opengl -ql` ran fine (exit 0, real mp4). So: don't assume OpenGL is
broken on this hardware — check `DISPLAY` first. X11: `echo $DISPLAY` (expect `:1`);
Wayland: `echo $WAYLAND_DISPLAY`.

### Quality tier
`-ql` is the right tier for a 2-core CPU / 55-83 video batches. Reserve `-qh` for a final
pass on a stronger machine if needed.
