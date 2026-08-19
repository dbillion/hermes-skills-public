# Notebook Cell Diagrams — reference

Pattern for "explain each code cell of a notebook with a mermaid diagram" study-guide repos (used for the 5 DSA Colab notebooks → 167 diagrams).

## Extractor logic (per code cell)
- `class X:` present → emit a **classDiagram** (`class X { +attr / +method() }`).
- `def fn(...)` present → emit a **flowchart**: `START → params → step nodes → return`.
- Steps = top-level statements of the function body (via `ast.parse` + `ast.unparse`), capped at ~6, plus the `return` value.
- NEVER hand-write diagrams for 100+ cells — generate them programmatically from the actual AST so they're accurate.

## Sanitizer (must strip, not convert)
Mermaid label text must NOT contain `[ ] { } ( ) = ' "`. Strip these chars entirely.
CRITICAL: a stadium/rounded node `R([Return X])` uses `([...])` as SHAPE — if you
rewrite `[`→`(` the inner parens collide with the shape delimiter → `Parse error ... got 'PS'`.
So: remove `()[]{}` from LABEL TEXT, keep `([...])` only as the deliberate shape wrapper.
Also replace `=`→` equals `, `->`→` to `, `<-`→` from `.` Collapse to ≤55 chars.

## Rendering 167 diagrams fast
`mmdc` spawns a full headless Chrome per invocation (~10–17s each) → serial is ~45 min.
Parallelize with xargs:
```bash
export PUPPETEER_EXECUTABLE_PATH=$(find ~/.cache/puppeteer/chrome-headless-shell -name chrome-headless-shell -type f | head -1)
cd docs/diagrams
find . -name '*.mmd' | xargs -P 4 -I{} bash -c 'mmdc -i "$1" -o "${1%.mmd}.png" -t neutral -w 1600' _ {}
# verify: every .mmd must have a .png
for f in $(find . -name '*.mmd'); do [ ! -f "${f%.mmd}.png" ] && echo "MISSING $f"; done
```
Note: 4-way parallel did NOT speed up much (Chrome is heavy per-process) but still
beats serial; budget ~13–15 min for ~167 diagrams. Failures are silent (exit 0) — the
post-loop MISSING check is mandatory.

## README layout this user wants (study guides)
- Main `README.md`: explains all notebooks, links each, repo layout, how-to-run.
- Per-notebook `README_<nb>.md`:
  - Diagram-first.
  - **Summary Table** at top: `# | Name | Kind | Complexity | Diagram(<img> thumb)`.
  - **Per-cell section**: one HORIZONTAL table per cell —
    `| Diagram | # | Name | Complexity | Parameters | Returns | Key Steps | Links |`
    with the `<img>` thumbnail inline in its own column.
- Thumbnail width: **320px**.
- Diagrams IN the table (not just links): use `<img>` (GitHub does NOT render `![]()`
  in table cells). Collapse multi-line steps with `<br>`, escape `|` as `\|`.

## Verifying the notebooks themselves (separate concern)
Notebook `.ipynb` `source` lines need trailing `\n` on all-but-last line or Colab MERGES
lines → SyntaxError. Verify by running on the Colab VM (`colab exec -f nb.ipynb`), NOT by
local compile (local `'\n'.join()+compile` hides the bug). See colab-operator skill.
