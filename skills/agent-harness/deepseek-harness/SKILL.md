---
name: deepseek-harness
description: Set up and run the DeepSeek Harness `dsh` CLI.
version: 1
author: hermes
license: proprietary
metadata:
  hermes:
    tags: [agent, harness, dsh, deepseek, cli, providers]
    related_skills: [native-mcp, hermes-agent]
---

# DeepSeek Harness (`dsh`)

## When to Use
- User mentions "deepseek harness", "dsh", "DeepSeek Harness", or wants to run/configure that agent.
- User wants to add non-DeepSeek providers (Groq, Mistral, OpenRouter, OpenAI, Anthropic, Gemini, Cerebras, NIM) to it.
- User wants it wired as an Open Design agent.
- Note: `dsh` is standalone — do NOT scope this skill to Open Design only.

The DeepSeek Harness is a Node.js CLI (`@deepseek-ai/dsh`) that boots "profiles" — ordered stacks of Cordis plugin-bundle layers — to run an agent with LLM providers, tools, and a local web UI. It is a **standalone tool**; it does not require Open Design or any other app to run.

## Install
- Package: `@deepseek-ai/dsh` — npm, global.
- **Version pin:** Open Design's `deepseek-harness` runtime def requires `dsh` **v0.1.0-rc.6** (`requireVersion: true`, `supportedVersions: ['0.1.0-rc.6']`). Install that exact version:
  `npm install -g @deepseek-ai/dsh@0.1.0-rc.6`
- The PyPI package named `deepseek-harness` is a DIFFERENT, entrypoint-less package — do NOT use it; it provides no `dsh` binary.
- Global npm install may trip the `allow-scripts` guard (native postinstalls for koffi/node-pty). The `dsh` binary still works for OD's purposes; only allow those scripts if native terminal features are later needed.

## Launch (standalone)
- **Web UI:** `dsh web` → serves at **http://127.0.0.1:3080**.
  - GOTCHA: `dsh --profile <name> web` ERRORS ("web takes none of parent --profile…"). Use bare `dsh web`, never `dsh --profile X web`.
- Other modes: `dsh --profile <name> headless "task"` (one-shot), `dsh --profile <name> tui`.

## Profile structure (`~/.dsh/profiles/<name>/`)
- `package.json` — `dsh.profile.bundles: ["@deepseek-ai/dsh-base"]` (the bundle list; add provider bundles here).
- `cordis.yml` — empty entry list `[]` (composed from bundles + patch; do not edit directly).
- `cordis.patch.yml` — YOUR override layer (top-level YAML array of loader patch entries). Edit this, not `cordis.yml`.
- Initialize a profile: `dsh --profile <name> --help` (runs pnpm init, creates the dir).
- Composed config (names only, no secret values): `dsh --profile <name> --dump-config`.

## Provider wiring (credentials)
- `dsh-base` only knows `DEEPSEEK_API_KEY`. Other providers are separate Cordis plugin bundles, not in base.
- **Credential rule (security):** NEVER copy literal API-key VALUES between tools/files. Instead rely on **env-var inheritance** — `dsh` inherits the parent shell's environment, so any provider key already present as an env var (e.g. `GROQ_API_KEY_1`, `CEREBRAS_API_KEY`, `NIM_API_KEY`) is already available to dsh with zero copying.
- To surface a provider: add its bundle to `package.json` `dsh.profile.bundles` AND reference its key env-var *name* in `cordis.patch.yml` — never the value.
- If a provider key is NOT in the environment (e.g. `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`), you cannot wire it without the user supplying the key (via their keyring / `export`); ask for the **env var name** that holds it, reference the name only, and never read the value.
- Verify provider wiring by name with `dsh --profile <name> --dump-config` (inspect provider ids / env references; do not print values).

## Open Design relationship
- OD has a `deepseek-harness` agent def that expects `dsh` on PATH, version v0.1.0-rc.6, and a `~/.dsh/profiles/open-design` profile (OD's `--profile open-design`).
- OD's resolver reads `DSH_BIN` from `process.env` (the env key for deepseek-harness is `DSH_BIN`) and scans `searchedDirs` (PATH + known toolchain dirs). A real executable file or `DSH_BIN` override pointing at the dsh binary satisfies it.
- OD's agent availability is computed live; if it reports the harness unavailable, that is an OD-internal detection quirk — it does NOT block the standalone `dsh` CLI/web UI, which works independently.

## Pitfalls (from real corrections this session)
- **Keep it standalone.** When the user asks about `dsh`/deepseek-harness, treat it as its own tool. Do NOT frame answers around Open Design (or any other tool) just because both happened to share the same session/terminal earlier. The user explicitly objected to Open Design being dragged into deepseek-harness discussions.
- **Do NOT restart/kill unrelated apps to fix dsh.** Restarting the entire Open Design stack (or any other app) to nudge a single dsh/OD sub-component is disruptive and was ineffective. The standalone `dsh` launch is independent — fix dsh on its own terms.
- **`dsh web`, not `dsh --profile X web`** — the latter errors.
- **Don't use the PyPI `deepseek-harness` package** — different thing, no binary.
- **Don't capture literal secrets** — env-var names only, ever.

## Support files
- `references/install-and-profile.md` — exact verified commands, profile layout, and the observed provider env-var inventory (names only).
