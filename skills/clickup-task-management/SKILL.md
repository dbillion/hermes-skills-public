---
name: clickup-task-management
description: Manage ClickUp tasks, projects, and content calendar from the terminal. Use when the user wants to create, update, search, or manage ClickUp tasks, sprints, docs, time tracking, or workspace organization.
metadata:
  tags: clickup, task-management, project-management, productivity, content-calendar
---

# ClickUp CLI (`cup`)

Full-featured CLI for ClickUp, purpose-built for AI agents.

## Prerequisites

```bash
npm install -g @krodak/clickup-cli
cup init --token pk_YOUR_TOKEN --team YOUR_TEAM_ID
cup auth  # verify
```

Get API token from: https://app.clickup.com/settings/apps
Get team ID from: URL `app.clickup.com/{TEAM_ID}/...`

## Environment Variables (alternative to config file)
```bash
export CU_API_TOKEN="pk_..."
export CU_TEAM_ID="12345678"
export CU_PROFILE="work"  # optional profile name
```

## Core Commands

### Tasks
```bash
cup tasks                    # List your tasks
cup tasks --all              # All assignees
cup tasks --search "keyword" # Search tasks
cup task TASK_ID             # Get task details
cup create                   # Create task (interactive)
cup create -l "LIST_ID" -n "Task Name" -d "Description" --priority 2 --tags "tag1,tag2"
cup update TASK_ID           # Update task
cup update TASK_ID --status "In Progress"
cup update TASK_ID --priority 1
cup update TASK_ID --due "2026-05-20"
cup delete TASK_ID           # Delete task
```

### Comments
```bash
cup comment TASK_ID          # Post comment
cup comments TASK_ID         # List comments
cup reply COMMENT_ID         # Reply to comment
```

### Workspace
```bash
cup spaces                   # List spaces
cup lists SPACE_ID           # List lists in space
cup sprint                   # Current sprint tasks
cup sprints                  # All sprints
```

### Time Tracking
```bash
cup time-start TASK_ID       # Start timer
cup time-stop                # Stop timer
cup time-entries             # List time entries
```

### Output Formats
```bash
cup tasks --json             # JSON output (for scripts)
cup tasks --markdown         # Markdown output
```

## Social Media Content Calendar

The content calendar is set up via `workspace/scripts/setup-content-calendar.js`.

### Content Task Template
```bash
cup create -l "LIST_ID" \
  -n "🎬 Post: AI Tools Carousel" \
  -d "Post to Instagram + TikTok + LinkedIn\n\nSlides: workspace/instagram-carousel/slides/\nVideo: workspace/output-video.mp4" \
  --priority 2 \
  --tags "instagram,tiktok,linkedin,carousel" \
  --due-date "2026-05-18"
```

### Workflow Integration
After posting to social media, update the task:
```bash
cup update TASK_ID --status "Posted" --comment "Posted to Instagram, TikTok, LinkedIn. Link: https://..."
```

## Multi-Profile Support
```bash
cup profile add work
cup profile add personal
cup profile list
cup profile use work
cup tasks -p work  # one-off profile override
```

## Config File
`~/.config/cup/config.json`:
```json
{
  "defaultProfile": "work",
  "profiles": {
    "work": {
      "apiToken": "pk_...",
      "teamId": "12345678"
    }
  }
}
```

## Common Pitfalls

- **`cup create` flags**: Use `-l` (not `--list`), `-n` (not `--name`), `-d` (not `--desc`). The CLI uses short flags for these positional params.
- **`cup tasks` scope**: `cup tasks` only shows YOUR assigned tasks by default. Use `cup tasks --all` for all assignees.
- **List ID vs Name**: `cup create -l` requires the numeric list ID, not the list name. Get it from `cup lists SPACE_ID`.
- **Priority values**: Use `urgent`, `high`, `normal`, `low` (or 1-4). Default is `normal`.
- **JSON output**: Use `--json` flag for machine-readable output. Without it, output is Markdown table (TTY) or plain text (piped).
- **Description in scripts**: When creating tasks from scripts, use `-d` flag. The `--desc` long form does NOT work.
