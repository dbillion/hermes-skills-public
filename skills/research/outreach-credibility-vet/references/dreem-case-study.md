# Case Study: hqdreem.com / "Kate Zhi" visa outreach → idreem.com (Dreem)

Worked example of the outreach-credibility-vet workflow. Use as the template.

## Input
Cold email thread to Oludayo Adeoye, subject "Re: Thought this might help with your visa":
- Sender: Kate Zhi <kate@hqdreem.com>, self-titled "Immigration Expert"
- Company claimed: HQ Dreem (hqdreem.com)
- Pitch: O-1A (non-immigrant, extraordinary ability) and EB-1A (green card)
- Hook: free in-depth attorney assessment (written review + strategy notes)
- Pattern: 2-touch cold email (Jun 17 + Jun 19 2026)

## WRONG first pass
Bare domain + NLM `research` → "no verifiable web presence for hqdreem.com or Kate Zhi"
→ drafted an infographic/deck saying company was unverifiable / likely risky.

## CORRECTION (user supplied idreem.com)
Domain resolution proved the first pass wrong:

```
$ curl -sI https://hqdreem.com/
HTTP/2 301
location: https://idreem.com/        <-- 301 redirect to the REAL brand

$ whois idreem.com
Creation Date: 2023-01-19
Registrant Organization: Domains By Proxy, LLC
Name Server: HUNTS.NS.CLOUDFLARE.COM / RIHANA.NS.CLOUDFLARE.COM

$ whois hqdreem.com
Creation Date: 2026-02-04            <-- younger redirect domain
Name Server: ANDY.NS.CLOUDFLARE.COM   <-- same Cloudflare operator family
$ dig +short hqdreem.com  -> 104.21.62.228, 172.67.139.233
$ dig +short idreem.com   -> 172.67.163.135, 104.21.42.160, 104.21.62.228, 172.67.139.233
                            ^^^^^^^^^^^^ shared IPs = same operator
```

## What idreem.com actually is (web_extract + web_search)
- **Dreem (Dreem Relocation Inc.)** — AI-powered immigration platform, Delaware
  (919 N Market St, Wilmington), founder **Dmitri Litvinov** (ex-Uber/Rakuten).
- 200+ clients, 1,000+ cases. Services O-1A / EB-1A / EB-2 NIW / L-1A — **matches the
  email pitch exactly**.
- Explicitly **NOT a law firm** — document prep + U.S.-licensed attorneys; money-back
  guarantee for qualified O-1A. Real testimonials + press (Pulse2 interview) + LinkedIn
  (11–50 employees).
- Official contacts use `@idreem.com` (e.g. `ask@idreem.com`), NOT `@hqdreem.com`.

## Residual risk (the part that stayed unverified)
- **"Kate Zhi" / `kate@hqdreem.com` has ZERO public footprint** on Dreem's site, team
  page, LinkedIn, or press. The founder is Dmitri Litvinov; no "Kate" appears.
- Brand naming mismatch: email says "HQ Dreem," company is "Dreem."

## Corrected verdict (two claims, never merged)
- *Company/brand:* REAL and matches the visa pitch — legitimate operation.
- *Sender identity:* UNVERIFIED — named sender not found on the real company. Verify via
  official channel (`ask@idreem.com` or Dreem LinkedIn) and ask for the attorney's name /
  state bar number before sharing passport / SSN / financial data.

## Commands that worked (reusable)
```
# read the email (no +read subcommand exists)
gws gmail users messages list --params '{"q":"subject:visa"}'
gws gmail users messages get --params '{"id":"<id>","format":"full"}'

# domain resolution
curl -sI https://<domain>/          # catch 301 location:
whois <domain>                      # creation date, registrar, NS
dig +short <domain>                 # compare IPs to the redirect target

# NotebookLM enrichment
NB_ID=$(nlm notebook create "Visa Outreach Analysis" --json | jq -r .notebook_id)
cp thread.txt /tmp/ && nlm source add "$NB_ID" --file /tmp/thread.txt --wait
nlm source add "$NB_ID" --url https://idreem.com/ --wait
nlm research start "<query>" --mode deep --notebook-id "$NB_ID" --auto-import   # server-side; poll w/ task id
nlm infographic create "$NB_ID" --orientation landscape --style professional --focus "..." --confirm
nlm slides create "$NB_ID" --format detailed_deck --length default --focus "..." --confirm
# download by NEW artifact id (filter studio status by id, not global grep)
nlm download infographic "$NB_ID" --id <id> --output out.png
nlm download slide-deck  "$NB_ID" --id <id> --output out.pdf
```

## Artifacts produced
- `/home/deeone/Desktop/visa_artifacts/infographic_v2.png` (panda badge composited)
- `/home/deeone/Desktop/visa_artifacts/discussion_deck_v2.pdf` (6 slides)
