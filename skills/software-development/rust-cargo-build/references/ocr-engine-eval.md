# OCR engine evaluation (Kreuzberg / Tesseract / PaddleOCR)

How to compare OCR backends for a Rust/Python forwarder when the user asks to
"test N scenarios and declare the best winner". Condensed from a real eval on
`tgforwarder-rs` (branch `ocr-eval-kreuzberg`, 8 real Telegram channel images).

## Method (reusable)
- Put every engine on the **same set of real images** (not synthetic). Use images
  the current engine already handles poorly — that's where differences show.
- For each engine record: **success rate** (images with non-empty text),
  **total chars extracted**, **avg latency/img**, and a **sample of the actual
  text** (char count alone hides garbage — eyeball the sample for correctness).
- Declare the winner on accuracy first, then speed. A 0% run is not a verdict
  if it errored — read the error.
- Keep the harness on a **separate git branch**; commit it but don't merge until
  the user approves integrating the winner.

## Kreuzberg (Rust core, Python bindings 4.10.2)
- OCR backends: `tesseract`, `paddleocr` (via its `paddle-ocr` feature / ONNX),
  EasyOCR. Python: `from kreuzberg import extract_file_sync, ExtractionConfig, OcrConfig`;
  `OcrConfig(backend="tesseract"|"paddleocr", language="en")`.
- **Finding:** Kreuzberg's *default* OCR backend IS Tesseract — so "kreuzberg only"
  and "kreuzberg→tesseract" produce **identical** output. They tie.
- Works out of the box on Linux; ~4 s/img on infographic images; clean text.

## PaddleOCR 3.x — environment caveats (knowledge bank, NOT a "broken tool" rule)
Verified on this host (Arch Linux, Python 3.13 venv, `paddleocr`+`paddlepaddle` 3.x):
- **CLI** (`paddleocr ocr -i img.png ...`): hard-requires `ccache` on PATH.
  Without it the CLI prints `which: no ccache` and never OCRs. `ccache` may be
  absent and not installable without sudo (agent safety policy) — so the CLI may
  be unusable in a locked-down env.
- **Python API** (`from paddleocr import PaddleOCR; ocr.predict(img)`): the
  `ocr.ocr(img, cls=True)` call is **deprecated/renamed** in 3.x (use `predict`).
  Worse, inference crashes here with
  `NotImplementedError: (Unimplemented) ConvertPirAttribute2RuntimeAttribute
  not support [pir::ArrayAttribute<pir::DoubleAttribute>]` — a PaddlePaddle 3.x
  PIR/ONNX backend incompatibility on this CPU. Models download fine (PP-OCRv6),
  so it is purely a runtime/backend issue.
- To actually compare PaddleOCR you likely need: PaddleOCR 2.x, a GPU runner, or
  a PaddlePaddle build with a working ONNX backend. Don't present PaddleOCR as
  "tested and worse" if it never ran — mark it BLOCKED with the error.

## Kreuzberg as a "single binary without Tesseract CLI" — BLOCKED (key finding)
When the user wants a self-contained Rust binary that does OCR **without** the
system Tesseract CLI, don't assume Kreuzberg delivers it. Verified by reading
Kreuzberg's published `Cargo.toml` (v4.10.2), not guessed:
- `paddle-ocr = [ ..., "ocr", ... ]` and `ocr = [ "dep:kreuzberg-tesseract", ... ]`.
  So the `paddle-ocr` feature **transitively enables `kreuzberg-tesseract`**,
  which compiles **leptonica + Tesseract from C++ source via `cmake`** at build time.
- Consequences:
  1. It needs `cmake` + a C++ toolchain installed (absent on many locked-down
     hosts; `cargo check --no-default-features --features ocr-kreuzberg` fails with
     `failed to execute command: No such file or directory ... is cmake not installed?`).
  2. Even when it builds, it **bundles Tesseract** — it is NOT Tesseract-free,
     just statically linked instead of calling the system CLI. Kreuzberg is a
     document extractor that *wraps* Tesseract/PaddleOCR; it does not replace Tesseract.
- Practical verdict: the `rusty-tesseract` (system Tesseract CLI) path is the
  simpler, working single-binary choice. Keep any Kreuzberg backend
  **feature-gated** (`ocr-kreuzberg`) so default CI/build never needs cmake.

## Verdict pattern from the eval
Kreuzberg (Tesseract-backed) won because it was the only engine that ran and
produced correct text at ~4 s/img. PaddleOCR was BLOCKED (env), not beaten.
Capture that distinction honestly in the result — a blocked engine is not a loser.
