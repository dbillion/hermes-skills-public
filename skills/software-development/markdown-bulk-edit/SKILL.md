---
name: markdown-bulk-edit
description: >-
  Bulk-edit markdown with Python; avoid header-boundary leaks.
---

# Markdown Bulk Edit (large READMEs / docs)

When a README or doc has dozens of repeated blocks (e.g. one per question or
per API entry) and you must insert the same structured section into each, do
NOT hand-edit — script it with Python. But the naive approach has a sharp
edge that corrupts output. Capture it here.

## The header-boundary leak (the bug that bites)

A common pattern: split the doc on `### ` headers, process each block, insert
a table. The trap: if your block scanner stops at the WRONG header set, it
accumulates code/method names from LATER blocks into the current one.

Concrete failure this session: inserting an "Optimised vs Modern rewrite"
table under each `### Qn.` / `### An.` / `### G0.` block. The scanner stopped
only at `^###\s+Q` headers, so algorithm (`### A1.`) and graph-extra (`### G0.`)
blocks ran until the NEXT `### Q` — pulling a `floydWarshall` method name from
a far-later block into every graph block's table. Three iterations of this
before the fix.

**Rule: when scanning a block, stop at ANY header — `^###\s` — not a subset
(`^###\s+Q`, `^###\s+[QA]`).** And reset per-block state (method name, code
token) at the start of EACH block, not once before the loop.

## Prefer a stable identifier over fragile parsing

Don't regex-parse Java/code signatures to name the section — signatures vary
(records, classes, constructors, `public static class X`). Instead pull the
block's own stable token: the `<code>scene_token</code>` already in each
header table. It is always present and always correct. Use it as the
identifier in the inserted text.

## Format preference (user correction — embed this)

For multi-attribute comparisons in a doc, the user explicitly preferred:
- ROWS over COLUMNS when columns "may not contain the functions properly."
  A 2-column table (Aspect | Detail) with stacked rows reads better than a
  wide 3-column layout for code-adjacent notes.
- Don't invent a "brute force" column if the codebase only has the optimised
  version — put the contrast in prose/README only, not by writing fake code.
- "Skip virtual threads" — don't force Java 25 virtual threads where the
  problem is sequential; only mention them where honest.

## Verification after a bulk edit

Always run a post-edit audit (don't trust the insert count):
- Count inserted sections == expected blocks.
- Assert NO block has >1 inserted section (duplicate) and NO block with a
  function + unit test has 0 (missing).
- Grep for any leaked identifier (e.g. the stray `floydWarshall`) — must be 0
  outside legit code blocks.
- Spot-check one iterative block and one stream-based block for correct text.

Back up the file first (`cp doc.md doc.md.bak_$(date +%Y%m%d_%H%M)`).

See `references/markdown_insert_template.py` for a known-good, reusable script.
