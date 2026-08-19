---
name: evening-review-notion
description: Generate an evening review from Notion task databases.
version: 0.1.0
author: community
license: MIT
prerequisites:
  env_vars: []
  alt_env: []
metadata:
  hermes:
    tags: [Notion, Productivity, Review, Evening, Tasks]
    homepage: https://developers.notion.com
---

# Evening Review from Notion

This skill outlines how to produce a concise evening review (wins, blockers, tomorrow's agenda, top 3 priorities) by querying Notion task databases.

## Trigger
Use when the user asks for an evening review based on Notion data, or when you need to summarize daily progress and upcoming tasks from Notion.

## Steps

### 1. Retrieve Notion token
Read the integration token from `~/.mcp_servers.json`:
```json
{
  "mcpServers": {
    "notion": {
      "env": {
        "NOTION_TOKEN": "ntn_your_token_here"
      }
    }
  }
}
```
The token is found at `.mcpServers.notion.env.NOTION_TOKEN`.

### 2. Find task databases
Search for databases related to tasks:
```bash
mcp-cli call notion API-post-search '{"query":"task"}'
```
If `mcp-cli` is not available, fall back to `curl` with the token and header `Notion-Version: 2022-06-28`.

From the results, select entries where `"object": "database"`. Collect their `database_id`s.

### 3. Identify a suitable database
For each candidate database, retrieve its metadata:
```bash
mcp-cli call notion API-retrieve-a-page '{"page_id":"<database_id>"}'
```
(Note: The `API-retrieve-a-page` tool works for databases as well.)

Look for:
- A **status property** (type `status`, `select`, or `checkbox`) that can indicate completion (e.g., options named "Done", "Completed", "Complete").
- A **date property** (type `date`) that stores the task's due date or scheduled date.

Pick the first database that has both. If none have a clear completion property, you may still proceed and infer completion from a checkbox or select property whose name suggests completion (e.g., "Done").

Record:
- `status_prop`: property name of the status field.
- `status_type`: its type (`status`, `select`, `checkbox`).
- `date_prop`: property name of the date field.

### 4. Query the database
Fetch all items (up to 100) with an empty filter:
```bash
mcp-cli call notion API-query-data-source '{"data_source_id":"<database_id>"}'
```
**Pitfall**: Some databases return zero results when using the `data_source_id` endpoint (`/v1/data_sources/{id}/query`). If you get no results, try using the `database_id` with the `/v1/databases/{id}/query` endpoint instead (via `curl` or equivalent). See the Notion skill for details on fallback.

### 5. Filter results
For each item in the results:
- Extract the **title** from the `title` property.
- Determine **completion**:
  - If `status_type` is `status`: check `item.properties[status_prop].status.name`.
  - If `status_type` is `select`: check `item.properties[status_prop].select.name`.
  - If `status_type` is `checkbox`: check `item.properties[status_prop].checkbox` (true = completed).
  - Consider a value as completion if it matches (case-insensitive) any of: "done", "completed", "complete", "finished".
- Extract the **date** from `item.properties[date_prop].date.start` (ISO string). Keep only the date part (YYYY-MM-DD).

Then:
- If completed **and** date equals today → add to **today's wins**.
- If **not** completed **and** date equals tomorrow → add to **tomorrow's agenda**.

### 6. Prepare output
Format the review as follows (no tables):

```
���🌙 Evening Review — <today's date>

��✅ Today's Wins
- <task 1>
- <task 2>
(or "No completed tasks logged")

���🚧 Blockers
- None

���📅 Tomorrow's Agenda
- <task 1>
- <task 2>
(or "Nothing scheduled")

���🎯 Top 3 for Tomorrow
1. <top task 1>
2. <top task 2>
3. <top task 3>
(or "Nothing scheduled" for each missing item)
```

Keep the list concise (max 5 items per section). Celebrate progress.

## References
- See the `productivity/notion` skill for basic Notion API usage, authentication, and MCP server setup.
- For details on API version 2022-06-28 changes, refer to that skill's "API Version 2022-06-28 — Important Changes" section.

## Cron / Scheduled Job Usage
This skill can be run in a cron job. Since it involves multiple API calls, consider using the MCP server for efficiency:
```bash
mcp-cli call notion API-post-search '{"query":"task"}'
```
Then follow the steps above using `mcp-cli` or `curl` fallbacks. If the MCP server returns empty output (silent failure), fall back to direct `curl` with the token from `~/.mcp_servers.json`.

---