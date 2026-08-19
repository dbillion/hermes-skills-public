---
name: tmux-orchestrator
description: Coordinate parallel work across multiple tmux windows using persistent agents.
---

# Tmux Orchestrator

Use this skill to run multiple agents in parallel across different tmux windows/panes. This is essential for long-running tasks or multi-component projects (e.g. Frontend + Backend).

## Setup & Prerequisites
1.  **tmux** must be installed on the system.
2.  Scripts are located in `~/.gemini/skills/tmux-orchestrator/`.

## Core Commands

### 1. Send Message to Agent
Send a prompt to an agent running in a specific tmux window.
```bash
~/.gemini/skills/tmux-orchestrator/send-claude-message.sh "session:window" "Your message here"
```

### 2. Schedule Check-in
Schedule a follow-up action for yourself or another agent.
```bash
~/.gemini/skills/tmux-orchestrator/schedule_with_note.sh [minutes] "Actionable note"
```

## Workflows

### Multi-Agent Coordination
*   **Orchestrator:** Monitors progress across all sessions.
*   **Project Manager (PM):** Manages a specific codebase/sub-task.
*   **Engineer:** Implements specific features or fixes bugs.

### Parallel Task Execution
1.  Create a new tmux window: `tmux new-window -n [name]`.
2.  Start an agent in that window.
3.  Use `send-claude-message.sh` to assign tasks from the main orchestrator window.

## Usage with Maestro
When using Maestro for complex plans, you can assign different phases to different tmux windows. The Orchestrator agent (running in the main window) uses `send-claude-message.sh` to trigger the `coder` or `tester` agents in their respective windows.

## Troubleshooting
*   **Window Not Found:** Ensure the session:window string is correct (e.g. `orchestrator:1`).
*   **Script Permissions:** Ensure scripts are executable (`chmod +x`).
