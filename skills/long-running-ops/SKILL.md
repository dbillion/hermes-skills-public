---
name: long-running-ops
description: 'Use when CLI jobs run long, stall, or hit rate limits.'
---

# Long-Running Ops

For CLI jobs that can run minutes, stall, rate-limit, or contend on locks
(large installs, embedding runs, syncs, downloads). One job, one hypotheses
each poll: check real progress before waiting longer.

## Conduct (non-negotiable)

- After EVERY tool-call batch, reply with an explicit summary of what ran
  and what it returned. An empty response after executing tools is a failure
  mode — the user flagged it 2026-09-03 and it must not recur.
- Report blockers honestly with the evidence; never invent output for a call
  that did not actually produce it.
- Batch independent reads/searches into one turn; serialize only on genuine
  dependency.

## Run

- Foreground max ~600s. Anything longer: `background=true` + `notify=true`,
  then `poll`. Never stack a second writer on a locked store — check the
  lock holder first (see references/gbrain-pglite-ops.md for the PGLite
  pattern: serve holds the single-writer lock; mint/sync/embed accordingly).
- Long sleeps are waits of last resort. Prefer polling with a progress probe.

## Progress probes

- Wall-clock tells nothing. For a live worker PID, compare `/proc/<pid>/io`
  `rchar`/`wchar` deltas across 60–90s plus `etime`: climbing counters =
  working (even if slow); flat counters + live process = backing off or
  wedged — investigate before killing.
- Watch the WRAPPER vs the WORKER: poll the child doing the work (e.g. the
  `bun ... embed` process), not the `sleep`/`tail` parent, or you will
  misread idle as stalled.

## Rate-limit backoff (API 429s)

- On `Too Many Requests`: stop hammering. Cooldown sleep (minutes, matching
  the service window), then retry with a smaller batch (`--batch-size 5`
  worked for Voyage after full-batch runs kept failing).
- Re-run the `--stale`-style incremental pass afterward and require the
  "0 stale / 0 remaining" output before declaring done. Partial counts
  ("embedded N, M failed") mean schedule another pass, not success.

## Env gap: foreground vs background shells

- Background shells do NOT inherit the session's exported env. A key present
  in the main session (`printenv KEY | wc -c` shows length) reads EMPTY
  (length 1) in a background job. Key-dependent verifies must run in the
  foreground session or re-export from a stored source.
- Never print key/token literals. Verify presence by length only; pass via
  `$VAR` references, never inline values.

## Verify, don't claim

- Subagent/background success claims are self-reports. Require a verifiable
  handle: fact id returned by recall, "0 stale" line, health JSON, file on
  disk. Re-read the destination to confirm remote effects landed.
