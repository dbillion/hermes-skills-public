---
name: ripwire-workflow
description: "Use when navigating, reviewing, or changing a repository. Starts repo work with ripwire instead of broad grep/read passes; falls back only when ripwire is unavailable or the repo is not git-backed."
metadata:
  hermes:
    category: software-development
    requires:
      bins: [ripwire, git]
      python_packages: []
---

# ripwire-workflow

Use `ripwire` as the default repo-navigation layer for any coding task. It gives a ranked code map and reduces token spend versus reading whole files or grepping blindly.

## When to use

- Any task touching `src/`, `lib/`, `packages/`, or repo-wide behavior
- Before edits: orient, find symbols, review blast radius
- After edits: tests to run, impacted callers, PR context

## Install path

Already cloned to `/home/deeone/ripwire`.

Install must run **outside the Hermas gateway session**:

```bash
cd /home/deeone/ripwire && bash install.sh
export PATH="$HOME/.local/bin:$PATH"
```

## Core commands

- Orient: `ripwire .`
- Task-oriented map: `ripwire . --for="..."` 
- Expand a symbol: `ripwire . --expand=SYM`
- Callers: `ripwire . --callers=SYM`
- Impact: `ripwire . --impact=SYM`
- Changed-files context: `ripwire . --situ`
- PR context: `ripwire . --pr-context=REF`
- HTML map: `ripwire . --html=map.html`

## Decision rules

- Prefer `--pack-task="..."` for edit prep
- Use `--rank-by=rrf --top-k=...` when the default ranking is too broad
- If `--html` is used, open the saved file and inspect only the relevant region
- If `ripwire` is missing or the repo has no git history, fall back to narrow `search_files` / `read_file` scoped to the task

## Anti-patterns

- Do not read entire source trees before ripwire has had a chance to rank relevance
- Do not treat `status: unknown` on a NotebookLM artifact as completion; verify with `nlm studio status`
- Do not run repo installs/restarts from inside the Hermes gateway session
