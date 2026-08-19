---
name: trend-to-strategy
description: "Integrated workflow for market intelligence. Discover live market signals (via google-news-trends MCP) and synthesize them into professional artifacts like pitch decks, reports, or audio overviews (via nlm CLI)."
---

# Trend to Strategy Workflow

Automates the transition from "Raw Market Data" to "Executive Strategy." Combines Google Trends/News MCP discovery with NotebookLM CLI synthesis.

## Core Pipeline

1. **Discovery**: Use `google-news-trends` MCP to find high-growth keywords
2. **Grounding**: Collect URL sources into a local document
3. **Synthesis**: Ingest sources into `nlm` to create structured output

## Tool Integration

### 1. Market Discovery (google-news-trends MCP)
```bash
mcp-cli call google-news-trends get_trending_terms '{"geo": "US"}'
mcp-cli call google-news-trends get_news_by_keyword '{"keyword": "AI tools 2026", "summarize": true}'
```

### 2. Deep Synthesis (nlm CLI)
```bash
# Create notebook from trends
nlm notebook create "Market Strategy: [Trend]"
NB_ID=$(nlm notebook list --json | jq -r '.[0].id)
nlm source add "$NB_ID" --url [URL from News MCP]

# Generate artifacts
nlm slides create "$NB_ID" --confirm
nlm audio create "$NB_ID" --format deep_dive --confirm
nlm report create "$NB_ID" --format "Briefing Doc" --confirm

# Download
nlm download video "$NB_ID" <artifact-id> --output pitch-deck.mp4
nlm download slide-deck "$NB_ID" <artifact-id> --output slides.pdf
nlm download report "$NB_ID" <artifact-id> --output strategy-report.md
```

## Workflow Patterns

### Pattern A: Business Opportunity
1. Identify 3 rising keywords in a specific region
2. Fetch top 5 news articles for the strongest keyword
3. Ingest summaries into `nlm`
4. Generate a **Competitive Analysis Report**

### Pattern B: Investor Pitch
1. Search for "best [category] products 2026"
2. Cross-reference with Reddit pain points
3. Ground findings in `nlm`
4. Generate a **McKinsey-style Pitch Deck**

## Best Practices

- **Grounding First**: Always ensure `nlm` has 3-5+ sources before generating complex artifacts
- **Piping**: Systematically add URLs to the notebook before synthesis
- **Token Efficiency**: Use `summarize: true` in News MCP to keep grounding text concise
