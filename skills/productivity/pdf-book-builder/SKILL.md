---
name: pdf-book-builder
description: "Bind PDFs into a navigable book with TOC and bookmarks."
version: 1.0.0
author: Hermes Agent
license: MIT
category: productivity
metadata:
  hermes:
    tags: [pdf, book, toc, bookmarks, reportlab, pypdf, cheatsheet]
    related_skills: [repo-cheatsheet-generator]
---

# PDF Book Builder

Turns a folder of independent per-topic PDFs into a single, navigable "book" — the
kind a reader opens and jumps between topics using the PDF viewer's sidebar bookmarks
or the printed Table of Contents page numbers.

## When to use
- "collect these cheatsheets into a book", "make a single PDF with a TOC",
  "bundle all the sheets into one navigable file", "add bookmarks so I can jump between topics".
- After a generator (e.g. `repo-cheatsheet-generator`) has emitted N one-file-per-topic PDFs
  and you want them bound into one document.

## Prerequisites
Install into the **target venv** you will run the merge from. For Hermes-internal work this is
the app venv, NOT `~/.venv`:
```
uv pip install --python /home/deeone/.hermes/hermes-agent/venv/bin/python reportlab pypdf
```
- `reportlab` builds the cover + TOC pages.
- `pypdf` (v6) merges pages and writes outline bookmarks. (`PyPDF2` / old `pypdf` naming is
  deprecated — use `pypdf`.)

## Workflow
1. **Collect + order.** Build an ordered manifest: list of `{id, title, section?}`.
   Source PDFs live at `<out>/<id>_cheatsheet.pdf` (or any consistent naming).
   Verify coverage: every id has a PDF, no extras, record each id's merged start page.
2. **Merge topic PDFs** into one `PdfWriter` (`algo_writer`). NOTE: `PdfReader` has **no**
   `add_page` — loop `PdfReader(p)` and call `algo_writer.add_page(pg)`.
3. **Group into sections** for navigation. Prefer a curated mapping over naive
   filename-prefix grouping (prefixes lie: `Astar` is a graph algo but starts with "A").
   Keep a `SECTION_NAMES` dict + an explicit override set (`GRAPH_IDS`) for cross-prefix topics.
4. **Two-pass TOC.** You cannot know the TOC's final page count until you build it, and the
   TOC's page numbers depend on that count. So: build a placeholder TOC (page numbers = 0),
   measure `len(toc_reader.pages)` = `n_toc`, then compute each algorithm's real 1-based page
   (`1 + n_toc + algo_start[id] + 1`) and rebuild the TOC with real numbers. Assert the page
   count didn't change between passes.
5. **Assemble final `PdfWriter`:** cover page(s) → TOC page(s) → merged topic pages.
6. **Outline bookmarks** (the real navigation win):
   - `writer.add_outline_item("Cover", 0)`
   - `toc_item = writer.add_outline_item("Table of Contents", 1)`
   - Per section: `sec_item = writer.add_outline_item(sec, dest0, parent=toc_item)` at the
     first algorithm's 0-based index.
   - Per algorithm: `writer.add_outline_item(title, dest0, parent=sec_item)`.
7. **Metadata** (`/Title`, `/Author`) via `writer.add_metadata({...})`.
8. **Verify** with pypdf: re-open, assert `len(reader.pages)` equals expected, walk
   `reader.outline` recursively and print each item's title + `reader.get_destination_page_number(item)`.

## Pitfalls
- **`PdfReader.add_page` does not exist** — merge with `PdfWriter.add_page`. This is the #1 error.
- **TOC page numbers need two passes** — a single pass can't know `n_toc`. Build placeholder →
  measure → rebuild. Final page index of an algorithm = `1 (cover) + n_toc + algo_start[id]`.
- **Naive prefix grouping mis-files topics** — curate overrides (`GRAPH_IDS` set).
- **TOC titles with `&` / `"`** — escape with `xml.sax.saxutils.escape` before a reportlab
  `Paragraph` / `Table` cell, or the XML parser throws.
- **Outline `parent=` must be the returned item**, not a title string.
- **reportlab may be missing from the app venv** even if `python3 -c "import reportlab"` works
  system-wide — install into the same venv you run the merge from.

## Verification
See `scripts/build_book.py` for a complete, parameterized, working implementation
(cover + 3-page TOC + 168 merged topic pages + nested bookmarks). Run it, then the verify
snippet in the workflow step 8.

## Support files
- `scripts/build_book.py` — generalized builder: takes a root dir + manifest JSON
  (`[{id,title,section}]`) or scans `*.pdf`, merges, builds cover/TOC, adds nested bookmarks,
  and verifies. Copy and adjust section grouping to your topic set.
