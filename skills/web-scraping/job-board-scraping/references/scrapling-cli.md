# scrapling CLI — job-board scraping reference

## Binary / venv locations (verified on this host)
- Binary: `~/.local/bin/scrapling`
- pipx venv (use its python for playwright installs):
  `~/.local/share/pipx/venvs/scrapling/bin/python`
- First-run requirement: install Chromium once —
  `~/.local/share/pipx/venvs/scrapling/bin/python -m playwright install chromium`

## Command tree
```
scrapling extract fetch      URL OUT.(md|html|txt)   # headless browser (DynamicFetcher)
scrapling extract stealthy-fetch URL OUT             # stealth fingerprint browser
scrapling extract get        URL OUT                 # raw GET (Fetcher.get)
scrapling extract post/put/delete URL OUT
scrapling install            # install all fetcher deps
scrapling shell              # interactive console
scrapling mcp                # MCP server
```

### fetch / stealthy-fetch options (key)
- `--disable-resources` : drop images/CSS for speed (use for job lists)
- `--timeout MS` (default 30000) — set 90000–120000 for slow boards
- `--wait MS` : extra wait after load
- `--no-headless` : show browser
- `--real-chrome` : use installed Chrome instead of bundled
- `-s, --css-selector` : extract only matching elements
- `--proxy "http://user:pass@host:port"`
- `-H "Key: Value"` : extra headers (repeatable) — NOTE: a custom User-Agent did NOT
  defeat RemoteOK's API block; the API returns a legal stub regardless.

## Working WWR parser (Python)
Save fetch output as `.html`, then:

```python
import re, html

with open("/home/deeone/jobs_check/wwr_search.html", encoding="utf-8", errors="replace") as f:
    raw = f.read()

blocks = re.split(r'<li class="[^"]*new-listing-container[^"]*"', raw)
jobs = []
for b in blocks[1:]:
    link_m = re.search(r'href="(/remote-jobs/[^"]+)"', b)
    if not link_m or "/find-your-plan" in link_m.group(1):
        continue
    link = "https://weworkremotely.com" + link_m.group(1)
    comp = re.search(r'href="/company/([^"]+)"', b)
    company = comp.group(1).replace("-", " ").title() if comp else "?"
    title_m = re.search(r'new-listing__header__title[^>]*>(.*?)</h3>', b, re.S)
    title = html.unescape(re.sub(r'<[^>]+>', '', title_m.group(1))).strip() if title_m else ""
    if title:
        jobs.append((title, company, link))

# dedupe + filter false positives (WWR matches loosely on "engineer")
keep_terms = ("data", "analytic", "ml", "machine learning", "pipeline", "etl")
seen, uniq = set(), []
for t, c, l in jobs:
    if l in seen:
        continue
    seen.add(l)
    if any(k in t.lower() for k in keep_terms):
        uniq.append((t, c, l))
```

## Verified board outcomes (2026-08-09)
- RemoteOK `/api?tags=c-data-engineer` → legal stub only (blocked).
- Indeed `/jobs?q=...` → HTTP 403.
- Remotive/Jobicy/Arbeitnow/HN Algolia JSON → raw newlines inside string values
  make `json.loads` fail (`Invalid control character`, `Unterminated string`).
  The `.txt` saved by `get` is NOT valid JSON — parse HTML instead.
- We Work Remotely `/remote-jobs/search?term=<query>` → WORKS, server-rendered.

## gotchas
- Output file MUST be `.md/.html/.txt` — `.json` raises ValueError.
- `write_content_to_file` writes JSON control chars verbatim → corrupts APIs.
- WWR has no `/remote-jobs/data` category; use the search endpoint.
