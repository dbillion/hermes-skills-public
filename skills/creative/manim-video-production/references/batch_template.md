# Batch Template Pattern — Producing Many Similar Explainer Videos

**Problem**: 23 Python trick videos with identical structure but different content. Hand-writing each scene = error-prone, inconsistent, slow.

**Solution**: Base class + YAML config + generated scene files.

## Architecture

```
redo/
├── template.py          # TrickScene base class (5 acts, helpers)
├── tricks.yaml          # All 23 configs
├── trick_XX_name.py     # 23 thin subclasses (just data + _run methods)
```

## 1. Base Class (`template.py`)

- `TrickScene(ThreeDScene)` implements all 5 acts as methods
- Subclass MUST define: `NAIVE_CODE`, `IDIOMATIC_CODE`, `INPUT_DATA`, `SOLID_TYPE`, `TITLE`, `INSIGHT_TEXT`, `BF_COMPLEXITY`, `OPT_COMPLEXITY`
- Subclass implements `_run_naive()` and `_run_optimized()` (synced highlight + particle logic)
- Helpers: `make_data_space()`, `highlight_line()`, `make_complexity_graph()`

## 2. Config YAML (`tricks.yaml`)

Each trick entry:
```yaml
- id: 01
  name: "Name Mangling"
  title: "Python Name Mangling"
  notebook_section: "1. Name Mangling"
  naive_code: "class User: ..."
  idiomatic_code: "class User: ..."
  input_data: ["_internal", "__mangled", "public"]
  solid_type: "spheres"
  insight_text: "Double underscore mangles to _ClassName__attr — prevents accidental override in subclasses"
  bf_complexity: "lambda x: x"
  opt_complexity: "lambda x: x"
```

## 3. Scene Files (23 thin subclasses)

```python
from template import TrickScene

class Trick01NameMangling(TrickScene):
    NAIVE_CODE = "..."
    IDIOMATIC_CODE = "..."
    INPUT_DATA = [...]
    SOLID_TYPE = "spheres"
    # ... other class attrs
    
    def _run_naive(self):
        lines = self.bf_code.code_lines
        for i in range(...):
            self.play(self.bf_hl.animate.move_to(lines[i]), run_time=0.2)
    
    def _run_optimized(self):
        ...
```

## Benefits

- **Consistency**: All 23 videos identical structure, timing, palette, camera
- **Speed**: Add new trick = 1 YAML entry + 1 thin Python file (20 lines)
- **Maintainability**: Fix timing/palette/camera in ONE place (template.py)
- **Reviewability**: Diff shows only content changes, not structural churn
- **Parallelization**: 23 scenes independent → render on multiple machines

## Render Pipeline

```bash
# Preview all (480p15)
for f in trick_*.py; do
  manim -pql "$f" $(basename "$f" .py | sed 's/trick_//' | sed 's/_/ /g' | sed 's/\b\(.\)/\u\1/g' | sed 's/ //g')
done

# Final (1080p60)
# Burn subs via existing burn_subs.sh
```

## From This Session

Created: 23 scene files + template.py + tricks.yaml + PLAN.md
All syntax-validated. Render blocked by CPU load (35+) on cloud runner — needs GPU machine.