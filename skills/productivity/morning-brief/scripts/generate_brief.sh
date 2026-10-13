#!/bin/bash
# Generate morning brief script
# Usage: ./generate_brief.sh

set -e

# Temporary files
TMPDIR=$(mktemp -d)
DATE_FILE="$TMPDIR/date"
EMAILS_RAW="$TMPDIR/emails_raw"
URGENT_EMAILS="$TMPDIR/urgent_emails"
NOTION_SEARCH="$TMPDIR/notion_search.json"
DATABASE_IDS="$TMPDIR/database_ids.txt"
NOTION_QUERY_RAW="$TMPDIR/notion_query_raw.json"
TASKS_FILE="$TMPDIR/tasks.txt"

# 1. Get current date
date +%Y-%m-%d > "$DATE_FILE"
CURRENT_DATE=$(cat "$DATE_FILE")

# 2. Get emails (limit 20) using +triage
gws gmail +triage | head -20 > "$EMAILS_RAW" 2>/dev/null || true

# 3. Extract urgent emails using awk (from references)
awk -F'[[:space:]]{2,}' '
NR>=3 {
    from=$2
    subject=$4
    for(i=5; i<=NF; i++) subject=subject" "$i
    combined=tolower(from" "subject)
    if (combined ~ /recruiter|deadline|invoice|urgent|important|offer|interview|application|signup|debt|earning/) {
        gsub(/[<>]/, "", from)
        print from": "subject
    }
}' "$EMAILS_RAW" > "$URGENT_EMAILS"

# 4. Get notion task databases
mcp-cli call notion API-post-search '{"query":"tasks"}' > "$NOTION_SEARCH" 2>/dev/null || true

# 5. Extract database IDs (object: data_source)
python3 -c "
import json
try:
    with open('$NOTION_SEARCH', 'r') as f:
        data = json.load(f)
    if data.get('object') == 'list' and 'results' in data:
        for item in data['results']:
            if item.get('object') == 'data_source':
                print(item['id'])
except Exception as e:
    pass
" > "$DATABASE_IDS"

# 6. Initialize tasks file
> "$TASKS_FILE"

# 7. For each database, query today's tasks
while IFS= read -r db_id; do
    [ -z "$db_id" ] && continue
    # Build filter JSON for today's date
    FILTER="{\"data_source_id\": \"$db_id\", \"filter\": {\"property\": \"Date\", \"date\": {\"on_or_after\": \"$CURRENT_DATE\", \"on_or_before\": \"$CURRENT_DATE\"}}}"
    echo "$FILTER" > "$TMPDIR/filter.json"
    mcp-cli call notion API-query-data-source --json "$(cat "$TMPDIR/filter.json")" >> "$NOTION_QUERY_RAW" 2>/dev/null || true
done < "$DATABASE_IDS"

# 8. Extract tasks from the notion query raw
python3 -c "
import json
try:
    with open('$NOTION_QUERY_RAW', 'r') as f:
        data = json.load(f)
    if data.get('object') == 'list' and 'results' in data:
        for item in data['results']:
            if item.get('object') != 'page':
                continue
            props = item.get('properties', {})
            title = None
            status = None
            # Find title
            for prop_name, prop_val in props.items():
                if prop_val.get('type') == 'title':
                    title_arr = prop_val.get('title', [])
                    if title_arr:
                        title = title_arr[0].get('text', {}).get('content', '')
                    break
            # Find status (select or status)
            for prop_name, prop_val in props.items():
                if prop_val.get('type') in ['select', 'status']:
                    select_val = prop_val.get('select') or prop_val.get('status')
                    if select_val and select_val.get('name'):
                        status = select_val.get('name')
                        break
            if title:
                if status:
                    print(title + ' — ' + status)
                else:
                    print(title)
except Exception as e:
    pass
" > "$TASKS_FILE"

# 9. Check if there's anything to report
if [ ! -s "$URGENT_EMAILS" ] && [ ! -s "$TASKS_FILE" ]; then
    echo "[SILENT]"
    rm -rf "$TMPDIR"
    exit 0
fi

# 10. Build the brief
echo "🌅 Morning Brief — $CURRENT_DATE"
echo ""
echo "📧 Email Highlights"
if [ -s "$URGENT_EMAILS" ]; then
    head -5 "$URGENT_EMAILS" | while read line; do
        echo "- $line"
    done
else
    echo "- No urgent emails"
fi
echo ""
echo "📋 Today's Tasks (from Notion)"
if [ -s "$TASKS_FILE" ]; then
    while read line; do
        echo "- $line"
    done < "$TASKS_FILE"
else
    echo "- No tasks found for today"
fi
echo ""
echo "🎯 Top 3 Priorities"
priorities=()
# Add first urgent email if exists
if [ -s "$URGENT_EMAILS" ]; then
    first_email=$(head -1 "$URGENT_EMAILS")
    sender=$(echo "$first_email" | cut -d':' -f1)
    priorities+=("Respond to urgent email from $sender")
fi
# Add first task if exists
if [ -s "$TASKS_FILE" ]; then
    first_task=$(head -1 "$TASKS_FILE")
    task_name=$(echo "$first_task" | cut -d' — ' -f1)
    priorities+=("Complete task: $task_name")
fi
# If we have less than 2, add generic ones
while [ ${#priorities[@]} -lt 2 ]; do
    priorities+=("Review overnight notifications")
done
while [ ${#priorities[@]} -lt 3 ]; do
    priorities+=("Plan afternoon focus block")
done
# Take top 3
for i in {0..2}; do
    if [ $i -lt ${#priorities[@]} ]; then
        echo "$((i+1)). ${priorities[$i]}"
    fi
done

# Cleanup
rm -rf "$TMPDIR"
exit 0