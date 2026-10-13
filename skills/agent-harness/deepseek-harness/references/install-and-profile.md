# DeepSeek Harness (`dsh`) — install & profile reference

Verified commands and structure from a working install (Node 24.19.0, Linux/EndeavourOS).

## Install (exact)
```
npm install -g @deepseek-ai/dsh@0.1.0-rc.6
dsh --version        # -> 0.1.0-rc.6
```
- OD pins `deepseek-harness` to v0.1.0-rc.6 (`requireVersion: true`). Other versions are rejected by OD's runtime def.
- The PyPI package `deepseek-harness` is unrelated and ships no `dsh` binary — ignore it.

## Launch
```
dsh web                       # OK  -> http://127.0.0.1:3080
dsh --profile X web           # ERROR: "web takes none of parent --profile, --patch, ..."
dsh --profile X headless "task"
dsh --profile X tui
```

## Profile layout (`~/.dsh/profiles/<name>/`)
- `package.json` — `dsh.profile.bundles: ["@deepseek-ai/dsh-base"]`
- `cordis.yml` — `[]` (composed from bundles + patch; do not edit)
- `cordic.patch.yml` is the user override layer
- Init a profile: `dsh --profile <name> --help` (pnpm init creates the dir)
- Inspect (names only): `dsh --profile <name> --dump-config`

## Provider env-var inventory (NAMES ONLY — values never captured)
Present in the working shell environment:
- `GROQ_API_KEY_1`, `GROQ_API_KEY_2`
- `CEREBRAS_API_KEY`
- `NIM_API_KEY`
- `DEEPGRAM_API_KEY`
- `NOTION_API_KEY`
- `STITCH_API_KEY`
- `WANDB_API_KEY`
- `TINKER_API_KEY`

NOT present in environment (would need the user to supply the key):
- `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`

`dsh-base` only references `DEEPSEEK_API_KEY` as a provider key; other providers are
separate Cordis plugin bundles not shipped in base. dsh inherits the parent shell env,
so any of the present keys above are already reachable without copying values.

## OD resolver notes
- OD reads `DSH_BIN` from `process.env` for the deepseek-harness agent.
- `searchedDirs` = PATH + known toolchain dirs (includes `~/.local/bin`).
- A real executable file (e.g. a wrapper at `~/.local/bin/dsh` with shebang +x) or
  a `DSH_BIN` override pointing at the dsh binary satisfies detection.
- If OD still reports the harness unavailable after the binary is present, that is an
  OD-internal detection quirk — the standalone `dsh web`/CLI works independently.
