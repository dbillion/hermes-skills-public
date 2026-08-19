---
name: using-git-worktrees
description: Use when starting feature work that needs isolation from current workspace or before executing implementation plans.
---

# Using Git Worktrees

## Overview

Ensure work happens in an isolated workspace. Detect existing isolation first, then create if needed.

**Core principle:** Detect existing isolation first. Never fight the harness.

## Step 0: Detect Existing Isolation

Check if you're already in a worktree:
```bash
GIT_DIR=$(git rev-parse --git-dir)
GIT_COMMON=$(git rev-parse --git-common-dir)
```

If `GIT_DIR != GIT_COMMON`, you're already in an isolated workspace. Skip creation.

## Step 1: Create Isolated Directory

Create a worktree for the feature:
```bash
git worktree add .worktrees/<feature-name> -b <branch-name>
```

## Step 2: Project Setup

Auto-detect and run appropriate setup (npm install, cargo build, pip install, etc.)

## Step 3: Verify Clean Baseline

Run tests to ensure workspace starts clean. If tests fail, report and ask before proceeding.

## Common Mistakes

- **Creating nested worktrees** — Always check Step 0 first
- **Not verifying .gitignore** — Ensure worktree directory is ignored
- **Proceeding with failing tests** — Report failures, get permission
- **Fighting the harness** — Use native tools if available

## Red Flags

**Never:**
- Create a worktree when already in one
- Skip baseline test verification
- Proceed with failing tests without asking
