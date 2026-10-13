---
name: seminary-notion-assignments
description: "Check for seminary writing assignments in Notion databases. Works with the notion skill to track academic work."
version: 0.1.0
author: community
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: [NOTION_TOKEN]
  alt_env: NOTION_API_KEY
  alt_config_path: ~/.mcp_servers.json
metadata:
  hermes:
    tags: [Notion, Productivity, Notes, Database, API, CLI, Workers, Seminary, Writing, Assignments]
    homepage: https://developers.notion.com
---

# Seminary Notion Assignments Skill

This skill provides tools to check for seminary writing assignments stored in Notion databases.
It is designed to work alongside the `notion` skill and provides a script to query assignment databases.

## Overview

Many seminary students use Notion to track their writing assignments, papers, and exegesis work.
This skill provides a script that searches for Notion databases related to assignments and reports
on upcoming deadlines and active work.

## Setup

This skill requires a Notion integration token. The token can be provided in two ways:

1. Set `NOTION_TOKEN` in your environment (preferred for Hermes MCP setup)
2. Set `NOTION_API_KEY` in your environment (fallback)

The token should be obtained from your Notion integrations page:
https://www.notion.so/my-integrations

Ensure that the integration has access to the databases/pages containing your assignments.

## Usage

The primary tool provided by this skill is the `check_seminary_assignments.py` script.

### Running the script

```bash
python3 scripts/check_seminary_assignments.py
```

The script will:
1. Search for Notion databases with names containing: assignment, paper, essay, exegesis
2. For each database, check for properties related to:
   - Assignment name (title property)
   - Due date (date property)
   - Status (select/status/checkbox property)
3. Report:
   - Active assignments (not completed and due today or in the future)
   - Upcoming deadlines (due within the next 7 days)
   - Suggested next action

### Example output

```
📝 Seminary Writing Check

📚 Active Assignments
- Exegesis on Romans 8 — due 2026-07-15 — In Progress
- Theology Paper — due 2026-08-01 — Not Started

📅 Upcoming Deadlines (next 7 days)
- 2026-07-15: Exegesis on Romans 8
- 2026-07-20: Greek Vocabulary Quiz

💡 Suggested Action
Work on 'Exegesis on Romans 8' which is due 2026-07-15
```

## How it works

The script uses the Notion API v2022-06-28 to:
1. Search for databases matching keywords
2. Retrieve database properties to identify relevant fields
3. Query each database for all entries
4. Extract assignment names, due dates, and status
5. Filter for active and upcoming work
6. Present a summary

## Dependencies

- This skill works best when the `notion` skill is available and configured
- Requires `jq` and `python3` to be available in the environment
- Requires a valid Notion integration token with access to your assignment databases

## Customization

To customize the search terms or properties checked, edit the `scripts/check_seminary_assignments.py` file:
- Modify the `search_terms` list to change which database names are searched
- Adjust the property type detection logic if your databases use different property names/types

## Notes

- This script is designed for use in Hermes cron jobs where direct code execution may be restricted
- It avoids using the `execute_code` tool by relying on standard Python and subprocess calls
- For complex Notion operations (creating pages, updating databases), consider using the `notion` skill directly
- The script only reads your Notion data - it does not modify it

## Related Skills

- `notion` - Core Notion API and CLI interactions
- `academic-paper` - For writing academic papers once assignments are identified