---
name: google-workspace-gws
description: >
  Use when the user asks to work with Google Workspace through the local gws
  CLI, including Drive, Docs, Sheets, Slides, Gmail, Calendar, Chat, Tasks,
  People, Forms, Keep, Meet, or Google Workspace workflows.
---

# Google Workspace via `gws`

Use the local `gws` CLI for Google Workspace work.

## CLI Basics

- Run `gws auth status` before remote Workspace work if authentication state is
  uncertain.
- Inspect a method before calling it with
  `gws schema <service.resource.method> --resolve-refs`.
- Call APIs with:

```bash
gws <service> <resource> [sub-resource] <method> --params '<json>' --json '<json>'
```

- `--params` is for path and query parameters.
- `--json` is for request bodies.
- `--upload <absolute-path>` uploads local media.
- `--output <absolute-path>` writes binary responses.
- `--format json` is the default; use `table`, `yaml`, or `csv` only when it
  helps the user.
- Use `--page-all --page-limit <n>` for paginated reads when needed.

## Session Context

At the beginning of Google Workspace sessions, establish user context when it is
relevant:

```bash
gws people people get --params '{"resourceName":"people/me","personFields":"names,emailAddresses"}'
```

For time-sensitive work, use the local system timezone or Calendar settings, and
display concrete dates and timezone abbreviations.

## Safety

Never execute writes without explicit user confirmation unless the user has
already clearly authorized the exact write. Writes include sending email,
creating/updating/deleting calendar events, modifying files, sharing files,
editing docs/sheets/slides, posting chat messages, and changing labels.

Before a write, show a short preview with the target, content, and consequences,
then wait for approval.

## Search And IDs

- Prefer Drive search with MIME filters for Workspace files.
- Do not manually extract IDs when a `gws` method accepts a URL. If a method
  requires an ID, use the exact ID from search results or metadata.
- Format multiple search results as numbered lists.

Common MIME filters:

```text
Google Docs: mimeType='application/vnd.google-apps.document'
Google Sheets: mimeType='application/vnd.google-apps.spreadsheet'
Google Slides: mimeType='application/vnd.google-apps.presentation'
Folders: mimeType='application/vnd.google-apps.folder'
```

## Useful Examples

List recent Drive files:

```bash
gws drive files list --params '{"pageSize":10,"fields":"files(id,name,mimeType,webViewLink,modifiedTime)"}'
```

Search Drive:

```bash
gws drive files list --params '{"q":"name contains '\''Budget'\'' and trashed=false","pageSize":10,"fields":"files(id,name,mimeType,webViewLink)"}'
```

Read a Sheet:

```bash
gws sheets spreadsheets values get --params '{"spreadsheetId":"<id>","range":"Sheet1!A1:D10"}'
```

List today's primary calendar events:

```bash
gws calendar events list --params '{"calendarId":"primary","timeMin":"2026-05-13T00:00:00-04:00","timeMax":"2026-05-13T23:59:59-04:00","singleEvents":true,"orderBy":"startTime"}'
```

## Service Skills

Use the service-specific `gws-*` skills when the task concerns Gmail, Google
Calendar, Google Docs, Google Sheets, Google Slides, or Google Chat. They contain
formatting and behavioral rules ported from the Gemini/Qwen Google Workspace
skills.
