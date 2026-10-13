# Session note: stale partial re-merge + background-launch false "done"

## Incident (DSA quiz deck, q01-55)
Regenerated deck_a/b/c with code-card embedding (the anti-drop fix). The ending
partial `deck4_1.pdf` (q49-55) was NOT in the JOBS list that run regenerated, so
the merge concatenated the OLD `deck4_1.pdf` (mtime 2026-08-11, from the pre-fix run).
Result: q01-48 had embedded Java code cards; q49-55 still carried NotebookLM's old
paraphrased output — which on some slides had been TRANSLATED to Python. User caught
it visually ("the ending is not Java, it's python").

## Fix applied
- Added a 4th JOB `("mentora","DSA-Q-D",range(49,56),deck4_1.pdf)` and a job-index
  arg (`python3 generate_rotate.py 3`) so a single partial can be rebuilt without
  redoing the good ones.
- After the partial regen, re-ran the merge + Ghostscript compress explicitly.

## Verification signal that was reliable
- `pdftotext -f 1 -l N deck.pdf - | wc -c` == 0 across all ranges => deck is
  rasterized (expected for detailed_deck). That alone can't prove code presence.
- The ONLY deterministic proof code survived is the embedded code-card IMAGE being
  placed; confirm via user eyeball or a working Gemini OCR. In this env the vision
  endpoint 404'd and tesseract on rasterized slides timed out/hallucinated.

## Background-launch trap (separate lesson)
- `nohup python3 script.py &` inside a `terminal` call + notify_on_complete fired the
  completion ping on the WRAPPER shell (which exits instantly), NOT on the python run.
  The real run kept going silently for ~1h.
- Prefer `terminal(background=True, notify_on_complete=True)` with the long command
  directly (no trailing `&`). A chained `nohup ./watcher.sh >/dev/null 2>&1 & echo pid`
  line tripped a zsh parse error and never started.
- `gemini -p "<prompt>"` rejects a positional prompt on stdin ("Cannot use both a
  positional prompt and --prompt"). Pipe prompt via stdin to `gemini -p` with no
  positional arg. The stored `~/.gemini/oauth_creds.json` access_token was 401 expired
  — don't assume Gemini OCR works without a fresh token.
