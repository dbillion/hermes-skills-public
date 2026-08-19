---
name: hermes-use-case-impl
description: Implement hermesatlas use cases into Hermes Agent.
---

# Implementing Hermes Ecosystem Use Cases

## Critical first check: which "Hermes" are we talking about?
hermesatlas.com catalogs the community **hermes-ecosystem (ksimback/hermes-ecosystem)**
— a *separate* project from the **Hermes Agent (Nous Research)** most users run.
Verify before installing:
```
hermes --version          # e.g. "Hermes Agent v0.20.0" = Nous
cd ~/.hermes/hermes-agent && git remote -v   # git@github.com:NousResearch/hermes-agent.git
```
Good news: the catalog's ~70 repos are third-party **add-ons** (skills, plugins,
MCP servers, web UIs, memory providers) built to plug INTO Hermes Agent — not a
rival system. So the use cases ARE applicable; each repo is an add-on to wire in.

## When to Use
- User references hermesatlas.com use cases or wants to "implement all these use cases".
- User asks to wire up community Hermes plugins/skills/MCP servers from a catalog.
- Any "I want to build X, which Hermes repos do I need" request.

## Workflow (do in order)
1. **Extract** the use case's repo stack (web_extract the detail page; some pages
   are narrative and omit the explicit 5-repo list — note Hermes-native equivalents).
2. **Audit native coverage FIRST.** Run `hermes insights`, `hermes --usage-file`,
   check built-in tools/skills (e.g. `browser_use`, Kanban, converse mode). Many
   catalog repos duplicate what Hermes already does — skip redundant installs.
3. **Install via supported paths only:**
   - Plugins: `hermes plugins install <owner/repo>` works for a GIT REPO URL/owner-repo, but
     **NOT for a local path** — it tries to git-clone the path as a URL and fails with
     `remote: Repository not found`. For a repo you already cloned locally, **symlink it into
     `~/.hermes/plugins/<internal-name>`** where `<internal-name>` matches the plugin's
     `name:` in its `plugin.yaml` (e.g. a plugin whose manifest says `name: memlock` must be
     symlinked as `memlock`, not `hermes-memlock`). Then `hermes plugins enable <name>` +
     `hermes plugins doctor <name>`. Doctor WARNs about manifest hook/Tool mismatches are benign.
   - Skills: **symlink each individual skill**, not a bundle dir — Hermes does NOT recurse a
     symlinked parent that contains many sub-skills (it stays undetected). Also it only reads
     `SKILL.md` (uppercase); if a repo ships lowercase `skill.md`, add `ln -s skill.md SKILL.md`
     inside it. Verify with `hermes skills list`.
   - MCP servers: add via `hermes config set` (see Pitfall 2) — and note MCP only loads at
     **gateway start** (see Pitfall 3).
   - Never hand-copy a plugin's internals; use the package manager or symlink so hooks register.
4. **Verify** each addition: `hermes plugins doctor <name>`, `show`, and a live
   smoke test. Don't assume install == working.
5. **Set a budget guardrail early** (see hermes-cost-control skill) — autonomous/
   scheduled use cases are where cost compounds silently.
6. **One use case at a time**, foundational-first:
   observability + guardrails → always-on host/memory → phone access →
   content/media/research/team layers.

## Pitfalls
- Don't install a heavy tool that duplicates native capability (e.g. `tokscale`
  vs `hermes insights`). Measure/audit before adding.
- Narrative catalog pages (use cases 05/08/11/13) hide the repo list — rely on the
  Hermes-native building blocks you already have (Kanban, Firecrawl, browser_use,
  converse mode, sandboxing).
- Gateway restart can't run inside a gateway-connected session — tell the user to
  run `hermes gateway restart` from a real terminal. **And it applies to EVERYTHING
  you just registered**: newly symlinked skills, enabled plugins, and added MCP
  servers are only scanned at gateway/session START. Until the user restarts, they
  won't appear in `hermes skills list` / `hermes plugins list` / `hermes mcp list`
  even though they're correctly on disk. (One restart activates all of them at once.)
- **`hermes config set mcp_servers.<name> '{...}'` stringifies the value** — the whole
  JSON object is stored as a *string*, so `hermes mcp list`/`test` crash with
  `'str' object has no attribute 'get'` and the server never connects. FIX: set each
  sub-key individually so a real dict is built:
  `hermes config set mcp_servers.<name>.command npx`,
  `...args '["-y","pkg"]'`, `...env '{"KEY":"val"}'`, `...timeout 2700`.
  Verify with a python yaml parse that the entry is a `dict`, not `str`.
- Plugin `enable` prompts about tool-override grants — declining (default) is correct
  and safe; WARNs about `provides_hooks`/`provides_tools` mismatches in the manifest
  are benign (the plugin still registers).

## References
- `references/mcp-plugin-install.md` — verified recipes for local plugin symlinking,
  skill-bundle registration, and the `hermes config set` MCP-dict fix.
- The 14-use-case extraction for this user lives at
  `/home/deeone/hermes-use-cases-reference.md` (repo stacks in build order).
- See hermes-cost-control for the plugin-install + budget technique (use case 04).
