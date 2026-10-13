---
name: skillz
description: Load Claude-style Agent Skills into pi using the skillz MCP server. Use when you want to discover and invoke skills from the skillz ecosystem.
---

# Skillz — Agent Skills Loader

Enables Anthropic-style Agent Skills in pi via the skillz MCP server.

## How It Works

Skills are directories containing SKILL.md files with YAML frontmatter. The skillz MCP server:
- Discovers all SKILL.md files in your skills directory
- Registers each skill as an MCP tool
- Returns skill instructions and absolute paths when invoked
- Enables progressive disclosure (load only what's needed)

## Using Skills

Skills are invoked automatically when relevant to your task. When a skill is invoked:
1. You receive the full SKILL.md content
2. Absolute paths to the skill's base directory are provided
3. Follow the instructions in the skill
4. Load additional resource files only when referenced

## Skills Directory

Skills are loaded from `~/.agents/skills/` by default.

## Skill Format

Each skill is a directory containing:
- **SKILL.md** — Entry point with YAML frontmatter and markdown instructions
- **resources/** — Optional supporting files
- **scripts/** — Optional executable code

Example SKILL.md:
```markdown
---
name: my-skill
description: What this skill does
---

# Skill Instructions

When invoked, do X, Y, Z...
```

## Finding Skills

- Anthropic skills repository: https://github.com/anthropics/skills
- Community skills: Search GitHub for "claude skills" or "SKILL.md"
