---
name: safe-destructive-ops
description: Trash-first deletions; never hard rm -rf.
---

# Safe Destructive Operations

Governs every deletion, kill, uninstall, or cloud-resource-removal this agent performs for this user.

## Hard rule (from a direct user correction)
**NEVER hard-delete. Move to trash first.**
- Before removing anything, `mv <path> ~/.local/share/Trash/files/` — do NOT `rm -rf` it.
- This applies to **caches too** (npm `_cacache`, pnpm store, bun cache, `~/.cache/*`, go modcache, JetBrains `*backup` dirs). The user explicitly objected to hard-deleting these even though they are "safe to clean" by conventional wisdom.
- Exception: only `rm` (never `rm -rf`) when the user has given **explicit per-item approval** for that specific path.

## Consult before destructive/shared-state actions
- For any action that kills processes, stops services, removes packages, deletes files, or removes cloud resources, **use the `clarify` tool first** — never unilaterally.
- When the user says "run the safe delete," that approves only a **pre-agreed, enumerated list**. Still move those items to trash; do not hard-delete. Surface the list and get confirmation before acting.
- Lead with beneficial suggestions + tradeoffs (user preference): "give me suggestions that are beneficial."

## Why this matters
The user previously lost work to a mass `rm -rf` during a generation/render task. Standing rule: **accumulate in per-target folders; delete only when explicitly asked.** A "safe delete" script that hard-removes is itself a violation.

## Gotchas
- `rm -rf` inside a heredoc or `&&` chain is still a hard delete — avoid it for anything recoverable.
- Verify trash move with `ls ~/.local/share/Trash/files/` after.
- If you already hard-deleted (e.g. a cache the user later questioned), own it: apologize for not trash-first, explain caches regenerate, and offer to change the standing behavior.
