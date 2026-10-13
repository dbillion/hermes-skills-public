---
name: gws-calendar
description: Manage Google Calendar events
---

# GWS Calendar

Use to interact with Google Calendar.
- List events: `gws calendar list`
- Create event: `gws events insert --summary "<title>" --start.dateTime "<ISO8601>" --end.dateTime "<ISO8601>" [--description "<description>"]`
- Add popup reminder (e.g., 10 min before): include `--reminders '{"use":false,"overrides":[{"method":"popup","minutes":10}]}'`
