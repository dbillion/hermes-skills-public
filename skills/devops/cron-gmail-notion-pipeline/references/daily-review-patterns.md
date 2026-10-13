# Daily Review Patterns

## Task Database Queries
- Check multiple date property names: Date, date, Due Date, Due date, Deadline, deadline
- Check multiple status property names: Status, status, State, state (as select or status type)
- For today's completed: date = today AND status in [Done, Completed, done, completed]
- For tomorrow's tasks: date = tomorrow AND status not in [Done, Completed, done, completed]

## Log Page Scanning
- Completed tasks: Lines containing "[x]"
- Blockers: Lines containing "blocked" or "stuck" (case-insensitive)

## Cron Job Best Practices
- Never put tokens in shell variables - read directly in Python
- Detect MCP-CLI silent failures (exit 0, empty stdout/stderr)
- Use standalone Python scripts to avoid shell interpretation issues