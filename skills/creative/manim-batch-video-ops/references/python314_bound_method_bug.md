# Python 3.14 bound-method bug — Manim Axes.plot complexity crash

## Symptom (exact)
```
TypeError: unsupported operand type(s) for /: 'Trick01NameMangling' and 'float'
```
raised at `manim/mobject/graphing/scale.py:123  return value / self.scale_factor`
inside `Axes.plot(...)` / `complexity_payoff(...)`. Happens at the LAST act
(the payoff graph), AFTER the rest of the scene rendered fine — so it looks
like a "random" late crash.

## Minimal reproduction
```python
from manim import *
class Broken(TrickScene):
    BF_COMPLEXITY = lin          # module-level function assigned as class attr
    def construct(self):
        complexity_payoff(self, self.BF_COMPLEXITY, self.OPT_COMPLEXITY, "a","b")
# self.BF_COMPLEXITY is a BOUND method in 3.14 -> lin(self, t) -> returns Scene
```
Verify the binding:
```python
import dsa_style as s
print(type(self).BF_COMPLEXITY is s.lin)   # False when broken (instance wraps it)
print(type(self).BF_COMPLEXITY(5))          # prints the Scene class, not 5
```

## Why
In Python 3.14 a function defined at class scope (e.g. `BF_COMPLEXITY = lin`)
becomes a bound method on instance access, just like a `def` method. So
`complexity_payoff(self, self.BF_COMPLEXITY, ...)` receives a bound method;
Manim calls it as `function(t)` → actually `lin(self, t)` → returns the Scene
instance → `coords_to_point(t, Scene)` → `Scene / float` → TypeError.

## Fix (in the base class helper)
```python
def play_act5_payoff(self):
    bf = type(self).BF_COMPLEXITY      # UNBOUND class attribute
    opt = type(self).OPT_COMPLEXITY
    complexity_payoff(self, bf, opt, "naive O(n^2)", "idiomatic O(n)")
```
`type(self).BF_COMPLEXITY` is the raw function (not bound).

## Related: Axes.plot arity
`Axes.plot(func, x_range=...)` calls `func(t)` with ONE argument. Helpers must
accept a single positional arg; use `def quad(t, *_): return t**2` so a stray
2nd arg (some Manim versions pass 2) is absorbed. Do NOT use a bare
`lambda t: t` either — a class-level `lambda` is ALSO bound in 3.14.

## Verification recipe
1. Standalone: `ax = Axes(...); ax.plot(lin, x_range=[0,10]); ax.plot(quad,...)`
   → both OK (proves the function itself is fine).
2. In-scene: replace `self.X` with `type(self).X` everywhere a complexity fn
   is passed to `complexity_payoff` / `Axes.plot`.
3. Re-render the previously-failing scene; it must reach "Rendered <SceneName>"
   and write the .mp4.
