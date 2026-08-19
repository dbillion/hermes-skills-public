# gws CLI gotchas (verified 2026-08-15)

The `gws-gmail` SKILL.md has a **typo**: it shows `gws gmail send`. The real subcommand
is `gws gmail +send` (the `+` prefix convention). `gws gmail send` returns:
`error: unrecognized subcommand 'send' ... a similar subcommand exists: '+send'`.

## Verified commands
- Send (with safe dry-run): `gws gmail +send --to <email> --subject <s> --body <b> --dry-run`
- Triage (the only inbox scan): `gws gmail +triage`  (no `list` command exists)
- Reply: `gws gmail +reply <message_id> --body <text>`

## From Python subprocess
gws is a Node script. DO NOT call the symlink directly via Popen — it fails with
"Cannot find module". Use the real JS path:
`/home/deeone/.nvm/versions/node/v25.6.1/lib/node_modules/@googleworkspace/cli/run-gws.js`
invoked as `node <realpath> <args>`. Pass args as a list (no `shell=True`) to avoid
injection from job titles/companies.

## Sheets writes
- `gws sheets +append` IGNORES `--range` and appends to the spreadsheet's FIRST tab only.
- To append to a specific tab, use the raw API:
  `gws sheets spreadsheets values append --params '{"spreadsheetId":"<ID>","range":"Outreach!A:J","valueInputOption":"RAW"}' --json '{"values":[[...]]}'`
- Create a tab first if missing: `gws sheets spreadsheets batchUpdate --params
  '{"spreadsheetId":"<ID>"}' --json '{"requests":[{"addSheet":{"properties":{"title":"Outreach"}}}]}'`
- Write headers: `gws sheets spreadsheets values update --params
  '{"spreadsheetId":"<ID>","range":"Outreach!A1:J1","valueInputOption":"RAW"}' --json
  '{"values":[[...10 headers...]]}'`

## mcp-cli path
`mcp-cli` lives at `/home/deeone/.local/bin/mcp-cli` (NOT under the nvm node bin dir).
Use a scoped config to avoid loading the whole 50+ server fleet (which hangs): pass
`-c <scope.json>` with only the servers you need (exa, etc.).
