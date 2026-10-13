# README explainer tables (GitHub constraint) — dsa-java-gradleqa

GitHub-Flavored Markdown tables CANNOT contain fenced code blocks (```) or a full-width
image. So each question/algorithm is an **HTML table**, not a markdown table.

## Per-question block shape
```html
<table>
<tr><th>Topic</th><th>Diagram</th><th>Question solved</th></tr>
<tr><td><strong>Arrays_Subarrays</strong><br><code>q05_missing_number</code></td>
    <td><img src="docs/diagrams/Q5_missingNumber.png" alt="diagram" width="220"></td>
    <td>Q5 missingNumber</td></tr>
<tr><th>Function(s) used</th><th colspan="2">Unit test (JUnit 5)</th></tr>
<tr><td><pre><code class="language-java">public static int missingNumber(int[] n){...}</code></pre></td>
    <td colspan="2"><pre><code class="language-java">assertEquals(2, Algorithms.missingNumber(...));</code></pre></td></tr>
<tr><td colspan="3" align="center"><img src="explainer_videos/gifs/Q05_MissingNumber.gif" alt="Q05_MissingNumber" width="100%"></td></tr>
</table>
```
Row1 = 3 cols (Topic | Diagram | Question). Row2 = 2 cols (Function | Unit test, colspan=2).
Row3 = full-width GIF (colspan=3). Repeat per question.

## Diagram path mapping
Diagram PNGs are named `Q5_missingNumber.png` style (NO zero-pad, first word letter
lowercased): `^([QASF])(\d+)_([A-Za-z0-9]+)$` → `pre + int(num) + "_" + word[0].lower()+word[1:]`.
S (single-path) and graph-extras (FloodFill/FloydWarshall/Astar/BellmanFord) have NO
diagram PNGs — render `—` in the Diagram cell, never a broken `<img>`.

## Topic index (clickable)
```
## Topics
- [Arrays & Subarrays](#arrays_subarrays)
- [Graphs](#graphs)
```
Anchor = topic lowercased, spaces→`-`, strip `&` and `/`. Each topic is a `### <Topic>`
heading. Group blocks under their topic heading.

## Data sources (extract, don't paraphrase)
- Functions: brace-match the real method from `src/main/java/dsa/Algorithms.java`
  (find `public static <name>(`, match braces).
- Unit test: the real `@Test` body from `_tests.json` keyed by `test_name`.
- GIF: map scene base → gif via `_render_map_full.json` `final` (names are inconsistent).

## Validation (run before committing)
- 0 broken `explainer_videos/gifs/*.gif` refs (every referenced gif exists on disk).
- 0 broken `docs/diagrams/*.png` refs (the only `<img>` tags; code-fence mentions don't count).
- balanced `<table>`/`<tr>`/`<pre>` counts.
- A standalone preview HTML (rewrite relative paths to `file://` abs) lets you eyeball render.
