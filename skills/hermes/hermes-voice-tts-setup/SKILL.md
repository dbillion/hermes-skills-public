---
name: hermes-voice-tts-setup
description: Install, verify, and switch Hermes TTS & voice providers.
version: 1
author: hermes-session
license: MIT
metadata:
  hermes:
    tags: [hermes, voice, tts, stt, edge, neutts, piper, cli, discord, telegram]
    related_skills: [hermes-agent]
---

# Hermes Voice / TTS Setup

## When to Use
Use this skill when the user wants to enable voice mode, check whether a TTS/STT
provider is installed/available, switch the active TTS provider, set up
local/offline TTS (NeuTTS/Piper), or debug voice replies on CLI, TUI, Discord,
or Telegram. Also use it to correct the common "Edge is local" / "provider is
per-platform" misconceptions.

## Trigger
User wants to: enable voice mode, check whether a TTS/STT provider is available,
switch the active TTS provider, set up local/offline TTS, or debug voice replies
(CLI, TUI, Discord, Telegram).

## Correct these common misconceptions (state them plainly if the user is wrong)
- **`tts.provider` is GLOBAL** — it applies to CLI, TUI, Discord, Telegram alike.
  There is NO per-platform TTS override. If "Discord is using gemini", the whole
  agent is — there is no Discord-specific routing. Switching `tts.provider` changes
  every surface at once.
- **Edge TTS is FREE but CLOUD.** It opens a websocket to Microsoft's servers and
  needs internet. It is NOT local. The thing that is "local and free" is
  faster-whisper (STT / listening), NOT Edge.
- **NeuTTS and Piper are the genuinely LOCAL/OFFLINE TTS options.** Edge and Gemini
  are cloud.
- **STT ≠ TTS.** Listening (`voice.provider: local` → faster-whisper, Groq fallback)
  is a separate config block from speaking (`tts.provider`). A working local STT does
  not imply local TTS.

## Check current state (read-only)
```
hermes config get tts.provider            # active TTS provider
hermes config get voice.provider          # STT provider (local/groq/openai)
grep -E "^GROQ_API_KEY=" ~/.hermes/.env   # STT cloud key (if present)
~/.hermes/hermes-agent/venv/bin/python -c "import edge_tts; print(edge_tts.__version__)"
~/.hermes/hermes-agent/venv/bin/python -c "import faster_whisper; print(faster_whisper.__version__)"
~/.hermes/hermes-agent/venv/bin/python -c "import neutts, llama_cpp; print('neutts+llama_cpp OK')"
```
All Hermes Python deps live in `~/.hermes/hermes-agent/venv`. Install with
`uv pip install --python ~/.hermes/hermes-agent/venv/bin/python <pkg>` — NEVER plain
`uv pip install` (that targets `~/.venv`, the wrong env).

## Switch active provider
```
hermes config set tts.provider edge      # or: neutts | piper | gemini | elevenlabs
```
No restart needed; the agent reads config per turn.

## Install local NeutTTS (the offline TTS option)
CRITICAL: the base `neutts` package does NOT include `llama-cpp-python`, but EVERY
neutts model is a GGUF file that requires `llama_cpp` at runtime. Install both:
```
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python neutts
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python "llama-cpp-python==0.3.34"
```
- `neutts` base pulls torch 2.13 + transformers (~2GB of wheels; installs fast once
  resolved).
- `llama-cpp-python` often has NO prebuilt wheel for this combo → builds from source.
  On a normal machine this takes ~30 MIN of CPU compile. Run it in the BACKGROUND
  with `notify_on_complete=true`; never foreground (the 600s cap kills it and it
  looks like a hang). See references/neutts-local-install.md for the full recipe and
  the stall-vs-real-compile checks.

## Verify NeutTTS end-to-end — do NOT use the raw API
The Python `NeuTTS.infer()` API requires `ref_codes` + `ref_text` (voice-clone style)
and is easy to misuse. Hermes ships a wrapper that supplies the bundled reference
voice — use it:
```
~/.hermes/hermes-agent/venv/bin/python ~/.hermes/hermes-agent/tools/neutts_synth.py \
  --text "test" --out /tmp/neutts_test.wav \
  --ref-audio ~/.hermes/hermes-agent/tools/neutts_samples/jo.wav \
  --ref-text  ~/.hermes/hermes-agent/tools/neutts_samples/jo.txt \
  --model neuphonic/neutts-air-q4-gguf --device cpu
```
First run loads the model (~60–90s) then synthesizes. Confirm real audio:
`soundfile` read, peak amplitude > 0.001. Default config model is
`neuphonic/neutts-air-q4-gguf`; the lighter `neuphonic/neutts-nano` also works.
Slow on CPU but fully offline.

## Verify Edge
```
~/.hermes/hermes-agent/venv/bin/python -c "import asyncio, edge_tts; \
  asyncio.run(edge_tts.Communicate('hi','en-US-AriaNeural').stream().__anext__())"
```
Or simply confirm `edge_tts` imports and `tts.edge.voice` is set (default
`en-US-AriaNeural`). Streaming a few chunks = working.

## Pitfalls
- Don't call a provider "local" unless it's NeutTTS or Piper. Edge and Gemini are cloud.
- Don't run 30-min source builds in foreground — they hit the 600s timeout and masquerade
  as a hang. Use background + notify.
- Don't use plain `uv pip install` — wrong venv.
- Don't hand-edit `~/.hermes/config.yaml` — it's guarded; use `hermes config set <key>`.
- Don't fight the raw `NeuTTS.infer()` API for verification; use the bundled
  `neutts_synth.py` with the `jo.wav`/`jo.txt` reference.
