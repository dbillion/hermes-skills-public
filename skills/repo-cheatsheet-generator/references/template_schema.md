# cheatsheet.json schema

`generate_cheatsheet.py` reads one JSON file. All fields are required except
`resolution_order`, which is optional.

```json
{
  "title": "requests",
  "tagline": "Python HTTP library for humans",
  "overview_bullets": [
    "Wraps urllib3 to make HTTP calls read like plain Python.",
    "Handles sessions, redirects, cookies, and JSON encoding for you.",
    "One function per HTTP verb: get, post, put, delete, etc."
  ],
  "analogy": "Think of it like a phone: you dial a number (URL) and say what you want (verb), and it hands back whatever the other side says.",
  "components": [
    {"name": "Session", "purpose": "Persist cookies/headers across calls", "example": "s = requests.Session()"},
    {"name": "Response", "purpose": "Holds status, headers, body", "example": "r.status_code, r.json()"},
    {"name": "adapters", "purpose": "Control retries/connection pooling", "example": "HTTPAdapter(max_retries=3)"}
  ],
  "examples": [
    {"label": "GET request", "code": "import requests\nr = requests.get('https://api.github.com')\nprint(r.status_code)"},
    {"label": "POST with JSON", "code": "r = requests.post(url, json={'a': 1})"},
    {"label": "Custom headers", "code": "r = requests.get(url, headers={'Authorization': 'Bearer TOKEN'})"}
  ],
  "conventions": [
    {"pattern": "Import alias", "example": "import requests as req  (rare — usually unaliased)"},
    {"pattern": "Session reuse", "example": "with requests.Session() as s: ..."}
  ],
  "setup_code": "pip install requests",
  "resolution_order": [
    "Explicit function args (headers=, params=)",
    "Session-level defaults",
    "Environment variables (e.g. proxies)"
  ],
  "best_practices": [
    "Always set a timeout= — requests never times out by default.",
    "Reuse a Session for multiple calls to the same host.",
    "Check r.raise_for_status() instead of manually checking status codes."
  ],
  "common_errors": [
    {"error": "ConnectionError", "cause": "No network / wrong host", "fix": "Check URL and network access"},
    {"error": "Hangs forever", "cause": "No timeout set", "fix": "Pass timeout=5"},
    {"error": "JSONDecodeError", "cause": "Response body isn't JSON", "fix": "Check r.text before calling r.json()"}
  ],
  "quick_revision": [
    "requests.get/post/put/delete for HTTP verbs",
    "r.status_code, r.json(), r.text on the response",
    "Use Session() to persist cookies/headers",
    "Always set timeout=",
    "raise_for_status() to fail fast on errors"
  ]
}
```

## Field notes

- `components`, `examples`, `conventions`, `common_errors` are arrays of
  objects with the exact keys shown above.
- `examples[].code` uses `\n` for line breaks within one snippet; keep each
  snippet to 2-6 lines.
- `resolution_order` — omit entirely (don't include the key) if not
  relevant to this repo/library.
- Keep every string short — this is a cheat sheet. If a bullet needs more
  than ~12 words, it belongs in documentation, not here.
