---
name: loop-engineering-workflow
description: Apply the loop-engineering methodology (maker/checker split, durable STATE outside the conversation, per-slice commit, L2 act-and-verify) to drive a well-specified multi-slice build to completion WITHOUT stopping to deliberate. Use when the user says "finish the rest", "continue without stopping", "the criteria are well defined", or references cobusgreyling/loop-engineering. Encodes the principles so an agent starts already knowing how to run the loop.
license: MIT
metadata:
  author: derived from github.com/cobusgreyling/loop-engineering
  version: '1.0'
---

# Loop Engineering Workflow

Drive a well-defined build to completion by running tight maker/checker loops. The repo
github.com/cobusgreyling/loop-engineering defines the pattern; this skill condenses the
principles that actually move a project forward.

## Principles (apply all)
1. **Maker / Checker split.** The implementer does the work; a SEPARATE verification gates it.
   Verification = build + tests + REAL tool output (curl, headless check, DB query) — never a
   status claim ("it should work"). This is the "verify by auditing, not labeling" rule.
2. **Durable STATE outside the conversation.** Keep a `STATE.md` at repo root recording
   DONE+verified and PENDING slices. It survives context compression, so the loop never
   re-does work or loses track. Update it after every committed slice.
3. **Budget + early exit.** If there is nothing actionable, exit cheap. Don't spin.
4. **L1 -> L2 progression.** Start report-only; graduate to acting. For well-defined criteria,
   run L2 directly: act + verify + commit + update STATE, then next slice. No pausing to ask
   "should I proceed?" when the criteria are explicit.
5. **Isolation.** Do risky work on a feature branch (or git worktree) so a bad slice is
   revertible. Commit a known-good state BEFORE editing.
6. **Human gate only for risky / ambiguous.** If the next slice is well-defined, just do it
   (L2) and report. Reserve clarification for genuine forks.

## The loop (repeat per slice)
```
for slice in remaining_slices:
    implement(slice)                      # maker
    verify(slice)  -> real tool output    # checker (curl/build/DB query)
    if verified: commit(slice); update STATE.md; update tracker issue
    else:        fix; re-verify; commit
```
Do NOT break the loop to deliberate. Each iteration is small and independently verifiable.

## Durable STATE.md template
```markdown
# Loop State — <project>
Last run: <date>
## DONE + VERIFIED (real output, committed)
- <what> — <how verified> (commit <sha>)
## PENDING SLICES (L2: act + verify, then commit)
- [ ] <slice>
```
Keep it a flat checklist; the loop advances it. This is also the artifact to show the user
for "what's done / what's left" — more useful than a prose summary.

## Tracker discipline
If the project has GitHub issues (or equivalent), comment/progress the relevant issue the
moment a slice is verifiably done. Don't let the tracker lag behind the code.

## When the user says "ignore X and continue with the rest"
Treat X as dropped from scope (note it in STATE as blocked/deferred) and keep running the loop
on the remaining slices. Don't re-litigate X. If X later becomes needed, it's a new slice.
