# Mermaid CLI Pitfalls & Fixes (session-verified)

## Chrome / Puppeteer missing
`mmdc` renders via headless Chrome. If you see:
```
Error: Could not find Chrome (ver. 131.0.6778.204)...
```
Fix — there is NO system chromium on this box, so do NOT use `/usr/bin/chromium`:
1. `npx puppeteer browsers install chrome-headless-shell` (downloads to ~/.cache/puppeteer)
2. Export the path to the downloaded binary:
   `export PUPPETEER_EXECUTABLE_PATH=$(find ~/.cache/puppeteer/chrome-headless-shell -name chrome-headless-shell -type f | head -1)`
This two-step sequence is what actually works here; bare `mmdc` without it errors every time.

## Parse errors — forbidden characters in node/edge labels
Mermaid's parser breaks on these inside `[...]` or `{...}` text:
- Literal `=` → use `equals` or `is`
- Square brackets `nums[i]` → use `nums i` (drop brackets)
- `seen[complement]` → `seen complement`
- `arr[x] = y` → `arr x equals y`
- **Apostrophe `'`**: `Andrew's monotone chain` → parse error. Use `Andrew monotone chain`.
- **Quoted `note for`**: `note for X "some text"` → parse error. Use `note for X some text`
  (unquoted) OR replace with a plain node `X --> N[some text]`.

`<br/>` is OK in labels but keep the surrounding text free of `=`, `[]`, `'`, and quotes.

## Batch render + verify
```bash
export PUPPETEER_EXECUTABLE_PATH=$(find ~/.cache/puppeteer/chrome-headless-shell -name chrome-headless-shell -type f | head -1)
for f in *.mmd; do
  mmdc -i "$f" -o "${f%.mmd}.png" -t neutral -w 1600 2>/dev/null || echo "FAIL $f"
done
# Verify all rendered (count must equal .mmd count)
for f in *.mmd; do [ ! -f "${f%.mmd}.png" ] && echo "MISSING: $f"; done
```
If a file is MISSING, re-run individually and read stderr (`head`) for the exact parse-error line
(usually "Parse error on line N"). Rendering is slow (~10-15s each) — for many diagrams, run the
loop in background and `wait` rather than blocking serially.

## GitHub renders mermaid natively
A fenced ```mermaid block in a README renders on github.com with NO binary needed. For repo docs,
lead the README with the ```mermaid source block, then embed the rendered PNG underneath, then the
narrative. This "diagram-first" ordering is what this user prefers for clone-and-scan readability.
