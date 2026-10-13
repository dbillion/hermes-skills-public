---
name: using-superpowers
description: Use when starting any conversation — establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions.
---

# Using Superpowers Skills

## The Rule

**Invoke relevant or requested skills BEFORE any response or action.** Even a 1% chance a skill might apply means you must invoke it.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional.

## Instruction Priority

1. **User's explicit instructions** — highest priority
2. **Superpowers skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

## Skill Priority

When multiple skills could apply:
1. **Process skills first** (brainstorming, debugging) — these determine HOW to approach the task
2. **Implementation skills second** — these guide execution

## Skill Types

**Rigid** (TDD, debugging): Follow exactly. Don't adapt away discipline.
**Flexible** (patterns): Adapt principles to context.

## Red Flags — You're Rationalizing

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |

## Available Skills

- `/skill:brainstorming` — Before creative work
- `/skill:test-driven-development` — Before implementation
- `/skill:systematic-debugging` — When bugs appear
- `/skill:writing-plans` — For multi-step tasks
- `/skill:executing-plans` — When executing plans
- `/skill:subagent-driven-development` — For parallel task execution
- `/skill:dispatching-parallel-agents` — For independent tasks
- `/skill:finishing-a-development-branch` — When work is complete
- `/skill:verification-before-completion` — Before claiming done
- `/skill:writing-skills` — When creating skills
- `/skill:using-git-worktrees` — For isolated work
- `/skill:receiving-code-review` — When receiving review
- `/skill:requesting-code-review` — Before merging
