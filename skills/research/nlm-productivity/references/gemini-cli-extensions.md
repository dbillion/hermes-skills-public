# Gemini CLI Extensions: Productivity Toolkit Reference

> Research compiled 2026-05-18. Installation commands, key features, and token impact.

## Extensions Covered

### Conductor (Google Official)
- **What**: Context-driven development. Formalize specs and plans in Markdown files in your repo.
- **Why**: Persistent context across sessions = ~50% reduction in context tokens per session.
- **Install**: `gemini extensions install https://github.com/gemini-cli-extensions/conductor`
- **Workflow**:
  - `/conductor:setup` — Define product, tech stack, workflow
  - `/conductor:newTrack` — Creates specs.md, plan.md with phases/tasks
  - `/conductor:implement` — Executes plan.md, saves state (pause/resume)

### Super Engineer (gemini-kit)
- **What**: Multi-agent dev team (Architect, Frontend, Backend, DevOps, QA, Security, Tech Writer, Code Reviewer).
- **Why**: Specialized agents = 40-60% token savings vs single generalist agent.
- **Install**: `gemini extensions install https://github.com/nth5693/gemini-kit`

### Maestro (maestro-orchestrate)
- **What**: Multi-agent orchestration with 4-phase workflow (Design → Plan → Execute → Complete) and explicit approval gates.
- **Why**: Structured workflows = 30-40% token savings. 12 specialized subagents.
- **Install**: `gemini extensions install https://github.com/josstei/maestro-orchestrate`
- **Usage**: `/maestro.orchestrate <task description>`

### Superpowers
- **What**: Core skills library — TDD, debugging, collaboration patterns.
- **Installs**: 189K+
- **Install**: `gemini extensions install https://github.com/obra/superpowers`

### Caveman
- **What**: Ultra-compressed communication style.
- **Why**: ~75% token reduction on prompts.
- **Installs**: 59K+

### Context7
- **What**: Up-to-date code docs injected on demand.
- **Why**: 30-50% token savings on library/framework questions.
- **Installs**: 55K+

## Token Caching
- Gemini CLI auto-caches with API key auth (GEMINI_API_KEY env var).
- First call: full cost. Subsequent calls: ~70% savings on cached context.
- View usage with /stats in Gemini CLI.

## Deep Research API
- Multi-step research: query, planning, gathering, synthesis.
- Priced on output tokens (4,000-8,000 tokens per full report).
- Can be automated via bash curl and piped into NotebookLM.

## Extension Ecosystem
- 783+ extensions at https://geminicli.com/extensions/
- Categories: Security, Agent Orchestration, Token Optimization, Knowledge, DevOps, Creative

## Verified Extension Versions (2026-05-18)
- Conductor v0.4.1 (Google official, pre-installed)
- Maestro v1.6.4 (pre-installed)
- Superpowers v5.1.0 (pre-installed)
- gemini-kit (Super Engineer) — installed fresh this session; shows YAML frontmatter warnings for agent definitions but skills install correctly
- Stitch v0.1.4, Angular v0.1.0, Antigravity Swarm v0.1.0, Co-researcher v2.1.0, Firebase v1.0.0, GKE MCP v0.12.0, Vertex v0.2.0 (all pre-installed)

## Installation Pitfalls
- **Always use `--consent` flag** for non-interactive installs: `gemini extensions install <url> --consent`
- Without `--consent`, the install hangs waiting for interactive `Y/n` confirmation
- **gemini-kit agent warnings**: Installing gemini-kit may show errors about missing YAML frontmatter in agent definition files. These are non-blocking — the skills still install successfully.
- **Extension install is per-user**: Extensions install to `~/.gemini/extensions/` and are available globally for that user
- **Do NOT use `echo "Y" | gemini extensions install ...`** — the pipe doesn't work. Use `--consent` flag instead.
