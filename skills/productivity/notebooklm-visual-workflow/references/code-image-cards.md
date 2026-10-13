# Code-as-Image Cards for NotebookLM Slide Decks

## Problem (verified this session)
NotebookLM `slides create --format detailed_deck` produces **image-only** output
with NO extractable text layer, and it *summarizes/restyles* the source instead of
copying it. A 53-page deck generated from sources that each contained a full Java
method + JUnit test had **0 selectable text characters** (proven via `pdftotext`
over every page range). The literal code (`assertEquals`, method signatures) never
appeared on the slides — confirmed by the user ("the generated slides has no codes").

## Root cause
NotebookLM paraphrases **text** sources but embeds **image** sources as-is. So any
code you want verbatim on a slide must be supplied as an IMAGE, and the prompt must
force embedding that image rather than redrawing the code.

## Recipe
1. Parse each source `.md` for its ```java fenced blocks. Typically [method, test].
2. Render each block to a PNG using a monospace font at high DPI (so it stays legible
   after NotebookLM downscales it). Title bar + white code area on light background.
   See `scripts/render_code_cards.py` (reusable generator; PIL + JetBrains Mono).
3. `nlm source add <nb> --file codecards/qNN_method.png --title "qNN method code (verbatim image)" --wait`
   (and `_test.png` similarly).
4. In `--focus`, MANDATE verbatim embedding — do NOT let it redraw:
   "CODE IS SUPPLIED AS READY-MADE IMAGES (the 'qNN_method' and 'qNN_test' source
   images). You MUST place BOTH onto the slide EXACTLY as given — do NOT redraw,
   retype, paraphrase, summarize, or omit any code. Embed at readable size."
5. Pass BOTH the question-source IDs and the code-card image IDs to
   `slides create --source-ids <all,comma-separated>`.

## Source-gap gotcha (found while building cards)
Some source files have a JUnit test but NO method block (just a
`*source: Algorithms.java*` placeholder). With `re.findall(r"```java\s*\n(.*?)```",
txt)` those yield only 1 fence → only a test card gets rendered; the method card is
impossible (code is missing upstream). Backfill the real method into the source
`.md` first, OR accept test-only slides. Detect this by counting java fences per file.

## Verification after generation
- `pdftotext deck.pdf - | wc -c` will be ~0 (expected — slides are rasterized). That
  does NOT mean code is missing; it means code is IN THE IMAGE. Verify visually
  (render a page with `pdftoppm` + `vision_analyze`, or OCR a downscaled copy).
- Confirm code survived by OCR: `convert page.png -resize 50% sm.png && tesseract sm.png stdout`
  (full-DPI OCR on heavy decks can time out; downscale first).

## Delivering the deck (Telegram `MEDIA:` + compression)
- **Telegram `MEDIA:` has a ~50 MB cap.** Rasterized NotebookLM decks are often 30–60 MB.
  A 57 MB deck silently fails to send — compress BEFORE delivering.
- **Compress with Ghostscript, NOT ffmpeg.** ffmpeg is audio/video only; it cannot
  shrink a PDF. Use:
  `gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE
  -dQUIET -dBATCH -sOutputFile=out.pdf in.pdf`
  (`/ebook` took a 57 MB deck to ~7 MB this session; `/screen` is smaller, `/printer`
  near-lossless). Verify with `pdfinfo out.pdf | grep Pages`.
- **Split with qpdf if still over 50 MB:** `qpdf --empty --pages in.pdf 1-27 -- p1.pdf`
  and `qpdf --empty --pages in.pdf 28-53 -- p2.pdf`. Output file goes LAST (after `--`);
  `--empty` is the required input placeholder; a "reported number of objects" warning
  is non-fatal.
- **Merge helper trap:** if a script wraps shell calls in a `run()` that prepends a
  prefix (e.g. `nlm`), a `pdfunite` call becomes `nlm pdfunite ...` and silently does
  nothing — the merged file never appears and `pdfinfo` reports empty. Call `pdfunite`
  via a raw `subprocess.run(["pdfunite", ...])`.
