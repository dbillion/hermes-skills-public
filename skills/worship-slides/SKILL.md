---
name: worship-slides
description: Design and generate high-fidelity church worship slide decks. Use when you need beautiful backgrounds, high-contrast typography, and projected lyrics.
---

# Worship Slide Designer

This skill specializes in creating visually stunning, projection-ready slide decks for church worship.

## Core Workflow

1.  **Content Analysis**: Extract lyrics and themes from source files (PDFs, Markdown, Web).
2.  **Slide Splitting**: Break lyrics into logical 4-6 line chunks for optimal projection.
3.  **Visual Selection**: Apply a consistent "Visual Mode" based on the song's tone:
    -   *Grateful/Hymn*: Dark textures, classic serifs, gold highlights.
    -   *Modern/Dynamic*: Gradients, bold sans-serifs, clean nature shots.
4.  **Generation**: Use `nlm slides create` with the `--template worship` or `--theme dark` flags.

## Visual Templates
- **Standard**: See [references/design_principles.md](references/design_principles.md).
- **Backgrounds**: Use high-resolution nature or architectural placeholders.

## Prompting for Generation
When calling the slide generator, always specify:
- "High-contrast white text on dark nature backgrounds"
- "Centered vertical and horizontal alignment"
- "Logical stanza-based slide breaks"
