---
name: hermes-cron-job-debugging
description: Debug Hermes cron jobs showing empty data; verify store.
version: 1.0.0
author: Hermes Agent (curator)
license: MIT
tags: [hermes, cron, debugging, journal, troubleshooting]
metadata:
  hermes:
    tags: [hermes, cron, debugging, journal, troubleshooting]
    related_skills: [systematic-debugging]
---

# Hermes Cron Job Debugging

## When to use
A Hermes `cronjob` reports no data ("no structured journal entry recorded today",
"no sessions today", blank summary) but you KNOW work happened that day. Or a
summary cron silently drops a day's activity.

## Core principle: trust-but-verify the negative
A cron's "nothing found today" is a SYMPTOM, not proof. The job's own detection
logic may point at a deprecated data source. Independently verify the live store
before accepting the negative. This session's bug: a journal job `ls`-ed
`~/.hermes/sessions/*.jsonl` (stale May data) and reported "no raw sessions
today" even though real August work existed in the live store.

## Debugging checklist (root-cause first — no guessing)
1. **Read the job definition.** `cronjob list`, then read the prompt from
   `/home/deeone/.hermes/cron/jobs.json` (top-level `jobs` array; each entry has
   `id`, `name`, `prompt`). Find what path/command it uses to locate "today's" data.
2. **Identify the data-source assumption.** Does it `ls` a dir, glob files, read a
   flat file, or query a DB? That assumption may be stale.
3. **Verify the live store independently.** Do NOT trust the job's own `ls`/glob
   (use `search_files` if a filesystem scan is needed). Query the actual current
   store directly (see references/session-store-check.md).
4. **Check for storage migration.** Hermes' session/state store has moved across
   versions. As of this user's setup the LIVE session store is
   `/home/deeone/.hermes/state.db` (`sessions` + `messages` tables; `started_at`
   is a Unix epoch float). The legacy `~/.hermes/sessions/*.jsonl` and
   `request_dump_*.json` files hold only STALE pre-migration data and will miss
   all recent activity. Re-confirm after any Hermes upgrade — do not hardcode.
5. **Fix at the source.** Patch the job prompt to query the live store, then
   re-run to backfill the missed day.

## Pitfalls
- A job that APPENDS a `# Daily Summary` section to a journal file is safe to
  re-run; it backfills the missed day.
- Date math: session timestamps are epoch floats. Convert with
  `datetime.fromtimestamp(ts, datetime.UTC)` (3.12+; `utcfromtimestamp` deprecated).
  Filter `started_at >= start_of_day_epoch AND < start_of_day+86400`.
- Use the job's `$DATE` variable; never hardcode the date in a fix.
- `cronjob list` is the live source of truth for job IDs and schedules.

## Verification before declaring fixed
Run the corrected detection query for the missed day and confirm it returns the
real sessions, THEN re-run the job. If the query still returns nothing, the
problem is elsewhere (permissions, empty journal, different store) — keep digging.

## References
- `references/session-store-check.md` — exact sqlite query to list a day's sessions.
