#!/usr/bin/env bash
# verify-views.sh — Convert ERB views to standalone HTML and screenshot at multiple breakpoints
# Usage: bash scripts/verify-views.sh <view_path> <output_name> [screenshot_dir]
#
# Examples:
#   bash scripts/verify-views.sh app/views/campaigns/index.html.erb campaigns
#   bash scripts/verify-views.sh app/views/dashboard/index.html.erb dashboard ./screenshots
#
# Requirements: chromium installed, Tailwind CDN accessible
# Output: <dir>/<name>-1440.png and <dir>/<name>-375.png

set -euo pipefail

VIEW_PATH="${1:?Usage: verify-views.sh <view_path> <output_name> [screenshot_dir]}"
VIEW_NAME="${2:?Usage: verify-views.sh <view_path> <output_name> [screenshot_dir]}"
SCREENSHOT_DIR="${3:-.stitch/screenshots}"

mkdir -p "$SCREENSHOT_DIR"
mkdir -p /tmp/crm-verify

HTML_PREFIX='<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
  theme: { extend: {
    colors: { primary: "#0D9488", "primary-hover": "#0F766E", "primary-subtle": "#CCFBF1", canvas: "#F8FAFB", ink: "#18181B", steel: "#71717A", border: "rgba(226,232,240,0.5)", surface: "#FFFFFF", success: "#059669", warning: "#D97706", error: "#DC2626", info: "#0284C7" },
    borderRadius: { DEFAULT: "12px" },
    fontFamily: { geist: ["Geist","system-ui","sans-serif"] },
  }}
}
</script>
<style>
@import url("https://fonts.googleapis.com/css2?family=Geist:wght@100..900&display=swap");
body{font-family:"Geist",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.animate-fade-up{animation:fadeUp .5s cubic-bezier(.16,1,.3,1) forwards}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
.btn-push:active{transform:scale(.98) translateY(1px);transition:transform .1s}
.transition-spring{transition:all .3s cubic-bezier(.16,1,.3,1)}
.scrollbar-hide{-ms-overflow-style:none;scrollbar-width:none}.scrollbar-hide::-webkit-scrollbar{display:none}
</style>
</head><body class="font-geist antialiased bg-canvas text-ink">'

HTML_SUFFIX='</body></html>'

# Convert ERB to testable HTML
erb_to_html() {
  python3 -c "
import re, sys

with open('$VIEW_PATH', 'r') as f:
    html = f.read()

# Remove content_for
html = re.sub(r'<\%\s*content_for.*?\%>', '', html)
# Remove ERB comments
html = re.sub(r'<\%#.*?\%>', '', html)
# Remove devise error blocks
html = re.sub(r'<\%\s*if\s+resource\.errors\.any\?\s*\%>.*?\<\%\s*end\s*\%>', '', html, flags=re.DOTALL)
# form_with → <form>
html = re.sub(r'<\%=\s*form_with[^%]*?do\s*\|\s*f\s*\|\s*\%>', '<form>', html)
# f helpers → HTML inputs
html = re.sub(r'<\%=\s*f\.search_field[^%]*placeholder:\s*\"([^\"]*)\"[^%]*\%>', r'<input type=\"search\" class=\"w-full bg-primary-subtle/30 border border-border rounded-lg py-2 pl-10 pr-4 text-sm\" placeholder=\"\1\"/>', html)
html = re.sub(r'<\%=\s*f\.label\s+:?\w+,\s*\"([^\"]*)\"[^%]*\%>', r'<label class=\"text-sm font-medium\">\1</label>', html)
html = re.sub(r'<\%=\s*f\.email_field[^%]*\%>', '<input type=\"email\" class=\"w-full px-4 py-3 rounded-xl border border-border bg-white text-sm min-h-[48px]\"/>', html)
html = re.sub(r'<\%=\s*f\.password_field[^%]*\%>', '<input type=\"password\" class=\"w-full px-4 py-3 rounded-xl border border-border bg-white text-sm min-h-[48px]\"/>', html)
html = re.sub(r'<\%=\s*f\.text_field[^%]*\%>', '<input type=\"text\" class=\"w-full px-4 py-3 rounded-xl border border-border bg-white text-sm min-h-[48px]\"/>', html)
html = re.sub(r'<\%=\s*f\.submit\s+\"([^\"]*)\"[^%]*\%>', r'<button type=\"submit\" class=\"w-full py-3.5 bg-primary text-white rounded-xl font-semibold btn-push\">\1</button>', html)
html = re.sub(r'<\%=\s*f\.hidden_field[^%]*\%>', '', html)
html = re.sub(r'<\%=\s*f\.check_box[^%]*\%>', '<input type=\"checkbox\"/>', html)
html = re.sub(r'<\%=\s*f\.select[^%]*\%>', '<select class=\"w-full px-4 py-3 rounded-xl border border-border bg-white text-sm min-h-[48px]\"><option>Select...</option></select>', html)
html = re.sub(r'<\%=\s*f\.collection_select[^%]*\%>', '<select class=\"w-full px-4 py-3 rounded-xl border border-border bg-white text-sm min-h-[48px]\"><option>Select...</option></select>', html)
html = re.sub(r'<\%=\s*f\.datetime_field[^%]*\%>', '<input type=\"datetime-local\" class=\"w-full px-4 py-3 rounded-xl border border-border bg-white text-sm min-h-[48px]\"/>', html)
html = re.sub(r'<\%=\s*text_field_tag[^%]*placeholder:\s*\"([^\"]*)\"[^%]*\%>', r'<input type=\"text\" class=\"w-full pl-10 pr-4 py-2 bg-white border border-border rounded-lg text-sm\" placeholder=\"\1\"/>', html)
# link_to
html = re.sub(r'<\%=\s*link_to\s+\"([^\"]*)\",\s*\w+_path[^,%]*,\s*class:\s*\"([^\"]*)\"[^%]*\%>', r'<a href=\"#\" class=\"\2\">\1</a>', html)
html = re.sub(r'<\%=\s*link_to\s+\w+_path[^,%]*,\s*class:\s*\"([^\"]*)\"[^%]*do\s*\%>', r'<a href=\"#\" class=\"\1\">', html)
html = re.sub(r'<\%=\s*link_to\s+\"([^\"]*)\",\s*\w+_path[^%]*%>', r'<a href=\"#\">\1</a>', html)
# button_to
html = re.sub(r'<\%=\s*button_to\s+[^,%]*,\s*class:\s*\"([^\"]*)\"[^%]*do\s*\%>', r'<button class=\"\1\">', html)
# ERB expressions → static fallbacks
html = re.sub(r'<\%=\s*current_user&\.name\s*\|\|\s*\"([^\"]*)\"\s*\%>', r'\1', html)
html = re.sub(r'<\%=\s*@\w+\s*\|\|\s*(\d+)\s*\%>', r'\1', html)
html = re.sub(r'<\%=\s*@\w+\s*\|\|\s*\"([^\"]*)\"\s*\%>', r'\1', html)
html = re.sub(r'<\%=\s*@\w+&\.\w+&\.\w+\s*\|\|\s*[\'\"]([^\'\"]*)[\'\"]\s*\%>', r'\1', html)
html = re.sub(r'<\%=\s*@\w+&\.\w+\s*\|\|\s*[\'\"]([^\'\"]*)[\'\"]\s*\%>', r'\1', html)
html = re.sub(r'<\%=\s*devise_error_messages!\s*\%>', '', html)
# Clean remaining ERB
html = re.sub(r'<\%\s*end\s*\%>', '', html)
html = re.sub(r'<\%\s*else\s*\%>', '', html)
html = re.sub(r'<%[^%=][^%]*%>', '', html)
html = re.sub(r'<%=[^%]*%>', '', html)

print('$HTML_PREFIX' + html + '$HTML_SUFFIX')
"
}

# Generate HTML
HTML_FILE="/tmp/crm-verify/${VIEW_NAME}.html"
erb_to_html > "$HTML_FILE"

# Take screenshots at multiple breakpoints
for WIDTH in 1440 375; do
  if [ "$WIDTH" = "1440" ]; then
    HEIGHT=900
  else
    HEIGHT=812
  fi
  OUTPUT="${SCREENSHOT_DIR}/${VIEW_NAME}-${WIDTH}.png"
  chromium --headless --disable-gpu --screenshot="$OUTPUT" --window-size=${WIDTH},${HEIGHT} --virtual-time-budget=5000 "$HTML_FILE" 2>/dev/null
  echo "✅ ${VIEW_NAME} @ ${WIDTH}px → $OUTPUT"
done
