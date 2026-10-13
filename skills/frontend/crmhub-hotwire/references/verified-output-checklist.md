# Verified Output Checklist — Stitch → Rails ERB Conversion

## Before Declaring a Page "Done"

### 1. Section Count Match
```bash
# Run on the Stitch source
grep -c '<section\|<nav\|<footer\|<header' /path/to/stitch.html

# Run on the Rails ERB output
grep -c '<section\|<nav\|<footer\|<header' app/views/path/to/view.html.erb
```
**Numbers must match.** If the Stitch HTML has 8 sections and your ERB has 5, you omitted 3.

### 2. Image Count Match
```bash
grep -c '<img' /path/to/stitch.html
grep -c '<img' app/views/path/to/view.html.erb
```
**Must be equal.** If the Stitch HTML has 4 `<img>` tags and your view has 0, you failed fidelity.

### 3. Image URL Integrity
```bash
# Extract all image URLs from Stitch
grep -oP 'src="[^"]*"' /path/to/stitch.html | sort

# Extract all image URLs from ERB
grep -oP 'src="[^"]*"' app/views/path/to/view.html.erb | sort
```
**Every URL in the Stitch HTML must appear in the ERB.** No exceptions — these are intentional design assets (lh3.googleusercontent.com and picsum.photos).

### 4. Class Token Mapped
```bash
# Check for Stitch Material Design tokens that should have been mapped
grep -rn 'pure-surface\|whisper-border\|on-surface\|surface-container' app/views/path/
grep -rn 'material-symbols-outlined' app/views/path/
grep -rn 'font-page-title\|font-section-heading\|font-card-title' app/views/path/
```
**No Stitch-native tokens should remain.** All should be mapped to our design system.

### 5. Layout Structure
- Public pages (landing, auth): NO sidebar render. Use `<nav>` for header navigation.
- Authenticated pages: MUST start with `<%= render "application/sidebar" %>`.
- No double sidebar (layout + view both rendering it).

### 6. HTTP Status Check (Post-Server Restart)
```bash
# Public pages should return 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/users/sign_in

# Authenticated pages should return 302 (redirect to sign-in) when not logged in
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/dashboard

# After login (cookie jar), should return 200
curl -s -b /tmp/cookies.txt -o /dev/null -w "%{http_code}" http://localhost:3000/dashboard
```

### 7. Screenshot Verification (via lightpanda)
```python
# From execute_code
from hermes_tools import mcp_lightpanda_goto, mcp_lightpanda_markdown
mcp_lightpanda_goto("http://localhost:3000/page")
result = mcp_lightpanda_markdown()
print(result["result"])

# For authenticated pages, login first via mcp_lightpanda_evaluate:
from hermes_tools import mcp_lightpanda_evaluate
mcp_lightpanda_evaluate("""
  document.querySelector('input[type="email"]').value = "owner@glowhair.com";
  document.querySelector('input[type="password"]').value = "password123";
  document.querySelector('input[type="submit"]').click();
""")
```
