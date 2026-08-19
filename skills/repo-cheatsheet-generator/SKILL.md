---
name: repo-cheatsheet-generator
description: Generates a structured, printable "cheat sheet" reference document for a code repository or library — organized into numbered sections (Overview, How to Use, Core Components table, Code Examples, Conventions, Installation, Common Errors & Solutions, Quick Revision checklist), with color-coded headers, tables, and callout boxes. Use this whenever the user asks for a cheat sheet, quick reference, one-pager, or study guide for a repo/codebase/library, or wants source material formatted for NotebookLM. Trigger on "make a cheat sheet for this repo", "summarize this codebase as a reference sheet", "NotebookLM source for my project", etc.
compatibility: Requires reportlab (pip install reportlab --break-system-packages)
---

# Repo Cheat Sheet Generator

Produces a dense, well-organized one-pager (or few-pager) reference document
for a codebase — the same kind of structure as a good study cheat sheet:
short definitions, a real-world analogy, a table of the main
components/modules, copy-pasteable code examples, conventions, a common
errors table, and a "quick revision" checklist at the end.

This is a **structural template**, not a copy of any particular source —
fill it with real content extracted from the target repo each time.

## Workflow

1. **Identify the target.** Ask (if not already clear) whether the user
   wants a cheat sheet for: the whole repo, one module/package, or one
   library the repo depends on.
2. **Analyze the repo** using `view`/`bash`:
   - Read `README`, `package.json`/`pyproject.toml`/`requirements.txt`, or
     equivalent manifest to learn name, purpose, and dependencies.
   - List top-level modules/packages (`view` the directory tree) to find the
     main components worth a table row each.
   - Skim 1-3 of the most-imported/most-central files for real usage
     patterns to turn into short code examples (don't invent APIs — pull
     real function/class signatures from the code).
   - Check for a lint/style config or CONTRIBUTING doc for naming
     conventions worth listing.
   - Note anything commonly mis-used (open issues, TODO/FIXME comments, or
     error-prone setup steps) for the "Common Errors" table.
3. **Fill the section template** (see `references/template_schema.md` for
   the exact JSON structure `generate_cheatsheet.py` expects, plus a full
   worked example). Keep every entry short — this is a cheat sheet, not
   documentation. Prefer:
   - Definitions: 1 sentence
   - Table rows: 3-6 words per cell
   - Code examples: 2-6 lines, real and runnable
   - Tips/notes: 1 sentence
4. **Generate the PDF**:
   ```bash
   python3 scripts/generate_cheatsheet.py --data cheatsheet.json --out cheatsheet.pdf
   ```
5. **Also emit the markdown source** the script writes alongside the PDF
   (`cheatsheet.md`) — plain text works well as a NotebookLM source and is
   easy to paste in even without a file upload.
6. **Deliver both files** with `present_files`. Don't just describe the
   sheet — always produce the actual files.

## Section template (in order)

1. **Header** — project/library name + one-line tagline
2. **Overview** — "What is it?" (2-4 bullets) + a short real-world analogy
   callout
3. **Core components table** — name / purpose / example use, one row per
   major module, class, or exported function group
4. **Code examples** — 4-8 short, real, labeled snippets covering the most
   common operations
5. **Conventions** — naming/aliasing/style conventions actually used in the
   repo (table: pattern → example)
6. **Setup** — install/build/run commands (short code block)
7. **How it resolves things** (optional, include only if relevant — e.g.
   config lookup order, module resolution, routing) — numbered list
8. **Best practices** — 4-6 short imperative bullets
9. **Common errors & solutions table** — error / likely cause / fix
10. **Quick revision checklist** — 6-10 short checkbox items recapping the
    whole sheet

## Design rules the script enforces

- Clean, readable single-column-per-section layout with color-coded section
  headers (a different accent color per section, cycling through a fixed
  palette) so sections are easy to scan.
- Tables for anything list-like with 2+ attributes per item.
- Monospace-font boxes for code.
- A distinct "tip" callout style, used sparingly (1-2 per sheet) for the
  single most useful piece of advice.
- Everything fits on as few pages as the content allows — this is a
  reference sheet, not a report.

## Reference files

- `references/template_schema.md` — exact JSON structure + a full worked
  example (a cheat sheet for a small example library).
