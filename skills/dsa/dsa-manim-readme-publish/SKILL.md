---
name: dsa-manim-readme-publish
description: Publish Manim DSA GIFs to a GitHub README (3+2+1, LFS).
---

# DSA Manim README Publish

Turn generated Manim DSA explainer GIFs (and their real function source + JUnit
tests) into a GitHub-readable README where each algorithm/question is a block:

  1. Row (3 cols):  Topic | Diagram (mermaid→PNG) | Question solved
  2. Row (2 cols):  Function(s) used (code block) | Unit test (code block)
  3. Row (full width, colspan=3): the Manim GIF

Then the next block repeats. A clickable topic index at the top links to each
topic anchor. This is the layout the user explicitly asked for and approved.

## When to use
- After a Manim DSA video batch is rendered (mp4s exist) and you want them in
  the repo README.
- The user says "embed the gif under each question", "make a README table with
  code + test + video", "publish the explainers", etc.
- **Also**: any OTHER publishing surface fed by the same 83-record model —
  per-algorithm markdown packs, LinkedIn articles/posts, social content.
  See `references/per_algorithm_markdown_packs.md` for the 83-standalone-`.md`
  variant (gif → diagram → function → test → complexity table → article → post),
  its parser pitfalls, and the validation gate. Reuse the data model; only the
  emitter changes.
- **Also**: the user asks to ADD a second version of each function ("modern
  rewrite", "Java 25 version", "stream version") to an already-published doc.
  See `references/additive_code_variants.md`. Non-negotiables from that session:
  the tested original is never edited (new block goes BELOW it, proven with a
  0-removed-lines difflib assert), variants are compiled and randomised-diffed
  against the originals rather than asserted equivalent, and the "streams are
  faster" premise gets corrected rather than silently obeyed.

## Hard constraints (GitHub-flavored Markdown)
- **Mermaid does NOT render inside table cells.** Use the pre-built PNG
  (`docs/diagrams/<name>.png`). Store diagrams as PNG, not live mermaid, in
  cells.
- **Fenced code blocks (```) do NOT render inside markdown table cells.** Use
  an HTML `<table>` with `<pre><code>` cells — GitHub renders that. This is the
  ONLY way to get a true colspan=3 full-row GIF and real code blocks side by
  side.
- Anchors: GitHub auto-generates `#topic-name` from `### Heading`. Build the
  index with `text.lower().replace(' ','-')` (strip `&` and `/`).

## Process
1. **Build the data model** (one record per scene):
   - `base` (scene file name, e.g. `q03_two_sum`), `cat` (Q/A/S/F/B from first
     char), `test_name` (from `_scene_spec.json`), `gif` (final gif name),
     `func` (real method source from `Algorithms.java`), `test` (real @Test body
     from `_tests.json`), `topic` (from `organized/` symlinks).
   - See `references/data_extraction.md` for the exact extraction recipe and the
     pitfalls that bit us (gif name mapping, topic via os.walk not glob, diagram
     path conversion, stack-impl methods with no extractable source).
2. **Generate any missing GIFs** from the mp4s (raw render in
   `scenes/media/videos/<base>/480p15/<SceneClass>.mp4`, OR the renamed final in
   `final_videos/`). Use the ffmpeg palette method in `references/gif_recipe.md`
   (480p, git-friendly). 70 of 83 is normal; the 13 "missing" are usually just
   un-giffed scenes, NOT deleted files — verify on disk before assuming loss.
3. **Assemble the README** as HTML tables per the layout above. Validate with the
   checker in `references/validate_readme.py` (counts `<table>`/`<tr>`/`<pre>`,
   checks every `gifs/*.gif` and `docs/diagrams/*.png` ref resolves on disk).
4. **Commit + push** via Git LFS (see below). Do NOT push without explicit user
   OK (user rule: no unilateral push).

## Git LFS (gifs are 100K–4M each; 83 ≈ 130M+)
- `git lfs install --local`
- `.gitattributes`: `*.gif filter=lfs diff=lfs merge=lfs -text`
- Stage ONLY `README.md` + `explainer_videos/gifs/*.gif`. Do NOT stage
  `scenes/media/` (thousands of raw mp4 partials — huge).
- Push may exceed 60s foreground timeout → run in background (`notify_on_complete`)
  and verify with `git fetch` + `git rev-list --left-right --count main...origin/main`
  → expect `0 0`.

## Pre-push safety (user demands this)
- Always `git fetch` and compare divergence BEFORE pushing. `git rev-list
  --left-right --count <branch>...origin/<branch>` → `0 <remote-only>` means
  remote moved; `local remote` (local-only) + remote-is-ancestor-of-local =
  fast-forward, no conflict. The user explicitly asked "did you check the commit
  doesn't conflict before pushing" — make this a mandatory step.
- Default branch name varies: this repo uses `main`; sibling repo
  `manim-storytelling-skills` uses `master`. Detect via `git branch -r` /
  `git rev-parse --abbrev-ref --symbolic-full-name @{u}`, never assume `main`.

## Rendering mermaid → PNG (mmdc)

`mmdc -i x.mmd -o x.png -b white -w 900`. If it dies with
`Could not find Chrome (ver. ...)` / puppeteer cache complaints, point it at a
system browser instead of installing puppeteer's bundled Chrome:

```bash
echo '{"executablePath":"/usr/bin/chromium","args":["--no-sandbox"]}' > /tmp/pp.json
mmdc -i x.mmd -o x.png -b white -w 900 -p /tmp/pp.json
```
Each render takes ~20–60s (browser cold start). Loop with
`timeout 90` per file and a generous outer timeout, or a 4-file batch will trip
the 60s foreground limit mid-run.

## Pitfalls (learned the hard way)
- **Glob `organized/*/*` returns nothing** when `organized/` holds symlinks to
  other dirs — use `os.walk` + `os.path.islink` to read topic→gif mapping.
- **Gif filename ≠ scene base.** The render map (`_render_map_full.json`) holds
  the authoritative `base → final` (gif) name. Match via that, then fall back to
  normalized (strip non-alphanumerics, case-insensitive) comparison.
- **Diagram PNG path**: `Q05_MissingNumber.gif` → `docs/diagrams/Q5_missingNumber.png`
  (no zero-pad, first word letter lowercased). Convert with the regex in
  `references/data_extraction.md`. If the PNG doesn't exist on disk, render a
  `—` cell, never a broken `<img>`.
- **Stack-impl methods** (MinStack, MaxStack, QueueWithStacks, LCA) have no
  top-level `public static` source — but they ARE recoverable: derive the type
  from the test body (`new Algorithms.MinStack()`) and brace-match
  `class <Name>` / `record <Name>` in `Algorithms.java`. Showing the @Test call
  instead is the LAST resort, not the first. Recipe + the generic-signature
  regex trap are in `references/per_algorithm_markdown_packs.md`.
- **Never pair code blocks by index.** 23 of 83 README blocks contain ONLY a
  test block, so `codes[0]=func, codes[1]=test` silently prints the test as the
  function. Split on the `**Function (Algorithms.java):**` /
  `**Unit test (JUnit 5):**` labels instead.
- **Diagram numbering diverges for `S*` and graph-extra scenes** — they map back
  to the ORIGINAL question numbers (`S03_BFS → A5_bfs`,
  `S14_Dijkstra → Q29_dijkstra`). Keep an explicit fix-up dict; the generic
  regex conversion above does not cover them.
- **Topic index with no topics** → empty sections → no blocks written. Always
  assign a fallback topic (e.g. "Misc") so every record emits a block.
- **`./gradlew test -q` prints nothing on success** — and also nothing when it
  no-ops on an up-to-date build. Never report "tests pass" from silence or from
  `BUILD SUCCESSFUL` alone; run `clean test` and count `tests=`/`failures=` out
  of `build/test-results/test/*.xml`. Snippet in
  `references/additive_code_variants.md`.
- **Phase-2 re-render overwrites `final_videos/` in place** (removes old then
  rewrites). `gifs/` is a separate folder and is NOT touched by it. If the user
  says "don't let regeneration affect the current output", redirect the re-render
  to a separate folder (e.g. `final_videos_v2/`) — the default script overwrites.

## Committing into a noisy working tree

This repo accumulates large untracked byproducts (`media/`, `collected_1080p/`,
`_gradle_test.log`, dated `README.md.bak_*`, batch txt files) — 41 untracked
entries in one session. **Never `git add -A` / `git add .` here.**

- Create a topic branch, then stage an **explicit allowlist** of paths for the
  work you actually did. Confirm with `git diff --cached --stat` before commit.
- Run the suite and count real numbers (see the XML snippet above) *before*
  committing, not after.
- After pushing, verify the branch actually landed rather than trusting push
  output:
  ```bash
  git ls-remote --heads origin <branch>
  git rev-parse HEAD origin/<branch>          # SHAs must match
  git ls-tree -r --name-only origin/<branch> | grep -c '^linkedin/'
  ```
- Branch naming: use the class of work (`java25-rewrites-and-linkedin`), not a
  dated or session-specific label.

## Relation to other skills
- `manim-dsa-storytelling` (and its siblings `manim-dsa-explainer`,
  `manim-dsa-single-path`) GENERATE the videos. This skill PUBLISHES them.
  NOTE: two copies of `manim-dsa-storytelling` exist in the skills dir
  (`/home/deeone/.hermes/skills/manim-dsa-storytelling` and
  `.../creative/manim-dsa-storytelling`) — ambiguous name; flag for curator
  consolidation. If you patch that skill, add a "Publish to README" pointer here.
