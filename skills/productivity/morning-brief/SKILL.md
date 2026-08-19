---
name: morning-brief
description: Generate Telegram morning brief from Gmail and Notion
version: 1.0.0
author: community
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: [NOTION_API_KEY]
  external_commands: [gws, mcp-cli]
---

# Morning Brief Skill

Generate a concise morning brief for Telegram delivery that checks:
1. Gmail for urgent emails (using specific keywords)
2. Notion for today's tasks (using date property filters)

## When to Use

Use this skill when you need to generate a daily summary for personal productivity tracking, especially in cron jobs or automated workflows where you want a Telegram-friendly update.

## Skill Overview

This skill combines GWS Gmail and Notion operations to create a morning brief with:
- Urgent email highlights (filtered by keywords)
- Today's tasks from Notion databases
- Top 3 priorities derived from emails and tasks
- Telegram-friendly markdown formatting (no tables)
- [SILENT] output when nothing to report

## Workflow

### 1. Check Gmail for Urgent Emails
```bash
# Get recent emails (limit 20) - NOTE: Use +triage, not list
gws gmail +triage | head -20

# Filter for urgent emails using keywords
gws gmail +triage | tail -n +3 | awk -F'[[:space:]]{2,}' '
{
    from=$2
    subject=$4
    for(i=5; i<=NF; i++) subject=subject" "$i
    combined=tolower(from" "subject)
    if (combined ~ /recruiter|deadline|invoice|urgent|important|offer|interview|application|signup|debt|earning/) {
        gsub(/[<>]/, "", from)
        print from": "subject
    }
}'
```

### 2. Check Notion for Today's Tasks
```bash
# Find task databases
mcp-cli call notion API-post-search '{"query":"tasks"}'

# For each database, query today's items
echo '{"data_source_id": "DATABASE_ID", "filter": {"property": "Date", "date": {"on_or_after": "TODAY", "on_or_before": "TODAY"}}}' | \
  mcp-cli call notion API-query-data-source
```

### 3. Format the Brief
Output format:
```
🌅 Morning Brief — [date]

📧 Email Highlights
- [urgent email 1]
- [urgent email 2]
(or No urgent emails)

📋 Today's Tasks (from Notion)
- [task 1] — [status/priority]
- [task 2] — [status/priority]
(or No tasks found for today)

🎯 Top 3 Priorities
1. [most urgent]
2. [important]
3. [if time permits]
```

## Key Points

- **Never use `gws gmail list`** - this command doesn't exist. Always use `+triage` for inbox scanning.
- **Urgent email keywords**: recruiter, deadline, invoice, urgent, important, offer, interview, application, signup, debt, earning
- **Notion date filtering**: Use `on_or_after` and `on_or_before` with today's date (YYYY-MM-DD format)
- **Output limits**: Max 5 urgent emails, max 5 tasks in the brief
- **Silent output**: If no urgent emails and no tasks, output exactly `[SILENT]`
- **Telegram-friendly**: Use emojis and dash lists, avoid tables

## Error Handling

- If GWS fails, continue with Notion portion and note the failure in priorities if needed
- If Notion MCP fails, fall back to direct curl with token from `~/.mcp_servers.json`
- If neither source has data, output `[SILENT]`

## Example Cron Job Entry

```
0 7 * * * /home/deeone/.hermes/skills/productivity/morning-brief/scripts/generate_brief.sh
```

## References

See `references/email_filtering.awk` for the ready-to-use email filtering script.
See `references/notion_query.json` for a template Notion query file.
See `scripts/generate_brief.sh` for the complete automation script.