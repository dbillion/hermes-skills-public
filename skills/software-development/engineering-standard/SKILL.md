---
name: gemini-standard
description: "Core engineering mandates and high-signal workflows. Use for architectural planning, bug reproduction, and maintaining senior-level standards (Plan -> Act -> Validate)."
---

# Engineering Standard

Senior-level engineering standards. Every action must follow the **Plan → Act → Validate** cycle.

## Core Mandates

### 1. Planning First
- **Trigger**: Any task requiring 3+ steps or architectural changes
- **Action**: Draft a spec before writing code
- **Constraint**: If requirements shift, STOP and re-plan

### 2. Autonomous Bug Fixing
- **Rule**: Never ask for hand-holding on reported bugs
- **Workflow**:
  1. Identify the failing component
  2. **Empirically reproduce** the failure with a test case
  3. Apply the surgical fix
  4. Verify the fix clears the failure

### 3. Engineering Quality
- **Standard**: Senior/Staff level. No "just-in-case" code
- **Elegance**: Consolidate logic into clean abstractions
- **Python**: Always use `uv` for package management and execution
- **Web**: Prefer Vanilla CSS; use React/TS for apps

### 4. Verification & Validation
- **Requirement**: No task is complete without proof of correctness
- **Methods**: Run tests, check logs, and perform status checks
- **Diffing**: When relevant, diff behavior between current state and the fix

## Efficiency Protocols

- **MCP-CLI**: Always verify tool schemas via `context7` before use
- **Data Hygiene**: Summarize large tool outputs (>2000 tokens) immediately
- **Memory-First**: Treat local JSON/SQLite history as the source of truth
