---
name: explainer-video-test-verification
description: Add verified-by-test panels to generated explainer videos.
---

# Explainer Video Test Verification

When you generate educational/explainer videos from code (Manim Community Edition is the
common case), do NOT end on the animation alone. Close each concept with a **verified-by-test
panel**: the real `@Test`/unit-test source plus the exact expected output, pulled from an
ACTUAL test run — not a hard-coded guess.

This is the "verification-as-education" principle: the final on-screen state must match what
the test asserts. The user explicitly values this ("verification-as-education, not just
animation") and will reject panels whose output was invented or can't be traced to a run.

## The mandatory panel shape

1. Run the project's real test suite (e.g. `./gradlew test`, `pytest`, `npm test`).
2. Capture per-test results to JSON keyed by method name (strip parens from names like
   `Q3_twoSum()` → `Q3_twoSum` so they map to scene files). Record PASS/FAIL and the actual
   asserted value (e.g. `[1,2,5,8,9]`, `[0,1]`, `9`, `true`).
3. In the video, show:
   - the real `@Test` body (verbatim from the repo, not a paraphrase), AND
   - a prominent "✓ Expected output: <value>" line, AND
   - a comment on the displayed test like `// -> <value>   (gradle test: PASS)` so the
     viewer sees the ground truth next to the code.

The test run is read-only w.r.t. the videos (writes only to gitignored `build/` / temp), so it
never clobbers existing renders.

## LEGIBILITY RULE (user correction — do not skip)

The user observed the verification panel was "too small to be seen." Make the expected-output
text LARGE and the code readable:

- Expected-output value (`val`): scale **~0.9–1.0** (was 0.55 → illegible at 480p). This is the
  "receipt" — it must dominate.
- Test code panel: `font_size` **~18** (was 14) and scale **~0.45** (was 0.34).
- Labels (`✓ Expected output:`, `Verified by test`): scale **~0.5–0.6**.
- At 480p a `scale(0.55)` Text is only ~23px tall — unreadable. Bump it.
- The 3D/animation scene is normally faded out *before* the test act, so the panel owns the
  frame — there is room to go big. Don't shrink to avoid overlap that isn't there.

## Injecting the panel into MANY generated scenes (gotchas)

When patching 10s–100s of generated `.py` scene files programmatically (e.g. an injector
script), these bugs bit hard and wasted cycles — encode them:

- **Insert at the LINE START, not the match start.** Anchoring on the last
  `self.play(FadeOut(` and inserting at `match.start()` strips the anchor line's leading
  whitespace, dropping `self.play(...)` to column 0 → `NameError: name 'self' is not defined`
  at runtime. Compute `line_start = src.rfind("\n", 0, match.start()) + 1` and insert there so
  the anchor keeps its indentation.
- **Import guard must match the import ITEM, not the substring.** Checking `if "test_panel" in
  src` is wrong — the injected *call* `test_panel(self, ...)` contains that substring, so the
  guard skips adding the import → `NameError: name 'test_panel' is not defined`. Check for the
  import form instead: `re.search(r"test_panel\s*[),]", src)` (matches `, test_panel)` / `test_panel,`
  inside an import line) before adding `from dsa_style import test_panel`.
- **Re-indent stray column-0 `self.` lines.** Subagent-generated scenes sometimes leave the
  teardown `self.play(FadeOut(...))` at column 0. `ast.parse` will NOT catch this (it's valid
  *syntax*; the `NameError` is runtime). Fix by re-indenting any line starting at column 0 that
  begins with `self.` to the method-body indent (8 spaces). A clean parse check is NOT
  sufficient — verify the anchor is actually inside the method.
- **`ensure_import` for multiline imports.** If the existing import is
  `from dsa_style import (\n   DARK_BG,\n   ...)` (multiline), a single-line regex replacement
  corrupts it. Prefer appending a clean standalone `from dsa_style import test_panel` line right
  after `from manim import *`.
- **Don't `pkill -f "manim"` to stop renders** — it matches and kills the shell/agent process
  too (exit -15). Kill specific PIDs instead, or let the background job finish.

## Verification before declaring done

- Render-test at least one scene that previously failed (e.g. the one that errored) to confirm
  the panel renders AND is legible — a green `ast.parse` is not proof of a working runtime panel.
- Confirm every scene's `test_panel` import resolves and the anchor line is indented.

## Companion / source of truth

The user's own `manim-storytelling-skills` repo (dbillion/manim-storytelling-skills, installed
via `npx skills add dbillion/manim-storytelling-skills --all`) is the production home of the
`test_panel` helper and the 5-act narrative. This skill is the methodology + pitfall capture;
the helper code lives in that user-owned repo. If you fix the helper there, make the expected
output legible per the rule above.
