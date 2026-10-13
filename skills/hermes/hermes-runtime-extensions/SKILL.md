---
name: hermes-runtime-extensions
description: "Install Python deps Hermes loads (voice, plugins)."
version: 1.0.0
author: Hermes Agent (captured from a voice-mode setup session)
tags: [hermes, voice, faster-whisper, venv, python, setup, plugins]
related_skills: [hermes-config-safe-edit, reproducible-agent-setup]
---

# Hermes Runtime Extensions (install Python deps that Hermes actually loads)

## The core gotcha
`which hermes` points at `/home/deeone/.local/bin/hermes`, but that file is a **bash launcher**:
```
unset PYTHONPATH
unset PYTHONHOME
exec "/home/deeone/.hermes/hermes-agent/venv/bin/hermes" "$@"
```
So Hermes runs from **`~/.hermes/hermes-agent/venv`**, NOT the default `uv` venv
(`~/.venv`) and NOT system `python3`. Installing a package anywhere else makes
`import X` succeed in your verify step but fail inside Hermes.

## Verify which venv Hermes uses (do this BEFORE installing)
```bash
grep -E 'exec ' "$(which hermes)"        # reveals the real venv path
HV=~/.hermes/hermes-agent/venv
"$HV/bin/python" -c "import faster_whisper; print('present')"   # the ONLY check that matters
```
Never trust `uv pip install X && python3 -c "import X"` as proof — that tests the
wrong interpreter.

## Install into the Hermes venv
```bash
HV=~/.hermes/hermes-agent/venv
"$HV/bin/python" -m pip install faster-whisper sounddevice numpy
# verify in the SAME venv:
"$HV/bin/python" -c "import faster_whisper, sounddevice, numpy; print('OK', faster_whisper.__version__)"
```
If `pip` is blocked by PEP 668 in that venv, prefer `uv pip install --python "$HV/bin/python" X`.

## Voice mode (zero-key STT) — full recipe
See `references/voice-mode-setup.md`. Summary:
1. Install `faster-whisper` + `sounddevice` + `numpy` into the Hermes venv (above).
2. System deps: `portaudio` (mic input) + `ffmpeg` (audio conversion) must be present.
   Check: `"$HV/bin/python" -c "import sounddevice; sounddevice.query_devices()"` and `command -v ffmpeg`.
3. Config: `stt.provider: local` + `stt.local.model: <size>` already works with NO key.
   If absent, set via `hermes config set stt.provider local` (nested blocks → see hermes-config-safe-edit).
4. Prove it loads: `"$HV/bin/python" -c "import faster_whisper; faster_whisper.WhisperModel('base', device='cpu')"`
   — downloads the ~150 MB base model on first call.
5. Ctrl+B in the Hermes CLI to talk; silence auto-detects end of speech.

## Pitfalls
- **Wrong venv** — the #1 mistake. `uv pip install` with no `--python` targets `~/.venv` (NOT Hermes).
  Always pin `--python "$HV/bin/python"` or call `"$HV/bin/python" -m pip`.
- **`python3 -c "import X"` lies** — it uses system python. Always verify with the Hermes venv python.
- **`pip --user` unsupported** — if you hit "pip's --user is unsupported (use a virtual environment instead)",
  install into the target venv directly (no `--user`).
- **portaudio missing** → mic is silent. Install `portaudio19-dev` (Ubuntu) / `portaudio` (brew) + ffmpeg.
- **User pref**: prefer `uv` over `pip` for speed, but MUST target the Hermes venv python explicitly.

## Overlap
Complements `hermes-config-safe-edit` (config changes) and `reproducible-agent-setup`
(capture/reinstall — its `bootstrap.sh` should install voice/plugin deps into this same venv).
