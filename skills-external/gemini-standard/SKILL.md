---
name: gemini-standard
description: "Core engineering mandates and high-signal workflows for the Gemini CLI. Use this skill for architectural planning, bug reproduction, and maintaining senior-level standards (Plan -> Act -> Validate)."
---

# Gemini Engineering Standard

This skill codifies the senior-level engineering standards required for this workspace. Every action must follow the **Plan -> Act -> Validate** cycle.

## Core Mandates

### 1. Planning First
- **Trigger**: Any task requiring 3+ steps or architectural changes.
- **Action**: Use `enter_plan_mode` to draft a spec before writing code.
- **Constraint**: If requirements shift, STOP and re-plan.

### 2. Autonomous Bug Fixing
- **Rule**: Never ask for hand-holding on reported bugs.
- **Workflow**: 
  1. Identify the failing component.
  2. **Empirically reproduce** the failure with a test case.
  3. Apply the surgical fix.
  4. Verify the fix clears the failure.

### 3. Engineering Quality
- **Standard**: Senior/Staff level. No "just-in-case" code.
- **Elegance**: Consolidate logic into clean abstractions.
- **Python**: Always use `uv` for package management and execution.
- **Web**: Prefer Vanilla CSS; use React/TS for apps.

### 4. Verification & Validation
- **Requirement**: No task is complete without proof of correctness.
- **Methods**: Run tests, check logs, and perform status checks.
- **Diffing**: When relevant, diff behavior between current state and the fix.

## Efficiency Protocols
- **MCP-CLI**: Always verify tool schemas and library documentation via `context7` before use.
- **Data Hygiene**: Summarize large tool outputs (>2000 tokens) immediately to preserve context.
- **Memory-First**: Treat local JSON/SQLite history as the source of truth; batch server requests with throttles.

## Tech Stack Specifics
- **Telegram/Bot Development**: 
  - Identify as 'Desktop' (v4.15.2) to bypass RPC 406.
  - Use `repomix` for analyzing protocol-level source code.
