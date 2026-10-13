---
name: safe-file-deletion
description: Move-to-trash never rm -rf; consult before deleting.
---

# Safe File Deletion

## When this applies
Any operation that removes files, directories, caches, or cloud resources: `rm -rf`, `rm`,
`gcloud ... delete`, `docker system prune`, `go clean -modcache`, `npm cache clean --force`, etc.
If not trivially reversible, this skill governs it.

## Core rules (enforced by direct user correction)
1. **Trash-first — never hard-delete by default.** Move targets to
   `~/.local/share/Trash/files/` instead of `rm -rf`. The user explicitly corrected a
   hard-delete of npm/pnpm/bun caches with: *"why didnt you move them to trash first"*.
   Hard `rm -rf` only after explicit, per-item approval.
2. **Consult before destructive/shared-state actions.** Standing user rule: before killing procs,
   stopping services, removing packages, or `rm -rf`, ASK via clarify with beneficial suggestions
   + tradeoffs ("give me suggestions that are beneficial"). Do not act unilaterally. An "approved
   safe delete" list covers only that list — not Docker VM, agent state, or user vaults.
3. **Classify before acting.**
   - *Safe-to-trash (regenerable):* npm `_cacache`/`_npx`, pnpm/bun caches, `~/.cache/*`,
     `go modcache`, JetBrains `*-backup/`, sdkman `tmp/*.zip`, browser caches, Trash itself.
   - *NEVER touch without explicit approval:* `~/.hermes` (agent state), `~/Documents` (vaults),
     active venvs, Docker VM if still needed, Android SDK if developing, LM Studio models, anything
     not created this session.
4. **Verify after.** `df -h /home/deeone` before/after; confirm gone from source.

## Procedure
1. List candidate paths; separate regenerable cache from precious.
2. Regenerable → `mv <path> ~/.local/share/Trash/files/` (use `mv`, not `rm`). Cross-device?
   `cp -r` then `rm` original only after copy confirmed.
3. Precious/ambiguous → STOP, clarify with options + tradeoffs.
4. Report before/after disk usage.

## Pitfalls observed with this user
- `pkill -f /tmp/p01svc` once killed the shell's own subshell (SIGTERM). Prefer `kill <pid>`
  by explicit PID from `ss -ltnp`, not pattern-matched `pkill`.
- A "system bloat report" CRITICAL flag is a suggestion, NOT approval. Still consult.
- The user wants to be asked FIRST. "run the safe delete" means the pre-agreed SAFE list only.
