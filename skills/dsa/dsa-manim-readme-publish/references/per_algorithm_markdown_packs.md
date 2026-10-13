# Per-algorithm markdown packs (LinkedIn / social) from the published README

Second consumer of the same 83-record data model: instead of ONE README with 83
blocks, emit **83 standalone `.md` files**, one per algorithm, each containing
both a long-form article and a short post.

Approved per-file layout (user-specified, verbatim order):

1. `## 1. Watch it run` — the GIF
2. `## 2. How it works (diagram)` — the mermaid PNG
3. `## 3. The function` — real ```java block from `Algorithms.java`
4. `## 4. The unit test (JUnit 5, passing)` — real ```java @Test body
5. `## 5. Complexity` — table: Measure | Value | Why
6. `## 6. Optimised vs modern Java 25 rewrite` — carried from README rows
7. `## LinkedIn article` — long form
8. `## LinkedIn post (short)` — hook + complexity + repo link + hashtags

Generator lives at `scripts/build_linkedin_md.py` in the repo; output to
`linkedin/`. Re-runnable and idempotent.

## Parse the README, not the JSON sidecars

The published `README.md` is the richest single source: it already joined
gif + diagram + function + test + topic + Java-25 rows per algorithm. Split it:

```python
for part in re.split(r"^### ", open("README.md").read(), flags=re.M)[1:]:
    gif  = re.search(r"gifs/([A-Za-z0-9_]+)\.gif", part)   # skip part if None
    png  = re.search(r"docs/diagrams/([A-Za-z0-9_]+)\.png", part)
    meta = re.search(r"<strong>(.*?)</strong><br><code>(.*?)</code>", part)  # topic, scene
```
Three `###` headings are section headers (`Interview Questions`, `Algorithms`,
`Graph Extras`) with no gif — skipping on "no gif match" yields exactly 83.

Unescape README HTML entities in titles: `&quot;`, `&#x27;`, `&amp;`.

## PITFALL: never split code blocks by ORDER

`re.findall(r"```java\n(.*?)```", part)` then `codes[0]=func, codes[1]=test` is
WRONG. 23 of 83 blocks have **only a test block** (the function cell reads
`*source: Algorithms.java*`), so the test got printed as the function.
Split on the README's own labels instead:

```python
fsec = re.search(r"\*\*Function \(Algorithms\.java\):\*\*(.*?)(?=\*\*Unit test|\*\*Optimised vs|\Z)", part, re.S)
tsec = re.search(r"\*\*Unit test \(JUnit 5\):\*\*(.*?)(?=\*\*Optimised vs|\Z)", part, re.S)
```
then take the first fenced block inside each section (empty string if absent).

## Recover missing function source from Algorithms.java

When the function section is empty, derive the symbol from the test body and
brace-match the real source (better than the SKILL.md's older advice to just
show the @Test call — that fallback is now a last resort):

- `new Algorithms.MinStack()` → `re.search(r"class\s+MinStack\b")` (also try
  `record\s+`) → brace-match the whole nested type.
- `Algorithms.heapSort(` → `re.search(rf"(public|private|protected)[\w\s<>\[\],?&.]*?\b{name}\s*\(")`.

**PITFALL — generic signatures break the return-type character class.** A naive
`[\w\s<>\[\],]*?` fails on
`public static <T extends Comparable<? super T>> List<T> heapSort(...)`
because of the `?` (and `&` in intersection bounds, `.` in qualified names).
Include `?&.` in the class. This silently left 1 of 83 as a placeholder.

Brace-match from the matched line start to the balanced closing `}`.

## Complexity table: hardcode a verified map, do not infer

Keep an explicit `CX = {gif_base: (time, space, why)}` dict covering all 83.
The `why` string is reused verbatim in the article and post prose (capitalize
first char), so write it as a sentence fragment: `"Kadane single pass"`,
`"binary-heap priority queue relaxation"`. Note real caveats in it — amortised,
average vs worst case, output-size-dominated (`subsets`, `permutations`).

## Diagram name mismatches (S* / graph-extra scenes)

Single-path `S*` gifs and the four graph extras don't follow the
`Q05_MissingNumber → Q5_missingNumber` rule; their diagrams live under the
ORIGINAL question numbering. Keep an explicit `PNG_FIX` dict, e.g.
`S06_ValidParentheses → Q13_isValidParentheses`, `S02_MergeSort → A2_mergeSort`,
`S03_BFS → A5_bfs`, `S14_Dijkstra → Q29_dijkstra`, `S08_SieveOfEratosthenes → A8_sieve`.
Build candidates by matching the gif's trailing word against
`docs/diagrams/[QAS]\d+_<word>.png` case-insensitively, then hand-verify.
Note `Q39_kthSmallEst.png` has an odd capital E — exact-match on disk, always.

## Authoring the 4 missing graph-extra diagrams

Astar / BellmanFord / FloodFill / FloydWarshall had NO diagram. Write
`docs/diagrams/G_<name>.mmd` flowcharts and render them rather than emitting a
"no diagram" placeholder. Quote every node label (`A["dist[src] = 0"]`) —
brackets and parens in labels break unquoted mermaid.

## Absolute raw URLs, not repo-relative paths

These files get pasted into LinkedIn / read outside the repo, so images must be
absolute:
`https://raw.githubusercontent.com/dbillion/dsa-java-gradleqa/main/<path>`
Validate every one resolves on disk before declaring done.

## Validation gate (run before reporting success)

Assert across all 83 files: count == 83; zero broken asset refs; zero
`No diagram generated`; zero `see src/main` / `see src/test` placeholders; all
8 section headings present; no `| Time | \`—\`` rows. A green count with
placeholders inside is NOT done — the user expects real code in every file.
