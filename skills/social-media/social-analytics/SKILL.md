---
name: social-analytics
description: "Social media scraping and analytics management. Query GA4/Search Console data and scrape TikTok, Instagram, and LinkedIn."
---

# Social Analytics & Scraping

Unified workflow for Google Analytics and cross-platform social media scraping.

## GA4 & Search Console

Use the `ga4-manager` MCP server (already configured in mcp-cli):
```bash
mcp-cli call ga4-manager run_report '{"property": "properties/XXXXX"}'
```

## Social Media Scraping (TikHub)

TikHub Python SDK supports 16+ platforms. Scripts at `/home/deeone/mcp_servers/TikHub-API-Python-SDK/examples`.

## Workflow Patterns

1. **Analytics Audit**: Run GA4 reports to check performance
2. **Competitor Scraping**: Track competitor profile growth across platforms
3. **Data Integration**: Bridge scraping results into local reports
