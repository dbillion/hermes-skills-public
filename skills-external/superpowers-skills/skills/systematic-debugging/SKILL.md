---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes.
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

## The Four Phases

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully** — Don't skip past errors or warnings. Read stack traces completely.
2. **Reproduce Consistently** — Can you trigger it reliably? What are the exact steps?
3. **Check Recent Changes** — What changed that could cause this? Git diff, recent commits.
4. **Gather Evidence** — Add diagnostic instrumentation. Log data at each component boundary.
5. **Trace Data Flow** — Where does bad value originate? Keep tracing up until you find the source.

### Phase 2: Pattern Analysis

1. **Find Working Examples** — Locate similar working code in same codebase
2. **Compare Against References** — Read reference implementation COMPLETELY
3. **Identify Differences** — List every difference, however small
4. **Understand Dependencies** — What other components does this need?

### Phase 3: Hypothesis and Testing

1. **Form Single Hypothesis** — "I think X is the root cause because Y"
2. **Test Minimally** — Make the SMALLEST possible change to test hypothesis
3. **Verify Before Continuing** — Did it work? Yes → Phase 4. No → New hypothesis.

### Phase 4: Implementation

1. **Create Failing Test Case** — MUST have before fixing
2. **Implement Single Fix** — Address the root cause, ONE change at a time
3. **Verify Fix** — Test passes, no other tests broken
4. **If Fix Doesn't Work** — STOP. If ≥3 fixes failed, question the architecture.

## Red Flags — STOP and Follow Process

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)

**If 3+ fixes failed:** Question the architecture. Discuss with the user before attempting more fixes.
