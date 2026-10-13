---
name: storytelling-for-technical-content
description: "Transform technical content into story-driven posts."
---

# Storytelling for Technical Content

Transform dry technical content into emotionally resonant, lead-generating articles using proven narrative frameworks.

## Core Principles

### 1. Sensory Grounding (PAST Framework)
Every article must ground the reader in a specific physical moment:
- **Place**: Exact location (not "an office" — "my kitchen table in Kalamaja, Tallinn")
- **Action**: Physical movement with active verbs ("dragged my sore self to the bathroom")
- **Speech**: Exact dialogue, not summaries ("Hurry up, we can't wait!")
- **Thoughts**: Raw, unfiltered internal monologue ("So many beautiful things to do and so little time")

### 2. Unpredictable Rhythm
Avoid linear "and then" storytelling. Use interruptions and non-linear flow:
- Start with a scene
- Get interrupted by another event
- Continue to another event
- Get interrupted again
- Land on the concept being taught

### 3. Emotional Resonance
Connect technical concepts to universal human experiences:
- Relationships (breakups, falling in love, sharing)
- Physical sensations (heat, cold, pain, relief)
- Life transitions (new job, moving, loss)

**Important**: Keep it professional. No inappropriate content. The emotion serves the concept, not vice versa.

### 4. Concept Connection
The hook must tie directly to what you're teaching:
- Ch03 (Ownership): "He gave her everything" → ownership moves, you can't have two owners
- Ch07 (Iterators): "Watching trees blur past" → iterators move through collections one item at a time

### 5. Location Authenticity
- Use the user's actual location (ask if unknown)
- Vary locations across articles (coffee shop, park, train, kitchen, rooftop, etc.)
- Include local details (Tallinn, Baltic Sea, Kalamaja, Telliskivi, etc.)

## Publishing to LinkedIn via Composio

### Image Preparation
```bash
pdftoppm -png -r 150 -f 1 -l 1 input.pdf output_prefix
```

### Posting with Images
**CRITICAL**: Use `images` array in payload. Do NOT use `--file` flag when `images` is set.

```bash
composio execute "LINKEDIN_CREATE_LINKED_IN_POST" -d @/tmp/payload.json
```

### Deleting Posts
```bash
composio execute "LINKEDIN_DELETE_LINKED_IN_POST" -d '{"share_id": "urn:li:share:XXXX"}'
```

## Pitfalls

1. **Generic openings**: "I'm sitting in my office" — too vague. Use specific sensory details.
2. **Same location**: Don't use "my office" for every article. Vary locations.
3. **Linear storytelling**: "And then... and then..." — use interruptions.
4. **No emotion**: Technical content without human connection is forgettable.
5. **Posting without permission**: Never publish without explicit user approval.
6. **Using --file with images array**: Causes validation error.

## Frameworks Reference

### CAT Structure (Talking Head)
- **Context**: Set the scene (1-2 lines max)
- **Adversity**: What went wrong, obstacles, pressure
- **Takeaway**: Single lesson learned

### CARD Structure (with Resolution)
Add **Resolution** when action was unexpected, outcome inspiring, or story incomplete.

### The Dance (Short-Form)
Constant oscillation between Context and Conflict until Payoff.

### 4 S's of Viral Content
- **Surprise**: Break expectations in first 6 seconds
- **Stakes**: Show what's on the line
- **Show, Don't Tell**: Visuals do heavy lifting
- **Simplicity**: 4th-5th grade reading level
