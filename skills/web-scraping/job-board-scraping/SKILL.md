---
name: job-board-scraping
description: Scrape live job listings via the scrapling CLI (WWR recipe).
category: web-scraping
---

# Job Board Scraping with the scrapling CLI

Use when the user asks to "check for jobs", "find <role> openings", "scrape job listings",
or "what <stack> roles are available" — especially remote/data-engineering roles.

`scrapling` is a GENERIC web fetcher/extractor. It has NO built-in jobs command. You must
point it at a job board's URL and parse the result yourself. See `references/scrapling-cli.md`
for the full command reference and the exact working parser recipe.

## Critical rules (learned the hard way — follow or waste an hour)

1. **Output file extension MUST end in `.md`, `.html`, or `.txt`.** Saving as `.json` raises
   `ValueError: Unknown file type`. Even when fetching a JSON API, save as `.txt` then parse.
2. **JSON API responses get mangled by scrapling's writer.** Remotive, Jobicy, Arbeitnow, and
   HN Algolia all return JSON with RAW newlines inside string values (e.g. in `description`).
   scrapling writes these verbatim, producing INVALID / truncated JSON that `json.loads` rejects
   (`Invalid control character`, `Unterminated string`). DO NOT rely on `get`/`stealthy-fetch`
   for these APIs. Prefer **server-rendered HTML via `scrapling extract fetch`** (headless
   Chromium) and parse the HTML with regex.
3. **First time using `fetch`/`stealthy-fetch`: install Chromium inside scrapling's venv.**
   Command: `~/.local/share/pipx/venvs/scrapling/bin/python -m playwright install chromium`
   (the scrapling binary lives at `~/.local/bin/scrapling`; its venv is the pipx one above).

## Board coverage (verified 2026-08-09)

| Board | Path tried | Result |
|---|---|---|
| RemoteOK API (`/api?tags=`) | `get`/`stealthy-fetch` | BLOCKED — returns only a legal-disclaimer stub |
| Indeed (`/jobs?q=...`) | `fetch` | 403 (bot protection) |
| Remotive (`/api/remote-jobs`) | `get` | JSON with raw newlines → unparseable |
| Jobicy (`/api/v1/remote-jobs`) | `get` | Wrong slug → landing page; JSON also newline-broken |
| Arbeitnow (`/api/job-board-api`) | `get` | JSON with raw newlines → unparseable |
| HN Algolia (`/api/v1/search`) | `get` | JSON with raw newlines → unparseable |
| **We Work Remotely** (`/remote-jobs/search?term=`) | `fetch` | **WORKS** — server-rendered HTML, parseable |

→ **Default to We Work Remotely** for reliable live listings. It has no data-specific category
page, but its search endpoint returns real, server-rendered cards.

## Working recipe — We Work Remotely

1. Fetch (server-rendered, not JS-dependent):
   `scrapling extract fetch "https://weworkremotely.com/remote-jobs/search?term=data%20engineer" jobs_check/wwr_search.html --disable-resources --timeout 120000`
2. Parse with the regex recipe in `references/scrapling-cli.md` (split on
   `<li class="...new-listing-container..."`, extract `listing-link--unlocked` anchor → link,
   `href="/company/..."` → company, `new-listing__header__title` → title).
3. Dedupe by link; FILTER false positives — WWR matches on "engineer" broadly, so
   "Sales Engineer" / "Security Agent" SWE listings from Datadog etc. appear. Keep only
   titles containing data/analytics/ML/pipeline terms for a true data-engineering list.
4. Save the cleaned list to a `.txt` file and present it (title / company / link per role).

## Verification
- Re-run the fetch and confirm the HTML size is > 100 KB and contains
  `listing-link--unlocked` anchors before claiming results.
- Count extracted links; if < 3, the search term or board may have changed — retry with a
  broader term or fall back to another board.

## Pitfalls
- WWR search matches loosely: "data engineer" also returns Sales/Support Engineer roles.
  Always filter by title, never trust the raw hit count.
- Saved `.txt` from a JSON API is NOT valid JSON — do not `json.load` it. Use `fetch` + HTML.
- RemoteOK/Indeed block programmatic access; don't burn time retrying — go straight to WWR.

## Tooling reality check — NotebookLM is NOT a job scraper

If the user asks to "use NotebookLM deep research to find jobs on LinkedIn" (or any
live job list), this is the WRONG tool and you will waste ~5 min. Verified 2026-08-09:
- `nlm research start "<query>" --mode deep` performs **web source discovery**, not
  scraping. It returns articles, guides, recruiter/agency lists, and remote job-board
  *links* — NOT a live, clickable list of individual LinkedIn postings.
- `nlm research start ... --auto-import` does NOT actually import. The task completes
  (`nlm research status <notebook_id>` → "Status: completed, Sources found: N"), but you
  MUST then run `nlm research import <notebook_id> <task_id>` to add the sources.
- The genuinely current LinkedIn listings come from **scrapling + the auth-cookie recipe
  above** (this skill), not from NotebookLM.
→ Use NotebookLM research only when the user wants curated *resources/how-to* about a topic.
  For actual job postings, use the scrapling LinkedIn (or WWR) recipe in this skill.
