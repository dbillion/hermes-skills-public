# gws (Google Workspace CLI) — verified command patterns

`gws` is a node script. Under subprocess call via `node $(realpath /home/deeone/.local/bin/gws)`
or the resolved path `/home/deeone/.nvm/versions/node/v25.6.1/lib/node_modules/@googleworkspace/cli/run-gws.js`.
Bare `gws` on PATH may fail in subprocess.

## Sheets
- Read: `gws sheets +read --spreadsheet <ID> --range "Tab!A1:J10"`
- Write: `gws sheets spreadsheets values update --params '{"spreadsheetId":..,"range":"Tab!A1","valueInputOption":"RAW"}' --json '{"values":[["x"]]}'`
- Append: `gws sheets spreadsheets values append --params '{"spreadsheetId":..,"range":"Tab!A:J","valueInputOption":"RAW"}' --json '{"values":[[...]]}'`
  (the `+append` helper writes to first sheet only — use raw `spreadsheets values append` with tab-qualified range)
- Add tab: `gws sheets spreadsheets batchUpdate --json '{"requests":[{"addSheet":{"properties":{"title":"Tab"}}}]}'`

## Drive (share)
- Public read: `gws drive permissions create --params '{"fileId":..}' --json '{"type":"anyone","role":"reader"}'`
- Share with SA (write): `--json '{"type":"user","role":"writer","emailAddress":"<sa>@<proj>.iam.gserviceaccount.com"}'`

## Gmail
- Dry-run send: `gws gmail +send --to x@y --subject s --body b --dry-run`
- Triage (read replies): `gws gmail +triage`
