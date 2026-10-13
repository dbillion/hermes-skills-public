---
name: recurring-activity-journal
description: Set up journal entries and Telegram cron day/week summaries.
---

# Recurring Activity Journal + Cron

## When to use
- "going forward, i want you to have a journal of daily activities... daily + weekly summary as a cron job to telegram."
- User wants persistent record of work, struggles, guidance needs, efficiency improvements.

## Entry schema (write on each working day)
For each tracked category the user cares about, capture:
- **Activities** — what was done.
- **Struggles** — what was hard / what failed.
- **Guidance wishes** — what better guidance would have helped.
- **Improvements** — changes to reduce mistakes / be more efficient.
- **Wins** — shipped milestones (e.g. PyPI publish).
This user's tracked categories: Agent Reach / OpenCLI / LinkedIn, Manim / DSA storytelling, tgforwarder, job search (LinkedIn + Java AI Job Finder Canada), pip/PyPI publishing.

## Setup
1. `mkdir -p ~/.hermes/journal/daily ~/.hermes/journal/weekly`.
2. Write today's entry (seed) so the pipeline has data to summarize.
3. **Daily cron** (e.g. `30 22 * * *`, `deliver='telegram'`): read today's journal file, summarize the 5 fields per category, append a "Daily Summary" section, deliver.
4. **Weekly cron** (e.g. `0 20 * * 0`, `deliver='telegram'`): aggregate last 7 daily files, surface RECURRING struggles + wins, write `~/.hermes/journal/weekly/YYYY-Www.md`, deliver.

## Cron anatomy (hermes)
- `action='create'`, `schedule='30 22 * * *'` (daily) or `'0 20 * * 0'` (weekly).
- `deliver='telegram'` — verify by checking an existing job's `last_status: ok` before trusting a new one.
- Prompt must be self-contained: reads journal files and ONLY summarizes what's recorded (no fabrication). Pin `cd /home/deeone` before mcporter/config calls if journal references agent-reach (config resolution is CWD-based; stray /tmp configs cause "Unknown MCP server" errors).

## Pitfalls
- Cron summarizes only what's recorded — never fabricate. If no entry for a day, note "no structured journal entry".
- Dependency: the agent must write the daily entry on working days. Cron alone can't create content from nothing.
- Weekly job's first run may be premature (created on Sunday fires hours later with one day of data). Offer to pause/re-enable, or let it smoke-test.
- Don't re-surface stale notifications as failures. A killed foreground process's buffered "Error: write EPIPE" is not a live error once the persistent (systemd) service is verified active.

## This session (reference)
- Created `/home/deeone/.hermes/journal/{daily,weekly}`.
- Two cron jobs: daily `6f1f3de69b8d` (22:30), weekly `54d48a51c795` (Sun 20:00), both `deliver=telegram` (verified working).
- Seed entry for 2026-08-09 covering Agent Reach/LinkedIn, Manim/DSA, tgforwarder, job search, PyPI win (tgforwarder live on PyPI).
