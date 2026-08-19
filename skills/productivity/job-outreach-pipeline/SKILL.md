---
name: job-outreach-pipeline
description: "Dayo job pipeline: Exa, SpiderFoot, Sheets board, Gmail."
version: 1
author: hermes
license: mit
metadata:
  hermes:
    tags: [job-search, outreach, spiderfoot, google-sheets, netlify, osint, dayo]
    related_skills: [agent-reach, gws-gmail]
---

# Job Outreach Pipeline (Dayo / dbillion inc)

## When to Use
Use for ANY task touching Dayo's Java AI job-lead automation: collecting leads, scoring/fit,
SpiderFoot company recon, the JobFit Board, Gmail outreach, or reply tracking. The system is
already built and verified — extend it, do not rebuild.

Recurring system for Dayo's Java AI job hunt. Verified end-to-end in session 2026-08-15/16.
All pieces are real and working — do not rebuild from scratch; extend what exists.

## Architecture (verified)
1. **Collect** Java AI leads via Exa (scoped `mcp-cli`) → `/home/deeone/.hermes/scripts/jobhunt-collect.sh`.
2. **Score + board** → `jobhunt-board.py` parses leads, computes FitScore/Grade/Value, writes a `JobBoard` tab in the Sheet.
3. **Company recon** → SpiderFoot (docker compose) scans the hiring company's domain (company-level only).
4. **Track** → Google Sheet `JobBoard` tab is source of truth; a Netlify static Kanban (`https://jobfit-board.netlify.app`) reads it + drag persists via a Function.
5. **Outreach** → `jobhunt-outreach.py` drafts a personalized email (references DSA Hub + tgforwarder), sends via `gws gmail +send` (dry-run default). LinkedIn hiring-manager lookup via `agent-reach`/`mcporter` is the preferred contact path.
6. **Track replies** → `jobhunt-track.py` scans Gmail for responses, marks `responded`/`successful`.

## Key paths
- Sheet ID: `1rmOzAFisZGWb4vI0KMQY91UbiiM1ipiS8Ol0vCy3Nfw` (tabs: `Outreach`, `JobBoard`, `BoardChat`)
- Scripts: `/home/deeone/.hermes/scripts/jobhunt-*.py` + `jobhunt-cron.sh`
- SpiderFoot: `/home/deeone/spiderfoot` (v4.0.0, port 5001)
- Board repo: `/home/deeone/job-board-netlify` (Netlify, dbillion team)
- SA key (write access): `/home/deeone/.hermes/secrets/jobfit-board-sa.json`

## Safe-scope rules (do NOT violate)
- **OSINT is company-level only.** Scan the hiring company's domain. NEVER target a person, scrape personal emails/socials, or use `sfp_accounts`/`sfp_name`/`sfp_email`/leak modules. A corporate email from public RIR/WHOIS (e.g. `firstname.lastname@company.com`) is acceptable.
- **Email sends default to dry-run.** Real sends only with `JOBHUNT_LIVE=1`. `gws gmail +send --dry-run` first.
- **No fabricated personal emails.** Derive `firstname.lastname@company-domain` only when no listed email; mark `guessed-linkedin`. Skip + log `needs_contact` otherwise.

## User preferences for tooling built for him (embed in any deliverable)
- Present options as an **A/B (or A/B/C) comparison table** with pros/cons, THEN pick the best — don't just pick.
- The artifact must be **editable by both him and the agent** (Sheet is the natural source of truth).
- Include an **in-app chat-to-agent** panel so he can talk to you from the tool.
- **Verify a CLI is actually absent before declaring it missing** — `find / -name <bin> 2>/dev/null` and check common SDK dirs. A failed `PATH` lookup is NOT proof of absence (gcloud was at `/home/deeone/google-cloud-sdk/bin` despite `which` failing).
- **Don't dismiss a loaded skill's capability without testing it.** agent-reach's LinkedIn path works via `mcporter`; verify before concluding "blocked".

## Step-by-step (run a scan + log it)
1. Pick the company from the `JobBoard` tab (first row = Infios in the verified run).
2. Resolve its real domain (aggregator postings hide it; the job title's "at X" is the employer).
3. Start SpiderFoot: `echo "start <domain> -m <company-modules> -n <name>" | python3 sfcli.py -s http://127.0.0.1:5001`
4. Poll: `echo "scaninfo <SID>" | python3 sfcli.py -s http://127.0.0.1:5001`
5. Dump: `echo "export <SID>" | python3 sfcli.py -s http://127.0.0.1:5001` → parse `@<domain>` emails (these are corporate, from RIR).
6. Write findings to the Sheet row via `POST https://jobfit-board.netlify.app/api/update` with `scanstatus` + `notes`.

## Pitfalls
- `gh search repos --json` does NOT accept `stargazerCount` or `nameWithOwner` (use `stargazersCount`, `name`,`owner`). For exact star counts, `gh api repos/{owner}/{name}`.
- `gws` is a node script — call via `node $(realpath)`; bare `gws` on PATH may fail under subprocess. `gws sheets spreadsheets values append` needs `range=Tab!A:J` in `--params` (not the `+append` helper).
- Netlify CLI crashes on a top-level-await bug under bun/Node here; pin `command` in `netlify.toml` and set env vars WITHOUT `--scope functions` (use `All` context).
- SpiderFoot `sfcli.py` command is `start`, NOT `scan`.

## References (condensed, verified)
- `references/spiderfoot-recon.md` — docker compose + sfcli commands, company-level module list, result parsing.
- `references/github-search.md` — `gh` search pattern + field-name gotchas.
- `references/gws-sheets.md` — working `gws` Sheets/Drive/Gmail command patterns.
- `references/netlify-sa-deploy.md` — static + Function + Service Account write pattern.

## Note for curator
`agent-reach` (user-owned, `~/.hermes/skills/agent-reach/`) should be patched with the working `mcporter` LinkedIn commands (search_people/get_company_profile/get_person_profile). It is NOT mine to edit — recommend `hermes curator adopt agent-reach` then patch, or ask the user.
