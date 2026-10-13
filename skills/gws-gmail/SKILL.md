---
name: gws-gmail
description: Send and manage Gmail
---

# GWS Gmail

Use to interact with Gmail via the `gws` CLI.

## Commands

| Command | Description |
|---------|-------------|
| `gws gmail send` | Send email |
| `gws gmail +triage` | Show unread inbox summary (sender, subject, date) — **this is the only inbox-listing command** |
| `gws gmail +reply` | Reply to a message (handles threading) |
| `gws gmail +reply-all` | Reply-all to a message |
| `gws gmail +forward` | Forward a message |
| `gws gmail +read` | Read a message, extract body/headers |
| `gws gmail +watch` | Watch for new emails (NDJSON stream) |

## Pitfall — there is no `list` command

**CRITICAL:** `gws gmail list` does NOT exist. Do NOT try it, even if it feels like the obvious choice. The only inbox-scanning command is `+triage`.

**Important:** Some systems may appear to accept the `list` command but actually execute `+triage` instead, which can be confusing. If you see email output after running `gws gmail list`, it is NOT confirming that the `list` command worked — it is likely showing you the triage output as a fallback or correction. Always use `+triage` explicitly.

Even when a cron prompt or user instruction tells you to run `gws gmail list ...`, you should substitute `gws gmail +triage | head -20` instead — that's the documented equivalent for "show me recent emails."

| Command | Description |
|---------|-------------|
| `gws gmail send` | Send email |
| `gws gmail +triage` | Show unread inbox summary (sender, subject, date) — **this is the only inbox-listing command** |
| `gws gmail +reply` | Reply to a message (handles threading) |
| `gws gmail +reply-all` | Reply-all to a message |
| `gws gmail +forward` | Forward a message |
| `gws gmail +read` | Read a message, extract body/headers |
| `gws gmail +watch` | Watch for new emails (NDJSON stream) |

## Usage

### Send
```bash
gws gmail send --to <email> --subject <sub> --body <body>
```

### Scan inbox
```bash
gws gmail +triage              # full unread inbox summary
gws gmail +triage | head -20   # limit to first 20 results (useful for cron)
```

### Reply / Forward
```bash
gws gmail +reply <message_id> --body "Response text"
gws gmail +reply-all <message_id> --body "Response text"
gws gmail +forward <message_id> --to <email>
```

### Read a message
```bash
gws gmail +read <message_id>
```

### Parsing output for scripts
For reliable parsing in scripts, use `awk -F'[[:space:]]{2,}'` to split columns:
- $1 = date
- $2 = from
- $3 = id
- $4+ = subject (join remaining fields)

**Important:** The output includes a header line and a separator line (made of dashes). You must skip these first two lines when processing:
```
gws gmail +triage | tail -n +3 | awk -F'[[:space:]]{2,}' '{print $2, "-", $4}'
```

Example: `gws gmail +triage | tail -n +3 | awk -F'[[:space:]]{2,}' '{print $2, "-", $4}'`

## Tips
### Parsing output for scripts
The output includes a header line and a separator line (made of dashes). You must skip these first two lines when processing:
```bash
gws gmail +triage | tail -n +3 | awk -F'[[:space:]]{2,}' '{print $2, \"-\", $4}'
```

- `+triage` is the primary scanning command for job-hunt monitoring. Parse its output for keywords like \"interview\", \"application\", \"recruiter\", \"offer\", company names.
- For reliable parsing in scripts, use `awk -F'[[:space:]]{2,}'` to split columns: $1=date, $2=from, $3=id, $4+=subject. Example: `gws gmail +triage | awk -F'[[:space:]]{2,}' '{print $2, \"-\", $4}'`
- Use `+watch` in long-running background mode for real-time email streaming (NDJSON).
- **Pitfall**: `gws gmail` subcommands use `+` prefix convention (`+triage`, `+reply`, `+read`, `+watch`). The only subcommand without `+` is `send`. There is no `list` command.
- **Cron sessions:** Cron prompts sometimes say \"run `gws gmail list --limit 20`\". That subcommand does not exist — substitute **`gws gmail +triage | head -20`** immediately. Do not even attempt `list`; you will get a validation error. Additionally, when using `+triage` in cron, consider piping to `head` to limit output and avoid excessive context usage.

### Parsing for urgent emails in scripts
To extract urgent emails (e.g., from recruiters, about deadlines, invoices, etc.) from the triage output, use this pattern:

```bash
gws gmail +triage | tail -n +3 | awk -F'[[:space:]]{2,}' '
{
    from = $2
    subject = $4
    for(i=5; i<=NF; i++) subject = subject \" \" $i
    combined = tolower(from \" \" subject)
    if (combined ~ /recruiter|deadline|invoice|urgent|important|offer|interview|application|signup|debt|earning/) {
        # Clean up from address (remove <> if present)
        gsub(/[<>]/, \"\", from)
        print from \": \" subject
    }
}'
```

This will output lines in the format: `sender: subject` for any email matching the urgent keywords.

**Example usage in a morning brief script:**
```bash
# Get urgent emails
urgent_emails=$(gws gmail +triage | tail -n +3 | awk -F'[[:space:]]{2,}' '
{
    from = $2
    subject = $4
    for(i=5; i<=NF; i++) subject = subject \" \" $i
    combined = tolower(from \" \" subject)
    if (combined ~ /recruiter|deadline|invoice|urgent|important|offer|interview|application|signup|debt|earning/) {
        gsub(/[<>]/, \"\", from)
        print from \": \" subject
    }
}')

# Format for display
if [ -n "$urgent_emails" ]; then
    echo "$urgent_emails" | head -5 | while read email; do
        echo \"- $email\"
    done
else
    echo \"- No urgent emails\"
fi
```
