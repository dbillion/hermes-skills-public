---
name: gws-google-sheets
description: >
  Use when the user wants to find, read, analyze, or update Google Sheets
  spreadsheets through the local gws CLI.
---

# Google Sheets via `gws`

Use `gws sheets ...` and `gws drive ...` for spreadsheet work.

## Finding Spreadsheets

Search with a Sheets MIME type filter:

```bash
gws drive files list --params '{"q":"mimeType='\''application/vnd.google-apps.spreadsheet'\'' and name contains '\''Budget'\'' and trashed=false","fields":"files(id,name,webViewLink,modifiedTime)","pageSize":10}'
```

For full-text search, use `fullText contains` instead of `name contains`.

## Reading Data

Inspect metadata:

```bash
gws sheets spreadsheets get --params '{"spreadsheetId":"<id>","fields":"spreadsheetId,properties.title,sheets.properties"}'
```

Read a specific range with A1 notation:

```bash
gws sheets spreadsheets values get --params '{"spreadsheetId":"<id>","range":"Sheet1!A1:D10"}'
```

Use `--format csv` for export-style output when helpful.

## Updating Data

Preview updates and get explicit confirmation first. Then use the schema to
confirm the exact request body:

```bash
gws schema sheets.spreadsheets.values.update --resolve-refs
```

Prefer narrow range updates over broad sheet writes.
