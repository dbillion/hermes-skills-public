---
name: anime-slidedeck
description: >-
  Generate rich, anime/cartoon-genre styled slide decks (Ghibli / Naruto / Superbook
  visual worlds) that teach technical concepts with colorful characters, beautiful
  scenery, and a friendly, mindful, happy tone — making information easy to consume and
  recall in an entertaining format. This is STATIC slide-deck art direction (NotebookLM
  PDF/PPTX), NOT animation/motion video. Use for DSA, CS, or any technical topic where the
  user wants an engaging cartoon visual style instead of a flat corporate deck. Drives
  NotebookLM (`nlm` CLI) slide generation with theme-specific --focus prompts and enriches
  via `nlm research` deep-search. Trigger on "anime slides", "Ghibli deck", "Naruto styled",
  "Superbook theme", "cartoon style", "kids anime", "rich characters", or any request to
  explain technical content in a friendly, entertaining, recal-friendly visual format.
---

# Anime / Cartoon-Genre Slide Deck Skill

Produce **slide decks with anime/cartoon visual art direction** — Ghibli / Naruto / Superbook
worlds — that explain technical concepts (DSA, algorithms, systems, anything) using rich,
colorful characters and beautiful scenery so the material is easy to consume and remember.

**Key clarification:** "anime" here means the *cartoon genre's visual style* applied to a
**static slide deck**. It is NOT motion/animation. We are not generating video. The deck is a
PDF/PPTX from NotebookLM whose art direction mimics a cartoon world: hand-painted palettes,
expressive characters, storybook framing. The goal is **recall through entertainment** — people
remember a friendly Ghibli spirit explaining Big-O far better than a bullet list.

## What makes it work
- **Cartoon characters as guides** — a recurring mascot (a little village ninja, a forest
  spirit, a glowing storybook elf) walks the learner through each concept.
- **Scene-as-metaphor** — each algorithm gets a tiny storybook scene (a tidy toolbox = hash
  table; a winding forest path = tree traversal) so the visual IS the mnemonic.
- **Warm, mindful tone** — calm, encouraging narration voice; no stress, no intimidation.
- **Color as memory aid** — consistent palette per theme so sections feel like chapters.

## Hard guardrails (never violate)
- **NO gore, NO blood, NO horror, NO graphic violence, NO unsettling or scary imagery.**
  Dark CS concepts (worst-case, cache miss, failure) are shown as mild cute metaphors
  (a sleepy cloud, a puzzled mascot) — never as harm.
- **Friendly, happy, mindful tone.** Encouraging, calm, never condescending.
- **Beautiful, not cluttered.** One clear idea per slide; characters polished, not creepy
  or over-sexualized.
- Technical accuracy first — the cartoon skin is decorative; facts come from the sources.

## Workflow

### 1. Notebook + enriched sources
```bash
nlm notebook create "DSA Anime Deck - <theme>"
NB=$(nlm notebook list --json | jq -r '.[0].id')

# local markdown sources
nlm source add "$NB" --file "/path/to/topic.md" --title "Topic Notes" --wait
# NOTE: .py files are REJECTED by NotebookLM — add as --text, not --file

# ENRICH with credible external sources (preferred over agent-authored prose)
nlm research start "how do <topic> work, beginner friendly, with visualizations" \
  --mode deep --notebook-id "$NB" --auto-import
# if --auto-import stalls: nlm research status "$NB"  →  nlm research import "$NB" <task-id>
# verify: nlm source list "$NB" --json | jq 'length'
```

### 2. Pick a theme → generate the deck
Choose one theme (or ask the user). Use the matching `--focus` prompt from
`references/anime-themes.md`. Example:
```bash
nlm slides create "$NB" --format detailed_deck --length default --confirm \
  --focus "$(cat references/themes/<theme>.focus.txt)"
nlm studio status "$NB" --json                       # get artifact id
nlm download slide-deck "$NB" --id <id> --output deck.pdf
```
NotebookLM sometimes renders flat/corporate. If so: strengthen the focus prompt, name
specific shows/artists, and/or attach a reference image via `nlm source add --image`. Iterate.

### 3. Verify
- Downloaded and non-empty: `ls -la deck.pdf`.
- Confirm no gore/violence slipped in; theme palette applied.
- If vision unavailable, state you could not visually verify; rely on prompt + size.

## Theme quick-reference
| Theme    | Vibe                                            | Palette                                 |
|----------|-------------------------------------------------|-----------------------------------------|
| ghibli   | Soft pastoral, hand-painted, gentle winds       | sage green, cream, sky blue, warm brown |
| naruto   | Energetic shōnen, headbands, leafy village      | orange, blue, green, parchment          |
| superbook| Retro 80s storybook, glowing book, cozy fantasy | amber, teal, violet, warm gold          |

Full prompt templates in `references/anime-themes.md`.

## Pitfalls
- NotebookLM **rejects `.py` uploads** → use `--text`.
- Slide decks are the SLOWEST artifact (~5–10 min); poll `nlm studio status`.
- `--auto-import` can return early; verify source count.
- Anime styling is NOT guaranteed by NotebookLM — iterate the focus; attach a reference image.
- **THIS IS A STATIC DECK, NOT A VIDEO. DO NOT USE HYPERFRAMES/ANIME.JS MOTION.** The user
  explicitly rejected a HyperFrames/anime.js video build: "slidedeck skills dont have
  animation features, anime here means cartoon genre that have rich visuals themes." If you
  start scaffolding `hyperframes init` / rendering MP4 for an "anime deck" request, STOP — that
  is the wrong deliverable. The anime look comes purely from the `--focus` prompt (theme,
  palette, mascot, metaphors). Only build a HyperFrames video if the user SEPARATELY and
  explicitly asks for motion/animation.
- **Enrich first (same as nlm-productivity Rule #2):** run `nlm research start ... --mode deep
  --auto-import` and verify `nlm source list | jq length` BEFORE `nlm slides create`. Generating
  then regenerating after research wastes the per-profile slide cap.
- **Collaboration for quota:** to let other profiles generate their own themed deck (Naruto/
  Superbook) from the shared sources, invite them as EDITORS: `nlm share invite <nb> <email>
  --role editor` (default role is viewer = cannot generate). Note: these profiles share one
  backend quota pool, so editor invites help run parallel *different* decks after the window
  resets, not bypass an active rate limit. For an active "wait a few minutes" limit, a 300s
  cooldown may still fail — retry ~25 min later (background retry script works well).
- Profile rotation: ~3 slide-decks/day per `nlm` profile; `nlm login switch <profile>` to
  bypass for bulk generation.
