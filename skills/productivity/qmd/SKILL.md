---
name: qmd
version: "1.0.0"
description: "Use qmd (Query Markup Documents) as a local search engine for skill docs, notes, and knowledge bases. Retrieve only relevant snippets instead of loading full files into context — critical for avoiding context-length errors in cron jobs and large-skill workflows."
argument-hint: 'qmd search "topic" | qmd vsearch "semantic query" | qmd get "path/to/doc.md"'
allowed-tools: Bash
metadata:
  openclaw:
    emoji: "🔍"
    requires:
      bins: [node, npx]
---

# QMD — Query Markup Documents

Local search engine for markdown files. Combines BM25 full-text search, vector semantic search, and LLM re-ranking — all running locally.

**Why this skill exists:** Many skills (e.g. `last30days`) have 1000+ line SKILL.md files. Loading them fully into context wastes tokens and causes context-length errors, especially in cron jobs. Use `qmd` to index your skills/notes/docs, then retrieve only the relevant snippets at runtime.

## Install

```bash
npm install -g @tobilu/qmd@2.0.1
# or
bun install -g @tobilu/qmd
```

## First-Time Setup (One-Time)

Before using qmd, index your skill docs and notes:

```bash
# Index skills directory
qmd collection add ~/.hermes/skills --name skills

# Index your notes/docs
qmd collection add ~/Documents --name docs
qmd collection add ~/notes --name notes 2>/dev/null

# Add context hints (helps search quality)
qmd context add qmd://skills "Hermes agent skills — SKILL.md files with workflow instructions"
qmd context add qmd://docs "Personal documents and reference materials"
qmd context add qmd://notes "Personal notes and ideas"

# Generate embeddings for semantic search (one-time, downloads ~2GB models)
qmd embed
```

Models are cached in `~/.cache/qmd/models/`. First `qmd embed` downloads ~300MB embedding model + ~640MB reranker + ~1.1GB query expansion model.

## Embeddings / Semantic Search

**⚠️ On this system:** The `qmd embed` command requires a working Vulkan/CUDA GPU driver. Without it, only BM25 keyword search works. This is fine for most use cases.

To attempt enabling semantic search:
```bash
# Check GPU support
qmd status

# Try generating embeddings (requires GPU)
qmd embed
```

If `qmd embed` hangs or crashes with `vk::IncompatibleDriverError`, your GPU driver is incompatible. BM25 keyword search (`qmd search`) works perfectly without embeddings.

**⚠️ Do not attempt `qmd embed` on systems without a working Vulkan/CUDA GPU.** The `node-llama-cpp` build will fail. See [references/qmd-embed-vulkan-fix.md](references/qmd-embed-vulkan-fix.md) for full details on fix attempts and alternatives.

## Cron Job Context Budget — Model Selection First

**Before using qmd/RTK in a cron job, ensure the model's context window exceeds the system prompt size.** On this system, `nvidia/nemotron-mini-4b-instruct` has a 4,096 token limit but the system prompt alone is ~6,600 tokens. No amount of qmd/RTK can fix this — you must switch models.

See the `rtk` skill's `references/cron-context-overflow.md` for the full error transcript and diagnosis steps.

**Optimization priority for cron jobs:**
1. Model with adequate context window (32K+ recommended)
2. No heavy skills (last30days = 130KB — never attach to cron)
3. Self-contained prompt with explicit word limits
4. qmd for targeted skill snippet retrieval
5. RTK for Bash output compression

## Core Workflow: Skill Retrieval Without Full Load

**Instead of loading a 1709-line SKILL.md into context:**

```bash
# Search for the specific section you need
qmd search "last30days LAW 1 LAW 2 output format" --name skills

# Get a specific document by path
qmd get "last30days-skill/skills/last30days/SKILL.md" --name skills

# Multi-get with glob
qmd multi-get "last30days-skill/skills/last30days/*.md" --name skills
```

**In a cron job prompt, use this pattern:**

```bash
# Step 1: Search for the relevant section
RELEVANT_SECTION=$(qmd search "last30days cron job invocation pattern" --name skills 2>/dev/null)

# Step 2: Read only what you need
echo "$RELEVANT_SECTION"
```

**To retrieve full skill files (use glob patterns, not exact paths):**

```bash
# Get all files in a skill directory
qmd multi-get "last30days-skill/**/*.md" --name skills

# Get specific file by partial match
qmd multi-get "last30days-skill/skills/last30days/*" --name skills
```

## Cron Job Integration

For cron jobs that use large skills, add this pattern to the cron prompt:

```
Before loading any skill with 500+ lines, run:
  qmd search "<specific topic you need>" --name skills
Use the search results instead of loading the full SKILL.md.
Only fall back to reading the full SKILL.md if qmd returns no results.
```

This can reduce token usage by 60-80% for skill-heavy cron jobs.

**For maximum token reduction, combine qmd with RTK:**
```bash
# RTK compresses the qmd output further
rtk read <(qmd search "topic" --name skills)
```

See the `rtk` skill for setup. RTK reduces terminal output tokens by 60-90% across all commands.

## MCP Server Mode

qmd can run as an MCP server for agent integration:

```bash
# Start MCP server (background)
qmd mcp --http --daemon

# Stop
qmd mcp stop
```

Configure in Claude Desktop / Hermes MCP config:
```json
{
  "mcpServers": {
    "qmd": {
      "command": "qmd",
      "args": ["mcp"]
    }
  }
}
```

## Binary Location & Install

The qmd binary may be at different paths depending on install method:

```bash
# Find it
find /home/deeone -name "qmd" -path "*/bin/qmd" 2>/dev/null

# Common locations:
# Volta temp:  ~/.volta/tmp/image/packages/.tmp*/lib/node_modules/@tobilu/qmd/bin/qmd
# Local:       ~/.local/qmd/node_modules/.bin/qmd
# Global:      $(npm root -g)/@tobilu/qmd/bin/qmd
```

If `qmd` is not on PATH, use the full path or create a symlink:
```bash
QMD_BIN=$(find /home/deeone/.local/qmd -name "qmd" -path "*/bin/qmd" 2>/dev/null | head -1)
mkdir -p /home/deeone/.local/bin
ln -sf "$QMD_BIN" /home/deeone/.local/bin/qmd
```

**Recommended install** (avoids npm global install issues):
```bash
mkdir -p ~/.local/qmd && cd ~/.local/qmd && npm init -y && npm install @tobilu/qmd@2.0.1
```

## Gmail Batch Operations

For bulk Gmail operations (search + trash) using `gws`, see [references/gmail-gws-patterns.md](references/gmail-gws-patterns.md) for the correct pagination pattern and rate limits.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `qmd: command not found` | `npm install -g @tobilu/qmd@2.0.1` or use full path |
| `better-sqlite3` binding error | Rebuild: `cd <qmd_dir> && npm rebuild better-sqlite3` |
| `vk::IncompatibleDriverError` on `qmd embed` | **Permanent limitation — DO NOT RETRY.** The bundled `node-llama-cpp` tries to compile llama.cpp from source with Vulkan support, but the Vulkan shader source files (`mul_mm.comp`, `flash_attn_cm2.comp`, etc.) are missing from the bundle. `NODE_LLAMA_CPP_GPU=false` does NOT prevent the build. `cmake-js` will keep retrying. Kill the process and use BM25 keyword search instead. |
| Built-in model downloader stuck on "Model: embeddinggemma" | **Do not wait.** The downloader hangs after downloading models because it can't compile the Vulkan shaders. BM25 search works without embeddings. |
| Slow first search | Normal for BM25 on first run. Subsequent searches are fast. Do NOT run `qmd embed` to "fix" this. |
| No results | Check collections: `qmd collection list` |
| Stale index | Re-embed: `qmd embed -f` |
| Models not downloading | Check `~/.cache/qmd/models/` — needs ~2GB disk |
| npm install hangs | Use local install: `mkdir -p ~/.local/qmd && cd ~/.local/qmd && npm init -y && npm install @tobilu/qmd@2.0.1` |

## Key Flags

```bash
qmd search "query" --name skills     # Search specific collection
qmd search "query" --limit 5         # Limit results
qmd get "path.md" --name skills      # Get full document
qmd multi-get "glob*.md"             # Batch retrieve
qmd collection list                  # List collections
qmd embed                            # Generate/rebuild embeddings
qmd embed -f                         # Force rebuild
```
