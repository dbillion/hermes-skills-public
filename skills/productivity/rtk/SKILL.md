---
name: rtk
version: "1.0.0"
description: "Use RTK (Rust Token Killer) to reduce LLM token consumption by 60-90% on common CLI commands. Proxy wrapper that compresses command output before it reaches the context window. Critical for cron jobs and any task with large tool outputs."
argument-hint: 'rtk read file.ts | rtk grep "pattern" . | rtk git status | rtk ls'
allowed-tools: Bash
metadata:
  openclaw:
    emoji: "✂️"
    requires:
      bins: [rtk]
---

# RTK — Rust Token Killer

CLI proxy that reduces LLM token consumption by **60–90%** on common dev commands. Single Rust binary, zero dependencies. Filters and compresses command output before it reaches the LLM context window.

**Why this skill exists:** Terminal tool outputs (git status, grep, cat, ls, test results) flood the context window with noise. RTK compresses these outputs — removing boilerplate, grouping similar items, truncating redundancy — so you can run more tool calls before hitting context limits. Essential for cron jobs.

## How It Works

Four strategies per command type:
1. **Smart Filtering** — Removes noise (comments, whitespace, boilerplate)
2. **Grouping** — Aggregates similar items (files by directory, errors by type)
3. **Truncation** — Keeps relevant context, cuts redundancy
4. **Deduplication** — Collapses repeated log lines with counts

## Install

```bash
# Quick install (Linux/macOS)
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
# Installs to ~/.local/bin

# Verify
rtk --version
rtk gain   # Show token savings stats
```

## Setup for Hermes

```bash
# Configure for Hermes agent
rtk init --agent hermes

# Global hook (Claude Code, Codex, etc.)
rtk init -g

# Restart Hermes after init
```

## Usage

### Automatic (via hook)
Once `rtk init -g` is configured, all Bash tool calls are automatically rewritten:
```
git status  →  rtk git status
cat file.ts →  rtk read file.ts
rg pattern  →  rtk grep "pattern" .
```

### Explicit (direct invocation)
```bash
# Files
rtk ls .                        # Token-optimized directory tree
rtk read file.rs                # Smart file reading
rtk read file.rs -l aggressive  # Signatures only (strips bodies)
rtk smart file.rs               # 2-line heuristic code summary
rtk find "*.rs" .               # Compact find results
rtk grep "pattern" .            # Grouped search results

# Git
rtk git status                  # Compact status
rtk git log -n 10               # One-line commits
rtk git diff                    # Condensed diff
rtk git add                     # → "ok"
rtk git commit -m "msg"         # → "ok abc1234"
rtk git push                    # → "ok main"

# GitHub CLI
rtk gh pr list                  # Compact PR listing
rtk gh pr view 42

# Tests
rtk test                        # Condensed test output
```

## Token Savings (Typical 30-min Session)

| Operation | Standard | RTK | Savings |
|-----------|----------|-----|---------|
| `ls` / `tree` | 2,000 | 400 | -80% |
| `cat` / `read` | 40,000 | 12,000 | -70% |
| `grep` / `rg` | 16,000 | 3,200 | -80% |
| `git status` | 3,000 | 600 | -80% |
| `git diff` | 10,000 | 2,500 | -75% |
| `npm test` | 25,000 | 2,500 | -90% |
| **Total** | **~118,000** | **~23,900** | **-80%** |

## Combining with qmd for Maximum Token Reduction

For cron jobs that use large skills, combine RTK with qmd:
```bash
# qmd finds relevant snippets, RTK compresses the output
rtk read <(qmd search "specific topic" --name skills)
```

This two-layer approach (targeted retrieval + output compression) can reduce token usage by 80-95% for skill-heavy cron jobs.

See the `qmd` skill for setup. Note: qmd BM25 keyword search works without GPU. Semantic embeddings (`qmd embed`) require a compatible Vulkan/CUDA GPU driver.

For cron jobs, RTK is automatically applied to all Bash tool calls once `rtk init -g` is configured. No changes needed to cron prompts.

To verify RTK is active in a cron job, add this to the cron prompt:
```
After any terminal command, check that output is compressed (not raw).
If you see full raw output, RTK is not hooked — use `rtk <command>` explicitly.
```

## Cron Job Context Budget — Model Selection Matters Most

**The #1 cause of cron job context overflow is not tool output — it's the model's context window being too small for the system prompt alone.**

Before optimizing with RTK/qmd, verify the model can even hold the system prompt:

```bash
# Check model context window
grep -r "context" ~/.hermes/logs/agent.log | grep -i "token\|context\|limit" | tail -5
```

**Rule: The model's context limit MUST be larger than the system prompt + tool schemas.** On this system:
- `nvidia/nemotron-mini-4b-instruct` → 4,096 tokens → **TOO SMALL** (system prompt alone is ~6,600 tokens)
- `openrouter/owl-alpha` → large context → **OK**

**Symptoms of wrong model:**
```
Context length exceeded: 6,620 tokens. Cannot compress further.
```
This means the model's context window is smaller than the base system prompt. RTK/qmd cannot fix this — you must switch models.

**Fix:** Set `model` explicitly in the cron job:
```
model: { provider: "openrouter", model: "openrouter/owl-alpha" }
```

**Optimization priority for cron jobs:**
1. **Model with adequate context window** (most important — no workaround if missing)
2. **No heavy skills** (last30days SKILL.md alone is 130KB/1709 lines — never attach to cron)
3. **Self-contained prompt** with explicit word/token limits
4. **RTK** for Bash output compression (60-90% reduction)
5. **qmd** for targeted skill snippet retrieval instead of full SKILL.md loads

## Important Notes

- The hook only runs on **Bash tool calls**. Built-in tools (Read, Grep, Glob) bypass it.
- For Hermes: `rtk init --agent hermes` rewrites terminal commands through rtk.
- For Claude Code / Codex: `rtk init -g` installs a PreToolUse hook.
- If `rtk gain` fails, you may have the wrong `rtk` package (Rust Type Kit). Reinstall via the install script.
- Config: `~/.hermes/config.yaml` (Hermes) or `~/.claude/settings.json` (Claude Code)
- Filters: `~/.config/rtk/filters.toml` (user-global filter rules)

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `rtk: command not found` | Reinstall: `curl -fsSL .../install.sh \| sh` |
| Hook not active | Run `rtk init -g` and restart the agent |
| Wrong rtk package | Use `curl` install script, NOT `cargo install rtk` |
| Output not compressed | Use explicit `rtk <command>` instead of raw command |
