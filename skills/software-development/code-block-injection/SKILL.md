---
name: code-block-injection
description: Inject a code block into many files without breaking them.
---

# Bulk code-block injection into many files

When you must add the same block (test-panel call, logging, decorator, import) to N
source files, do it with a Python script over the file tree — never hand-edit each.
But naive `src[:m.start()] + block + src[m.start():]` insertion has FOUR traps that
will corrupt files and only surface at render/runtime. Captured here so you don't
relearn them across a 2-hour debugging loop (exactly what happened on the 83-scene
Manim DSA injection).

## The 4 pitfalls (priority order)

### 1. Insertion point strips the anchor's indentation
`re.finditer(r"self\.play\(FadeOut\(")` gives matches whose `.start()` points at the
first character of `self.play`, NOT the start of the line. Inserting
`src[:m.start()] + block + src[m.start():]` drops the line's leading whitespace, pushing
the anchor to column 0 → `NameError: name 'self' is not defined` at runtime (NOT at
parse — `self.play(...)` at col 0 is *syntactically valid Python*, so `ast.parse` passes
and the bug hides until render).

FIX: compute `line_start = src.rfind("\n", 0, m.start()) + 1` and insert at `line_start`
(i.e. include the anchor's own indentation). Keep the block indented to
`indent = src[line_start:m.start()]` (the anchor's real indent), falling back to 8 spaces
for method-body level.

### 2. The import guard matches the CALL, not the import
If the block contains `test_panel(self, ...)`, a guard like `if "test_panel" in src:
return src` (skip adding import) will ALWAYS trigger — the call is already in `src` — so
the import is never added → `NameError: name 'test_panel' is not defined`.

FIX: guard on the import *item* form only, e.g. `re.search(r"test_panel\s*[),]", src)`
(matches `, test_panel)` or `test_panel,` inside an import line). Or simply append a
standalone `from dsa_style import test_panel` line after `from manim import *` every time
(robust for single- and multi-line imports).

### 3. Multi-line imports break a naive single-line regex
`re.sub(r"from dsa_style import[^\n]*", ...)` only touches the FIRST physical line. A
multiline import `from dsa_style import (\n  A, B,\n  C)` is left half-edited → syntax
error or dangling comma.

FIX: prefer the standalone-import-line approach (pitfall 2 fallback) over mutating the
existing import line.

### 4. `ast.parse` gives FALSE confidence
`self.play(...)` at column 0 is syntactically valid, so `ast.parse` succeeds even though
the file is broken at runtime. A "parse check passed" is NOT proof the injection is
correct.

FIX: after injection, assert **zero** column-0 method-body lines:
```python
bad = sum(1 for ln in src.splitlines()
          if ln[:1] not in " \t" and ln.strip().startswith("self."))
assert bad == 0
```
And always validate with a real render of 1–3 representative files, not just parse.

## Canonical injector skeleton (reuse, adapt)

```python
import re, glob, os, ast

def ensure_import(src):
    if re.search(r"test_panel\s*[),]", src):   # pitfall 2
        return src
    new, n = re.subn(r"(from manim import \*(\n[ \t]*#[^\n]*)*\n)",
                      r"\1from dsa_style import test_panel\n", src, count=1)
    return new if n else "from dsa_style import test_panel\n" + src

def inject(path, block_fn):
    src = open(path).read()
    if "test_panel(" in src:
        return "already"
    matches = list(re.finditer(r"self\.play\(FadeOut\(", src))
    if not matches:
        return "no-anchor"
    m = matches[-1]
    line_start = src.rfind("\n", 0, m.start()) + 1
    indent = src[line_start:m.start()] or "        "
    block = block_fn(indent)
    new = src[:line_start] + block + src[line_start:]   # pitfall 1
    return ensure_import(new)

# Pre-pass for files already at col-0 (subagent-generated files often are):
for f in files:
    lines = open(f).read().splitlines(keepends=True)
    fixed = [("        "+ln.lstrip() if (ln[:1] not in " \t"
              and ln.strip().startswith("self.")) else ln) for ln in lines]
    open(f, "w").write("".join(fixed))   # pitfall 4: zero col-0 self.
```

## Workflow that actually works (sequence)

1. **Revert pass** first (an idempotent revert script that strips previously-injected
   blocks + import additions) so re-runs are safe. Reverting must restore the anchor's
   indentation — verify with the col-0 assert, not just parse.
2. **Re-indent pass**: fix any col-0 `self.` lines to method indent (8) across ALL files,
   not just the ones that failed parse (pitfall 4 — the broken ones often parse fine).
3. **Inject pass** with the skeleton above.
4. **Verify**: col-0 assert + render 3 representative files (one formerly-broken, one
   multiline-import, one plain).

## Clean rebuild order (when a prior run corrupted state)
revert → re-indent(col-0 self.→8) → inject(corrected) → verify(render 3). Any other
order leaves files half-broken that `ast.parse` won't catch.

## References
See `references/injection-pitfalls.md` for the exact failure transcripts and the fixes
that worked, plus the Manim `test_panel` 4-mobject unpack gotcha (helper returns 4
values; an old 3-value unpack crashes at runtime even though it parses).
