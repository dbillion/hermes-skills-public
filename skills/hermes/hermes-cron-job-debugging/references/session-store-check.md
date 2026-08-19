# Session store check — list a day's Hermes sessions

Live session store (current setup): `/home/deeone/.hermes/state.db`
Tables: `sessions`, `messages`. `sessions.started_at` = Unix epoch float.

## Query a specific day (replace 2026-08-16)
```python
import sqlite3, datetime
con = sqlite3.connect('/home/deeone/.hermes/state.db'); cur = con.cursor()
d = datetime.date(2026, 8, 16)
start = (datetime.datetime(d.year, d.month, d.day) - datetime.datetime(1970,1,1)).total_seconds()
end = start + 86400
cur.execute(
    "SELECT id, title, message_count, started_at FROM sessions "
    "WHERE started_at >= ? AND started_at < ? ORDER BY started_at", (start, end))
for r in cur.fetchall():
    print(f"{datetime.datetime.fromtimestamp(r[3], datetime.UTC).strftime('%H:%M')} | {r[1]}")
```

## Notes
- Legacy `~/.hermes/sessions/*.jsonl` and `request_dump_*.json` are STALE (May data).
  Do NOT use them to detect "today's" activity — this is the bug that caused the
  Daily Journal Summary to report empty days.
- After any Hermes upgrade, re-verify the store path/table names; they can change.
- Cron job prompts reference `~/.hermes/journal/daily/$DATE.md` for structured
  entries and this store for raw session activity.
