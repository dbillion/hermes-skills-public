---
name: social-analytics
description: Perform social media scraping and analytics management. Use when you need to query GA4/Search Console data or scrape TikTok, Instagram, and LinkedIn using TikHub.
---

# Social Analytics & Scraping

This skill provides a unified workflow for managing Google Analytics and performing cross-platform social media scraping.

## GA4 & Search Console Management

Use the `ga4-manager` CLI and MCP server to automate analytics tasks.
- **Commands**: See [references/ga4_usage.md](references/ga4_usage.md)
- **Primary Tool**: `ga4-manager` MCP tools.

## Social Media Scraping (TikHub)

Use the TikHub Python SDK to extract data from 16+ social platforms.
- **SDK Reference**: See [references/tikhub_sdk.md](references/tikhub_sdk.md)
- **Local Scripts**: Browse `/home/deeone/mcp_servers/TikHub-API-Python-SDK/examples` for templates.

## Workflow Patterns

1. **Analytics Audit**: Run `ga4 report` to check performance and `ga4 cleanup` to remove dead dimensions.
2. **Competitor Scraping**: Generate a Python script using the TikHub SDK to track competitor profile growth.
3. **Data Integration**: Use `browseruse` to bridge scraping results into local reports.
