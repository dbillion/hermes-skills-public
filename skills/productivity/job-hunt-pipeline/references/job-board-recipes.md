# Job Board Recipes (verified this session)

## 1. Google Sheet: create tab + make public-read + share with SA
```bash
GWS=/home/deeone/.nvm/versions/node/v25.6.1/lib/node_modules/@googleworkspace/cli/run-gws.js
NODE=/home/deeone/.nvm/versions/node/v25.6.1/bin
SID=<spreadsheetId>

# create tab (errors if it already exists — guard with a tab-exists check first)
"$NODE/node" "$GWS" sheets spreadsheets batchUpdate \
  --params "{\"spreadsheetId\":\"$SID\"}" \
  --json '{"requests":[{"addSheet":{"properties":{"title":"JobBoard"}}}]}'

# make whole sheet public-read (anyone with link)
"$NODE/node" "$GWS" drive permissions create \
  --params "{\"fileId\":\"$SID\"}" \
  --json '{"type":"anyone","role":"reader"}'

# share with a Service Account as writer (for Function write-back)
"$NODE/node" "$GWS" drive permissions create \
  --params "{\"fileId\":\"$SID\"}" \
  --json '{"type":"user","role":"writer","emailAddress":"<sa-email>"}'

# append a row to a named tab (range-qualified)
"$NODE/node" "$GWS" sheets spreadsheets values append \
  --params "{\"spreadsheetId\":\"$SID\",\"range\":\"JobBoard!A2:N\",\"valueInputOption\":\"RAW\"}" \
  --json '{"values":[["...row..."]]}'
```

## 2. Read Sheet from a static site (no API key)
```
https://docs.google.com/spreadsheets/d/<SID>/gviz/tq?tqx=out:csv&sheet=JobBoard
```
Parse with a real CSV parser (Python `csv`), NOT `awk -F,` — the Technologies column has quoted commas.

## 3. Service Account for Netlify Function write-back
```bash
gcloud iam service-accounts create jobfit-board-sa --display-name="JobFit Board Sheet Writer" --project=<proj>
gcloud iam service-accounts keys create sa-key.json --iam-account=jobfit-board-sa@<proj>.iam.gserviceaccount.com --project=<proj>
netlify env:set GOOGLE_SA_JSON "$(cat sa-key.json)"   # NOT committed, NOT in web dir
```
Function: RS256 JWT (iss=client_email, scope=sheets, exp=now+3600) -> POST oauth2.googleapis.com/token -> PUT `sheets.googleapis.com/v4/spreadsheets/<SID>/values/JobBoard!K<row>?valueInputOption=RAW` `{"values":[[status]]}`. Row = 1-based CSV line (NO +1).

## 4. Netlify deploy (avoid interactive crash)
`netlify.toml`:
```toml
[build]
  publish = "."
  command = "echo 'static site, no build'"
  functions = "functions"
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/api/:splat"
  status = 200
```
`netlify deploy --prod --functions functions`. Set env WITHOUT `--scope` (silently fails for prod otherwise).

## 5. agent-reach / LinkedIn hiring-manager lookup
```bash
mcporter call 'linkedin.get_company_profile(company_name: "Cresta")'   # -> company_urn
mcporter call 'linkedin.search_people(keywords: "hiring manager", current_company: "<URN>")'
mcporter call 'linkedin.get_person_profile(linkedin_username: "<u>")'  # confirm + maybe email
```
OpenCLI Browser Bridge `people-search` is DEAD (error 69) — use `mcporter` + `linkedin-scraper-mcp`.

## 6. SpiderFoot (company-only OSINT)
```bash
cd /home/deeone/spiderfoot
docker compose up -d --build     # port 5001, v4.0.0
# control: sfcli.py (CLI -> :5001) or REST /query
```
Scan company DOMAIN only; exclude personal-data modules. Feed real domain + published careers@/press to board ScanStatus.
