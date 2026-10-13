---
name: maestro
description: Use for multi-agent development orchestration — specialist agents, phase-based execution, parallel subagents, and structured review/debug/security/perf commands.
---

# Maestro — Multi-Agent Orchestration

## Overview

Maestro is a multi-agent development orchestration platform with specialist agents, phase-based execution, native parallel subagents, and persistent sessions.

## Key Concepts

- **Specialist Agents** — Domain-specific agents for different aspects (review, debug, security, perf, SEO, a11y, compliance)
- **Phased Execution** — Work proceeds through defined phases with validation
- **Parallel Subagents** — Independent tasks dispatched concurrently
- **Persistent Sessions** — State maintained across interactions

## Settings

| Setting | Environment Variable | Description |
|---------|---------------------|-------------|
| Disabled Agents | `MAESTRO_DISABLED_AGENTS` | Comma-separated list of agents to exclude |
| Max Retries | `MAESTRO_MAX_RETRIES` | Max retry attempts per phase |
| Auto Archive | `MAESTRO_AUTO_ARCHIVE` | Auto-archive session on completion |
| Validation | `MAESTRO_VALIDATION_STRICTNESS` | strict/normal/lenient |
| State Directory | `MAESTRO_STATE_DIR` | Base directory for session state |
| Max Concurrent | `MAESTRO_MAX_CONCURRENT` | Max parallel subagents per batch |
| Execution Mode | `MAESTRO_EXECUTION_MODE` | parallel/sequential/ask |

## When to Use

- Complex multi-component development tasks
- When you need specialized review (security, performance, accessibility)
- When orchestrating parallel implementation work
- When structured phase-based execution is needed
