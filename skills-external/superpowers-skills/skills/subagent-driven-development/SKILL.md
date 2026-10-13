---
name: subagent-driven-development
description: Use when executing implementation plans with independent tasks in the current session.
---

# Subagent-Driven Development

Execute plan by dispatching fresh subagent per task, with two-stage review after each: spec compliance review first, then code quality review.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration

**Continuous execution:** Do not pause to check in between tasks. Execute all tasks from the plan without stopping. Stop only for: BLOCKED status, ambiguity, or all tasks complete.

## When to Use
- You have an implementation plan
- Tasks are mostly independent
- Staying in the same session

## The Process (Per Task)

1. **Dispatch implementer subagent** with full task text + context
2. **Answer questions** if subagent asks (before and during work)
3. **Subagent implements, tests, commits, self-reviews**
4. **Spec compliance review** — verify code matches spec exactly
5. **Code quality review** — verify implementation is well-built
6. **Fix issues** — if either review finds problems, fix and re-review
7. **Mark task complete**, move to next

## Model Selection

- **Mechanical tasks** (isolated functions, clear specs, 1-2 files): use a fast, cheap model
- **Integration tasks** (multi-file, pattern matching, debugging): use a standard model
- **Architecture/design/review tasks**: use the most capable available model

## Handling Implementer Status

- **DONE:** Proceed to spec compliance review
- **DONE_WITH_CONCERNS:** Read concerns, address if about correctness
- **NEEDS_CONTEXT:** Provide missing context and re-dispatch
- **BLOCKED:** Assess blocker — provide more context, or break task down

**Never** ignore an escalation or force the same model to retry without changes.

## Red Flags

**Never:**
- Start implementation on main/master without explicit consent
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed issues
- Move to next task while either review has open issues
- Start code quality review before spec compliance is ✅
