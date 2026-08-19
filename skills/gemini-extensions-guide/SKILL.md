---
name: gemini-extensions-guide
description: "Guidelines and workflows for using the 'conductor' and 'maestro' Gemini CLI extensions. Use this skill when you need to orchestrate complex projects, manage track-level plans, or coordinate specialized sub-agents."
---

# Gemini Extensions Guide

This skill provides the unified workflow for utilizing the `conductor` and `maestro` extensions to manage high-complexity software engineering projects.

## Conductor: Project & Track Management
`conductor` is responsible for project-level documentation and tracking individual work streams (tracks).

### Key Files & Locations
- **Project Index**: `conductor/index.md`
- **Tracks Registry**: `conductor/tracks.md`
- **Product Definition**: `conductor/product.md`
- **Tech Stack**: `conductor/tech-stack.md`

### Track Workflow
1.  **Locate Track**: Find the `<track_id>` in `conductor/tracks.md`.
2.  **Read Index**: Check `conductor/tracks/<track_id>/index.md` for the current status.
3.  **Review Plan**: The source of truth for work is `conductor/tracks/<track_id>/plan.md`.
4.  **Update Progress**: After execution, update the track's index and plan files.

## Maestro: Multi-Agent Orchestration
`maestro` is the orchestration layer that coordinates 12 specialized sub-agents through a 4-phase lifecycle.

### Orchestration Phases
1.  **Design**: Use `maestro orchestrate` to initiate a design dialogue.
2.  **Plan**: Generate a detailed `implementation-plan.md` using the `implementation-planning` skill.
3.  **Execute**: Delegate tasks to sub-agents (e.g., `coder`, `tester`, `debugger`) using the `execution` skill.
4.  **Complete**: Validate the work using the `validation` skill and archive the session.

### Sub-Agent Registry
- **Architect**: System design and high-level structure.
- **Coder**: Implementation and feature development.
- **Tester**: Unit and integration testing.
- **Debugger**: Root-cause analysis and bug fixes.
- **Technical Writer**: Documentation and README updates.

## Combined Workflow
For a new feature:
1.  **Conductor**: Create a new track in `conductor/tracks.md`.
2.  **Maestro**: Run `maestro orchestrate` to design the feature.
3.  **Conductor**: Save the design/spec to `conductor/tracks/<track_id>/spec.md`.
4.  **Maestro**: Generate the plan and execute via sub-agents.
5.  **Conductor**: Update the track status to `completed`.
