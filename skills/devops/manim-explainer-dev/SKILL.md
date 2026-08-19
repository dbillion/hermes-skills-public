---
name: manim-explainer-dev
version: 1.0.0
description: Manim explainer skill dev workflow and evidence upgrades.
---

# Manim Explainer Skill Development

## When to use
- Creating a new Manim explainer skill (DSA, math, science) or a style layer for one.
- Patching / upgrading an existing explainer skill (new conventions, color / numeric
  encoding grammar, QA checklists, shared style layer).
- Using research (NotebookLM) to evidence-base skill conventions instead of inventing them.

## Core workflow (run in this order)
1. **Isolate.** Prototype in a SEPARATE folder (e.g. `/home/deeone/<name>-v2/`).
   Never edit the existing generation / current renders in place — a bad patch to a
   shared `dsa_style.py` silently breaks 80+ scenes (this happened: Act 6 test_panel
   was dropped from 80 of 83 scenes despite the helper existing). Copy the improved
   helper in, import it locally, prove it there first.
2. **Syntax-check with the uv manim venv**, not the default analyzer (see
   references/manim_venv_and_render.md). The default Python raises false LSP
   "manim unresolved / X is not defined" because `manim` lives in the `uv tool manim`
   venv. The user explicitly flagged this — check with the uv venv python.
3. **Patch the SKILL.md** with the learned convention (shared style layer, color
   grammar, QA checklist, numeric/state encoding grammar).
4. **Verify a render on disk** (background + notify, then check the mp4 exists under
   `media/videos/<Scene>/480p15/`). Exit code 0 alone is not proof.
5. **Evidence-base with NotebookLM** (references/notebooklm_research.md) before
   finalizing encoding conventions — cite sources, don't invent color mappings.

## Patching conventions into an explainer skill
- Port a **"Shared style layer"** section: 10 creative rules (one idea/shot,
  motion = meaning, transform-not-fade, <=3 motions, every scene has an aha,
  works sound-off), a color grammar (active / result / error / solution), and an
  extended QA checklist.
- Add a **"Numerical & state encoding grammar"**: fill/empty state via color ramp,
  data movement via color-coded flow lines (in-transit / accepted / rejected),
  vector = Arrow length driven by a ValueTracker, matrix/DP = heatmap cell fill,
  all driven by `always_redraw + ValueTracker` so the number and its spatial
  encoding stay in lockstep (meaningful, never decorative).
- Demote generic cubes to a neutral "data tray" layer; give each structure its own
  housing shape (node-link tree, bucket-grid hash, cone-tree heap) so structures
  read as distinct — fixes the "every video is a row of cubes" monotony.

## Pitfalls (caught this session)
- **HTML `<img>` in generated Markdown MUST be raw, never `html.escape()`'d.**
  Escaping turns `<img src="...">` into `&lt;img&gt;`, which GitHub renders as
  visible text — the exact "mermaid column not rendering" bug. Escape only text
  content (alt, labels); emit tags raw.
- **LSP "manim unresolved" errors are false positives** under `uv tool manim`.
  Check with the uv venv python, not the default interpreter.
- **Never animate >3 independent motions at once**; stagger with `lag_ratio`.
  Transform (not FadeOut+FadeIn) to preserve object identity.
- **Don't run deep renders/research foreground** — they exceed the 60s cap. Use
  `terminal(background=true, notify_on_complete=true)` and poll.
- **Color encodes meaning** (state / movement / result), not decoration. 5-color max.
- **NotebookLM `research start --mode deep` is ~5 min**; always background it.

## References
- `references/notebooklm_research.md` — NotebookLM `nlm` CLI: discover + mine sources
  for skill upgrades.
- `references/manim_venv_and_render.md` — uv venv path, syntax-check, background
  render verification.
