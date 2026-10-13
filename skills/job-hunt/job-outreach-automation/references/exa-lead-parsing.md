# Exa web_search_exa output format + parsing recipe

## Output shape
`exa web_search_exa` returns JSON: `{ "content": [ { "type": "text", "text": "..." } ] }`.
The `text` block repeats entries, each with lines like:
```
Title: <job title>
URL: https://...
Published: N/A
Author: N/A
Highlights:
<title again>
...
# <title>
<company name>
## Role overview
...
```
There is usually ONE big text blob (not blank-line-separated blocks), so splitting on
`\n\n` misses most entries. **Split on `Title:` boundaries instead.**

## Parsing recipe (Python)
```python
import re, json
data = json.loads(out.stdout)
text = " ".join(b.get("text","") for b in data.get("content",[]) if isinstance(b,dict))
parts = re.split(r"(?i)\n\s*Title:\s*", text)
for p in parts[1:]:
    title = p.strip().splitlines()[0].strip()
    url_m = re.search(r"(?i)URL:\s*(\S+)", p) or re.search(r"https?://\S+", p)
    if not url_m: continue
    link = url_m.group(1).rstrip(")")
    # company: "at X" then stop at | @ or whitespace+hyphen or end
    m = re.search(r"\bat\s+([A-Za-z0-9&.]+(?:\s+[A-Za-z0-9&.]+)*?)(?:\s*[|\-–]|@|$)", title)
    company = m.group(1).strip() if m else ""
    if not company:
        m2 = re.search(r"^([A-Za-z0-9&.]+(?:\s+[A-Za-z0-9&.]+)*?)\s*[|–-]\s", title)
        company = m2.group(1).strip() if m2 else ""
    # dedup by link, keep first 8
```
This correctly yields: Cresta, 3Pillar, AutoDesk, Infios (from "X |"), Meld, Alphasense.

## Note
Exa free tier via mcp-cli works. The job text rarely contains a real email; company
domains are often job boards. That is why contact-finding must reject aggregator domains
and fall back to `needs_contact`.
