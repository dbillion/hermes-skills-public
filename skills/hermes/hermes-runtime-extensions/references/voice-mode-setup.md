# Voice Mode Setup (zero-key local STT)

Full recipe for enabling Hermes voice input with **no API keys**, using
faster-whisper (runs locally on CPU). Targets Hermes's own venv.

## 1. Locate Hermes's venv (critical)
```bash
grep -E 'exec ' "$(which hermes)"          # -> ~/.hermes/hermes-agent/venv/bin/hermes
HV=~/.hermes/hermes-agent/venv
```
Everything below uses `"$HV/bin/python"` — never plain `python3`.

## 2. Install Python deps into that venv
```bash
"$HV/bin/python" -m pip install faster-whisper sounddevice numpy
# or: uv pip install --python "$HV/bin/python" faster-whisper faster-whisper[sounddevice] sounddevice numpy
```

## 3. System deps (mic + audio conversion)
- `portaudio` (mic input): `sudo apt install portaudio19-dev` (Ubuntu) / `brew install portaudio` (macOS)
- `ffmpeg` (format conversion): `sudo apt install ffmpeg` / `brew install ffmpeg`
Check:
```bash
"$HV/bin/python" -c "import sounddevice; print(len(sounddevice.query_devices()), 'devices')"
command -v ffmpeg
```

## 4. Config (already default on most installs)
Hermes STT defaults to local when faster-whisper is present:
```yaml
stt:
  enabled: true
  provider: local
  local:
    model: small      # base/small/medium; base ~150 MB downloads on first use
```
Set via `hermes config set stt.provider local` if absent.

## 5. Prove the model loads (downloads base on first call)
```bash
"$HV/bin/python" -c "import faster_whisper; faster_whisper.WhisperModel('base', device='cpu', compute_type='int8'); print('LOADED')"
```

## 6. Use it
Press **Ctrl+B** in the Hermes CLI to record; silence auto-ends the recording and
Hermes transcribes locally. No key, no cloud.

## Pitfall recap
- Installing into default `~/.venv` or system python = Hermes still can't import it.
- `python3 -c "import faster_whisper"` passing means nothing — verify in `"$HV/bin/python"`.
- If mic is silent, portaudio is missing (step 3).
