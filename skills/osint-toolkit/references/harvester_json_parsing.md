# Harvesting Emails – JSON Parsing Notes

When using `theHarvester -f -` (JSON output), the tool prints a banner and summary lines before the actual JSON object. The JSON is the **last line** that starts with `{` and ends with `}`.

**Problem**: Early versions of the skill attempted to `json.loads()` the full stdout, causing `JSONDecodeError`.

**Fix**: Extract the JSON line before parsing:

```python
output = proc.stdout
json_str = None
for line in reversed(output.splitlines()):
    line = line.strip()
    if line.startswith('{') and line.endswith('}'):
        json_str = line
        break
if not json_str:
    json_str = output.strip()  # fallback if no banner
data = json.loads(json_str)
```

**Dependencies**: TheHarvester may require additional Python packages not listed in its repo (e.g., `ujson`, `cffi`, `greenlet`, `playwright`, `uvloop`). Install them in the virtual environment before running:

```
uv pip install ujson cffi greenlet playwright uvloop
```

**Testing**: Run with a known domain and a source that works without API key (e.g., `duckduckgo`) to verify JSON output:

```
theHarvester -d example.com -b duckduckgo -l 5 -f -
```