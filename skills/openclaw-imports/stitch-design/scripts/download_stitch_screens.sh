#!/usr/bin/env bash
# Download all screens from a Stitch project as HTML + PNG
# Usage: ./download_stitch_screens.sh <project_id> <api_key> <output_dir>
#
# Dependencies: curl, jq (optional but recommended)
# Rate limit: 0.5s between get_screen calls

set -euo pipefail

PROJECT_ID="${1:?Usage: $0 <project_id> <api_key> <output_dir>}"
API_KEY="${2:?Usage: $0 <project_id> <api_key> <output_dir>}"
OUTPUT_DIR="${3:?Usage: $0 <project_id> <api_key> <output_dir>}"

mkdir -p "$OUTPUT_DIR"
MCP_URL="https://stitch.googleapis.com/mcp"

echo "Fetching screen list..."

# Step 1: List all screens
LIST_RESP=$(curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "X-Goog-Api-Key: $API_KEY" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"list_screens\",
      \"arguments\": {
        \"projectId\": \"$PROJECT_ID\"
      }
    }
  }")

# Step 2: Parse screens, deduplicate by title (keep last/newest)
# Requires jq. If not available, use a simple Python fallback.
if command -v jq &> /dev/null; then
  SCREENS_JSON=$(echo "$LIST_RESP" | python3 -c "
import json, sys
raw = json.loads(sys.stdin.read())
text = raw['result']['content'][0]['text']
data = json.loads(text)
screens = data.get('screens', [])
# Deduplicate by title, keep last occurrence
latest = {}
for s in screens:
    title = s.get('title', 'Untitled').replace('/', '-').replace(' ', '-').lower()
    # Strip non-alphanumeric except dash/underscore
    import re
    title = re.sub(r'[^a-z0-9_-]', '', title[:60])
    latest[title] = s
for title, s in latest.items():
    print(json.dumps({'title': title, 'id': s['name'].split('/')[-1]}))
")
else
  echo "jq not found, using Python..."
  SCREENS_JSON=$(python3 -c "
import json, re
raw = json.loads('''$LIST_RESP''')
text = raw['result']['content'][0]['text']
data = json.loads(text)
screens = data.get('screens', [])
latest = {}
for s in screens:
    title = s.get('title', 'Untitled')
    title = re.sub(r'[^a-z0-9_-]', '', title.replace('/', '-').replace(' ', '-').lower()[:60])
    latest[title] = s
for title, s in latest.items():
    print(json.dumps({'title': title, 'id': s['name'].split('/')[-1]}))
")
fi

echo "Downloading screens..."
COUNT=0
TOTAL=$(echo "$SCREENS_JSON" | wc -l)

echo "$SCREENS_JSON" | while IFS= read -r line; do
  title=$(echo "$line" | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['title'])")
  screen_id=$(echo "$line" | python3 -c "import json,sys; print(json.loads(sys.stdin.read())['id'])")
  COUNT=$((COUNT + 1))
  echo "[$COUNT/$TOTAL] $title ($screen_id)..."

  # Step 3: get_screen for fresh download URLs
  GET_RESP=$(curl -s -X POST "$MCP_URL" \
    -H "Content-Type: application/json" \
    -H "X-Goog-Api-Key: $API_KEY" \
    -d "{
      \"jsonrpc\": \"2.0\",
      \"id\": 2,
      \"method\": \"tools/call\",
      \"params\": {
        \"name\": \"get_screen\",
        \"arguments\": {
          \"projectId\": \"$PROJECT_ID\",
          \"screenId\": \"$screen_id\",
          \"name\": \"projects/$PROJECT_ID/screens/$screen_id\"
        }
      }
    }")

  # Step 4: Extract download URLs
  HTML_URL=$(echo "$GET_RESP" | python3 -c "
import json, sys, re
raw = json.loads(sys.stdin.read())
text = raw.get('result', {}).get('content', [{}])[0].get('text', '{}')
data = json.loads(text)
html = data.get('htmlCode', {}).get('downloadUrl', '')
print(html)
" 2>/dev/null)

  PNG_URL=$(echo "$GET_RESP" | python3 -c "
import json, sys, re
raw = json.loads(sys.stdin.read())
text = raw.get('result', {}).get('content', [{}])[0].get('text', '{}')
data = json.loads(text)
img = data.get('screenshot', {}).get('downloadUrl', '')
print(img)
" 2>/dev/null)

  # Step 5: Download files
  if [ -n "$HTML_URL" ]; then
    curl -sL -f "$HTML_URL" -o "$OUTPUT_DIR/$title.html" && echo "  ✅ $title.html" || echo "  ❌ $title.html failed"
  else
    echo "  ⚠️  No HTML for $title"
  fi

  if [ -n "$PNG_URL" ]; then
    curl -sL -f "$PNG_URL" -o "$OUTPUT_DIR/$title.png" && echo "  ✅ $title.png" || echo "  ❌ $title.png failed"
  else
    echo "  ⚠️  No screenshot for $title"
  fi

  # Rate limit
  sleep 0.5
done

echo ""
echo "Done! Files saved to $OUTPUT_DIR/"
ls -la "$OUTPUT_DIR/"*.html "$OUTPUT_DIR/"*.png 2>/dev/null || true
