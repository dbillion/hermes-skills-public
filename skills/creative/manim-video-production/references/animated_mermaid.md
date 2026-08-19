# Animated Mermaid Diagrams in Manim

**Problem**: Static mermaid PNG (`ImageMobject`) appears all at once. Teaching value = near zero.

**Solution**: Rebuild the diagram as Manim mobjects (nodes = `Circle`/`RoundedRectangle`, edges = `Arrow`/`Line3D`), then animate node-by-node with `Create`/`GrowFromCenter`/`LaggedStart` synced to narration.

## Pattern

```python
def build_flow_diagram():
    """Returns (VGroup root, list of (anim, subcaption_text))"""
    root = VGroup()
    steps = []
    
    # 1. Source node
    src = Circle(radius=0.3, color=PRI).move_to(LEFT * 3)
    src_lbl = Text("word stream", font_size=12).next_to(src, DOWN)
    src_lbl.rotate(90 * DEGREES, axis=RIGHT)  # billboard upright
    root.add(src, src_lbl)
    steps.append((Create(src), "The input: a stream of words"))
    
    # 2. Decision diamond
    diamond = Square(side_length=0.8).rotate(45 * DEGREES).move_to(ORIGIN)
    diamond_lbl = Text("counting?", font_size=12).move_to(diamond)
    diamond_lbl.rotate(90 * DEGREES, axis=RIGHT)
    root.add(diamond, diamond_lbl)
    steps.append((Create(diamond), "How do we count?"))
    
    # 3. Naive path (red)
    naive_box = RoundedRectangle(width=2, height=0.6, color=ACCENT).move_to(DOWN * 2 + LEFT * 2)
    naive_lbl = Text("naive 2-loop", font_size=11).move_to(naive_box)
    naive_lbl.rotate(90 * DEGREES, axis=RIGHT)
    naive_arrow = Arrow(src.get_bottom(), naive_box.get_top(), color=ACCENT)
    root.add(naive_box, naive_lbl, naive_arrow)
    steps.append((Create(naive_arrow), "Approach 1: nested loops"))
    steps.append((Create(naive_box), "Every pair — O(n²)"))
    
    # 4. Optimized path (green)
    opt_box = RoundedRectangle(width=2, height=0.6, color=GOOD).move_to(DOWN * 2 + RIGHT * 2)
    opt_lbl = Text("Counter 1-pass", font_size=11).move_to(opt_box)
    opt_lbl.rotate(90 * DEGREES, axis=RIGHT)
    opt_arrow = Arrow(src.get_bottom(), opt_box.get_top(), color=GOOD)
    root.add(opt_box, opt_lbl, opt_arrow)
    steps.append((Create(opt_arrow), "Approach 2: Counter"))
    steps.append((Create(opt_box), "One pass — O(n)"))
    
    return root, steps

# In construct():
flow_root, flow_steps = build_flow_diagram()
self.add_fixed_in_frame_mobjects(flow_root)  # BILLBOARD — else slanted on floor
for anim, subcap in flow_steps:
    self.play(anim, run_time=1.5)
    if subcap:
        self.add_subcaption(subcap)
```

## Key Rules

- **Billboard everything**: `add_fixed_in_frame_mobjects(root)` BEFORE any positioning. All labels: `rotate(90°*DEGREES, axis=RIGHT)` so they stand upright, not flat on the xy floor.
- **LaggedStart** for cascading reveals: `LaggedStart(*[Create(n) for n in nodes], lag_ratio=0.1)`
- **Colors from palette**: `ACCENT = "#f2a154"` (naive), `GOOD = "#5ad1a6"` (optimized), `PRI = "#58C4DD"` (neutral)
- **Camera**: fixed `phi=65°`, `theta=-45°` — no ambient rotation during diagram build