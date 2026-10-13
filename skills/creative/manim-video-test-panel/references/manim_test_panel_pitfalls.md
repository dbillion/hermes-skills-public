# Manim Test-Panel Bulk-Inject Pitfalls (with transcripts)

Captured from a real session: injecting a "Verified by test" panel into 83
generated Manim scenes. These four bugs each silently broke the scenes and
costed many cycles because the errors were runtime/whitespace, not syntax.

## Pitfall 1 — Insertion offset strips the anchor indentation

**Symptom:** `NameError: name 'self' is not defined` at the teardown line
`self.play(FadeOut(axes), ...)`. The line sat at COLUMN 0 (module level) even
though it belonged inside `construct`.

**Cause:** the injector inserted the block at `last.start()` — the position of
the `s` character of the matched `self.play(FadeOut(`. That excludes the
leading whitespace, so the anchor line loses its indentation when reassembled.

**Fix:** insert at the anchor's LINE start, which includes the indentation:
```python
line_start = src.rfind("\n", 0, last.start()) + 1
new_src = src[:line_start] + act + src[line_start:]
```
Verify after: grep for `^self.play(FadeOut(axes)` — there must be NONE at col 0.

## Pitfall 2 — Import guard matches the call, not the import

**Symptom:** `NameError: name 'test_panel' is not defined` at the unpack line
`_tl, _tc, _to, _tv = test_panel(self, _tcode, ...)`.

**Cause:** `ensure_import` did `if "test_panel" in src: return src` — but the
just-injected block contains `test_panel(self, ...)`, so the guard thought the
import was already present and skipped adding it.

**Fix:** guard on an IMPORT item, not the bare name:
```python
if re.search(r"test_panel\s*[),]", src):   # ", test_panel)" or "test_panel," in an import
    return src
# else add a clean standalone line after `from manim import *`:
new, n = re.subn(r"(from manim import \*(\n[ \t]*#[^\n]*)*\n)",
                 r"\1from dsa_style import test_panel\n", src, count=1)
```
This works for BOTH single-line (`from dsa_style import (...)`) and multi-line
imports (the original failure case was a multiline tuple import where the
single-line regex only touched the first line).

## Pitfall 3 — Parse-gate false negatives

**Symptom:** the pipeline reported "parse errors: NONE" but scenes crashed at
render with `self` undefined.

**Cause (two):**
- `self.play(...)` at column 0 is *syntactically valid Python* — `ast.parse`
  passes; the failure is a runtime `NameError`. So `ast.parse` is NOT a
  sufficient render-safety check.
- A shell-heredoc verification snippet had a dead first assignment
  (`bad=[... lambda ...]; bad=[]`) that reset the list, so it printed "NONE"
  even when real errors existed.

**Fix:** after injection, assert ZERO column-0 `self.` lines across ALL files:
```python
rem = 0
for f in glob.glob("scenes/*.py"):
    for ln in open(f).read().splitlines():
        if ln[:1] not in " \t" and ln.strip().startswith("self."):
            rem += 1
assert rem == 0
```
Plus always render-test 1–3 scenes (incl. a previously-broken one) before the
full batch.

## Pitfall 4 — git can't restore untracked generated scenes

**Symptom:** a bad bulk-inject corrupted 17/83 scenes; `git checkout` /
`git revert` did nothing.

**Cause:** the scene files were never committed (untracked). git cannot restore
them, so there is no "undo".

**Fix:** keep a python revert script (string-remove the injected block +
import) AND, to repair indentation corruption, re-indent only column-0
method-body lines:
```python
new = [("        " + ln.lstrip()
        if (ln[:1] not in " \t" and ln.strip().startswith("self."))
        else ln) for ln in lines]
```
Do NOT re-indent the module docstring (`"""`) — that corrupts it. Column-0
`self.` is always method-body content and safe to indent to 8.
