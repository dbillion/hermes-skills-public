---
name: finishing-a-development-branch
description: Use when implementation is complete, all tests pass, and you need to decide how to integrate the work.
---

# Finishing a Development Branch

## Overview

Guide completion of development work by presenting clear options and handling chosen workflow.

**Core principle:** Verify tests → Present options → Execute choice → Clean up.

## The Process

### Step 1: Verify Tests

Before presenting options, verify tests pass. If tests fail, stop — cannot proceed.

### Step 2: Present Options

```
Implementation complete. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

### Step 3: Execute Choice

**Option 1 — Merge Locally:**
- Checkout base branch, pull, merge, verify tests, cleanup

**Option 2 — Push and Create PR:**
- Push branch, create PR. Don't clean up worktree (user needs it).

**Option 3 — Keep As-Is:**
- Report status. Don't cleanup.

**Option 4 — Discard:**
- Require typed "discard" confirmation
- Delete branch and cleanup

## Common Mistakes

- **Skipping test verification** — Always verify tests before offering options
- **Cleaning up worktree for Option 2** — Only cleanup for Options 1 and 4
- **Deleting branch before removing worktree** — Merge first, then cleanup, then delete
- **No confirmation for discard** — Require typed "discard" confirmation

## Red Flags

**Never:**
- Proceed with failing tests
- Merge without verifying tests on result
- Delete work without confirmation
- Clean up worktrees you didn't create

**Always:**
- Verify tests before offering options
- Get typed confirmation for discard
- Clean up worktree for Options 1 & 4 only
