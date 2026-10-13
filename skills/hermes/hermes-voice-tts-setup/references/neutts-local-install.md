# NeutTTS Local Install — Full Recipe & Stall Detection

## Confirmed-working recipe (this machine, Python 3.11.15 x86_64, Hermes venv)
```
VENV=~/.hermes/hermes-agent/venv
uv pip install --python $VENV/bin/python neutts
uv pip install --python $VENV/bin/python "llama-cpp-python==0.3.34"
```
- `neutts` base (no `[all]` extra) installed in ~1s after resolution; pulls
  torch 2.13.0, transformers 5.1.0, triton 3.7.1 (no llama-cpp-python).
- `llama-cpp-python==0.3.34` built from source in **~30 minutes** of CPU compile
  (no prebuilt cp311 wheel was selected). Output: `Built llama-cpp-python==0.3.34`.

## Stall vs. real compile — how to tell apart
A genuine llama-cpp-python build is CPU-bound. If it is NOT compiling, it is hung
(most often a stalled network fetch of the llama.cpp source during configure).

Signs it is REAL (keep waiting):
- `find /tmp/tmp*/build -name "*.o" -newermt "-30 seconds" | wc -l` returns >0
- `.so` files appear under `/tmp/tmp*/build/bin/` (libllama.so, libggml.so)
- `ps aux` shows `cc1plus`/`g++`/`ninja`/`cmake` (transient; may miss in a snapshot)

Signs it is HUNG (kill it, retry — the network blip is usually transient):
- Process `State: S (sleeping)` on `anon_pipe_read`, ZERO compiler children,
  ZERO new `.o` for many minutes.
- Seen once in this session: first attempt sat 25+ min sleeping on a pipe, no CPU,
  no children. Killed; second attempt compiled fine and finished.

## Run in background — never foreground
The build exceeds the 600s foreground cap. Always:
```
# terminal action="terminal" with background=true, notify_on_complete=true
uv pip install --python $VENV/bin/python "llama-cpp-python==0.3.34" 2>&1
```
Then `process(action=wait)` in chunks; don't poll a sleeping pipe.

## End-to-end verification (bundled wrapper — NOT raw API)
Raw `NeuTTS.infer(text, ref_codes, ref_text, ...)` needs a reference clip + text
(voice-clone style). Use Hermes's wrapper which supplies the bundled "jo" voice:
```
$VENV/bin/python ~/.hermes/hermes-agent/tools/neutts_synth.py \
  --text "Hello, this is a local offline test of neutts." \
  --out /tmp/neutts_hermes.wav \
  --ref-audio ~/.hermes/hermes-agent/tools/neutts_samples/jo.wav \
  --ref-text  ~/.hermes/hermes-agent/tools/neutts_samples/jo.txt \
  --model neuphonic/neutts-air-q4-gguf --device cpu
```
Confirm real audio (not silence):
```
$VENV/bin/python -c "import soundfile as sf, numpy as np; d,sr=sf.read('/tmp/neutts_hermes.wav'); print('peak', round(float(np.abs(d).max()),3), 'dur', round(len(d)/sr,2))"
```
Expected: peak ~0.4, duration ~3.4s. First run loads model ~60-90s (HF cache
~2.6GB), then synthesizes on CPU.

## Config
`tts.provider: neutts` activates it. `tts.neutts.model` default
`neuphonic/neutts-air-q4-gguf`; `neuphonic/neutts-nano` is lighter. `tts.neutts.ref_audio`
/ `ref_text` override the bundled voice. Slow on CPU but fully OFFLINE.
