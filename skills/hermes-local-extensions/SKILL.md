---
name: hermes-local-extensions
description: "Install Hermes plugins/skills from cloned repos via symlink."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, plugins, skills, install, extension, local]
---

# Hermes Local Extensions

Install Hermes **plugins** (`plugin.yaml`) and **skills** (`SKILL.md`) into a
running agent from repos already cloned to local disk. This is for community
repos (GitHub, hermesatlas catalog, forks) — NOT hub installs, which use
`hermes skills install <id-or-url>`.

The working pattern was proven during a bulk install of 44 hermesatlas repos
(2026-08-14) and several top-skills collections. Full detail + copy-paste
commands: `references/installing-community-plugins-skills.md`.

## TL;DR

- **Plugins:** `ln -sfn /path/repo ~/.hermes/plugins/<name>` → `hermes plugins enable <name>` → `hermes plugins doctor <name>`.
- **Skills:** `ln -sfn /path/skill-dir ~/.hermes/skills/<prefix>-<name>`.
- The plugin symlink basename MUST equal the plugin's internal `name:` in
  `plugin.yaml` (e.g. dir `hermes-memlock` with `name: memlock` → symlink `memlock`).
- Bundled skill repos keep SKILL.md in a `skills/` SUBDIR — symlink each
  sub-skill individually; Hermes does not reliably recurse.
- New links need a **gateway restart** to appear in `hermes skills/plugins list`.

## Critical pitfall: `hermes plugins install <local-path>` does NOT work for local dirs
It treats the argument as a repo URL to CLONE. A local path resolves to
`https://github.com/<cwd-owner>.git` and fails "Repository not found". Always
symlink instead.

## When to use this skill
- User pastes a GitHub repo and says "install it as a Hermes plugin/skill."
- Bulk "implement all use cases" / "install all these repos" tasks.
- `hermes skills install` fails because the repo isn't in a hub.

## When NOT to use
- The repo is a hub skill → just `hermes skills install <id>`.
- The repo is an app needing a build (package.json/pyproject/go.mod with no
  SKILL.md/plugin.yaml) → stage it, don't symlink; flag the build step.

## Safe-route bulk pattern
1. Clone all targets (shallow `--depth 1`) into one staging dir.
2. Classify: SKILL / PLUGIN / APP / other.
3. Register only SKILLs + PLUGINs (symlink + enable + doctor).
4. Stage APPs/others as reference (need builds/services/mobile/GPU).
5. Report live-vs-staged honestly — never claim "done" when only cloned.

## Activation gotcha (easy to miss)
Symlinked plugins/skills don't show in `hermes plugins/skills list` until the
skill index is rescanned at session/gateway START. From a gateway-connected
session you usually CANNOT restart the gateway (it's the parent process) — tell
the user to run `hermes gateway restart` from a separate terminal. Never claim
a skill is "live" before that restart.
