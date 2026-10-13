---
name: markdown-doc-editing
description: Edit large markdown docs; prefer stacked rows over columns.
---

# Markdown Doc Editing (large files, per-section insertion)

## User layout preference (capture this)
When adding comparison content (brute vs optimised, "Optimised version" vs "Modern rewrite"), the user PREFERS **stacked rows in a 2-column table** (Aspect | Detail) over a side-by-side **3-column table**. Verbatim reason: columns "may not contain the functions properly." Pattern per section:
```
**Optimised vs Modern rewrite (Java 25 LTS):**

| | Detail |
|---|---|
| **Optimised version (tested)** | `<code_token>` — the implementation under JUnit above. |
| **Modern rewrite (Java 25 LTS)** | ... honest note: where a Stream rewrite would be a regression, say so ... |
| **Gains** | ... same complexity, less mutable state ... |
```
Keep original Function + Unit-test rows INTACT above the new table.

## Technique: programmatic per-block insertion (in-process Python, NOT subagents)
For a 2000+ line README with repeated `### Qn.` blocks, edit with a Python script that:
1. Splits the file on lines matching `^### ` (any header).
2. For each block, extracts what it needs (e.g. the `<code>token</code>` from the header table) and builds new content.
3. Inserts right before the GIF/end marker.

### CRITICAL PITFALL (cost real iterations this session)
- **Block-boundary regex MUST stop at ANY `^### ` header** — use `re.match(r"^###\s", line)`. Do NOT restrict to a subset like `^###\s+Q` or `^###\s+[QA]`. If restricted, the inner scan runs past the next header of a different type (e.g. `### A1.`, `### G0.`) and **captured state (func_code, method name) leaks into the wrong block** — a later algorithm's method (floydWarshall) bled into an earlier block's table. Silent until an audit pass.
- **Reset all per-block state vars** (`func_code = ""`, `code_token = ""`, `saw_unit = False`) at the START of each block iteration.
- **Prefer a stable in-block token over fragile code parsing.** Extracting a Java method name via regex over a code fence is brittle (constructors, `record`, multi-method fences). Use the `<code>token</code>` already in the block's header table — always correct.

## Steps
1. Back up: `cp README.md README.md.bak_$(date +%Y%m%d_%H%M)` before scripting.
2. Write the Python pass; run once; verify with a block audit — every `### ` block with function+test has exactly ONE inserted section; zero duplicates; zero leaked identifiers.
3. Spot-check 2–3 blocks (one iterative, one stream-based, one algorithm/G0) for correct identifiers.
4. Commit to a branch, push remote (user's git preference: branch + commit + create remote branch).

## Pitfalls
- Don't use subagents to edit ONE shared file — concurrent edits risk corruption; in-process script avoids rate limits (this user's subagents hit 429 fast).
- Don't fabricate "modern rewrite" code where a Stream rewrite would regress (e.g. Kadane into Stream adds mutable-accumulator boilerplate). State honestly where iterative is already optimal.
- If a block has no function fence, skip the table rather than invent one.
