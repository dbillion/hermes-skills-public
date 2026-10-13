# QMD Troubleshooting Reference

## `vk::IncompatibleDriverError` on `qmd embed`

**Symptom:** `qmd embed` crashes with:
```
terminate called after throwing an instance of 'vk::IncompatibleDriverError'
  what():  vk::createInstance: ErrorIncompatibleDriver
```

**Cause:** `node-llama-cpp` (qmd's dependency) bundles llama.cpp source and always compiles from source with Vulkan GPU support. If your system has no compatible Vulkan GPU driver (headless server, no GPU, or driver mismatch), the compiled binary crashes.

**What does NOT work:**
- Renaming/removing `localBuilds/linux-x64-vulkan` — source rebuilds automatically
- `NODE_LLAMA_CPP_SKIP_DOWNLOAD=1` — source is already bundled, this only skips *downloading* source
- `LLAMA_VULKAN=0` / `GGML_VULKAN=0` — CMake build includes Vulkan regardless
- Faking a prebuilt binary in `localBuilds/` — source build still triggers (node-llama-cpp checks for source first)
- Setting `NODE_LLAMA_CPP_SKIP_DOWNLOAD=1` alone — doesn't prevent compilation of bundled source

**Working fix:** Remove the llama.cpp source directory to prevent source builds, AND ensure no `localBuilds/` directory exists so it falls back to the prebuilt CPU binary. Also set `NODE_LLAMA_CPP_GPU=false` to force CPU-only mode:

```bash
# 1. Remove source directory (this is the critical step)
rm -rf ~/.local/qmd/node_modules/node-llama-cpp/llama/llama.cpp

# 2. Remove any localBuilds (Vulkan or otherwise)
rm -rf ~/.local/qmd/node_modules/node-llama-cpp/llama/localBuilds

# 3. Verify the prebuilt CPU binary exists
ls ~/.local/qmd/node_modules/@node-llama-cpp/linux-x64/bins/linux-x64/llama-addon.node

# 4. Run embed with GPU disabled
export NODE_LLAMA_CPP_GPU=false
qmd embed
```

**If the built-in model downloader gets stuck** (stuck on "Model: embeddinggemma" for 10+ min):
The `node-llama-cpp` model downloader can hang on slow connections. Download manually:

```bash
mkdir -p ~/.cache/qmd/models

# Embedding model (~300MB)
curl -L --progress-bar \
  "https://huggingface.co/ggml-org/embeddinggemma-300M-GGUF/resolve/main/embeddinggemma-300M-Q8_0.gguf" \
  -o ~/.cache/qmd/models/embeddinggemma-300M-Q8_0.gguf

# Reranker model (~640MB)
curl -L --progress-bar \
  "https://huggingface.co/ggml-org/Qwen3-Reranker-0.6B-Q8_0-GGUF/resolve/main/qwen3-reranker-0.6b-q8_0.gguf" \
  -o ~/.cache/qmd/models/qwen3-reranker-0.6b-q8_0.gguf

# Query expansion model (~1.1GB)
curl -L --progress-bar \
  "https://huggingface.co/tobil/qmd-query-expansion-1.7B-gguf/resolve/main/qmd-query-expansion-1.7B-q4_k_m.gguf" \
  -o ~/.cache/qmd/models/qmd-query-expansion-1.7B-q4_k_m.gguf
```

Then run `qmd embed` — it should detect the downloaded models and skip downloading.

**⚠️ CPU embedding is very slow:** Even with the Vulkan fix, generating embeddings for 689+ files on CPU can take 30-60+ minutes. The process may appear stuck on "Model: embeddinggemma" — it's actually computing. Check CPU usage with `ps aux | grep qmd` to confirm it's working. For large collections, consider running overnight.

**Alternative:** BM25 keyword search works without embeddings. Skip `qmd embed` entirely if you don't need semantic/hybrid search. `qmd search "query"` works immediately after indexing.
