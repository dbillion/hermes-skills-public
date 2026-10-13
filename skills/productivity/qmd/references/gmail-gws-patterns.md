# GWS Gmail — Operational Notes

## Pagination Pattern

`gws gmail users messages list` returns a single JSON object (not NDJSON) with `nextPageToken`. The `--page-all` flag times out on large result sets (200+ results). Use manual pagination instead:

```python
import subprocess, json, re, time

def list_all_ids(query, max_results=100):
    ids = []
    page_token = None
    while True:
        params = {"userId": "me", "q": query, "maxResults": max_results}
        if page_token:
            params["pageToken"] = page_token
        result = subprocess.run(
            ["gws", "gmail", "users", "messages", "list",
             "--params", json.dumps(params)],
            capture_output=True, text=True, timeout=60
        )
        # Parse JSON — skip non-JSON lines like "Using keyring backend: keyring"
        match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
        if not match:
            break
        data = json.loads(match.group())
        ids.extend(m["id"] for m in data.get("messages", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.3)  # Rate limit between pages
    return ids
```

**Important:** The output includes non-JSON preamble lines (e.g., "Using keyring backend: keyring"). Always use regex extraction (`re.search(r'\{.*\}', output, re.DOTALL)`) rather than parsing the entire output as JSON.

## Batch Trashing

`gws` does not support batch trash. Trash messages one at a time with proper error handling:

```python
def trash_single(msg_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["gws", "gmail", "users", "messages", "trash",
                 "--params", json.dumps({"userId": "me", "id": msg_id})],
                capture_output=True, text=True, timeout=60  # 60s, not 15s
            )
            if result.returncode == 0:
                return True
            # 404 = already trashed, that's fine
            if "404" in result.stderr or "notFound" in result.stderr:
                return True
        except subprocess.TimeoutExpired:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return False
    return False
```

**Key settings:**
- **Timeout: 60 seconds** (not 15) — gws trash operations can be slow under load
- **Retry: 3 attempts** with exponential backoff (1s, 2s, 4s)
- **Rate limit: 0.1s** between requests (~10 req/sec)
- **Progress save:** Save trashed IDs to a JSON file every 100 operations for crash recovery

## Query Syntax

Gmail search operators that work with `gws`:
- `category:promotions` — promotional emails
- `category:social` — social media
- `category:updates` — updates/notifications
- `newer_than:90d` — time-based (omit for all time)
- `-invoice` — exclusion
- `(a OR b) -c` — boolean combinations

**Note:** `resultSizeEstimate` is capped at 201 by the Gmail API. Actual counts can be much higher. Always paginate through all results using `nextPageToken`.

## Rate Limits

- List: ~5 req/sec
- Trash: ~6 req/sec sustained, but can slow down under heavy load
- Add 0.15s delay between trash operations to avoid 429 errors
- For large batch operations (1000+), use 0.1s delays and 60s timeouts

## Resumable Progress Pattern

For large batch operations (10,000+ emails), crashes are inevitable. Implement resumable progress:

```python
PROGRESS_FILE = "/tmp/gmail-cleanup-progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"trashed_ids": [], "completed_categories": []}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

# In trash_batch, skip already-trashed IDs:
already_trashed = set(progress.get("trashed_ids", []))
for msg_id in ids:
    if msg_id in already_trashed:
        continue
    # ... trash and track
    progress["trashed_ids"].append(msg_id)
    if count % 100 == 0:
        save_progress(progress)
```

**Key:** Save progress every 100 operations. On crash, the script resumes from where it left off. Already-trashed IDs return 404 from the API — treat these as success.
