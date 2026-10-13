# Board Playbook — ready-to-run snippets

## 1. We Work Remotely (most reliable)

Fetch:
```bash
scrapling extract fetch \
  "https://weworkremotely.com/remote-jobs/search?term=data%20engineer" \
  wwr.html --disable-resources --timeout 120000
```

Extract (Python):
```python
import re, html
raw = open("wwr.html", encoding="utf-8", errors="replace").read()
blocks = re.split(r'<li class="[^"]*base-search-card', raw)
jobs = []
for b in blocks[1:]:
    link_m = re.search(r'href="(/remote-jobs/[^"]+)"', b)
    if not link_m or "/find-your-plan" in link_m.group(1):
        continue
    comp = re.search(r'href="/company/([^"]+)"', b)
    company = comp.group(1).replace("-", " ").title() if comp else "?"
    tm = re.search(r'base-search-card__title[^>]*>(.*?)</h3>', b, re.S)
    title = html.unescape(re.sub(r'<[^>]+>', '', tm.group(1))).strip() if tm else ""
    if title:
        jobs.append((title, company, "https://weworkremotely.com" + link_m.group(1)))
```

## 2. LinkedIn (auth-cookie reuse)

Build cookie from MCP profile, then fetch:
```bash
COOKIE=$(python3 -c "import json;[print(f\"{c['name']}={c['value']}\",end='; ') for c in json.load(open('/home/deeone/.linkedin-mcp/cookies.json'))]")
scrapling extract stealthy-fetch \
  "https://www.linkedin.com/jobs/search/?keywords=data%20engineer&f_AL=true" \
  li.html --real-chrome --disable-resources --timeout 120000 -H "Cookie: $COOKIE"
```

### Remote-friendly variant — add `f_WT=2` (LinkedIn "Remote" work mode)
```bash
scrapling extract stealthy-fetch \
  "https://www.linkedin.com/jobs/search/?keywords=data%20engineer&f_WT=2" \
  li_remote.html --real-chrome --disable-resources --timeout 120000 -H "Cookie: $COOKIE"
```
NOTE: `f_WT=2` = LinkedIn's "Remote" filter, but listings still show a home-base city
(e.g. "New York, NY") because LinkedIn tags a region, not fully-distributed. For
truly-distributed roles, also grep titles/locations or cross-check a remote job board.
Pagination: append `&start=N` (N = 25, 50, 75, ...) for more pages.

Extract (Python) — per-job URL lives in the title anchor:
```python
import re, html
raw = open("li.html", encoding="utf-8", errors="replace").read()
positions = [m.start() for m in re.finditer(r'base-search-card__title', raw)]
jobs = []
for p in positions:
    b = raw[raw.rfind('<li', 0, p): p+700]
    am = re.search(r'<a[^>]*href="([^"]+)"[^>]*>.*?base-search-card__title', b, re.S)
    url = html.unescape(am.group(1)) if am else "https://www.linkedin.com/jobs/search/?keywords=data+engineer"
    tm = re.search(r'base-search-card__title"[^>]*>\s*(.*?)\s*</h3>', b, re.S)
    title = html.unescape(re.sub(r'<[^>]+>', '', tm.group(1))).strip() if tm else None
    if not title:
        continue
    cm = re.search(r'base-search-card__subtitle"[^>]*>\s*(.*?)\s*</h4>', b, re.S)
    company = html.unescape(re.sub(r'<[^>]+>', '', cm.group(1))).strip() if cm else "?"
    lm = re.search(r'base-search-card__metadata[^>]*>\s*(.*?)\s*</span>', b, re.S)
    location = html.unescape(re.sub(r'<[^>]+>', '', lm.group(1))).strip() if lm else "?"
    jobs.append((title, company, location, url))
```

## 3. JSON-API repair (Remotive/Jobicy/Arbeitnow/HN when truncation occurs)
```python
import re, json
raw = open("api.txt", encoding="utf-8", errors="replace").read()
cleaned = re.sub(r'[\x00-\x1f\x7f]', ' ', raw)
try:
    data = json.loads(cleaned)
except json.JSONDecodeError as e:
    print("still broken:", e)   # often truncated mid-string -> use HTML board instead
```

## Boards that do NOT work (skip)
- Indeed: 403 bot wall.
- RemoteOK API: blocks non-browser UAs (returns legal stub only); HTML is JS-rendered.
- Remotive/Jobicy/Arbeitnow/HN: JSON has embedded raw newlines + scrapling truncates -> unreliable.
