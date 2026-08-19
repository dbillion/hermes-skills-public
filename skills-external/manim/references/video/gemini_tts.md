# Gemini TTS for Manim voiceover

Generate spoken narration for Manim videos via Gemini's TTS API. Works when a
`GEMINI_API_KEY` is available (store gitignored at `~/.config/manim-voice/.env`,
NEVER in a repo). Skipped mid-session by user request; technique retained.

## Endpoint
```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key=KEY
{
  "contents":[{"parts":[{"text":"<narration>"}]}],
  "generationConfig":{
    "responseModalities":["AUDIO"],
    "speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":"Kore"}}}
  }
}
```
Response: `candidates[0].content.parts[0].inlineData.data` = base64 **raw PCM**
(16-bit, 24000Hz, mono). Gemini does NOT return a WAV container.

## CRITICAL: wrap raw PCM in a WAV header
Writing the base64 bytes straight to `*.wav` makes ffmpeg reject it
("Invalid data found"). Use the `wave` module:
```python
import wave, base64
pcm = base64.b64decode(b64)
with wave.open(path, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
    w.writeframes(pcm)
```

## Rate limiting (HTTP 429)
Gemini TTS is strict. Firing N calls back-to-back 429s. Pace requests:
- `time.sleep(15)` between calls.
- On 429, exponential backoff (`time.sleep(20*(attempt+1))`, retry up to 5x).
- Skip clips that already exist (`if os.path.getsize(p) > 1000: continue`) so a
  resumed run doesn't re-hit the limit on finished clips.

## Pipeline
1. Extract per-scene narration from plan.md (exact text, in video order).
2. TTS each -> `voiceover_clips/Sn.wav` (proper WAV header).
3. Normalize: `ffmpeg -i Sn.wav -ar 24000 -ac 1 -c:a pcm_s16le Sn_n.wav`.
4. Concat: `ffmpeg -f concat -safe 0 -i list.txt -c copy voiceover_full.wav`.
5. Mux onto video: `ffmpeg -i final.mp4 -i voiceover_full.wav -c:v copy -c:a aac out.mp4`.

## Groq fallback (was DEAD this session)
`GROQ_API_KEY_1` in env returned 403 even for chat — invalid/expired. Groq TTS
(playai-tts) is an alternative if a valid key appears. No GEMINI_API_KEY /
ElevenLabs / OpenAI key was present.
