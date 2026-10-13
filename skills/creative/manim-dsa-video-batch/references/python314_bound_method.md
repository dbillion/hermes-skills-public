# Python 3.14 Bound-Method Trap (Manim complexity graph crash)

## Symptom
A scene that calls `complexity_payoff(self, self.BF_COMPLEXITY, self.OPT_COMPLEXITY, ...)`
or `Axes.plot(self.BF_COMPLEXITY, ...)` crashes at the complexity-graph act with:

```
TypeError: unsupported operand type(s) for /: 'Trick01NameMangling' and 'float'
  File ".../manim/mobject/graphing/scale.py", line 123, in inverse_function
    return value / self.scale_factor
```

The `'Trick01NameMangling'` (the Scene CLASS) is being used as the y-value.

## Root cause
In Python 3.14, a plain function assigned as a **class attribute** becomes a
**bound method** when accessed on an instance — just like a normally-defined
method. So:

```python
class Trick(Scene):
    BF_COMPLEXITY = lin          # module-level function, e.g. def lin(t,*_): return t

t = Trick()
type(t.BF_COMPLEXITY)   # <class 'method'>   <- BOUND, not the function!
t.BF_COMPLEXITY(5)      # returns Trick instance (self leaked in), NOT 5
```

`complexity_payoff` then calls `function(t)` → returns the Scene → Manim does
`Scene / float` → TypeError.

A `lambda t, *_: t` assigned at class level ALSO binds — same failure.

## The fix
Pass the **class-level** (unbound) attribute, not the instance attribute:

```python
def play_act5_payoff(self):
    bf = type(self).BF_COMPLEXITY      # unbound function reference
    opt = type(self).OPT_COMPLEXITY
    complexity_payoff(self, bf, opt, "naive O(n²)", "optimized O(n)")
```

Verify in a quick REPL:
```python
import dsa_style as s, inspect
class T(TrickScene): pass
T.BF_COMPLEXITY is s.lin          # True  (class level = the function)
type(T().BF_COMPLEXITY)           # <class 'method'>  (instance = bound!)
type(T).BF_COMPLEXITY is s.lin    # True  (use THIS)
```

## How to catch it early
Before a 55-scene batch, test-render ONE scene that uses the complexity graph
(e.g. a 5-act comparison scene) plus ONE additive-shape scene (torus/cone/prism)
to surface this and any shapes3d API mismatch at runtime, not after 50 renders.
