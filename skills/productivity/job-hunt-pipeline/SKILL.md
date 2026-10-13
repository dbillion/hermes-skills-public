---
name: job-hunt-pipeline
description: A reusable skill for checking job application status via Gmail and Notion, producing a concise pulse report.
version: 1.0.0
author: community
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: [NOTION_TOKEN]
  external_tools: [gws, mcp-cli, awk, curl]
metadata:
  hermes:
    tags: [job-hunt, gmail, notion, productivity, pipeline]
---
# Job Hunt Pipeline

A reusable skill for checking job application status via Gmail and Notion, producing a concise pulse report.

## When to Use

Run this skill as a cron job or on-demand to summarize:
- New recruiter/job-related emails from Gmail
- Job tracker status from a Notion database or page
- Follow‑up actions needed
- Today’s recommended action

## Prerequisites

- `gws` CLI installed and authenticated for Gmail (`gws gmail` commands work)
- Notion integration token available (via `NOTION_TOKEN` env var or MCP server)
- `mcp-cli` configured for the Notion MCP server (or direct curl fallback)

## Steps

### 1. Scan Recent Gmail for Job‑Related Messages

Use the `+triage` command (the only inbox‑listing command) and filter for keywords.

```bash
gws gmail +triage | tail -n +3 | awk -F'[[:space:]]{2,}' '
{
    sender=$2; subject=$4; for(i=5;i<=NF;i++) subject=subject" "$i
    combined=tolower(sender" "subject)
    if (combined ~ /interview|application|recruiter|offer|follow|speechify|deutsche telekom|sacsops|feedback|position|opportunity/) {
        gsub(/[<>]/,"",sender)
        print sender": "subject
    }
}'
```

- If no matches, report “No new recruiter emails”.

### 2. Query Notion for Job Tracker

Prefer the Notion MCP server; fall back to curl if needed.

**MCP method:**
```bash
mcp-cli call notion API-post-search '{"query":"job tracker"}'
```
Parse the JSON output to extract page/database titles that contain job‑related keywords (job, application, interview, offer, etc.).  
For each matching database, you may want to query its contents:
```bash
echo '{"database_id":"<id>", "filter":{"property":"Status","select":{"equals":"Applied"}}}' | \
  mcp-cli call notion API-query-data-source
```

**Fallback (curl) method:**
```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"query":"job tracker"}'
```

### 3. Determine Follow‑Ups

From the Notion data, look for items with status like “Applied”, “Interviewing”, or “Offer” that lack a recent updated date (e.g., >3 days old).  
Create a list of:
- Company
- Role
- Status
- Suggested action (e.g., “Follow up on application”, “Prepare for interview”)

If none, output “None”.

### 4. Today’s Action

Pick the highest‑priority item from the follow‑up list (e.g., oldest application, or any with status “Applied”) and prescribe a concrete step:
- Send a follow‑up email
- Update the Notion entry with a note
- Prepare interview materials

### 5. Output Format

Keep the report under 300 words, using plain text (no markdown tables). Follow this template:

```
💼 Job Hunt Pulse

📧 New Responses
- [from] — [subject] — needs action: yes/no
(or No new recruiter emails)

📊 Pipeline (from Notion)
- [company] — [role] — status: [applied/interviewing/offer/rejected]
(or No job tracker found)

⚠️ Follow-ups Needed
- [company] — last contact [date] — [action]
(or None)

🎯 Today's Action
[One specific thing to do]
```

## Pitfalls

- **Do NOT use `gws gmail list`** – it does not exist; always use `+triage`.
- In Notion queries, property names in filters must match **exactly** (case-sensitive). Common mismatches include using "Date" when the property is named "Due Date" or "Status" when it's "State". If you get a validation error like "Could not find property with name or id: X", double-check the exact property name in your Notion database.
- In cron jobs, avoid `execute_code`; use plain shell tools (`awk`, `grep`, `curl`, `mcp-cli`).
- The Notion MCP server may silently fail if the token is missing; fall back to curl with `NOTION_TOKEN` from environment.
- Rate‑limit: Notion API allows ~3 requests/sec; throttle if querying many databases.

## References

- `references/gws-gmail-triage.md` – details on parsing `+triage` output
- `references/notion-job-tracker-query.md` – example MCP and curl queries

## Example

See the session log for a concrete run (this skill was used to produce the pulse report).