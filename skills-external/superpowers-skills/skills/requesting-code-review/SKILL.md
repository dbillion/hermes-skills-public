---
name: requesting-code-review
description: Use when completing tasks, implementing major features, or before merging to verify work meets requirements.
---

# Requesting Code Review

Dispatch a code reviewer to catch issues before they cascade. Review early, review often.

## When to Request Review

**Mandatory:**
- After completing major feature
- Before merge to main
- After fixing complex bug

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)

## How to Request

1. **Identify the scope:** What was changed and why
2. **Provide context:** Link to plan/spec, describe requirements
3. **Specify focus areas:** What to look at closely
4. **Act on feedback:** Fix Critical immediately, Important before proceeding, Minor for later

## Integration with Workflows

- **Subagent-Driven Development:** Review after EACH task
- **Executing Plans:** Review after each task or at checkpoints
- **Ad-Hoc Development:** Review before merge

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification
