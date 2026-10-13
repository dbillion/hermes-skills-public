# Cron Mode Best Practices for GWS Gmail

When running `gws gmail +triage` in cron mode (scheduled jobs without user presence), certain tools are restricted for security reasons.

## Key Restriction

The `execute_code` tool is **blocked** in cron mode because it runs arbitrary Python code that could bypass shell-string approval checks. Attempting to use it will result in an error like:

```
BLOCKED: execute_code runs arbitrary local Python (including subprocess calls that bypass shell-string approval checks). Cron jobs run without a user present to approve it. Use normal tools instead, or set approvals.cron_mode: approve only if this cron profile is intentionally trusted.
```

## Recommended Approach

Instead of using `execute_code` for parsing Gmail output, use shell command chaining which works fully in cron mode:

### Basic Pattern
```bash
gws gmail +triage | tail -n +3 | awk -F'[[:space:]]{2,}' '{print $2, " - ", $4}'
```

### Searching for Keywords (e.g., Job-related emails)
```bash
gws gmail +triage | tail -n +3 | awk -F'[[:space:]]{2,}' '{print $2, " - ", $4}' | grep -i -E "interview|application|recruiter|offer|follow-up|Speechify|Deutsche Telekom|Sacsops|feedback|position|opportunity"
```

### Limiting Output for Context Windows
```bash
gws gmail +triage | tail -n +3 | head -20 | awk -F'[[:space:]]{2,}' '{print $2, " - ", $4}'
```

## Why This Works

- `tail -n +3`: Skips the header and separator lines
- `awk -F'[[:space:]]{2,}'`: Splits on multiple spaces (reliable for gws output)
- `grep -i -E`: Case-insensitive extended regex search
- `head -20`: Limits output to prevent excessive context usage

All of these are standard shell tools that execute successfully in cron mode without restrictions.

## Example: Job Hunt Monitoring Cron Job

A complete cron-friendly command for checking job-related emails:
```bash
#!/bin/bash
# Check for job-related emails from specific sources
RESULTS=$(gws gmail +triage | tail -n +3 | awk -F'[[:space:]]{2,}' '{print $2, " - ", $4}' | grep -i -E "interview|application|recruiter|offer|follow-up|Speechify|Deutsche Telekom|Sacsops|feedback|position|opportunity")

if [ -n "$RESULTS" ]; then
    echo "💼 Job Hunt Pulse"
    echo "📧 New Responses:"
    echo "$RESULTS" | head -5 | while read line; do
        echo "  • $line — needs action: yes"
    done
else
    echo "[SILENT]"
fi
```

This approach avoids all restricted tools and works reliably in cron mode.