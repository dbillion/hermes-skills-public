# GWS CLI — Full Command Reference

## Installation
```bash
npm install -g @googleworkspace/cli
```

## Auth
```bash
gws auth setup    # First-time: creates GCP project, enables APIs, OAuth login
gws auth login    # Subsequent: scope selection + login
gws auth status   # Check current auth state
gws auth export   # Export credentials for headless/CI use
```

## Gmail (uses +helpers, NOT REST subcommands)
```bash
gws gmail +triage                              # Inbox summary
gws gmail +read --params '{"id": "..."}'       # Read message
gws gmail +send --params '{"to": "...", "subject": "...", "body": "..."}'
gws gmail +reply --params '{"id": "...", "body": "..."}'
gws gmail +reply-all --params '{"id": "...", "body": "..."}'
gws gmail +forward --params '{"id": "...", "to": "..."}'
gws gmail +watch                               # Stream new emails (NDJSON)
gws gmail users messages list --params '{"userId": "me", "maxResults": 10}'
gws gmail users messages get --params '{"userId": "me", "id": "..."}'
gws gmail users labels list --params '{"userId": "me"}'
```

## Drive
```bash
gws drive files list --params '{"pageSize": 10}'
gws drive files get --params '{"fileId": "..."}'
gws drive files create --params '{"name": "New File"}'
gws drive files delete --params '{"fileId": "..."}'
```

## Calendar
```bash
gws calendar events list --params '{"calendarId": "primary", "maxResults": 10}'
gws calendar events get --params '{"calendarId": "primary", "eventId": "..."}'
gws calendar events insert --params '{"calendarId": "primary", "summary": "Meeting", "start": {"dateTime": "2026-05-18T10:00:00Z"}, "end": {"dateTime": "2026-05-18T11:00:00Z"}}'
```

## Sheets
```bash
gws sheets spreadsheets get --params '{"spreadsheetId": "..."}'
gws sheets spreadsheets values get --params '{"spreadsheetId": "...", "range": "Sheet1!A1:D10"}'
```

## Docs
```bash
gws docs documents get --params '{"documentId": "..."}'
gws docs documents create --params '{"title": "New Document"}'
```

## Slides
```bash
gws slides presentations get --params '{"presentationId": "..."}'
gws slides presentations create --params '{"title": "New Presentation"}'
```

## Tasks
```bash
gws tasks tasklists list --params '{"maxResults": 10}'
gws tasks tasks list --params '{"tasklist": "TASKLIST_ID"}'
```

## Global Options
```bash
gws --dry-run <command>        # Validate locally without sending
gws --format table <command>   # Table output (default: json)
gws --format yaml <command>    # YAML output
gws --format csv <command>     # CSV output
```

## Key Pitfalls
1. Gmail uses `+helpers` not REST: `gws gmail +triage` not `gws gmail messages list`
2. Drive/Sheets/Calendar use standard subcommands: `gws drive files list`
3. Always use `--params` for request bodies
4. userId for Gmail: use `"me"` for authenticated user
5. calendarId: use `"primary"` for main calendar
