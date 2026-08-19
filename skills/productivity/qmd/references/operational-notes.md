# QMD — Operational Notes

## Installation (when npm global install hangs)

If `npm install -g @tobilu/qmd` hangs (common in restricted environments), use local install:

```bash
mkdir -p ~/.local/qmd && cd ~/.local/qmd && npm init -y && npm install @tobilu/qmd@2.0.1
# Binary: ~/.local/qmd/node_modules/.bin/qmd
# Symlink: ln -sf ~/.local/qmd/node_modules/.bin/qmd ~/.local/bin/qmd
```

## First-Time Setup

```bash
# Index skills directory
qmd collection add ~/.hermes/skills --name skills

# Index documents
qmd collection add ~/Documents --name docs

# Generate embeddings (~2GB download, takes time — run in background)
qmd embed
```

## Embed Models

Three models are auto-downloaded to `~/.cache/qmd/models/`:
- `embeddinggemma-300M-Q8_0.gguf` — vector embeddings (~300MB)
- `qwen3-reranker-0.6b-q8_0.gguf` — re-ranking (~640MB)
- `qmd-query-expansion-1.7B-q4_k_m.gguf` — query expansion (~1.1GB)

Until embeddings are generated, `qmd search` uses BM25 keyword search only (still useful).

**If the built-in downloader gets stuck** (stuck on "Model: embeddinggemma" for 10+ min), download manually with curl — see [references/vulkan-gpu-fix.md](references/vulkan-gpu-fix.md).

## Binary Locations

```bash
# Find the binary
find /home/deeone -name "qmd" -path "*/bin/qmd" 2>/dev/null

# Common:
# Volta temp: ~/.volta/tmp/image/packages/.tmp*/lib/node_modules/@tobilu/qmd/bin/qmd
# Local:      ~/.local/qmd/node_modules/.bin/qmd
# Symlink:    ~/.local/bin/qmd
```

## better-sqlite3 Binding Error

If you get `Could not locate the bindings file` for `better-sqlite3`, the native module wasn't compiled. Fix:

```bash
cd <qmd_install_dir> && npm rebuild better-sqlite3
```

If rebuild hangs, use the local install method above (it compiles during install).

## Cron Job Token Savings

Measured token reduction when using qmd instead of loading full SKILL.md:
- `last30days` skill: 1709 lines → ~30 lines via qmd search = **~98% reduction**
- Typical large skill (500+ lines): **60-80% reduction**

Pattern for cron job prompts:
```
Before loading any skill with 500+ lines:
  1. Run: qmd search "<specific topic>" --name skills
  2. Use search results instead of full SKILL.md
  3. Fall back to full SKILL.md only if qmd returns no results
```
