# Text & Typography

## The four text classes — pick the right one

| Class | Use for | Notes |
|---|---|---|
| `Text` | Plain prose, labels, captions | Uses system/Pango fonts, not LaTeX. Fast, no LaTeX install needed. |
| `MarkupText` | Prose needing inline style changes (bold word, colored word, mixed size) within one mobject | Pango markup syntax, e.g. `MarkupText('An <b>important</b> word')`. |
| `Tex` | Any LaTeX content that isn't pure math (text with occasional inline math) | Requires a LaTeX install (texlive or MiKTeX). |
| `MathTex` | Pure math formulas | Also LaTeX-based. **Always use this over `Text` for formulas** — spacing/kerning for math is only correct through LaTeX. |

```python
Text("Hello world", font_size=48, color=WHITE, font="Helvetica")
MarkupText('Use <span foreground="yellow">color</span> inline')
Tex(r"The area is $A = \pi r^2$.")
MathTex(r"\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}")
```

### Splitting MathTex for selective animation

Pass multiple string args to `MathTex` to get separately-addressable parts (needed for `TransformMatchingTex`, per-term coloring, or `Indicate`-ing just one piece):
```python
eq = MathTex("E", "=", "m", "c", "^2")
eq[0].set_color(YELLOW)         # color just "E"
self.play(Indicate(eq[2]))      # highlight just "m"
```
Alternative: pass `tex_to_color_map={"E": YELLOW, "m": BLUE}` to color by matching substring without manual indexing.

## Code blocks

`Code` — syntax-highlighted source, reads from a file or a string, many Pygments styles available.
```python
Code(code_file="script.py", language="python", background="window",
     tab_width=4, font_size=18)
```
Combine with `TypeWithCursor`/`AddTextLetterByLetter` for a "typing out code live" explainer beat.

## Structured text

`Paragraph` (multi-line `Text` block with per-line alignment), `BulletedList` (auto-bulleted `Tex` items, animate items in with `LaggedStart`), `Title` (a `Tex` styled + auto-positioned as a scene title, with an underline).
```python
BulletedList("First point", "Second point", "Third point", height=4)
Title("Section 2: Rotations")
```

## Writing/reveal effects, ranked by "produced" feel

1. `Write` — default, handwriting-like stroke draw. Good general default for `Tex`/`MathTex`/`Text`.
2. `AddTextLetterByLetter` / `AddTextWordByWord` — literal typewriter reveal, no stroke animation. Good for captions/subtitles appearing in sync with narration.
3. `TypeWithCursor` — typewriter reveal **with a blinking cursor glyph** — closest to an actual terminal/IDE feel; best default for code blocks.
4. `FadeIn(text, shift=UP)` — simplest, use when text is secondary (e.g. a passing label) and shouldn't draw attention to itself.

Don't use `Write` on a `Code` block — the stroke-drawing looks wrong on monospace code; use `TypeWithCursor` or `AddTextLetterByLetter` instead.

## Fonts and LaTeX templates

- `Text(..., font="Font Name")` uses whatever fonts are installed on the system (`fc-list` to check on Linux). Falls back silently to a default if the name isn't found — verify the font is installed rather than assuming.
- For non-default LaTeX packages/macros in `Tex`/`MathTex`, build a custom `TexTemplate`:
```python
from manim import TexTemplate
template = TexTemplate()
template.add_to_preamble(r"\usepackage{physics}")
tex = MathTex(r"\bra{\psi}\hat{H}\ket{\psi}", tex_template=template)
```
- `TexTemplateLibrary` ships several presets (e.g. for different engines/fonts) — check it before hand-rolling a template for a common need.

## Common LaTeX gotchas

- Raw strings (`r"..."`) for every `Tex`/`MathTex` argument — backslashes are ubiquitous in LaTeX and will otherwise be misinterpreted by Python.
- Curly braces in an f-string combined with LaTeX get confusing fast (`{{` escaping) — prefer building the LaTeX string first as a plain variable, then passing it, over inlining an f-string directly into `MathTex(...)`.
- If `Tex`/`MathTex` throws a LaTeX compile error, the actual cause is almost always in the `.log` file Manim points to, not in Manim itself — read that error rather than guessing.
- Missing LaTeX install is the most common `Tex`/`MathTex` failure in a fresh environment — verify with `latex --version` before debugging Manim-side.
