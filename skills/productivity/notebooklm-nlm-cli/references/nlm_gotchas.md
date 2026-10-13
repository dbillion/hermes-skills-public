# nlm CLI — verified gotchas (from a real 83-source upload session)

## Exact error strings seen
1. `--file` upload (remote MCP can't read local disk):
   `Error: Could not add file source: API error (code 3): INVALID_ARGUMENT`
   `Hint: File paths must be accessible on the machine running nlm or the MCP server. Received path: /home/...`
   → Fix: use `--text "$(cat file.md)"`.

2. `--text` over the size cap (~50KB):
   `Error: Could not add text source.` (no 429, no detail, exit code 0 from CLI but no source added)
   → Fix: split into ~10KB chunks.

3. Transient backend failure (intermittent, no 429):
   `Could not add text source.` on a 7KB chunk that succeeded on retry.
   → Fix: retry once after 2-3s.

4. Wrong/unauthenticated profile:
   `Error: Profile 'dayo4ai' not found. Run 'nlm login' first.`
   → Only `oludayo35` (default) is authenticated. Use it for all writes.

## Split recipe (large doc → chunks)
```python
import re, os, glob
text = open("big.md").read()
parts = re.split(r'(?=^## Judges \d+)', text, flags=re.M)  # per-chapter
chunks = [p.strip() for p in parts if p.strip()]
os.makedirs("/tmp/chunks", exist_ok=True)
for c in chunks:
    n = re.match(r'## Judges (\d+)', c).group(1)
    open(f"/tmp/chunks/ch{n}.md","w").write(c)   # each 3-9KB, well under cap
```
Then `nlm source add <NBID> --text "$(cat /tmp/chunks/chN.md)" --title "Judges N WEB"`.

## Resumable bulk uploader shape
Keep `done.txt` (one id per line). Loop over ids; skip done; on success append;
on transient fail retry once; on 429 sleep 20s. Pace `time.sleep(1.2)` between calls.

## reportlab location
`/usr/bin/python3` has reportlab 5.0.0; Hermes venv (`/home/deeone/.hermes/hermes-agent/venv/bin/python3`)
does NOT. When shelling out to a reportlab generator, hardcode the interpreter path.
