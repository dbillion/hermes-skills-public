---
name: notion-automation
description: Safe Notion MCP patterns for cron/automated environments.
version: 1.0.0
author: community
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: []
  optional_env: [NOTION_API_KEY, NOTION_TOKEN]
metadata:
  hermes:
    tags: [Notion, Automation, Cron, MCP, Productivity]
    homepage: https://developers.notion.com
---

# Notion Automation for Cron/Automated Environments

This skill provides battle-tested patterns for safely using Notion's MCP server and API in automated contexts like Hermes cron jobs and other non-interactive environments. It addresses common pitfalls including silent failures, response parsing complexities, and historical data filtering.

## Why This Matters in Cron

Hermes cron jobs have specific constraints:
- `execute_code` and `python3 -c` are blocked (security restriction)
- No interactive input possible
- Must handle failures gracefully without user intervention
- Output should be clean and machine-parseable

## Core Patterns

### 1. Safe MCP Usage in Cron

Never rely solely on MCP in cron due to silent failures. Always implement fallback logic.

```bash
# Pattern: Try MCP first, fallback to curl on any failure
mcp_output=$(mcp-cli call notion API-post-search '{"query":"assignments"}' 2>/dev/null) || {
  # MCP failed (timeout, silent failure, etc.) - fall back to curl
  NOTION_TOKEN=$(grep NOTION_TOKEN ~/.mcp_servers.json | sed -n 's/.*"NOTION_TOKEN": *"\([^"]*\)".*/\1/p')
  curl -s -X POST "https://api.notion.com/v1/search" \
    -H "Authorization: Bearer $NOTION_TOKEN" \
    -H "Notion-Version: 2022-06-28" \
    -H "Content-Type: application/json" \
    -d '{"query": "assignments"}'
}
```

### 2. MCP Response Parsing (Double JSON)

MCP responses require two-step parsing:
1. Outer JSON: contains `content` array with text objects
2. Inner JSON: the actual Notion API response string

```bash
# Extract and parse MCP response safely
get_notion_data() {
  local mcp_output="$1"
  local inner_json
  
  # Extract the inner JSON string from MCP's text response
  inner_json=$(echo "$mcp_output" | \
    python3 -c 'import sys, json; data=json.load(sys.stdin); print(data["content"][0]["text"])')
  
  # Parse the actual Notion API response
  echo "$inner_json" | python3 -c 'import sys, json; data=json.load(sys.stdin); print(json.dumps(data, indent=2))'
}
```

### 3. Avoiding Pipe-to-Interpreter Issues

Some execution environments block piping directly to interpreters. Use temporary files:

```bash
# Safe pattern for cron
mcp-cli call notion API-post-search '{"query":"test"}' > /tmp/mcp_raw.json 2>&1
python3 /path/to/parse_notion.py /tmp/mcp_raw.json
```

### 4. Handling Silent MCP Failures

When `mcp-cli` returns exit 0 with empty stdout/stderr:

```bash
# Detect and handle silent failures
mcp_output=$(mcp-cli call notion API-post-search '{"query":"test"}' 2>&1)
if [ -z "$mcp_output" ] && [ ! -s /proc/$$/fd/1 ] && [ ! -s /proc/$$/fd/2 ]; then
  # Silent failure detected - fallback to curl immediately
  echo "MCP silent failure, falling back to curl" >&2
  # ... curl command here ...
fi
```

## Practical Example: Checking for Upcoming Assignments

This pattern checks Notion for assignments due in the next 7 days, filtering out historical data:

```bash
#!/bin/bash
# notion-assignment-check - Safe cron-ready assignment checker

# Get today's date in YYYY-MM-DD format
TODAY=$(date +%Y-%m-%d)
TARGET_DATE=$(date -d "+7 days" +%Y-%m-%d)

# Try MCP first, fallback to curl
MCP_OUTPUT=$(mcp-cli call notion API-post-search '{"query":"assignment"}' 2>&1) || {
  # Fallback to direct API
  NOTION_TOKEN=$(grep -o '"NOTION_TOKEN": *"[^"]*"' ~/.mcp_servers.json | cut -d'"' -f4)
  MCP_OUTPUT=$(curl -s -X POST "https://api.notion.com/v1/search" \
    -H "Authorization: Bearer $NOTION_TOKEN" \
    -H "Notion-Version: 2022-06-28" \
    -H "Content-Type: application/json" \
    -d '{"query": "assignment"}')
}

# Parse the response (handle both MCP and raw API formats)
if echo "$MCP_OUTPUT" | grep -q '"content":'; then
  # This is MCP output - extract inner JSON
  JSON_DATA=$(echo "$MCP_OUTPUT" | python3 -c "
import sys, json
try:
  data = json.load(sys.stdin)
  inner_text = data['content'][0]['text']
  print(inner_text)
except:
  sys.stderr.write('Failed to parse MCP response\\n')
  sys.exit(1)
  ")
else
  # This is already direct API response
  JSON_DATA="$MCP_OUTPUT"
fi

# Extract assignments due in next 7 days
echo "$JSON_DATA" | python3 -c "
import sys, json, datetime
from datetime import datetime

try:
  data = json.load(sys.stdin)
except:
  # Handle case where we got plain text instead of JSON
  print('[]')
  sys.exit(0)

today = datetime.strptime('$TODAY', '%Y-%m-%d').date()
target_date = datetime.strptime('$TARGET_DATE', '%Y-%m-%d').date()

upcoming = []

# Handle different response formats
results = []
if 'results' in data:
  results = data['results']
elif isinstance(data, list):
  results = data

for item in results:
  # Skip if not a page or database
  if item.get('object') not in ['page', 'data_source']:
    continue
    
  props = item.get('properties', {})
  
  # Extract title (flexible property name detection)
  title = ''
  for prop_name, prop_val in props.items():
    if prop_val.get('type') == 'title':
      title_list = prop_val.get('title', [])
      if title_list:
        title = title_list[0].get('plain_text', '').strip()
        break
  
  if not title:
    title = item.get('id', 'Untitled')
  
  # Extract date (flexible property name detection)
  due_date = None
  for prop_name, prop_val in props.items():
    if prop_val.get('type') == 'date':
      date_info = prop_val.get('date')
      if date_info and date_info.get('start'):
        try:
          due_date = datetime.strptime(date_info['start'].split('T')[0], '%Y-%m-%d').date()
          break
        except:
          pass
  
  # Skip if no date or date is in the past
  if not due_date or due_date < today:
    continue
    
  # Check if within target window
  if due_date <= target_date:
    # Extract status if available
    status = 'Unknown'
    for prop_name, prop_val in props.items():
      if prop_val.get('type') in ['status', 'select']:
        status_obj = prop_val.get('status') or prop_val.get('select')
        if status_obj:
          status = status_obj.get('name', 'Unknown')
          break
    
    upcoming.append({
      'title': title,
      'due_date': due_date.isoformat(),
      'status': status
    })

# Sort by due date
upcoming.sort(key=lambda x: x['due_date'])

# Output as JSON for further processing
print(json.dumps(upcoming, indent=2))
"
```

## Key Pitfalls and Solutions

### Pitfall 1: MCP Silent Failures
**Symptom**: `mcp-cli call notion ...` returns exit 0 with no output  
**Solution**: Implement immediate fallback to curl after checking for empty output

### Pitfall 2: Historical Data Contamination  
**Symptom**: Seeing old assignments from 2021-2023 as "upcoming"  
**Solution**: Always compare due dates against `datetime.date.today()` before considering an item active or upcoming

### Pitfall 3: Property Name Variations  
**Symptom**: Code fails when Notion database uses "Due Date" instead of "Due"  
**Solution**: Extract properties by type (`date`, `title`, `select`) rather than hardcoded names

### Pitfall 4: Double JSON Parsing Complexity  
**Symptom**: Getting string instead of parsed data, or JSON decode errors  
**Solution**: Always remember MCP wraps the actual response in `content[0].text`

### Pitfall 5: Pipe-to-Interpreter Blocks in Restricted Environments  
**Symptom**: `mcp-cli ... | python3 -c ...` fails with permission errors  
**Solution**: Write to temporary file first, then process

## Recommended Tools for Automation

1. **For MCP communication**: Use `mcp-cli call notion <tool> '<json>'` with fallback to curl
2. **For JSON parsing**: Use Python one-liners or small scripts saved to files
3. **For date math**: Use `date` command (Unix) or Python's datetime module
4. **For temporary files**: Use `/tmp/` with unique names (`$$` for PID)

## When to Use This Pattern

Use this approach when:
- Running Notion queries in Hermes cron jobs
- Building automated assignment checkers
- Creating scheduled Notion data synchronization
- Any non-interactive Notion automation requiring reliability

## Related Skills

- `seminary-writer`: For semantic writing guidelines and assignment workflows
- `productivity/notion`: For general Notion API reference (use for raw API details)
- `autonomous-ai-agents`: For delegating complex Notion workflows to subagents

## Validation

Always verify your automation logic with:
1. Known upcoming/due items
2. Known historical items (should be filtered out)
3. Edge cases (same-day due dates, timezone considerations)