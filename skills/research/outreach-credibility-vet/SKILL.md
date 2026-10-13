---
name: outreach-credibility-vet
description: Vet a cold outreach email; resolve sender domain.
---

# Outreach Credibility Vet

Recurring task for this user: cold recruiter / visa / sales emails land in Gmail and
get forwarded with "who is this / is it legit?" The goal is a fast, evidence-based
credibility verdict — NOT a snap "scam" or "safe" call — plus a shareable artifact
for discussion.

## The core correction (learned the hard way)
A bare-domain search + NotebookLM `research` can MISS the real brand because a
sender's domain often **301-redirects** to a different, legitimate site. In one
session the sender was `kate@hqdreem.com` ("HQ Dreem") and the first pass concluded
"no verifiable web presence." The user then supplied `idreem.com` — which turned out
to be the target of a `hqdreem.com` 301 redirect, i.e. **Dreem (Dreem Relocation
Inc.)**, a real AI immigration platform (founder Dmitri Litvinov, ex-Uber/Rakuten;
200+ clients; O-1A/EB-1A). Lesson: **never write "no presence / likely scam" from a
single bare-domain search.** Always resolve redirects first.

## Workflow
1. **Extract the facts from the email.** Sender name, email (note the DOMAIN), claimed
   role/company, what they're pitching, the hook (e.g. "free assessment"), and the
   outreach pattern (1-touch vs 2-touch follow-up). Use `gws gmail`:
   - Find it: `gws gmail users messages list --params '{"q":"subject:<keyword>"}'`
     (there is NO `+read`; read via `gws gmail users messages get --params '{"id":"<id>","format":"full"}'`).
   - NOTE: the gws-gmail skill documents a `+read` command that the CLI rejects
     (`unrecognized subcommand`); use the raw `users messages get` API instead.
2. **Resolve the sender domain (CRITICAL).** Run, in parallel:
   - `curl -sI https://<domain>/` → look for `location:` 301/302 redirects. Follow
     mentally to the FINAL host. That final host is the brand to research.
   - `whois <domain>` → Creation Date (newer = younger operation), Registrar,
     Name Server (shared Cloudflare IPs across related domains is a clue they're the
     same operator), Registrant (often Domains By Proxy / privacy).
   - `dig +short <domain>` → IPs; compare to the redirect-target's IPs.
3. **Cross-check the claimed brand vs reality.** If the email says "HQ Dreem" but the
   site is "Dreem," note the naming mismatch. Read the real site (web_extract) for:
   founder, legal entity, services offered, "are we a law firm?" disclaimer,
   testimonials, press. Search `"<claimed person name>" <company>` — if the named
   sender has ZERO public footprint on the company's site/team/LinkedIn/press, that is
   the RESIDUAL RISK (company legit, specific sender unverified).
4. **Write the verdict as TWO separate claims:**
   - *Company/brand:* real & matches the pitch, OR unverifiable, OR red-flagged.
   - *Sender identity:* verified via official channel, OR unverified (name/email not
     found on the real company). Never merge these.
5. **Enrich with NotebookLM (optional but recommended).** See the NLM pitfalls below —
   research FIRST, then generate. Add the email thread + the real site URL as sources.
6. **Produce artifacts for discussion:** a branded infographic + a slide deck (see
   NLM pitfalls for generation/download). Optionally draft a *verification* reply that
   asks the sender to confirm via an official channel (e.g. `ask@<real-domain>`) and
   to provide the attorney's name / state bar number before any passport/SSN/financial
   data is shared.

## Red-flag vs green-flag signals (keep both sides)
- Green: real registered company, matching services, founder with verifiable background,
  press coverage, detailed testimonials, clear "not a law firm / attorney-reviewed"
  disclaimer, official contact on the real domain.
- Red / residual-risk: sender name absent from the company's public footprint; domain
  naming mismatch ("HQ Dreem" vs "Dreem"); generic shared mailbox; free-assessment hook
  used to collect personal data; pressure to share passport/SSN/financials before identity
  is verified.

## NotebookLM tooling pitfalls (when enriching / generating)
- **REGENERATION polling must filter by the NEW artifact ID.** `nlm studio status`
  returns ALL artifacts, including previously-completed ones. A global `grep completed`
  will match an OLD infographic/slide still in the list and falsely report done while the
  new ones are `unknown`. Capture the IDs printed at `create` time and filter:
  `jq -r --arg id "$NEW_ID" '.[] | select(.id==$id) | .status'`.
- **`nlm source add --file <path>` can fail with `NOT_FOUND`** for user-home paths
  (e.g. `~/Desktop/...`): "File paths must be accessible on the machine running nlm."
  Copy the file to `/tmp` first, then add from there.
- **`nlm research start` is server-side and outlives the 60s CLI timeout.** If the
  foreground call times out, the task is still running server-side. A second `research
  start` correctly refuses with "Research already in progress" + a Task ID — use that
  Task ID for `nlm research status` / `nlm research import`. Don't treat the refusal as
  failure.
- **Brand a generated infographic with a local PNG** using a circular badge compositor
  (`nlm-productivity` owns `scripts/composite_badge.py` after `hermes curator adopt
  nlm-productivity`); generic call: `python3 composite_badge.py <brand.png> <infographic.png>`.

## See also
- `references/dreem-case-study.md` — full worked example (hqdreem.com → idreem.com / Dreem
  visa outreach), the exact commands run, and the corrected verdict. Use as the template
  for future outreach-vetting sessions.
- `gws-gmail` skill — for `+triage` scanning and the actual `users messages get` read path.
- `nlm-productivity` skill — full NotebookLM generation/download command surface. Recommend
  `hermes curator adopt nlm-productivity` so its tooling pitfalls can be patched in place.
