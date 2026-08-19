# Deck code-drop fix — diagnosis + recipe

## Diagnosis (verified, real session)
- **Symptom:** generated `detailed_deck` quiz slides had no Java method / JUnit test code, even though
  the prompt demanded "include the exact code verbatim."
- **Proof the deck was rasterized:** `pdftotext -f 1 -l 13 deck.pdf - | wc -c` -> 0; repeated for all
  4 page ranges (1-13, 14-26, 27-39, 40-53) -> all 0 selectable chars. A 53-page deck had ZERO text.
  => NotebookLM synthesized/restyled the layout; prose-requested code was dropped, not copied.
- **Sources were fine:** all 55 `sources/qNN.md` contained the method + test in ```java fences. So the
  loss was in generation output, not input.

## Why it happens
NotebookLM `detailed_deck` returns image-based slides. It paraphrases/restyles *text* but embeds
*image sources as-is*. Asking for code in prose invites the model to redraw it (and drop it).

## The fix (works)
1. Pre-render each question's EXACT method + test as a code-card PNG (monospace font, light bg).
2. Add PNGs as image sources to the notebook (per question).
3. FOCUS prompt: embed the method+test images verbatim, explicitly forbidding redraw/paraphrase.
4. Pass question source id + both code-card source ids to `slides create --source-ids`.

## Backfill gotcha
18 of 55 question `.md` files had only a JUnit test + a `*source: Algorithms.java*` placeholder — no
method code. Recovered the real methods by brace-matching-slicing them from the actual
`Algorithms.java`, then re-ran the card generator. Always check source completeness BEFORE rendering.

## Verification after regen
- `pdftotext` will still report 0 (rasterized is expected) — that's fine.
- The code now only survives via the embedded image cards. Spot-check 2-3 content slides visually.
- Confirm `pdfinfo merged.pdf | grep Pages` matches expected question count (else merge silently failed).

## Fonts used
JetBrains Mono ExtraBold at /usr/share/fonts/TTF/JetBrainsMono-ExtraBold.ttf (system has it). PIL 12.x.
