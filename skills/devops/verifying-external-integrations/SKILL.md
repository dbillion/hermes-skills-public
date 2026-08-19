---
name: verifying-external-integrations
description: Diagnose stale API integrations and 403 permission failures.
version: 1.0.0
author: Hermes Agent
license: MIT
hermes:
  tags: [integrations, api, debugging, auth, cli, mcp, verification]
  related_skills: [social-analytics, systematic-debugging]
---

# Verifying External Integrations

## When to Use
- A tool or skill wrapping an external API errors with "model not found", 400, 401, or 403.
- A skill-documented subcommand fails with "unknown command" (doc drift).
- "It used to work" / "it doesn't work" on a third-party CLI, MCP server, or skill.
- You suspect hardcoded model/option allow-lists are stale versus the live provider.

When a skill or tool that wraps an external API "used to work" or "doesn't work,"
the cause is almost always one of three things: (1) the provider deprecated a
model/option in a hardcoded allow-list, (2) the skill doc cites a subcommand that
no longer exists, or (3) auth succeeds but the identity lacks a per-resource ACL
(403). This skill gives a fast, evidence-first path to the real cause instead of
guessing or editing code blind.

## Phase 1 — Reconcile the documented surface with the binary / live API

### CLI subcommands
Run the help chain and diff against what the skill says:
    <bin> --help
    <bin> <group> --help          # e.g. `ga4 gsc --help` (NOT `ga4 gsc list` — that command doesn't exist)
Then use the *real* subcommands. A documented command that errors with
"unknown command" means the skill doc is stale — fix the doc, not the tool.

### Model / option allow-lists
Do NOT trust a hardcoded list in code or a skill. Query the live provider catalog:
- Groq:    `GET https://api.groq.com/openai/v1/models` (Header `Authorization: Bearer $KEY`)
           → filter ids for whisper/audio/transcribe.
           (Confirmed 2026-08: only `whisper-large-v3` + `whisper-large-v3-turbo` exist;
           `distil-whisper-large-v3-en` was decommissioned → 400 "no longer supported".)
- OpenAI:  `GET https://api.openai.com/v1/models`.
- General: find the provider's `/models` (or `/v1/models`) endpoint; list, then
  keep only ids present in the live response. The live response is the source of
  truth — reconcile code/skill to it.

## Phase 2 — Auth vs permission (the 403 trap)
- 401 / "unauthorized" / "API key not set"  → credential missing or invalid.
- 403 "does not have sufficient permission for site X" → identity is VALID but
  lacks a per-resource ACL. This is the most common "it authenticates but fails"
  case. Example: a GCP service account authenticates to Google Search Console but
  was never added as a *user on the property* — GSC permission is per-property and
  is NOT inherited from the GCP project that owns the service account.
  Fix: grant the identity the resource-level permission (Search Console → Settings
  → Users and permissions → Add user → Owner), not just project-level IAM.

## Phase 3 — Fix propagation
Skills often live in several copies. After editing, find and sync all of them:
    find ~ -path '*/<skill-name>/references/<file>.md'
Common dirs: ~/.hermes/skills, ~/skills, ~/.gemini, ~/.agents, ~/hermes-repo,
~/hermes-setup. Edit the canonical one, then `cp` to the rest so they don't drift
back to the stale text.

## Pitfalls
- "Command not found" is not "not installed": the binary may exist under a
  different name (e.g. `ga4-manager` vs `ga4`) and/or only be on PATH in the
  *interactive* shell (zsh `~/.zshrc` may export `~/go/bin` while bash `~/.bashrc`
  does not). Symlink `<name>` → the real binary inside a PATH dir; add the dir to
  both rc files. Verify with the actual interactive shell (e.g. `zsh -ic 'command -v ga4'`).
- Don't encode provider state as a permanent rule ("X model is gone forever").
  Model lists change — re-probe live each time you suspect drift.
- Don't write up untested retry sequences as "best practice." Only capture what
  you actually verified against the live API.

## References
- [references/probe_recipes.md](references/probe_recipes.md) — copy-paste probes
  (Groq live models list; GA4/GSC 403 diagnosis & fix recipe).
