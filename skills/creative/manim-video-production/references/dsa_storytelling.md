# DSA Storytelling Pattern (manim-dsa-storytelling skill)

**Use with:** `manim-dsa-storytelling` skill (installed at ~/.hermes/skills/creative/manim-dsa-storytelling)

## 5-Act Narrative Structure (~45-90s total)

1. **Cold Open** — Problem as spatial 3D shape (array = cubes on axes, graph = torus, set = spheres)
2. **Brute Force** — Exhaustive particle sweep with synced code highlight (nested loops, dense trail)
3. **Insight** — Single beat naming the fact the optimized version exploits
4. **Optimized** — Same space, direct path, clean trail, synced highlight
4. **Payoff** — 2D complexity graph with TRUE functions (not hand-drawn)

## Non-Negotiable Rules (from skill)

- **Code-and-visual duality**: Real `Code` mobject (from notebook, not paraphrase) fixed-in-frame left; 3D space shifted right. Synced `SurroundingRectangle` tracks line numbers live.
- **Split-screen layout**: `Code` panel + 3D data space. Shift 3D group by `SCENE_SHIFT = RIGHT * 3.0`.
- **Billboard ALL text**: `add_fixed_in_frame_mobjects()` BEFORE positioning for HUD. For 3D-anchored labels: `rotate(90°*DEGREES, axis=RIGHT)` so they stand upright.
- **Camera reuse**: EXACT same `ThreeDAxes` + camera between brute and optimized beats.
- **Insight beat NOT optional**: Single text beat, full breath.
- **True complexity curves**: `Axes.plot(lambda x: x**2)` for O(n²), `lambda x: x` for O(n) — not hand-drawn.

## 3D Solid Vocabulary (from skill)

| Solid | Use For | Why |
|-------|---------|-----|
| Cube/Prism row on x-axis | Arrays, sequences | Discrete, ordered, indexable |
| Torus / torus knot | Cyclic structures | Loop is the point |
| Sphere cluster | Unordered sets / hash sets | No implied order |
| Cone/pyramid stack | Trees, heaps, recursion | Vertical taper = levels |
| Surface/mesh grid | DP tables, 2D grids | Height = DP value |

## Color Palette (Dark Studio)

- `DARK_BG = "#0e0f12"` — background
- `CUBE_COLOR = "#3a3f4b"` — data solids
- `ACCENT = "#f2a154"` — brute/naive particle & highlight
- `GOOD = "#5ad1a6"` — optimized particle & highlight
- `PANEL_BG = "#17181c"` — code panel bg

## Template Pattern (from this session)

```
base/
  template.py       # TrickScene base class with 5 acts
  tricks.yaml       # 23 configs: naive_code, idiomatic_code, input_data, solid_type, complexity curves, insight
scenes/
  trick_XX_name.py  # inherits TrickScene, implements _run_naive/_run_optimized
```

Each scene: ~9-15s, 480p15 preview → 1080p60 final → hardsub via burn_subs.sh