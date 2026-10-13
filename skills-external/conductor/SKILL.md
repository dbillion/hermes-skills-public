---
name: conductor
description: Use for project management and structured development workflows. Manages product definitions, tech stacks, workflow plans, and track-based execution.
---

# Conductor — Project Management

## Overview

Conductor provides a structured project management framework with tracks, plans, and specifications organized in a `conductor/` directory.

## Universal File Resolution Protocol

To find a file within a specific context:

1. **Identify Index:** Determine the relevant index file:
   - **Project Context:** `conductor/index.md`
   - **Track Context:** `conductor/tracks/<track_id>/index.md`

2. **Check Index:** Read the index file and look for a matching link.

3. **Resolve Path:** Resolve path **relative to the directory containing the index.md**.

4. **Fallback:** If index is missing, use default paths below.

5. **Verify:** Always verify the resolved file exists on disk.

## Standard Default Paths (Project)

| Document | Default Path |
|----------|-------------|
| Product Definition | `conductor/product.md` |
| Tech Stack | `conductor/tech-stack.md` |
| Workflow | `conductor/workflow.md` |
| Product Guidelines | `conductor/product-guidelines.md` |
| Tracks Registry | `conductor/tracks.md` |
| Tracks Directory | `conductor/tracks/` |

## Standard Default Paths (Track)

| Document | Default Path |
|----------|-------------|
| Specification | `conductor/tracks/<track_id>/spec.md` |
| Implementation Plan | `conductor/tracks/<track_id>/plan.md` |
| Metadata | `conductor/tracks/<track_id>/metadata.json` |

## When to Use

- When the user mentions a "plan" or asks about the plan
- When managing multiple development tracks
- When organizing product definitions and specifications
- When working with structured project documentation
