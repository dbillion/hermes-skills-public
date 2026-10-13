---
name: github-readme-rich-media
description: Use when a README table is squeezed or media won't render.
---

# GitHub README — Rich Media Layouts

Use this when a README must show, per item (question / algorithm / API): the real
problem statement, a diagram, the actual source code, the unit test, and a
full-width animation — without the layout breaking or rendering as plain text.

## When to use
- User asks to embed Manim / asciinema / Loom GIFs + code in a README.
- User says a table is "too squeezed", "useless", or "crammed into one file".
- User wants each question/algorithm to show its real description, not just a label/number.
- Building a per-item catalog (DSA problems, API endpoints, library features) in Markdown.

## CRITICAL GitHub Flavored Markdown constraints (these bite everyone)
1. **Mermaid does NOT render inside a table cell.** If you put a ```mermaid block in a
   `<td>`, GitHub shows the raw text. Fix: pre-generate the diagram to PNG (e.g. with
   `mmdc`) and embed `<img src="docs/diagrams/X.png">`.
2. **Fenced code blocks (```) do NOT render inside a Markdown table cell.** The cell
   shows the literal backticks + code. Fix: use an **HTML `<table>`** with
   `<pre><code class="language-java">…</code></pre>` cells. GitHub DOES render
   `<pre>`/`<code>` inside HTML tables.
3. **A full-width image spanning a table** needs `colspan` on the cell, e.g.
   `<tr><td colspan="3" align="center"><img src="…gif" width="100%"></td></tr>`.
4. **HTML `<img>` in a Markdown table cell works**; a Markdown `![alt](url)` in a cell
   also works, but only HTML gives you `colspan`/`width="100%"`.
5. Validate before pushing: grep the built README for every `explainer_videos/gifs/X.gif`
   and `docs/diagrams/X.png` and assert the file exists on disk (a path typo = broken
   image on GitHub, no local error). Also count `<table>`==`</table>`, `<tr>`==`</tr>`,
   `<pre>`==`</pre>` to catch unbalanced HTML.

## Preferred layout (what this user wants)
Per item, in this order — NOT one giant squeezed table:
```
### Q1. <real problem statement from the source of truth>
<sub>topic: <Topic> · <code>base_name</code></sub>

| Diagram | Function (source) | Unit test |
|---|---|---|
| <img …png width=260> | <pre><code>…real method…</code></pre> | <pre><code>…real @Test…</code></pre> |

<p align="center"><img src="…gif" width="100%"></p>
```
- The **heading is the real question/problem sentence**, pulled from the authoritative
  source (e.g. an upstream notebook / spec file), not a bare `Q1 maxSumSubarray` label.
  Map by normalizing names (camelCase ↔ snake_case) — mismatches produce wrong numbers.
- Order sections by category: Interview Questions → Algorithms → Single-Path → Graph
  extras. Add a clickable **Index** at the top listing each item by its real sentence
  (GitHub heading anchors are auto-generated from `### Heading Text`).
- Keep a separate **Quick start / Testing / Layout / Tech** section block at the BOTTOM
  (preserve prior descriptions — do not drop them when restructuring).

## Embedding media that lives in the repo
- Commit GIFs/PNGs via **Git LFS** if the repo has no `.gitattributes`/LFS and assets are
  >~50MB total; add `*.gif filter=lfs diff=lfs merge=lfs -text` to `.gitattributes`
  BEFORE the first `git add` of the assets. Stage ONLY the assets + README, not the
  heavy render-cache dirs (`scenes/media/`, `build/`).
- Relative paths in the README (`explainer_videos/gifs/X.gif`) resolve on GitHub only
  if those files are committed + pushed.

## Push hygiene (this user's standing rule)
- Before pushing a restructured README, `git fetch` + `git rev-list --left-right
  --count main...origin/main` to confirm `0 0` (fast-forward, no conflict).
- Do not push without explicit go-ahead; prefer a NEW commit on top over rewriting
  already-pushed history (amend only for a local, unpushed commit).

## Generator
See `scripts/generate_rich_readme.py` — takes a JSON list of items
`{heading, topic, base, diagram_png, func, test, gif}` and emits the HTML-table README
(Index + per-category blocks). Copy + adapt; it does the GFM-safe HTML for you.
