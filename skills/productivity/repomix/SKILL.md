---
name: repomix
description: "Token-optimized repository packing and code analysis using repomix CLI. Use for efficient codebase exploration, documentation generation, and AI-friendly code context with 60-90% token savings."
---

# Repomix

Packs entire repositories into single AI-friendly files with intelligent compression. Already installed: repomix v1.13.1.

## Quick Reference

```bash
# Ultra-compressed codebase snapshot (90% token savings)
repomix --compress --remove-comments --remove-empty-lines --stdout

# Git-aware context (current work + history)
repomix --compress --include-diffs --include-logs --include-logs-count 5

# Token analysis (find heavy files)
repomix --token-count-tree 100 --verbose

# Filtered subsystem analysis
repomix --include "src/**/*.ts,**/*auth*" --compress --style markdown
```

## Core Commands

```bash
# Pack repository
repomix                          # Default XML output
repomix --stdout                 # Output to stdout for piping
repomix --copy                   # Copy to clipboard
repomix -o context.md --style markdown  # Custom output

# Token optimization
repomix --compress               # Maximum compression
repomix --remove-comments        # Remove comments
repomix --remove-empty-lines     # Remove empty lines
repomix --no-files               # Metadata only

# File filtering
repomix --include "src/**/*.ts,**/*.tsx"
repomix --ignore "*.test.js,docs/**,*.md"

# Git integration
repomix --include-diffs          # Include current changes
repomix --include-logs           # Include commit history

# Large repos
repomix --split-output 500kb     # Split into chunks
```

## Token-Saving Workflows

```bash
# Quick overview (metadata only)
repomix --no-files --token-count-tree 50

# Deep dive on specific area
repomix --include "src/auth/**" --compress --stdout

# Code review context
repomix --include-diffs --include-logs --compress -o review-context.md
```

## Token Savings

| Task | Traditional | Repomix | Savings |
|------|------------|---------|---------|
| Read 10 files | 5,000 tokens | 500 tokens | 90% |
| Analyze auth module | 8,000 tokens | 800 tokens | 90% |
| Code review context | 12,000 tokens | 1,500 tokens | 87% |
