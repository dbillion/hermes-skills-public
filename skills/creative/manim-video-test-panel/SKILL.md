---
name: manim-video-test-panel
description: Add a real test panel to generated Manim explainer videos.
---

# Manim Video "Verified by Test" Panel

When you generate explainer videos from a code repo (DSA algorithms, library
APIs, interview questions), the most credible closing beat is a panel that
shows the real unit test AND its expected output — pulled from an actual test
run, not invented. This skill captures the end-to-end pattern and the pitfalls
that bite when you bulk-edit dozens of generated scene files.

## When to use
- Building a video per `@Test` / test case and the user wants the output shown.
- "Get the test output and store it so I know what the repo gives" (ground truth).
- Adding a correctness receipt to an existing batch of explainer scenes.

## The pattern (5 steps)

### 1. Capture ground truth from a real test run
Run the project's tests and SAVE the results — do NOT eyeball expected values.
- Java/Gradle: `./gradlew test --console=plain` → parse
  `build/test-results/test/TEST-*.xml` (testcase `name` attr, `failure` element).
- Python: `pytest -v` → parse the summary, or `pytest --junitxml=...`.
Store as JSON keyed by test method name (strip `()` from `name="Q3_twoSum()"`):
`{ "Q3_twoSum": {"status": "PASS", "expected": "[0,1]"}, ... }`.
A test run only writes to gitignored `build/` — it does NOT touch your videos.

### 2. Extract the real `@Test` / test body
For each mapped scene, extract the actual test source (brace-matched grep, or
read the test file). Show it VERBATIM in the panel — the value of the beat is
that a viewer can reproduce it.

### 3. Render the panel (helper signature)
A `test_panel(scene, test_code, expected_text, label="Verified by test")`
helper should return 4 mobjects: `(label, code, out_label, out_value)` so the
caller can fade all four out. Make the EXPECTED OUTPUT big and centered — a
tiny caption is invisible and defeats the purpose. Add a trailing comment line
to the displayed test code, e.g.:
`} // -> [1,2,5,8,9]   (gradle test: PASS)` — this is the "comment showing the
output" the user asked for.

### 4. Bulk-inject into N scene files (scripted, not by hand)

**Pre-step (MANDATORY): re-indent every column-0 `self.` line to 8 spaces across
ALL scene files BEFORE injecting.** A prior bad injection pass strips the anchor's
indentation, and a `revert` script CANNOT restore untracked generated scenes
(`git checkout`/`git revert` are no-ops on untracked files). The only safe cleanup
is to normalize `self.`-at-column-0 → 8 spaces. Do this for all N files, not just
the ones that fail `ast.parse` — both the anchor-strip and the import-guard
false-negative bite *silently* (a `self.play(...)` at col 0 is syntactically valid
Python; it only NameErrors at render time). A one-line check like `bad=[]; ...; bad=[]`
inside a shell heredoc also prints "NONE" even when errors exist — use a dedicated,
clean parse check.

Then write a python injector that, for each scene file:
- matches the last teardown anchor (`re.finditer(r"self\.play\(FadeOut\(")`),
- inserts the test act BEFORE the anchor's LINE START (keep its indentation),
- adds the `test_panel` import via a standalone `from dsa_style import test_panel`
  line after `from manim import *` (works for single- AND multi-line imports).
Skip helpers (`dsa_style.py`, `template.py`, etc.).

**Reusable scripts in this skill** (copy + adapt): `scripts/reindent_col0.py`
(MANDATORY pre-step), `scripts/inject_test_panel.py` (the injector above),
`scripts/revert_injection.py` (safe cleanup for untracked scenes — git can't).

### 5. Verify, then render
After injection, `ast.parse` EVERY file (not just a sample). Then render-test
1–3 representative scenes (incl. one that was previously broken) BEFORE launching
the full batch. Only then run the full re-render.

## FOUR PITFALLS (see references/manim_test_panel_pitfalls.md)
1. **Insertion offset strips the anchor's indentation** → `self` undefined at
   runtime. Insert at the anchor LINE start (`src.rfind("\n",0,last.start())+1`),
   NOT at `last.start()` (the char), which drops the leading whitespace.
2. **Import guard matches the call, not the import** → `test_panel` undefined.
   Guard on `re.search(r"test_panel\s*[),]", src)` (an import item), NOT on the
   bare substring `"test_panel"` (present in `test_panel(self, ...)`).
3. **Parse-gate false negatives** → a `self.play(...)` at column 0 is syntactically
   valid (NameError is runtime). `ast.parse` PASS does NOT mean it'll render.
   Also: a buggy one-line `bad=[]; ...; bad=[]` check in a shell heredoc prints
   "NONE" even when errors exist. Always re-verify with a clean dedicated check.
4. **git can't restore untracked files** → `git checkout` / `git revert` does
   NOTHING for untracked generated scenes. If you must revert a bad bulk edit,
   keep a python revert script; fix column-0 method-body lines (`self.` at col 0
   → re-indent to 8) rather than guessing.
   - **Pre-push no-conflict check (MANDATORY before any push):** fetch, then
     `git rev-list --left-right --count <branch>...origin/<branch>` — expect
     `1 0` (1 local commit, 0 remote). Confirm the edited file is unchanged on
     remote vs your merge-base. Then `git merge-base --is-ancestor origin/<branch>
     <branch>` must be TRUE (push will fast-forward). **The default branch is NOT
     always `main`** — verify with `git branch -r` / `git symbolic-ref
     refs/remotes/origin/HEAD`. A wrong branch name makes the check error with
     "unknown revision", which is NOT a conflict — re-run against the real branch.
   - **User rule — don't stop a running batch to redirect output:** if a long
     render batch is writing to the "wrong" folder, do NOT `pkill`/kill it and
     restart (the user will say "don't stop anything"). Instead leave it running
     and start the NEW output into a separate folder, or let it finish. `pkill`
     can also kill the agent's own shell (exit -15) — avoid it.

## From rendered mp4 → GIF → embedded in a README
Once scenes are rendered (mp4), turn them into git-friendly GIFs and embed them
so a repo reader sees the animated explanation next to the code.

### mp4 → GIF (two-pass palette, 480p)
```bash
W=854; H=480   # 480p is git-friendly; 1080p blows up repo size
name=$(basename "$f" .mp4); gif="gifs/$name.gif"
pal=$(mktemp /tmp/pal.XXXX.png)
ffmpeg -y -i "$f" -vf "fps=15,scale=${W}:${H}:flags=lanczos,palettegen" "$pal"
ffmpeg -y -i "$f" -i "$pal" -lavfi "fps=15,scale=${W}:${H}:flags=lanczos[x];[x][1:v]paletteuse" "$gif"
rm -f "$pal"
```
Batch: loop over `final_videos/*.mp4`, noop if `gifs/$name.gif` already exists.

### Embed under each question (not a flat gallery)
In the README, place each GIF **directly under its interview question / algorithm
row**, not in a separate index table. Map the gif filename to the table's short
key (strip leading zeros: `Q06_GroupAnagrams` → `Q6`) and insert a line after the
matching `| Qn |` / `| An |` row:
`  - Manim: ![Manim Q06_GroupAnagrams](explainer_videos/gifs/Q06_GroupAnagrams.gif)`
Multiple gifs per question (e.g. brute vs optimized) → insert all matches.
For GitHub to render, the gifs MUST be committed + pushed (relative paths don't
resolve otherwise). Mirror the source repo's style (e.g. a Colab-notebook README's
table-driven lead) when restructuring.

## Delivery / repo hygiene (user rule)
- Do NOT run `git push` / `git config` / force-push on the user's repos without
  explicit OK. Commit locally is fine; pushing is a shared-state action.
- Do NOT `rm -rf` during generation/render tasks unless explicitly told.
- Local files: state the absolute path in the CLI reply; do NOT emit `MEDIA:`
  tags (those are for messaging platforms, not the CLI).
