# NLM Source Extraction Guide

How to extract book and source metadata from NotebookLM for APA citations.

## Step 1: Find Your Notebook

```bash
# List all notebooks
nlm notebook list --json | jq -r '.[] | "\(.id) | \(.title)"'

# Search for a specific notebook by title
nlm notebook list --json | jq -r '.[] | select(.title | test("keyword"; "i")) | .id'
```

## Step 2: Discover Sources (Auto Web Search)

NotebookLM can search the web and auto-add sources for you. This is the fastest way to build a research library.

### Via NotebookLM Web UI
1. Open your notebook in NotebookLM
2. Click **"Discover sources"** (or the search icon)
3. Type your research question or topic
4. NotebookLM searches the web and returns relevant academic sources
5. Select the sources you want — they're auto-added to your notebook

### Via CLI (Manual URL Addition)
If you find sources yourself, add them directly:
```bash
# Add a URL source
nlm source add <notebook-id> --url "https://example.com/article" --wait

# Add a PDF file
nlm source add <notebook-id> --file ~/books/theology-book.pdf --wait

# Add YouTube lecture
nlm source add <notebook-id> --youtube "https://youtube.com/watch?v=..." --wait

# Add Google Drive document
nlm source add <notebook-id> --drive <doc-id> --wait

# Add raw text
nlm source add <notebook-id> --text "content" --title "Source Title"
```

### Tips for Discover Sources
- Be specific: "Pauline theology of grace in Romans" not just "grace"
- Look for academic sources: journal articles, books, seminary publications
- Avoid: Wikipedia, personal blogs, non-academic websites
- Aim for 6-8 sources per paper (minimum 5, 3 must be printed)
- After discovering, verify each source has complete metadata (author, year, publisher)

## Step 3: List All Sources

```bash
# Get all sources with metadata
nlm source list <notebook-id> --json

# Pretty print for reading
nlm source list <notebook-id> --json | jq '.[] | {title, type, url}'
```

The source list returns objects with:
- `id`: unique source identifier
- `title`: source title (book title, article title, etc.)
- `type`: source type (pdf, url, youtube, drive, text)
- `url`: original URL (for web sources)
- `status`: ready, processing, error

## Step 4: Query for Citation Details

Use NLM's AI to extract structured citation info from your sources:

```bash
# Extract bibliography info for all sources
nlm notebook query <notebook-id> "List all sources with: author name, year of publication, title, publisher, type (book/journal/website). Return as a formatted list."

# For a specific book
nlm notebook query <notebook-id> "For the book [TITLE], give me: author full name, year published, publisher, city/pages if mentioned. Format as APA reference."

# Extract specific quotes with page numbers
nlm notebook query <notebook-id> "Find quotes about [TOPIC] from [BOOK TITLE]. Include page numbers if available."

# Get all authors in the notebook
nlm notebook query <notebook-id> "List all unique author names mentioned across all sources."
```

## Step 5: Generate a Source Report

```bash
# Create a briefing doc of all sources
nlm report create <notebook-id> --format "Briefing Doc" --confirm

# Check status
nlm studio status <notebook-id> --json | jq -r '.[] | select(.type=="report") | "\(.type) \(.status) \(.id)"'

# Download the report
nlm download report <notebook-id> --id <artifact-id> --output sources-report.md
```

## Step 6: Build Your Reference List

For each source found, create an APA 7 reference:

### From a PDF Book
Query: "What are the publication details for [book title]?"
Look for: Author, Year, Publisher, City

### From a Journal Article
Query: "Give me the full citation for [article title]"
Look for: Author, Year, Journal name, Volume, Issue, Pages, DOI

### From a YouTube Video

Use NLM to extract transcripts from YouTube videos — no external packages needed:

```bash
# Add YouTube video as source
nlm source add <notebook-id> --youtube "https://youtu.be/VIDEO_ID" --wait

# Extract transcript
nlm notebook query <notebook-id> "Extract the full transcript with timestamps."

# Get citation details (speaker, channel, date, title)
nlm notebook query <notebook-id> "What is the title, channel name, speaker, and upload date of this video?"
```

APA reference format for YouTube:
```
Channel Name. (Year, Month Day). Title of video [Video]. YouTube. URL
```

**Best practice**: Use NLM's `--youtube` source feature as the primary transcript extraction method. Do NOT install `youtube-transcript-api` — NLM handles it natively. The Zapier YouTube MCP (`zapier-youtube-mcp`) does NOT extract transcripts either.

## Bonus: Generate Slide Decks from Sources

If your assignment includes a presentation, NLM can generate a visual slide deck from your sources:

```bash
# Basic slide deck
nlm slides create <notebook-id> --confirm

# Detailed 18-page deck with visual focus
nlm slides create <notebook-id> --format detailed_deck --length dynamic --confirm \
  --focus "Act as a senior presentation designer. Dark luxury aesthetic. One message per slide. Max 4 bullets, 12 words each. 18 pages."

# Check status
nlm studio status <notebook-id> --json | jq -r '.[] | select(.type=="slide_deck") | "\(.type) \(.status) \(.id)"'

# Download
nlm download slide-deck <notebook-id> --id <artifact-id> --output slides.pdf
```

## Tips for Better Extraction

1. **Be specific in queries**: "Who wrote Chapter 3 of [book]?" not "tell me about sources"
2. **Ask for APA format directly**: "Give me the APA 7 reference for this source"
3. **Verify by cross-referencing**: Use Google Scholar or the publisher's website to confirm
4. **Handle missing info gracefully**: If NLM can't find publisher, search for it directly
5. **Save extracted references**: Build your reference list as you go, don't wait until the end
6. **Use Discover first**: Let NLM find sources automatically, then supplement with your own

## Multi-Notebook Extraction

```bash
# Query across specific notebooks
nlm cross query --all "List all sources about [TOPIC] with citation details"

# Target specific notebooks
nlm cross query --notebooks "Theology Research" --notebooks "Bible Commentary" "Find books by [AUTHOR]"
```

## Profile Rotation

If you hit rate limits (INVALID_ARGUMENT error), switch profiles:
```bash
# List available profiles
nlm login profile list

# Switch profile
nlm login switch <profile-name>
```

Available profiles: dayozoe, mentora, trinity, abiodun, default, adeoye53, oludayo35, glorious, architect, adeoye55er

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Source has wrong metadata | Use `nlm source add ... --title "Correct Title"` to override |
| Rate limit (code 8) | Wait 5 min, switch profile, or use lighter format |
| Large PDF won't process | Add without `--wait`, proceed with other sources |
| Missing citation details | Search Google Scholar directly for the source |
| Notebook not found | Check `nlm notebook list` — may need shared access |
| Discover returns poor sources | Refine your search query, be more specific |
| Slides look generic | Use `--focus` with detailed design instructions |
