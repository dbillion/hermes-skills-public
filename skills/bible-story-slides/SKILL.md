---
name: bible-story-slides
description: Generates black-and-white slide decks (.pptx) that retell Bible stories for children ages 6-9, formatted so they can be used as NotebookLM source material or presented directly. Use this skill whenever the user asks for a Bible story slideshow/deck/presentation for kids, a Sunday school lesson deck, a children's ministry slide set, or NotebookLM source slides about a Bible story. Also trigger on requests like "make a slide deck about [Bible story] for kids" or "black and white Bible story presentation."
compatibility: Requires python-pptx (pip install python-pptx --break-system-packages)
---

# Bible Story Slides (black & white, ages 6-9)

Builds a simple, high-contrast, black-and-white slide deck that tells one
Bible story in short, child-friendly beats. Designed for two uses:

1. **Direct presentation** to a 6-9 year old audience (large text, one idea
   per slide, simple black-line illustration placeholders that can double as
   coloring pages if printed).
2. **NotebookLM source material** — the deck's text is written in clean,
   self-contained sentences so it works well as a source document/notebook
   for NotebookLM to generate an Audio Overview, FAQ, or study guide from.

## Workflow

1. **Get the story.** Ask the user which Bible story (e.g. "David and
   Goliath", "Noah's Ark", "The Good Samaritan") and roughly how many slides
   they want (8-14 is typical for this age group). If they give a passage
   reference instead of a title, use the passage.
2. **Break the story into beats.** Write 8-14 short beats, one per slide:
   - Title slide (story name + a one-line "big idea")
   - 6-10 story beats in chronological order, each ONE simple sentence
     (aim for 8-12 words, present tense, concrete nouns/verbs — this is the
     age band's reading level)
   - A "What can we learn?" recap slide with 1-2 child-friendly takeaways
   - A closing/discussion-question slide (1-2 simple questions for a leader
     to ask the group)
   Keep language simple and concrete. Avoid violence/frightening detail —
   summarize hard moments gently and age-appropriately (e.g. "Goliath was a
   very big, scary soldier" rather than graphic combat detail).
3. **Do not reproduce scripture text verbatim at length.** Paraphrase the
   story in your own words rather than quoting long Bible passages; a short
   phrase (under ~10 words) is fine if it adds value, but the deck should be
   an original retelling, not a copy of a specific Bible translation.
4. **Generate the deck** by calling the script:
   ```bash
   python3 scripts/generate_deck.py --story-json /path/to/story.json --out /path/to/output.pptx
   ```
   Build `story.json` yourself first (see `references/story_schema.md` for
   the exact structure and a full worked example). The script handles all
   layout, fonts, and the black-and-white styling — you only supply content.
5. **Package for download.** Zip the finished `.pptx` (and, if useful, the
   `story.json` alongside it) and present it to the user with `present_files`.
   Don't just describe the deck — always produce the actual file.

## Design rules the script enforces (don't fight these)

- Pure black text/lines on a pure white background — no grayscale fills, no
  color, so it stays cheap to print and easy to adapt into coloring pages.
- One idea per slide, large type (44pt+ for body text) — this age group
  reads slowly, so slides must not be text-heavy.
- A simple black-outline illustration placeholder frame on every story-beat
  slide, labeled with a short scene description, so a human or another tool
  can drop in / hand-draw the actual artwork later.
- Consistent, plain sans-serif font throughout for readability.

## When the user wants illustrations actually drawn in

The script only places labeled placeholder frames (it does not generate
images). If the user wants real black-and-white line art in each frame,
say so explicitly and offer to generate simple SVG line illustrations per
slide as a follow-up step, or suggest they add their own images to the
placeholders in PowerPoint/Google Slides afterward.

## Reference files

- `references/story_schema.md` — the exact JSON structure `generate_deck.py`
  expects, plus a complete worked example ("David and Goliath").
