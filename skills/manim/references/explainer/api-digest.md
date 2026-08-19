# Manim API digest — the digest-lies pitfall

## What happened
User suggested: pack ManimCommunity/manim with `repomix`, upload to NotebookLM,
query for API signatures. We did this. NotebookLM returned a WRONG `Code` signature
(`code=`, `insert_line_no=`, `font_size=` as direct kwargs) — because the repo HEAD
diverged from the installed 0.20.1 build. Following that produced
`unexpected keyword argument 'code'` errors.

## The reliable path (use this)
1. `repomix` the repo FULL (omit `--compress`; keep method bodies):
   `repomix --style markdown --include "manim/mobject/text/code_mobject.py,manim/scene/three_d_scene.py,..." -o api.md`
2. Upload to NotebookLM as a source for context.
3. BUT confirm every signature against the ACTUALLY INSTALLED package:
   ```python
   /path/to/manim/bin/python -c "import inspect; from manim import Code; print(inspect.signature(Code.__init__))"
   ```
   The installed 0.20.1 `Code.__init__` is:
   `(code_file=None, code_string=None, language=None, formatter_style=None, tab_width=4,
     add_line_numbers=False, line_numbers_from=1, background='rectangle', background_config={},
     paragraph_config=None)`
   → use `code_string=`, `paragraph_config={"font_size": N}`, `add_line_numbers=`.

## Lesson
Repo digests and NLM answers reflect a possibly-different version. The installed
package is ground truth. When a signature mismatch occurs, `inspect` the live build
before trusting any external source.
