---
name: investor-pitch-deck
description: Build black-and-gold PowerPoint pitch decks.
category: creative
tags: [powerpoint, pitch-deck, investors, black-gold, python-pptx]
related_skills: [powerpoint, humanizer]
---

# Investor Pitch Deck Skill

Produce professional PowerPoint (.pptx) pitch decks with a premium black-and-gold theme for investors, using `python-pptx` directly (not NotebookLM slides). The theme is hard-coded from the color palette below; callers supply slide-specific content, not hex codes.

## Color Palette

| Variable     | Hex       | Use                        |
|--------------|-----------|----------------------------|
| BLACK        | `#0A0A0A` | Slide background           |
| GOLD         | `#D4AF37` | Titles, accents, chart bars|
| GOLD_LIGHT   | `#F0DC68` | Subtitles, highlights      |
| WHITE        | `#FFFFFF` | Body text                  |

RGB equivalents: GOLD = (212, 175, 55), GOLD_LIGHT = (240, 220, 100).

## Workflow

### 1. Prepare content
Gather the analysis data (startup counts, funding figures, sector breakdowns, founder demographics). The deck structure follows a standard investor narrative:

1. **Cover** — title, subtitle, stats line, gold border
2. **Executive Summary** — key metrics as bullets
3. **Data-driven story** — charts, tables, timelines (1–3 slides)
4. **Market/traction** — sector evolution, international footprint
5. **Investment thesis** — why now, why this, why you
6. **Ask/use-of-funds** — clear ask with numbers
7. **Closing** — thank you, contact

### 2. Generate with the helper script
Use `scripts/build_deck.py` with a JSON spec that defines slides. The script:
- Sets a 16:9 canvas (13.33" × 7.5")
- Applies solid black background to every slide
- Draws a gold border rectangle on title/cover slides
- Styles all titles in gold, subtitles in gold-light, body text in white
- Renders bar charts using gold rectangles with white value labels
- Renders tables with gold headers and black data-row backgrounds

```bash
python scripts/build_deck.py deck_spec.json output.pptx
```

### 3. Verify
Run `pptx_read.py output.pptx --outline` (from the `powerpoint` skill) to confirm slide count and content. For visual verification, use `pptx_render.py` to export PNGs and review with `vision_analyze`.

## JSON Spec Format

```json
{
  "title": "Tehnopol Startup Ecosystem",
  "subtitle": "2021–2025 Strategic Insights",
  "slides": [
    {
      "layout": "cover",
      "title": "Tehnopol Startup Ecosystem",
      "subtitle": "Trend Analysis & Strategic Insights",
      "stats": ["129 startups", "€12.8M raised", "30% defense focus"],
      "notes": "Cover slide"
    },
    {
      "layout": "bullets",
      "title": "Executive Summary",
      "bullets": [
        "129 startups across 8 programs",
        "€12.8M total funding raised in 2025",
        "30% defense-focused portfolio"
      ],
      "notes": "Summary"
    },
    {
      "layout": "table",
      "title": "Funding Landscape Evolution",
      "headers": ["Program", "2021–2023", "2024–2025", "Trend"],
      "rows": [
        ["NATO DIANA", "€100K", "€100K→€150K", "+50% projected"],
        ["Cyber", "N/A", "€60K", "New"]
      ],
      "notes": "Table slide"
    },
    {
      "layout": "bar_chart",
      "title": "Sector Evolution",
      "data": {"Defense": 30, "Cyber": 25, "HealthTech": 20, "GreenTech": 15, "AI": 10},
      "notes": "Chart slide"
    }
  ]
}
```

### Layout types

| Layout      | Description                                           |
|-------------|-------------------------------------------------------|
| `cover`     | Title, subtitle, stats line, gold border, corner arcs |
| `bullets`   | Title + bullet list, optional gold accent line        |
| `table`     | Title + data table (gold headers, black rows)         |
| `bar_chart` | Title + horizontal bar chart (gold bars, white vals)  |
| `closing`   | Centered title + subtitle + contact footer          |

## Pitfalls

- **Do NOT use the generic `powerpoint` skill's JSON spec** for premium-themed decks. It lacks per-layout theme defaults and forces manual hex specification on every element. This skill's `build_deck.py` bakes in the black-gold palette.
- **Cover slide corner accents**: render as small gold arc rectangles (`MSO_AUTO_SHAPE_TYPE.RECTANGLE`) at each corner since `add_connector` with `LINE` type is not available in this python-pptx version.
- **Cell API change**: use `cell.text_frame.paragraphs[0]` not `cell.paragraphs[0]` — the `_Cell` object exposes text via `.text_frame` in current python-pptx.
- **Blank layout index**: `prs.slide_layouts[6]` is the blank layout; pass it explicitly to `add_slide()` or the call fails.
- **Table background fill**: call `cell.fill.solid()` before setting `fore_color.rgb` on `_Cell` objects — the fill is not active by default.

## References

- `references/deck-spec-template.json` — a full 12-slide spec template pre-filled with the Tehnopol investor deck structure.