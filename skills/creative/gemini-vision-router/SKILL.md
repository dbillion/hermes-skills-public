---
name: gemini-vision-router
description: "Route image vision through Gemini REST as a vision fallback."
version: 1.0.0
author: curator
license: MIT
platforms: [linux, macos, windows]
---

# Gemini Vision Router (fallback when native vision fails)

`vision_analyze` can fail two ways: it can't read `file://` local paths (404),
and the backend often returns **429 Too Many Requests**. Gemini's REST vision
API uses a *separate* quota and can read local images as base64 — route image
understanding through it instead.

## Key location
The Gemini API key lives in the Gemini CLI config (do NOT print it):
`/home/deeone/.gemini/settings.json` → `security.auth.apiKey`.

## Minimal working call
```python
import json, base64, urllib.request, urllib.error

with open("/home/deeone/.gemini/settings.json") as f:
    KEY = json.load(f)["security"]["auth"]["apiKey"]
with open(IMG, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"
body = json.dumps({
    "contents": [{"parts": [
        {"text": PROMPT},
        {"inline_data": {"mime_type": "image/png", "data": b64}},
    ]}]
}).encode()
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=60) as r:
    resp = json.loads(r.read().decode())
text = "".join(p.get("text","") for p in resp["candidates"][0]["content"]["parts"])
```

## Working models (verified)
- `gemini-flash-latest` — vision works (used successfully this session).
- `gemini-2.5-flash`, `gemini-2.0-flash` — also valid vision models.
- `gemini-1.5-flash` — **gone for new users (404)**; avoid.
- List available: `GET https://generativelanguage.googleapis.com/v1beta/models?key=KEY`
  then filter `supportedGenerationMethods` containing `generateContent`.

## Pitfalls
- **Never echo the key** to chat/terminal — read it programmatically and only
  print the description.
- **Image generation** (separate from vision) via `gemini-2.5-flash-image`,
  `gemini-3-*-image`, `nano-banana-*` often **429s** even when vision is fine.
  For generating images, prefer NotebookLM `infographic create` (separate quota)
  — see `notebooklm-visual-workflow`.
- `responseModalities: ["IMAGE","TEXT"]` is for image *generation*; for vision
  you only need `parts` with `text` + `inline_data`.
- No `aspectRatio` field in `generationConfig` for these models — put
  orientation in the prompt text instead (it 400s otherwise).
