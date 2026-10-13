---
name: gws-google-calendar
description: >
  Use before creating, querying, or managing calendar events through the local
  gws CLI. Trigger on calendar, schedule, meeting, event, or availability tasks.
---

# Google Calendar via `gws`

Use `gws calendar ...` for calendar work.

## Timezone-First Workflow

Establish the user's timezone before calendar operations. Use concrete ISO 8601
datetimes with timezone offsets, never bare datetimes.

Always display event times with dates and timezone abbreviations.

## Always Pass `calendarId`

Pass `calendarId: "primary"` on every calendar call unless the user explicitly
asks for a different calendar.

Examples:

```bash
gws calendar events list --params '{"calendarId":"primary","timeMin":"2026-05-13T00:00:00-04:00","timeMax":"2026-05-13T23:59:59-04:00","singleEvents":true,"orderBy":"startTime"}'
```

```bash
gws calendar events get --params '{"calendarId":"primary","eventId":"<event-id>"}'
```

## Creating Or Changing Events

Preview all event writes and ask for confirmation first. Include title, date,
time, timezone, attendees, location/conference details, and recurrence.

Before creating or updating, inspect the schema:

```bash
gws schema calendar.events.insert --resolve-refs
gws schema calendar.events.update --resolve-refs
```

## "Next Meeting" And Schedule Queries

For "next meeting", "today's schedule", and similar:

- Fetch the full day's context in the user's timezone.
- Filter out declined meetings unless explicitly requested.
- If a meeting is in progress, mention it before upcoming meetings.
- Keep full day context available for follow-up questions.
