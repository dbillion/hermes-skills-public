# Career — LinkedIn (hiring-manager lookup, jobs)

## VERIFIED WORKING BACKEND (2026-08): `mcporter` → `linkedin` (linkedin-scraper-mcp)

The old `opencli linkedin people-search` path is DEAD (Browser Bridge extension
not connected → exit code 69, "LinkedIn people-search requires the Browser
Bridge extension"). Do NOT use it. The live backend is the `linkedin` MCP server
exposed via `mcporter`.

Confirm with: `agent-reach doctor --json` → expect `linkedin` backend `status: ok`
via `linkedin-scraper-mcp` (tier 2), `mcporter list` shows `linkedin` with ~19 tools.

## Hiring-manager lookup chain (verified end-to-end)

Goal: given a company name, find a named hiring manager / recruiter and their
profile (no personal email is ever fabricated).

1. **Resolve company → URN + domain**
   ```bash
   mcporter call 'linkedin.get_company_profile(company_name: "Precisely")'
   ```
   Returns `references.company_urn` (e.g. `3722186`) and the company domain
   (e.g. `preciselycontracts.com`). NOTE: aggregator job-board names may NOT
   match the real hiring company — verify the domain.

2. **Search people at that company (hiring managers / recruiters)**
   ```bash
   mcporter call 'linkedin.search_people(keywords: "engineering manager", current_company: "3722186")'
   ```
   - `current_company` takes the **URN id** (string), NOT the name.
   - Returns names + LinkedIn URLs + titles. Pick titles containing
     "hiring"/"recruiter"/"engineering manager"/"head of".

3. **Get a person's profile (confirm + capture any listed email)**
   ```bash
   mcporter call 'linkedin.get_person_profile(linkedin_username: "oscarklink")'
   ```
   - Returns full profile (name, title, company, about, activity).
   - Email is RARELY present. If absent, derive `firstname.lastname@<company-domain>`
     and mark it `guessed` — never fabricate a personal address.

## Job search
- `mcporter call 'linkedin.search_jobs(keywords: "...", location: "...")'` works,
  but job-board aggregators (jobgether/hiretik/remoterocketship) dominate results
  and their "company" field is muddy. Prefer resolving the REAL company domain
  before any outreach.

## Pitfalls
- `opencli linkedin people-search` → dead (error 69). Use `mcporter` + `linkedin`.
- `search_people` arg is `keywords` (plural) + `current_company` (URN), NOT
  `keyword`/`limit`.
- `get_company_profile` arg is `company_name`, NOT `linkedin_username`.
- CUL cost: each LinkedIn call is ~10–30s and consumes daily quota — cache URNs
  locally (e.g. `/tmp/linkedin_urn_cache.json`) across runs.
- Never email a fabricated personal address; aggregator-inbox guesses bounce.
