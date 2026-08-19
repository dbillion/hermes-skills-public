# DSA Slide Deck Generation Session Reference

## Session Summary
Generated two slide decks from user's DSA interview prep files using NLM CLI:
- Source files: `/home/deeone/Desktop/jobhunting/dsa/dsa-ultimate.md` and `DSA_Interview_Questions_40.md`
- Notebook: "DSA SOLID Patterns Slide Deck"
- Two slide decks generated with different `--focus` prompts

## Exact Workflow Executed

```bash
# 1. Create notebook
nlm notebook create "DSA SOLID Patterns Slide Deck"
NB_ID=$(nlm notebook list --json | jq -r '.[0].id')

# 2. Add source files (markdown)
nlm source add "$NB_ID" --file "/home/deeone/Desktop/jobhunting/dsa/dsa-ultimate.md" --title "DSA Ultimate" --wait
nlm source add "$NB_ID" --file "/home/deeone/Desktop/jobhunting/dsa/DSA_Interview_Questions_40.md" --title "DSA 40 Questions" --wait

# 3. Generate Slide Deck 1 - Academic Style
nlm slides create "$NB_ID" --format detailed_deck --length default --confirm \
  --focus "Act as a McKinsey Senior Designer and senior software architecture teacher. CREATE A VISUAL WONDER: target a comprehensive 18-page deck for job-hunting and interview prep using the uploaded DSA sources, especially dsa-ultimate.md. Content requirements: explain when to use 20 core algorithms and data structures; include and organize 40 DSA interview questions; explain how SOLID principles influenced classic OOP design patterns (with humorous analogies); practical insights on when and why to use algorithms and patterns."

# 4. Generate Slide Deck 2 - McKinsey Visual Wonder (Dark Luxury)
nlm slides create "$NB_ID" --format detailed_deck --length default --confirm \
  --focus "Act as a McKinsey Senior Designer and senior software architecture teacher. CREATE A VISUAL WONDER: target a comprehensive 18-page deck for job-hunting and interview prep using the uploaded DSA sources, especially dsa-ultimate.md. Content requirements: explain when to use 20 core algorithms and data structures; include and organize 40 DSA interview questions; explain how SOLID principles influenced classic OOP design patterns (with humorous analogies); practical insights on when and why to use algorithms and patterns. VISUAL STYLE: Dark luxury aesthetic — obsidian/charcoal backgrounds (#0a0a0a, #1a1a2e), burnished gold/bronze accents (#c5a04a, #b8860b), deep emerald highlights (#1a5c4a). Typography: Playfair Display for headlines, Inter for body. High contrast, cinematic lighting effects, generous whitespace. One key message per slide. Max 3-4 bullets, 10 words each. No clipart. Premium executive presentation quality."

# 5. Check status and download
nlm studio status "$NB_ID" --json
nlm download slide-deck "$NB_ID" --id <artifact-id-1> --output slide1.pdf
nlm download slide-deck "$NB_ID" --id <artifact-id-2> --output slide2.pdf
```

## Generated Artifacts
- `slide1.pdf` - 16.4MB (Academic/Clean style)
- `slide2.pdf` - 21.0MB (McKinsey Dark Luxury style)

## Key Learnings

### Focus Prompt Engineering for Slides
- `--focus` parameter accepts detailed design instructions
- Visual style specifications (colors, fonts, contrast) work well
- Content density constraints ("max 3-4 bullets, 10 words each") are respected
- Role framing ("Act as McKinsey Senior Designer") produces executive-quality output

### File Delivery on Telegram
- MEDIA: protocol works for files up to ~20MB
- 21MB PDF delivery may be intermittent
- Consider splitting large artifacts or compressing if delivery fails
- Alternative: upload to file sharing service (0x0.st, transfer.sh) as fallback

### Rate Limit Considerations
- Two sequential slide deck generations completed without rate limits
- Video/audio generation would require 5-min spacing
- Profile rotation across 10+ NLM profiles available for heavy workloads

### Source File Handling
- Local markdown files upload and process quickly with `--wait`
- NLM extracts structure from markdown headings effectively
- No need for repomix preprocessing for documentation/markdown sources

## Deep Research / Source Discovery (CRITICAL — do NOT skip)

NotebookLM can discover and ingest **credible external web sources** itself via the
`research` command. This is the preferred way to enrich a notebook with authoritative
material instead of authoring content from the agent's own training data. The user
explicitly relies on this for credible sourcing.

```bash
# Start a deep web search (~40 sources, ~5 min) and auto-import into a notebook
nlm research start "<detailed query>" --mode deep --notebook-id "$NB_ID" --auto-import

# Or start, then poll + explicitly import (use if --auto-import didn't finish):
nlm research start "<query>" --mode deep --notebook-id "$NB_ID"
nlm research status "$NB_ID"            # wait until Status: completed
nlm research import "$NB_ID" <task-id>  # add discovered sources to notebook
```

**Flags:**
- `--mode fast` (~30s, ~10 sources) or `--mode deep` (~5min, ~40 sources, web only)
- `--source web` (default) or `--source drive`
- `--title <t>` to create a NEW notebook instead of `--notebook-id`
- `--auto-import` waits for completion and imports automatically
- `--force` starts even if a task is already pending

**Workflow:** always run `research` BEFORE generating artifacts when the topic needs
external credibility (hardware, compilation, complexity theory, etc.). Imported sources
then feed slides/video/audio/report generation. A single deep search can add 40-64
sources (notebook grew from 15 → 141 sources in one run).

**Gotcha:** `--auto-import` sometimes returns before all sources land; run
`nlm research import "$NB_ID" <task-id>` explicitly to be safe, then verify with
`nlm source list "$NB_ID" --json | jq 'length'`.