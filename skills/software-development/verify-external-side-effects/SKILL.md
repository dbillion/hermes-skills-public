---
name: verify-external-side-effects
description: Re-read the destination to confirm a remote action landed.
---

# Verify External Side-Effects

When an agent performs an action whose success is observable ONLY outside the local
process — forwarding a message, uploading a file, posting to an API, writing to a DB,
sending an email, creating a remote resource — the tool's own return value or "Done"
log is NOT proof it worked. **Re-read the destination and confirm the effect is actually
there before reporting success.**

## The trap (seen in production)
A CLI reported `Done. {'forwarded': 4711, 'failed': 0}` and the agent announced success.
In reality 0 files landed. The `4711` was a CUMULATIVE cache-marker count across many
runs, not messages delivered this run. The per-run forwarded count was 0. The user saw
an empty inbox and said "why are you lying." Lesson: a summary number from the tool is
the thing most likely to be wrong. Confirm independently.

## When to apply
Any time you would otherwise say "I forwarded / uploaded / created / sent X" and the
only evidence is the tool's stdout or return object. Especially when:
- The tool maintains a local cache / DB / state file and reports counts derived from it.
- The operation targets a remote system you can also READ back from.
- The claimed count seems high relative to what you observed (or 0 landed despite "ok").

## How to verify (cheap, decisive)
1. After the action, perform a READ against the destination with the same client/session:
   - Forwarded to Telegram Saved Messages? Re-read the target chat and count
     `fwd_from.saved_from_peer == source_id` (or re-fetch the exact returned message id).
   - Uploaded a file? `HEAD`/`GET` it back or list the bucket/folder.
   - POSTed to an API? `GET` the resource by id.
   - Wrote to a DB? `SELECT` the row.
2. Compare the BEFORE and AFTER counts (or existence), not the tool's self-report.
3. Report the VERIFIED number. If you can't read it back, say "initiated, not verified"
   — never "done."

## Per-run vs cumulative (metric hygiene)
If a tool reports a counter, know whether it is per-run or cumulative:
- A cumulative SQLite/state count will look impressive and is useless as proof of a
  single run. Track a per-run counter separately (increment only on a confirmed send)
  and report THAT.
- When building such a tool, print BOTH: `forwarded this run: N | cache total: M`.

## Anti-patterns
- Trusting `cache.stats()` / a DB row count as "delivered this run."
- Printing a tool's `forwarded: N` summary verbatim as your status update.
- Re-running with `--start` against an already-cached source and reporting the cache
  count as new work (dedup correctly skips it → 0 new, but the log looked like success).
