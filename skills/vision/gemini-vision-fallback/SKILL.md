---
name: gemini-vision-fallback
description: "Vision fallback: Gemini REST API if vision_analyze blocked."
version: 1.0.0
author: curator
license: MIT
platforms: [linux, macos, windows]
---

# Gemini Vision Fallback

When the native `vision_analyze` tool fails to read an image — specifically a `404` on
`file://` local paths (the vision backend cannot reach the filesystem) or `429 Too Many
Requests` on the default vision backend (throttled) — route image understanding through
**Google Gemini's `generateContent` REST API**. Gemini has its own quota and is not subject
to the native backend's 429.

## When to use
- You must describe/analyze a local image (PNG/JPG) and `vision_analyze` returns 404 or 429.
- A Gemini API key is available. Common locations: `~/.gemini/settings.json` →
  `security.auth.apiKey`, or any `GEMINI_API_KEY` / Google AI Studio key.

## Method
POST `https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}`
with a JSON body containing the image as base64 `inline_data`.

## Model fallback chain (observed on a shared key)
- `gemini-flash-latest` → works for vision (aliases a currently-serving model). Try this first.
- `gemini-2.5-flash` → `404` "no longer available to new users" for some keys.
- `gemini-2.0-flash` → `429` quota exceeded on free/shared tier.

To list models a key can use:
`GET https://generativelanguage.googleapis.com/v1beta/models?key={KEY}` and keep those whose
`supportedGenerationMethods` includes `generateContent`.

## Rules
- Never print the API key to chat. Load it from the config file inside a script; only emit the description.
- Keep image read + base64 inside the script; do not `cat` secrets into the shell.
- Vision ONLY (describe). For image *generation* use the comfyui / image-gen skills.

## Ready-to-run script
```python
#!/usr/bin/env python3
import json, base64, sys, urllib.request, urllib.error

KEY_FILE = "/home/deeone/.gemini/settings.json"   # override if your key lives elsewhere
IMG = "/home/deeone/Desktop/obsidian/owl.png"      # set per call
PROMPT = "Describe this image in fine detail for an illustrator who must reproduce it exactly."

with open(KEY_FILE) as f:
    KEY = json.load(f)["security"]["auth"]["apiKey"]
with open(IMG, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

MODELS = ["gemini-flash-latest", "gemini-2.5-flash", "gemini-2.0-flash"]
for model in MODELS:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={KEY}"
    body = json.dumps({"contents": [{"parts": [
        {"text": PROMPT},
        {"inline_data": {"mime_type": "image/png", "data": b64}},
    ]}]}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read().decode())
        parts = resp.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)
        if text.strip():
            print(f"[model: {model}]\n{text}"); sys.exit(0)
        print(f"{model}: EMPTY", file=sys.stderr)
    except urllib.error.HTTPError as e:
        print(f"{model}: HTTP {e.code} {e.read().decode()[:200]}", file=sys.stderr)
    except Exception as e:
        print(f"{model}: {type(e).__name__} {e}", file=sys.stderr)
print("ALL_MODELS_FAILED", file=sys.stderr); sys.exit(1)
```
