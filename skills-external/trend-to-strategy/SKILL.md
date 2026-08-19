---
name: trend-to-strategy
description: Integrated workflow for market intelligence. Use when the user needs to discover live market signals (via google-news-trends) and synthesize them into professional artifacts like pitch decks, reports, or audio overviews (via NotebookLM CLI nlm).
---

# Trend to Strategy Workflow

This skill automates the transition from "Raw Market Data" to "Executive Strategy." It combines the discovery power of the Google Trends/News MCP with the grounding and synthesis capabilities of the NotebookLM CLI (`nlm`).

## Core Pipeline

1. **Discovery**: Use `google-news-trends` to find high-growth keywords or news topics.
2. **Grounding**: Collect URL sources or search results into a local document or source list.
3. **Synthesis**: Ingest sources into `nlm` to create structured output.

## Tool Integration

### 1. Market Discovery (google-news-trends)
Use these tools to find what parents/users are searching for *now*:
- `mcp-cli call google-news-trends get_trending_terms '{"geo": "US"}'`
- `mcp-cli call google-news-trends get_news_by_keyword '{"keyword": "educational tech trends", "summarize": true}'`

### 2. Deep Synthesis (NotebookLM CLI `nlm`)
Once you have the trends, use `nlm` to transform them:
- **Create Notebook**: `mcp-cli call nlm create_notebook '{"title": "Market Strategy: [Trend]"}'`
- **Add Sources**: `mcp-cli call nlm add_source '{"url": "[URL from News MCP]"}'`
- **Generate Artifacts**:
    - **Pitch Deck**: `mcp-cli call nlm generate_slides '{"style": "McKinsey", "topic": "[Strategy Name]"}'`
    - **Audio Overview**: `mcp-cli call nlm create_audio_overview`
    - **Strategic Report**: `mcp-cli call nlm generate_report '{"format": "executive_summary"}'`

## Workflow Patterns

### Pattern A: The "High-Gain" Business Opportunity
1. Identify 3 rising keywords in a specific region (CA/US/UK/AU).
2. Fetch top 5 news articles for the strongest keyword.
3. Ingest summaries into `nlm`.
4. Generate a **Competitive Analysis Report**.

### Pattern B: The Investor Pitch
1. Search for "best [category] products 2026".
2. Cross-reference with Reddit pain points (using `playwright`).
3. Ground the findings in `nlm`.
4. Generate a **McKinsey-style Pitch Deck** using the `notebooklm-visuals` protocol.

## Best Practices
- **Grounding First**: Always ensure the `nlm` tool has enough sources (at least 3-5) before generating a complex artifact like a Pitch Deck.
- **Piping**: If a search result returns a list of URLs, systematically add them to the notebook before running the synthesis command.
- **Token Efficiency**: Use `summarize: true` in the News MCP to keep the grounding text concise and high-signal.
