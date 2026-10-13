# Gemini TTS voiceover (optional)

## Key handling
- Store the key OUTSIDE the repo in a gitignored file, e.g.
  `/home/deeone/.config/manim-voice/.env` as `GEMINI_API_KEY=...`.
- Read it at runtime; NEVER print or commit it.

## API call (raw PCM returned, NOT wav)
```python
import os, json, base64, urllib.request, wave
KEY = open("/home/deeone/.config/manim-voice/.env").read().split("=",1)[1].strip()
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={KEY}"
body = {"contents":[{"parts":[{"text":NARRATION}]}],
        "generationConfig":{"responseModalities":["AUDIO"],
          "speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":"Kore"}}}}}
req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type":"application/json"})
d = json.load(urllib.request.urlopen(req, timeout=60))
pcm = base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
# Gemini returns RAW PCM 16-bit, 24000Hz, mono -> must wrap in a WAV header
with wave.open(path,"wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
```

## Pitfalls
- Writing raw `pcm` bytes to a `.wav` file makes ffmpeg say "Invalid data found" —
  you MUST wrap with `wave` (WAV header) first.
- **429 Too Many Requests**: Gemini TTS rate-limits hard. Fire calls with a gap
  (e.g. `time.sleep(15)` between), skip already-existing clips, and retry with
  backoff (`time.sleep(20*(attempt+1))`). 6 clips took ~3 min with pacing.
- If no key: skip voice; ship hardsubbed captions only.
