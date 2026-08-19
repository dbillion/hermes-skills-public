# 4D Math Reference

All functions below use plain `numpy`, independent of Manim, so they can be unit-tested before wiring into a Scene.

## 1. The six 4D rotation planes

In 3D there are 3 rotation planes (xy, yz, xz — equivalently "rotation around an axis"). In 4D there is no single "axis" of rotation; rotations happen *in a plane*, and 4D has **6** independent coordinate planes: `xy, xz, xw, yz, yw, zw`.

```python
import numpy as np

def rotation_matrix_4d(plane: str, angle: float) -> np.ndarray:
    """Returns a 4x4 rotation matrix for one of the six coordinate planes.
    plane in {'xy','xz','xw','yz','yw','zw'}
    """
    idx = {'x': 0, 'y': 1, 'z': 2, 'w': 3}
    i, j = idx[plane[0]], idx[plane[1]]
    m = np.eye(4)
    c, s = np.cos(angle), np.sin(angle)
    m[i, i] = c
    m[j, j] = c
    m[i, j] = -s
    m[j, i] = s
    return m
```

**Key visual fact:** rotating in the `xw` plane alone leaves `y` and `z` fixed — from a 3D-viewer's perspective this looks like the shape "morphing" as w-depth changes, NOT a familiar spin. Rotating simultaneously in two *orthogonal* planes that share no axis (e.g. `xw` and `yz` together) produces a "double rotation" — the signature tumbling look of a true 4D rotation, and what makes tesseract animations look genuinely 4-dimensional rather than like a spinning cube with a gimmick.

```python
def double_rotate(vertices_4d, angle, plane_a='xw', plane_b='yz', ratio=1.0):
    ra = rotation_matrix_4d(plane_a, angle)
    rb = rotation_matrix_4d(plane_b, angle * ratio)
    return vertices_4d @ ra.T @ rb.T
```

`ratio` != 1 (e.g. golden-ratio-irrational) avoids the rotation ever repeating/synchronizing, which reads as more organic over a long ambient rotation.

## 2. Projection: 4D → 3D

### Perspective projection (preferred — matches viewer intuition)

Treat `w` like `z` is treated in normal 3D→2D perspective: things further away in `w` are smaller.

```python
def project_4d_to_3d(v4, viewer_distance=3.0):
    x, y, z, w = v4
    denom = viewer_distance - w
    k = viewer_distance / denom if abs(denom) > 1e-6 else 1e6
    return np.array([x * k, y * k, z * k])
```

Choose `viewer_distance` > max |w| in your shape (for a unit tesseract, |w| <= 1, so distance=3 is safe and gives a visible but not extreme perspective effect). Too close to the shape and it inverts/explodes near the projection singularity — keep `viewer_distance` comfortably larger than the shape's extent.

### Orthographic projection (simpler, flatter — use only for comparison/teaching moments)

```python
def project_4d_to_3d_ortho(v4):
    return v4[:3]  # just drop w
```

Use orthographic briefly, side-by-side with perspective, if you want a teaching beat that shows *why* perspective is needed — this is a move Grant Sanderson uses to build viewer trust in the projection.

## 3. Cross-sections (the "hyperplane slice" technique)

Veritasium and 3b1b both lean on cross-sections heavily because they turn an unshowable 4D object into a sequence of ordinary, showable 3D shapes.

To slice a 4D shape with the hyperplane `w = c`:

```python
def slice_edges_at_w(vertices_4d, edges, c):
    """Returns 3D points where edges of a 4D wireframe cross the w=c hyperplane."""
    points = []
    for i, j in edges:
        w_i, w_j = vertices_4d[i][3], vertices_4d[j][3]
        if (w_i - c) * (w_j - c) < 0:  # edge crosses the hyperplane
            t = (c - w_i) / (w_j - w_i)
            point_4d = vertices_4d[i] + t * (vertices_4d[j] - vertices_4d[i])
            points.append(point_4d[:3])
    return points
```

Animate `c` sweeping from `-1` to `1` (for a unit tesseract) with a `ValueTracker` — the classic payoff is: cube → larger cube (truncated) → cuboctahedron-like shape at c=0 → shrinks back → point. For a **hypersphere** (4D ball, radius r), slicing at `w=c` gives an ordinary 3D sphere of radius `sqrt(r^2 - c^2)` — this is the cleanest possible cross-section demo and a good "second example" after the tesseract, since the radius formula is one line and immediately verifiable by the audience.

```python
def hypersphere_cross_section_radius(r, c):
    return np.sqrt(max(r**2 - c**2, 0))
```

## 4. Vertex/edge/face counting (for the "counting the pattern" beat)

For an n-dimensional hypercube:
- vertices: `2**n`
- edges: `n * 2**(n-1)`
- k-dimensional faces in general: `C(n, k) * 2**(n-k)` (combinations formula)

```python
from math import comb

def hypercube_k_faces(n, k):
    return comb(n, k) * 2 ** (n - k)
```

Show this table live (n=1..4) — it's a strong "predict the next row" moment right before revealing the tesseract has 16 vertices / 32 edges / 24 faces / 8 cubic cells.

## 5. Generalizing beyond 4D

Everything above generalizes to n dimensions by:
- Using `n`-length coordinate vectors and an `n x n` rotation matrix acting on any 2 of the `n` axes (there are `C(n,2)` rotation planes total).
- Projecting recursively: project n→(n-1) with the perspective formula (divide by distance minus the highest coordinate), repeat until you reach 3D.
- This recursive-projection technique is exactly how to build a "5D shape" demo as a bonus/stretch beat if the user wants to go further than a tesseract.

