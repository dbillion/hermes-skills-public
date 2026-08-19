---
name: seminary-writer
description: Write seminary-level theological papers that pass AI detection. Combines NLM source extraction, APA 7 citation formatting, humanization rules (banned AI words, simple language, conversational tone), and the 80/20 writing rule. Use for all seminary assignments, research papers, and theological writing.
---

# Seminary Writer Skill

**Supersedes: `theological-research`** — This is the authoritative skill for all seminary writing. It combines everything from `theological-research` plus NLM source extraction, humanization/anti-AI-detection, banned-word lists, and simple-language rules.

Write theological papers that sound like a real student wrote them — not a machine.

## Core Principles

1. **80/20 Rule**: 80% student's own words, 20% expert quotes max
2. **Simple language**: Short sentences, everyday words, no jargon
3. **Human voice**: Conversational, first-person, stories, questions
4. **APA 7 citations**: Strict format, every claim sourced
5. **5+ sources minimum**: 3+ printed books/journals, no Wikipedia/blogs
6. **Zero AI tells**: No banned words, no em dash abuse, no uniform paragraphs

## Workflow

### Phase 1: Source Extraction (from NotebookLM)

Extract book and source metadata from NLM notebooks:

```bash
# List all notebooks
nlm notebook list --json | jq -r '.[] | "\(.id) | \(.title)"'

# Get source list for a notebook
nlm source list <notebook-id> --json

# Query specific content
nlm notebook query <notebook-id> "List all books with author, year, publisher"

# Download report with all sources
nlm report create <notebook-id> --format "Briefing Doc" --confirm
nlm download report <notebook-id> --id <artifact-id> --output sources.md
```

See `references/nlm-extraction.md` for detailed extraction patterns.

### Phase 2: Research & Thesis

1. Read the assignment prompt carefully
2. Identify the core theological question
3. Form a clear thesis statement (1-2 sentences)
4. Extract relevant quotes and ideas from NLM sources
5. Note APA citation details for each source (author, year, title, publisher, pages)

### Phase 3: Outline

Structure the paper:
- **Introduction** (10% of word count): Hook + thesis + roadmap
- **Body** (80%): 3-5 sections with clear headings
  - Each section: claim → evidence (quotes) → analysis (own words) → application
- **Conclusion** (10%): Summary + personal reflection + contemporary relevance

See `references/paper-structure.md` for templates.

### Phase 4: Drafting

Write following these rules:

**MUST DO:**
- Use "I" when appropriate — personal voice is expected
- Ask rhetorical questions: "Why does this matter?"
- Vary sentence length — mix short punchy ones with longer flowing ones
- Use contractions: "don't", "can't", "it's"
- Include personal stories, ministry examples, prayer moments
- Use simple words: "use" not "utilize", "help" not "facilitate"
- Short paragraphs (2-6 sentences), vary the length
- Clear descriptive headings: "The Big Shift" not "Historical Context"

**MUST NOT DO:**
- See `references/banned-words.md` for full banned AI word list
- Use em dashes (—) — use commas or restructure
- Start sentences with "Furthermore", "Additionally", "Moreover"
- Use "delve", "crucial", "pivotal", "leverage", "synergize"
- Write uniform paragraphs (all same length)
- Use passive voice when active works better
- Include throat-clearing openers: "In this section, we will discuss..."

### Phase 5: Citation Check

Every source must follow APA 7 format:

**In-text:**
- `(Author, Year)` — general reference
- `(Smith, 2023, p. 45)` — specific page
- `(Smith, 2023, pp. 45-47)` — page range

**Bibliography:**
```
Author, A. A. (Year). Title of book. Publisher.
Author, A. A. (Year). Title of article. Title of Journal, Volume(Issue), pages. DOI
```

See `references/apa7-guide.md` for complete format rules.

### Phase 6: Humanization Pass

After drafting, run the humanization checklist:

1. Read every sentence aloud — does it sound like a person talking?
2. Check for banned AI words (see `references/banned-words.md`)
3. Verify paragraph length variation (no two paragraphs same length)
4. Confirm first-person voice where appropriate
5. Add at least 2-3 personal reflections or ministry examples
6. Check that no paragraph starts with "In this section" or similar filler
7. Replace any remaining fancy words with simple alternatives
8. Add natural transitions instead of formulaic ones

## Source Requirements

- **Minimum 5 sources** (excluding Bible and lecture notes)
- **At least 3 must be printed** (books or journal articles)
- **Preferred**: Seminary journals, Google Scholar, academic publishers
- **Avoid**: Wikipedia, personal blogs, non-academic websites
- **Bible**: Cite book, chapter, verse (not in reference list)

## Quality Checklist

Before submitting, verify:

- [ ] Clear thesis statement in introduction
- [ ] 5+ sources, 3+ printed
- [ ] Every claim has a citation
- [ ] APA 7 format throughout
- [ ] 80% own words, 20% quotes max
- [ ] No banned AI words
- [ ] Conversational, personal tone
- [ ] Varied sentence and paragraph length
- [ ] Personal stories/reflections included
- [ ] Contemporary application to modern church
- [ ] Clear descriptive headings
- [ ] Proper bibliography
- [ ] Read aloud — sounds human

## Checking Writing Progress (Notion Tracker)

**IMPORTANT**: If Notion MCP returns empty output (exit 0 with no stdout/stderr), times out, or returns a 404 error (especially "object_not_found" for databases), **immediately fall back** to the reliable `references/assignment-checker.py` script or the direct curl method in `references/notion-tracker.md`. Do **not** retry MCP multiple times - this wastes time in cron contexts.

**MCP Response Parsing Note**: When using `mcp-cli call notion <tool> '<json_args>'`, the response is wrapped in MCP format and requires double parsing:
1. Parse the outer JSON to get the `content` array
2. Access `content[0].text` which contains the actual JSON string from Notion
3. Parse that inner JSON string to get the actual data
See `references/notion-tracker.md` for detailed parsing examples.

**Critical Note on Database Access**: If you receive a 404 "object_not_found" error when querying a database, verify that:
1. The database ID is correct
2. The database is shared with your Notion integration (go to the database in Notion and ensure your integration has access)

When the user asks to check seminary writing progress (e.g., "check my assignments", "what's due", "seminary writing check"):

**RECOMMENDED APPROACH**: Use the `references/assignment-checker.py` script which handles MCP fallback automatically:
```bash
python3 references/assignment-checker.py
```

This script implements the patterns learned from real-world usage:
1. Tries MCP first for each operation (search, retrieve page, query database) with retry mechanism (up to 2 attempts)
2. Immediately falls back to direct curl on MCP failure (silent output, timeout, or error) with retry mechanism (up to 2 attempts)
3. Uses `Notion-Version: 2022-06-28` for all requests (critical for authentication)
4. Extracts NOTION_TOKEN from `~/.mcp_servers.json` using grep/sed (cron-safe)
5. Extracts data by property type rather than hardcoded names (handles varying database schemas)
6. Filters out past-due and completed assignments
7. Deduplicates results by (title, due_date)
8. Outputs in the expected format

**MANUAL APPROACH PATTERNS** (if implementing manually):
1. Search Notion for the terms: `"assignment"`, `"paper"`, `"essay"`, `"exegesis"` (returns pages and databases)
2. For each result:
   a. If page: retrieve properties via `/v1/pages/{id}`
   b. If database: query via `/v1/databases/{id}/query` (use `page_size` to limit)
3. For each page (from pages or database rows):
   a. Extract title from property of type `title`
   b. Extract due date from property of type `date` (use `start` date, split at "T")
   c. Extract status from property of type `select` or `status` (default "Not Started")
   d. Consider active if due date >= today and status not in {"Done", "Completed", "Finished", "Closed"}
   e. Consider upcoming if due date <= today + 7 days and active
4. Deduplicate by (title, due_date)
5. Report: Active assignments, Upcoming deadlines (next 7 days), Recently completed, Suggested action

**KEY PATTERNS LEARNED**:
- **MCP Response Parsing**: MCP responses require double parsing:
  1. Parse outer JSON to get `content` array
  2. Access `content[0].text` (contains actual Notion API JSON string)
  3. Parse that inner JSON string for actual data
  (See `references/notion-tracker.md` for examples)
- **Cron Constraints**: `execute_code` and `python3 -c` are blocked in cron - use subprocess calls to mcp-cli/curl and write JSON to files for parsing
- **Immediate Fallback**: If MCP returns empty output (exit 0 with no stdout/stderr), immediately fall back to curl - do not retry MCP multiple times
- **API Version**: Always use `Notion-Version: 2022-06-28` for direct curl (2025-09-03 causes 401 errors)
- **Property Flexibility**: Property names vary widely (e.g., "Assignment Name", "Due Date", "Status") - always extract by type, not name
- **Historical Data**: Many databases contain past semesters' entries - always check dates against today before flagging as upcoming
- **Deduplication**: Same assignment may appear as both a page and in a database - deduplicate by (title, due_date)

**Patterns**: For detailed patterns discovered during sessions for checking assignments, see `references/assignment-check-patterns.md`.

**Cron Mode**: The `assignment-checker.py` script is designed to work within cron constraints:
- Uses only subprocess calls to mcp-cli and curl
- Writes intermediate JSON to files for parsing when needed
- Avoids complex shell quoting and pipe-to-interpreter patterns
- Handles MCP silent failures gracefully with immediate fallback

## Course Assignment Workflow (KEV404, PRT396, etc.)

When working on seminary course assignments:

1. **Create NLM notebook** for the course: `nlm notebook create "Course Name"`
2. **Ingest ALL course materials** — PDFs, slides, articles, assignment sheets:
   - `nlm source add <nb_id> --file <pdf_path> --wait` for PDFs
   - `nlm source add <nb_id> --text "<passage>" --title "Reference"` for Bible passages
3. **Query NLM** for assignment requirements: `nlm notebook query <nb_id> "From the assignment PDF, extract the complete requirements: word count, formatting, what to include, reflection questions"`
4. **Query NLM** for proper APA citations: `nlm notebook query <nb_id> "For each source, provide full bibliographic citation in APA 7 format"`
5. **Write paper** following the seminary-writer skill
6. **Use NLM** to extract lesson-specific content (e.g., five-step prayer model, Prayer of Exchange steps) for accurate in-text citations

**PITFALL**: Do NOT install youtube-transcript-api or pdftotext for NLM work. NLM handles PDF and YouTube natively via --file and --youtube flags.

**Formatting note**: The user wants proper APA 7 in-text citations throughout — (Author, Year) for paraphrases, (Author, Year, p. XX) for direct quotes — and a full reference list at the end. This is non-negotiable for seminary papers.

## Reference Files

- `references/apa7-guide.md` — Complete APA 7 citation rules
- `references/banned-words.md` — Full banned AI word and phrase list
- `references/nlm-extraction.md` — How to extract sources from NotebookLM
- `references/paper-structure.md` — Paper templates and structure guide
- `references/humanization-checklist.md` — Detailed anti-AI-detection rules
- `references/notion-tracker.md` — Notion MCP integration for assignment tracking
- `references/assignment-check-patterns.md` — Patterns for checking seminary assignments in Notion
- `references/assignment-check-patterns.md` — Patterns for checking seminary assignments in Notion

## Templates

- `templates/exegetical-paper.md` — Exegetical paper template
- `templates/systematic-theology.md` — Systematic theology template
- `templates/ministry-paper.md` — Ministry/practical theology template
- `templates/weekly-bible-study-report.md` — PRT396 weekly Bible study report template
