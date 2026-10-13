---
name: job-outreach-automation
description: Automate job-lead outreach and response tracking.
version: 1
author: hermes
license: mit
metadata:
  openclaw:
    tags: [job-hunt, outreach, gmail, sheets, exa, automation]
    related_skills: [gws-gmail, agent-reach]
---

# Job Outreach Automation

## When to Use
- User wants to find jobs AND email hiring managers / recruiters (not just collect links).
- User says an existing job-hunt cron "just sends links" and wants it to go further: find
  the contact, reference their projects, send, and track replies.
- User wants a measurable outreach funnel (sent / responded / successful / bounced) logged
  to a Sheet.
- NOT for: hand-written cover letters, or LinkedIn posting/connecting.

End-to-end pipeline that turns collected job leads into personalized outreach emails
with full tracking — replacing the "dump links in chat" pattern with a logged,
measurable funnel (sent / responded / successful / bounced).

## Hard rules (non-negotiable)
1. **Never fabricate a person's email.** If no real contact surfaces, log the lead as
   `needs_contact` and skip sending. Do NOT invent `firstname.lastname@company.com`.
2. **Reject job-board / aggregator domains.** Leads from jobgether, hiretik,
   remoterocketship, indeed, linkedin, greenhouse, lever, ashby, workable, etc. have NO
   real hiring-manager address — emailing `careers@remoterocketship.com` reaches the
   board, not the company, and bounces (verified: 6 mailer-daemon failures). Only email a
   *real company domain*.
3. **Dry-run gate before every real send.** Always run `gws gmail +send --dry-run` first;
   only flip to a real send when the user explicitly enables it (e.g. `JOBHUNT_LIVE=1`).
   Cron jobs stay dry-run by default.
4. **Log to Sheet, not chat.** The cron summary is short; the detail lives in the
   Outreach tab. Don't paste long descriptions into Telegram.

## Pipeline
1. **Collect** Java AI job leads via Exa (scoped mcp-cli, see references/exa-lead-parsing).
2. **Parse** title / company / location / link. Company often needs extraction from the
   title ("at X", "X | rest") — see scripts/jobhunt-outreach.template.py.
3. **Find contact** best-effort: explicit email in listing -> real company domain guessed
   `careers@domain` -> else `needs_contact`.
4. **Draft** a personalized email referencing the candidate's REAL projects + 3 concrete
   value props. Keep it short; invite a forward if wrong inbox.
5. **Send** via `gws gmail +send` (dry-run first). See references/gws-gotchas for the
   correct command (the gws-gmail skill doc has a typo: it is `+send`, not `send`).
6. **Log** one row per lead to the Outreach Sheet tab (schema below).
7. **Track** responses: scan Gmail (`gws gmail +triage`), match reply From-domain to sent
   domains, mark `responded` / `successful` (interview/offer keywords) / `bounced`.

## Outreach Sheet schema (tab "Outreach")
Columns: `Date, Title, Company, Location, Link, ContactEmail, ContactSource,
Status, Subject, LastChecked`.
Status values: `needs_contact`, `dryrun_ok`, `sent`, `send_fail`, `responded`,
`successful`, `bounced`.

## Tool commands (verified)
- Exa (scoped): `mcp-cli -c <scope.json> call exa web_search_exa '{"query":...,"numResults":8}'`
- Gmail send: `gws gmail +send --to <email> --subject <s> --body <b> [--dry-run]`
- Sheet append (tab-qualified!): `gws sheets spreadsheets values append --params
  '{"spreadsheetId":<ID>,"range":"Outreach!A:J","valueInputOption":"RAW"}' --json '{"values":[[...]]}'`
- Gmail triage: `gws gmail +triage` (parse from col $2, skip header+separator)

## Pitfalls
- **Don't assume a tool is blocked — call it.** When an MCP/CLI looks unavailable, do a
  real scoped call before concluding it fails. The 21st-dev `generate` is paywalled, but
  `search`/`get_component` work free (2 retrievals/day).
- **`gws sheets +append` ignores `--range`** and appends to the first tab only. To write a
  specific tab, use `gws sheets spreadsheets values append` with a `range` param.
- **gws is a node script** — when calling from Python `subprocess`, pass the real JS path
  via `node`, not the symlink, or Popen fails. Use list-form args (no `shell=True`) to avoid
  injection from job titles.
- **Contact guessing to aggregators bounces** (verified). Gate on real-company-domain only.
- **Netlify redeploy**: `--team` is only valid with `--create-site`; for an existing site
  use `netlify deploy --prod` (no `--team`).

## References
- references/gws-gotchas.md — verified gws CLI corrections.
- references/exa-lead-parsing.md — Exa output format + parsing recipe.
- scripts/jobhunt-outreach.template.py — templated outreach engine.
- scripts/jobhunt-track.template.py — templated response tracker.
