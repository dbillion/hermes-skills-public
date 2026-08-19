# Injection pitfalls — concrete transcripts & fixes

From the 83-scene Manim DSA injection. Each pitfall with the real error and the fix
that worked, so you don't re-derive it.

## Pitfall 1 — anchor indentation stripped

Symptom at render (NOT at parse):
```
self.play(FadeOut(axes), FadeOut(cubes), FadeOut(labels),
^^^^
NameError: name 'self' is not defined
```
Root cause: inserted at `m.start()` (the `s` of `self.play`), so the anchor's
leading whitespace was excluded; the line landed at column 0. `ast.parse` passed
(`self.play(...)` at col 0 is valid syntax), hiding it.

Fix: `line_start = src.rfind("\n", 0, m.start()) + 1`; insert `src[:line_start] +
block + src[line_start:]`. Verify with the col-0 assert (pitfall 4).

## Pitfall 2 — import guard matched the call

Symptom at render:
```
NameError: name 'test_panel' is not defined
```
Root cause: block text contained `test_panel(self, ...)`; guard `if "test_panel" in
src: return src` saw the call and skipped adding the import.

Fix: guard on import-item shape: `re.search(r"test_panel\s*[),]", src)`. Better: always
append `from dsa_style import test_panel` after `from manim import *` (works for
single- and multiline imports alike).

## Pitfall 3 — multiline import broken

`re.sub(r"from dsa_style import[^\n]*", repl, src)` rewrote only the first line of:
```python
from dsa_style import (DARK_BG, CUBE_COLOR, ACCENT, GOOD, SCENE_SHIFT,
                       make_cube_row, fixed_title, code_panel, make_highlight,
                       test_panel)
```
leaving a dangling tuple. Avoided entirely by the standalone-import-line approach.

## Pitfall 4 — false confidence from ast.parse

After fixing 1–3, a file still failed because a col-0 `self.` line existed. `ast.parse`
passed. The discriminator:
```python
bad = sum(1 for ln in src.splitlines()
          if ln[:1] not in " \t" and ln.strip().startswith("self."))
assert bad == 0
```
Subagent-generated scenes often had the final teardown at column 0 (broken from the
start, yet they had "rendered" — because the batch only checked exit code, not
validity). Re-indent ALL col-0 `self.` lines to 8 across every file, not just the
ones that failed parse.

## Manim test_panel 4-mobject gotcha (bonus)

The `test_panel` helper returns 4 mobjects: `(label, code, out_label, out_val)`.
An OLD 3-value unpack `tl, tc, tk = test_panel(...)` parses fine but raises
`ValueError: too many values to unpack` at runtime. Always unpack 4.

## Verified sequence (use this exact order)

1. revert (strip injected blocks + import additions, idempotent)
2. re-indent col-0 `self.` → 8 (all files)
3. inject (line_start insertion, standalone import)
4. verify: col-0 assert + render 3 files (formerly-broken, multiline-import, plain)
