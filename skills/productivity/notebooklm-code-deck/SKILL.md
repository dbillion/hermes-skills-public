---
name: notebooklm-code-deck
description: Build NotebookLM decks keeping code via code-as-image PNGs.
---

# NotebookLM Code Deck Workflow

Build a slide deck in NotebookLM where the REAL code must survive generation.

## Why this exists
NotebookLM's `detailed_deck` format **rasterizes text and drops synthesized/paraphrased
code** — slides come out with 0 selectable text and the method/JUnit lines missing, even
when the source has them. Verified: a 53-page deck had 0 text chars; OCR of a slide showed
the code was simply absent. NotebookLM embeds *images* as-is, though, so the fix is to
pre-render code as PNGs and force the prompt to embed them verbatim.

## Environment
- CLI: `nlm` (v0.9.6). Auth: `nlm login switch <profile>`.
- Profiles to ROTATE to dodge per-account rate limit (code 8): mentora, trinity, glorious
  (also adeoye53, abiodun, adeoye55er, architect exist). One deck per profile.
- DSA quiz project: `/home/deeone/Desktop/quiz` (sources in `sources/qNN.md`,
  code cards in `codecards/`, driver `generate_rotate.py`).

## Steps
1. **Prepare sources** with the method AND the JUnit test each in a ```java fence.
   (If a source only has a test + a `*source: Algorithms.java*` placeholder, extract the
   real method from the Java file and backfill it first.)
2. **Generate code-card PNGs** — one `qNN_method.png` and `qNN_test.png` per question, via
   PIL (JetBrains Mono). Render verbatim, high contrast. Non-artifact, no NotebookLM cost.
3. **Rotate profiles**: switch profile per deck. `generate_rotate.py` does mentora→trinity→glorious.
4. **FOCUS prompt MUST say**: code is supplied as ready-made images; place BOTH images
   EXACTLY as given — do NOT redraw/retype/paraphrase/summarize/omit any code. Mandatory.
5. **Add the PNGs as image sources** alongside the markdown question sources.
6. **Generate** with `nlm slides create --format detailed_deck --confirm --source-ids ... --focus ...`.
   Poll `nlm studio status` until `completed`, then `nlm download slide-deck`.
7. **Merge** the per-profile PDFs with a RAW `subprocess.run(["pdfunite", ...])`.
   CRITICAL: do NOT route pdfunite through a helper that prepends `nlm` — it silently
   no-ops and you get `MERGED []` with no output file.
8. **Compress for Telegram** (<50 MB cap): `gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4
   -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH -sOutputFile=out.pdf in.pdf`.
   (ffmpeg does NOT compress PDFs — it's audio/video only.)

## Pitfalls
- `detailed_deck` output is image-only: verify code landed by rendering a page and OCR'ing,
  not by `pdftotext` (text layer will be empty even when code images are present).
- The `run()` wrapper in generate_rotate.py prepends `nlm` to every arg — fine for nlm
  commands, fatal for `pdfunite`/`gs`. Use raw subprocess for non-nlm binaries.
- Telegram media upload via `MEDIA:/abs/path` works; 50 MB hard cap for standard accounts.
- Vision endpoint (vision_analyze) was 404/unreliable here; tesseract OCR on full-res
  images times out — downscale to ~640px before OCR.
