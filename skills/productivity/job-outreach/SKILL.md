---
name: job-outreach
description: >-
  Automate Java AI job-lead outreach, scoring, and tracking.
metadata:
  class_level: true
  version: "1.0.0"
  author: "hermes"
  license: "mit"
  hermes:
    tags: ["job-search", "outreach", "linkedin", "spiderfoot", "google-sheets", "netlify"]
    related_skills: ["agent-reach"]
---

# Job Outreach Pipeline (Java / AI roles)

## When to Use
- User wants automated job hunting / lead collection for Java or AI roles.
- User wants a job-tracking board (fit score, tech, status) editable by both.
- User wants to find a hiring manager and email them referencing their projects.
- User wants company OSINT enrichment (SpiderFoot) or a Netlify Kanban view.

Repeatable architecture for Dayo's job-search automation. Env-specific values
(Sheet IDs, token paths) are placeholders — substitute the user's real ones.

## Verified workflow (tested 2026-08)

1. **Collect** Java AI job leads via Exa (scoped `mcp-cli`):
   `mcp-cli -c <scope> call exa web_search_exa '{"query":"Java AI backend engineer jobs Canada remote hiring 2026","numResults":8}'`
   Parse blocks split on `Title:` → extract title/URL/company/location.
   Company regex: `\bat\s+([A-Za-z0-9&.]+ …)(?:\s*[|\-–]|@|$)`.

2. **Score right-fit** against the candidate profile (Senior Java Architect:
   Java/Spring/AWS/AI/ML/distributed; Canada/remote). Weighted FitScore 0–100,
   grade A≥70 / B≥50 / C≥35. Map value props per role stack
   (tgforwarder for Java/distributed, DSA Hub for TS/AI, secure-EdTech for security).

3. **Track in Google Sheet** — a `JobBoard` tab with columns
   Date,Title,Company,Location,Technologies,Seniority,Remote,FitScore,Grade,
   ValueI Offer,Status,ScanStatus,Notes. Status drives Kanban columns
   (new→scanning→contacted→responded→offer). Write via `gws sheets
   spreadsheets values append/update` (list-form subprocess, no shell=True).

4. **Find hiring manager** → use `agent-reach` LinkedIn via `mcporter` (see
   agent-reach/references/career.md — NOT opencli). Chain:
   get_company_profile → URN → search_people(current_company=URN) →
   get_person_profile. Never fabricate a personal email.

5. **Enrich company (OSINT)** → SpiderFoot (docker compose, port 5001).
   Company-domain ONLY, never personal emails/socials. Scan, pull real domain
   + published role-based contacts, write back to the Sheet row's ScanStatus.

6. **Surface as a board** → static Netlify site reads the Sheet via the
   secret-free public CSV export:
   `https://docs.google.com/spreadsheets/d/<ID>/gviz/tq?tqx=out:csv&sheet=JobBoard`
   (Sheet must be shared "anyone with link: viewer"). Drag-drop + chat panel
   call Netlify Functions; vendored SortableJS (no CDN).

## PITFALLS / OPEN STEPS (NOT yet verified — do not present as working)
- **Netlify deploy**: the `netlify` CLI crashed on a top-level-await bug under
  bun/Node 25 and prompts interactively (can't run headless). The static site
  + Function code is built and the read path is proven, but the production
  deploy was NOT completed this session. Retry with a stable CLI or have the
  user run `netlify deploy --prod --functions functions` in a normal terminal.
- **Write-back + chat persistence** need a Google Service Account JSON as a
  Netlify env var (`GOOGLE_SA_JSON`); SA creation needs `gcloud`/a GCP project
  (absent here). Until then the board is read-only + optimistic-local drag.
- Aggregator leads (jobgether/hiretik/remoterocketship) have muddy "company"
  names and no real email — resolve the REAL company domain before outreach.
- `gws` is a symlink; call it via `node <realpath>/run-gws.js`, never bare.
- `gh search repos --json` star field is `stargazersCount` (not `stargazerCount`);
  `addSheet`/values calls need `--json` with a JSON *string* (json.dumps), not a dict.

## User constraints (hard)
- No fabricated personal emails. Aggregator inboxes are never emailed.
- Outreach defaults to dry-run; real sends only with explicit `JOBHUNT_LIVE=1`.
- SpiderFoot: company-level only, never individuals.
