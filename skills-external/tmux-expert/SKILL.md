---
name: tmux-expert
description: Advanced session management, high-performance configuration, and secure terminal orchestration based on official tmux documentation.
---

# Tmux Expert Workflow

Advanced workflow based on official tmux documentation for session persistence, performance, and secure orchestration.

## Core Commands & Best Practices

### 1. Persistent Session Management
*   **Self-Healing Sessions:** Use `tmux new-session -A -s <name>` to behave like `attach-session` if the session already exists.
*   **Adaptive Detachment:** Configure `set -g detach-on-destroy off`. This prevents the client from exiting when a session is destroyed; instead, it switches to the most recently active remaining session.
*   **Process Persistence:** Set `set -g remain-on-exit on` for critical panes to inspect output after process exit.
*   **Session Grouping:** Use `tmux new-session -t <group-name>` to share windows across multiple clients while maintaining independent offsets.

### 2. High-Performance Configuration
*   **True Color (RGB):** Set `set -as terminal-features ",xterm*:RGB"` and `set -g default-terminal "tmux-256color"`.
*   **Latency:** Set `set -s escape-time 10` for responsive applications like Vim.
*   **Mouse Support:** Enable `set -g mouse on` for easy pane management.
*   **Extended Keys:** Enable `set -g extended-keys on` for complex key combinations.

### 3. Advanced Orchestration
*   **Synchronized Execution:** Toggle `setw synchronize-panes` to send input to all panes in a window.
*   **Pane Marking:** Use `select-pane -m` to mark a pane, making it the target for `join-pane` or `swap-pane`.
*   **Zooming:** Use `resize-pane -Z` to temporarily maximize the active pane.
*   **Layouts:** Use `select-layout -E` to spread panes evenly.

### 4. Security & Environment
*   **Socket Path:** Use `TMUX_TMPDIR` for custom, secure socket directories.
*   **Access Control:** Use the `server-access` command to manage ACLs for the tmux server.
*   **Hidden Variables:** Use `%hidden VAR=val` or `set-environment -h` for internal tmux variables.
*   **Safe Git Context:** Use `split-window -c "#{pane_current_path}"` to ensure git state is inherited correctly.

### 5. Parallel & Concurrent Execution (Maestro/Superpowers Integration)
*   **Background Tasks:** Use `run-shell -b` for background command execution.
*   **Semaphores:** Use `wait-for -S <channel>` to synchronize concurrent workflows.
*   **Virtual Terminals:** Launch Maestro phases in dedicated tmux windows for visibility and persistence.
