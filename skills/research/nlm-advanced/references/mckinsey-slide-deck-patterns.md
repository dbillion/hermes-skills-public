# McKinsey-Style Slide Deck Generation Reference

## Session Summary
Generated executive-level McKinsey-style slide decks from DSA interview prep sources using NLM CLI with custom `--focus` prompts.

## Focus Prompt Patterns That Worked

### Pattern 1: McKinsey Visual Wonder (Dark Luxury)
```bash
nlm slides create <notebook-id> --format detailed_deck --length default --confirm \
  --focus "Act as a McKinsey Senior Designer and senior software architecture teacher. CREATE A VISUAL WONDER: target a comprehensive 18-page deck for job-hunting and interview prep using the uploaded DSA sources, especially dsa-ultimate.md. Content requirements: explain when to use 20 core algorithms and data structures; include and organize 40 DSA interview questions; explain how SOLID principles influenced classic OOP design patterns (with humorous analogies); practical insights on when and why to use algorithms and patterns. VISUAL STYLE: Dark luxury aesthetic — obsidian/charcoal backgrounds (#0a0a0a, #1a1a2e), burnished gold/bronze accents (#c5a04a, #b8860b), deep emerald highlights (#1a5c4a). Typography: Playfair Display for headlines, Inter for body. High contrast, cinematic lighting effects, generous whitespace. One key message per slide. Max 3-4 bullets, 10 words each. No clipart. Premium executive presentation quality."
```
**Output**: 21MB PDF, 18 slides, dark luxury aesthetic

### Pattern 2: Academic/Clean Style
```bash
nlm slides create <notebook-id> --format detailed_deck --length default --confirm \
  --focus "Act as a McKinsey Senior Designer and senior software architecture teacher. CREATE A VISUAL WONDER: target a comprehensive 18-page deck for job-hunting and interview prep using the uploaded DSA sources, especially dsa-ultimate.md. Content requirements: explain when to use 20 core algorithms and data structures; include and organize 40 DSA interview questions; explain how SOLID principles influenced classic OOP design patterns (with humorous analogies); practical insights on when and why to use algorithms and patterns."
```
**Output**: 16MB PDF, 18 slides, clean academic style

## Key Design Principles for Executive Decks

1. **Role framing**: "Act as McKinsey Senior Designer" sets quality bar
2. **Visual specification**: Explicit hex codes, font names, contrast requirements
3. **Content density limits**: "Max 3-4 bullets, 10 words each" prevents clutter
4. **Slide count target**: "18-page deck" sets scope expectation
5. **One message per slide**: Forces clarity
6. **Negative constraints**: "No clipart" prevents low-quality elements

## Cross-Reference
- Full workflow with exact commands and timing: `nlm-productivity/references/dsa-slide-deck-generation.md`
- Sacred aesthetic variant also documented in nlm-advanced SKILL.md (Dark Luxury / Sacred Aesthetic template)

## Artifact Sizes
- Academic style: ~16MB
- Dark luxury style: ~21MB
- Both generated sequentially without rate limits