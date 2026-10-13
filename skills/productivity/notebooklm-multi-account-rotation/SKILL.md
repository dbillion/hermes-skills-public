---
name: notebooklm-multi-account-rotation
category: productivity
version: 0.1.0
description: Rotate NotebookLM generation across multiple Google accounts; share notebooks to editors; avoid rate limits; automate invites and execution.
triggers:
  - NotebookLM rate limits when generating artifacts (video/audio/slides)
  - Need to distribute NotebookLM generation across multiple Google accounts
  - NLM CLI automation for large multi-notebook pipelines
---

# NotebookLM multi-account rotation for generation

## When to use
- You’re generating many NotebookLM artifacts (video/audio/slides/report/quiz/etc.) and hit rate limits.
- You have multiple Google accounts/profiles logged in to `nlm` and want to rotate usage.

## Core idea
1. **Owner account shares notebooks** to other accounts as **editors**.
2. Rotate `nlm login switch <profile>` per phase/batch.
3. Generate artifacts in each account’s quota window.

## Steps

### 1) Identify notebook IDs
Source file (example):
- `/tmp/ai-eng-nlm/notebook-ids.txt`
Format:
```
<phase> <notebook_id>
```

### 2) Collect collaborator emails
Get emails from Google account switcher (e.g., NotebookLM app) or `gemini accounts list`.
Use a single CSV string:
```
EMAILS="a@gmail.com,b@gmail.com,c@gmail.com"
```

### 3) Invite collaborators as editors
Use the **owner profile** (the one that created the notebook):
```bash
nlm login switch <owner_profile>

for nb_id in $(awk '{print $2}' /tmp/ai-eng-nlm/notebook-ids.txt); do
  nlm share invite "$nb_id" "a@gmail.com" --role editor
  nlm share invite "$nb_id" "b@gmail.com" --role editor
  # ...repeat for all emails
  sleep 1

done
```

**Pitfall:** `nlm share batch` may return `INVALID_ARGUMENT` with multiple emails — use `nlm share invite` per email instead.

**Pitfall:** `PERMISSION_DENIED` means you are not the owner for that notebook — switch to its owner profile and re-run invites.

### 4) Rotate profiles for generation
Assign phases to profiles (example):
- dayozoe → phases 00–04
- mentora → phases 05–09
- trinity → phases 10–14
- abiodun → phases 15–19

Then:
```bash
nlm login switch <profile>
# run generation commands for that profile’s phases
```

### 5) Rate‑limit handling
- For video/audio: pause 60–180s between creates.
- If you see `Rate limited — API error (code 8)`:
  - Switch to the next profile.
  - Continue generation on that profile.

## Verification
- `nlm share status <notebook_id>` shows collaborators and roles.
- `nlm studio status <notebook_id> --json` shows generated artifacts.

## Output collection
Download artifacts after status shows `completed`.

## Forcing real code into generated slides (anti-drop fix)

**Symptom:** you prompt NotebookLM for "include the exact code / JUnit test" but the rendered
`detailed_deck` slides contain **no code** (or code is paraphrased/restyled illegibly).

**Root cause (verified):** NotebookLM `detailed_deck` output is **rasterized images** — it
*paraphrases/restyles text* but **embeds image sources as-is**. Any code you ask for in prose gets
redrawn (and dropped). Confirmed by checking the PDF text layer: a 53-slide deck had **0 selectable
text characters** across every page range — proof the model synthesized the layout instead of copying.

**Fix — feed code as images, forbid redraw:**
1. Extract each question's EXACT method + test from the source (e.g. ```java fences in the `.md`
   source files, or slice from the real `.java`). Render each as a clean code-card PNG
   (see `scripts/render_code_cards.py`).
2. Add the PNGs as **image sources** to the notebook per question.
3. In the FOCUS prompt, make embedding mandatory and explicit:
   > CODE IS SUPPLIED AS READY-MADE IMAGES (the 'qNN_method' and 'qNN_test' source images).
   > You MUST place BOTH the method image and the test image onto the slide EXACTLY as given —
   > do NOT redraw, retype, paraphrase, summarize, or omit any code. This is mandatory, not optional.
4. Pass both the question source id AND the two code-card source ids to `slides create --source-ids`.

**Pitfall — source files may lack the method:** when backfilling, some question `.md` files had only
a JUnit test and a `*source: Algorithms.java*` placeholder (no method code at all). Slice the real
method from the Java source before rendering cards, or those slides will ship test-only.

**Pitfall — backfill can DUPLICATE the marker line:** when inserting a ```` ```java ```` method block
after `**Function (Algorithms.java):**`, a naive replace that rewrites the marker can leave TWO
`**Function (Algorithms.java):**` lines (original + inserted), breaking the 2-fence assumption and
code-card extraction. After backfill, collapse adjacent/blank-separated duplicate markers with a
one-shot regex (`re.sub(r"(\*\*Function \(Algorithms\.java\):\*\*\n)\n+\*\*Function \(Algorithms\.java\):\*\*", r"\1", t)`) and assert exactly **one** marker + **two** ```` ```java ```` fences per file.

**Verification after generation:** run `pdftotext -f 1 -l N deck.pdf - | wc -c` on a few page ranges.
If it reports 0, the deck is rasterized — that's expected for `detailed_deck`, but it means the ONLY
way code survived is via the embedded image cards. Visually spot-check 2–3 content slides to confirm
the code image is present and legible (OCR/vision may be unreliable in some envs — the text-layer
check is the deterministic signal).

## Merge bug — do NOT route pdf tools through an nlm-prepending runner

**Pitfall:** if your generation script has a helper like `run(args)` that does
`subprocess.run(["nlm"] + args, …)`, calling `run(["pdfunite", …])` silently executes
`nlm pdfunite …` (a no-op) and the merge never happens — `pdfinfo` then reads a missing file and
prints an empty `MERGED []` that *looks* like success. **Always call `pdfunite`/`pdfinfo` via a raw
`subprocess.run(["pdfunite", …], check=True)`.** Verify the merged file exists and `pdfinfo` reports
the expected page count before declaring done.

**Pitfall — a previously-generated PARTIAL deck can be STALE and silently re-merged:** the merge step concatenates fixed filenames (e.g. `deck4_1.pdf`). If an earlier run produced that partial and a later run regenerates only the OTHER partials, the merge pulls in the OLD partial — with its old bugs. Seen in practice: the q49–55 ending deck's mtime was days older than the re-run, so its slides still carried NotebookLM's old paraphrased/Python code while q01–48 were fixed. **Fix:** (a) make the pipeline support selective re-run of one partial via a job-index arg (`python3 generate_rotate.py 3` runs only `JOBS[3]`), and/or (b) before merging, assert every partial's mtime is newer than the last source change, or just regenerate ALL partials. Always `stat` each partial's mtime and confirm it matches the current run before trusting the merged output.

## Delivery to Telegram (50 MB cap)

- Telegram's standard-account upload limit is **50 MB**. A 55-slide `detailed_deck` PDF is often
  50–60 MB and will fail to send via `MEDIA:/path`.
- **Compress with Ghostscript** (NOT ffmpeg — ffmpeg is audio/video only and cannot shrink a PDF):
  ```bash
  gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
     -dNOPAUSE -dQUIET -dBATCH -sOutputFile=out.pdf in.pdf
  ```
  `/ebook` downsamples embedded images; a 57 MB deck typically drops to ~6–7 MB with acceptable
  legibility. `/screen` is smaller but lower quality.
- If still over 50 MB, split with `qpdf --empty --pages in.pdf 1-27 -- part1.pdf` (note `--empty` is
  required as the input placeholder) and send both parts.

## Long-running re-run: how to actually get notified when it FINISHES

A NotebookLM full re-run takes ~1–2h (per-deck polling is `range(90)` × 20s). Background-launch it
correctly or you'll get a false "done" ping:

- **Do NOT** wrap the run in `nohup python3 script.py &` inside a `terminal` call and rely on
  `notify_on_complete` — the *wrapper shell* exits instantly (the `&` detaches), so the completion
  notification fires on the wrapper, not the Python process. The real run keeps going silently.
- **PREFERED:** pass the long-running command directly to `terminal(background=True,
  notify_on_complete=True)` WITHOUT a trailing `&`. Hermes tracks that actual process and pings when
  IT exits. (But see next pitfall — even this can be blocked for wrapper-style lines.)
- **Pitfall:** a launch line shaped like `… nohup ./watch_rerun.sh >/dev/null 2>&1 & echo "pid"` trips a
  shell parse error (zsh: `parse error near 'echo'`) and the watcher never starts. If you must chain a
  watcher, put the watcher logic INSIDE the backgrounded script (it polls the python PID, then
  verifies+compresses+writes a `.rebuild_done` flag) and launch that script alone via
  `terminal(background=True)`.
- **Verification while it runs:** `pgrep -f 'generate_rotate.py'` confirms the real process is alive;
  `tail rerun.log` shows progress (note Python buffers `print`, so the log lags during the slow
  `nlm source add --wait` phase — look for `reuse notebook` then `art <id>` then `done`).
- **OCR/visual check is unreliable in this env:** the vision endpoint returned 404 and `tesseract` on
  the rasterized slides timed out/hallucinated. The deterministic signal is the **text-layer check**
  (`pdftotext … | wc -c` == 0 means rasterized, expected). For confirming embedded code images, rely
  on the USER's eyeball or a working Gemini OCR. Note: `gemini -p "<prompt>"` REJECTS a positional
  prompt on stdin (`Cannot use both a positional prompt and --prompt`); pipe prompt via stdin to
  `gemini -p` with NO positional arg, and the stored `~/.gemini/oauth_creds.json` access_token was
  expired (401) — don't assume Gemini OCR works without a fresh token.

## References
- See `references/notebooklm-rotation-session.md` for recent session details, errors, and email list format.
- See `references/deck-code-drop-fix.md` for the full diagnosis + fix recipe (code-card technique).
- See `scripts/render_code_cards.py` for a reusable code-card PNG generator.
- See `scripts/gen_deck_pipeline.py` for a known-good `generate_rotate.py` template: per-profile JOBS,
  code-card source injection, verbatim-embed FOCUS, raw `pdfunite` merge, and a job-index arg
  (`python3 gen_deck_pipeline.py 3`) for selective partial re-runs (fixes the stale-partial pitfall).
- See `references/stale-partial-and-background-launch.md` for the incident where an OLD partial
  `deck4_1.pdf` was silently re-merged (Python leakage on ending slides) + the background-launch
  false-"done" trap.
