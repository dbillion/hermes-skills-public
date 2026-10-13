# qmd Embed — Vulkan Build Failure Details

> Session: 2026-05-19. Multiple attempts to fix qmd embed on this system. All failed.

## Root Cause

The `node-llama-cpp` package (bundled with qmd) tries to compile llama.cpp from source with Vulkan GPU support. The compilation fails because:

1. **Missing Vulkan shader source files**: The bundled llama.cpp is missing critical shader files:
   - `ggml/src/ggml-vulkan/vulkan-shaders/mul_mm.comp`
   - `ggml/src/ggml-vulkan/vulkan-shaders/flash_attn_cm2.comp`
   - (and many others)

2. **`NODE_LLAMA_CPP_GPU=false` does NOT help**: The env var is checked AFTER the build starts. The cmake-js build process is triggered regardless.

3. **Multiple competing processes**: Each `qmd embed` attempt spawns new cmake-js/glslc processes that don't clean up properly.

## Failed Fix Attempts

| Attempt | What was tried | Result |
|---------|---------------|--------|
| 1 | `NODE_LLAMA_CPP_GPU=false qmd embed` | Still tries Vulkan build |
| 2 | `rm -rf localBuilds/` | Recreates on next run |
| 3 | Manual model download to `~/.cache/qmd/models/` | Models download fine, but embed still fails at shader compilation |
| 4 | Killing cmake-js processes | New ones spawn on retry |
| 5 | `NODE_LLAMA_CPP_SKIP_DOWNLOAD=1` | Skips model download but not shader build |

## What Works

**BM25 keyword search** works perfectly without embeddings:
```bash
qmd search "topic" --name skills
qmd search "topic" --name docs
```

## Recommendation

**Do NOT attempt `qmd embed` on this system.** The Vulkan shader source files are fundamentally missing from the bundled llama.cpp. This is a packaging issue in `node-llama-cpp`, not a configuration issue.

BM25 keyword search is sufficient for skill retrieval and document search. If semantic search is needed, consider:
- Using a cloud embedding API (OpenAI, Gemini)
- Using `llama.cpp` directly with a prebuilt CPU-only binary
- Using a different embedding tool (e.g., `sentence-transformers` via Python)
