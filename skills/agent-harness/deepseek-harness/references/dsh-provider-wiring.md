# dsh multi-provider wiring — verified mechanism

Source-verified against `@deepseek-ai/dsh@0.1.0-rc.6` (`dsh-llm-pi-ai` bundle).

## The working method: `llm-pi-ai` settings section

Providers beyond DeepSeek are NOT added via `package.json` bundles + `cordis.patch.yml`
(that path was attempted and did NOT surface the providers). The correct route is the
**`llm-pi-ai` multi-provider adapter**, shipped dormant in `dsh-base` and activated by a
settings section.

Proof from source (`dsh-llm-pi-ai/lib/index.js`):
- `const name = "llm-pi-ai";` and `NS = settingsNamespace("llm-pi-ai");` → settings key is `llm-pi-ai`.
- `installSettingsSection(ctx, NS, Config, config, {...})` → the section is read from the settings doc.
- `assertUsableApiKey(hit, "llm-pi-ai", ref)` → keys resolve per request from the environment.
- README example: `providers: { deepseek: { apiKeyEnv: … } }`.

## Settings location

`$DSH_HOME/settings.yaml` (default `~/.dsh/settings.yaml`; perms should be `rw-------`).
Edit it; the dormant adapter activates the moment the `llm-pi-ai:` section supplies provider
profiles. Each provider uses `apiKeyEnv: <ENV_VAR_NAME>` — a **credential reference**, never a value.

## Schema (verified)

```yaml
llm-pi-ai:
  providers:
    groq:
      apiKeyEnv: GROQ_API_KEY_1
      baseURL: https://api.groq.com/openai/v1
      api: openai-completions
    cerebras:
      apiKeyEnv: CEREBRAS_API_KEY
      baseURL: https://api.cerebras.ai/v1
      api: openai-completions
    nim:
      apiKeyEnv: NIM_API_KEY
      baseURL: https://integrate.api.nvidia.com/v1
      api: openai-completions
    mistral:
      apiKeyEnv: MISTRAL_API_KEY
      baseURL: https://api.mistral.ai/v1
      api: openai-completions
    openrouter:
      apiKeyEnv: OPENROUTER_API_KEY
      baseURL: https://openrouter.ai/api/v1
      api: openai-completions
    openai:
      apiKeyEnv: OPENAI_API_KEY
      baseURL: https://api.openai.com/v1
      api: openai-completions
    anthropic:
      apiKeyEnv: ANTHROPIC_API_KEY
      baseURL: https://api.anthropic.com/v1
      api: anthropic-messages
    gemini:
      apiKeyEnv: GEMINI_API_KEY
      baseURL: https://generativelanguage.googleapis.com/v1beta
      api: gemini
```

- `api` accepts: `openai-completions` | `anthropic-messages` | `gemini` (and others per pi-ai catalog).
- `baseURL` is the OpenAI-compatible (or provider-native) gateway.
- Omitting `apiKeyEnv` leaves the route unauthenticated; a reference that resolves to nothing fails with `MISSING_CREDENTIAL` (safe fail).

## Security (carry forward)

Never write literal key **values** into this file. Only env-var **names**. The harness pulls
the value from the inherited process environment at request time. Providers whose env var is
present in the launching shell authenticate immediately; the rest stay dormant until that env
var is exported into `dsh`'s launch environment.

## Verification pitfalls

- `dsh --profile <name> --dump-config` prints the **bundle tree only** — it does NOT render
  settings overlays, so a correct `llm-pi-ai` section will NOT appear there. Don't use it to
  confirm provider wiring.
- Verify instead by: (a) clean boot of `dsh web` with no validation error, or (b) the web UI
  **Models** page listing the providers.
- Guessed REST endpoints (`/api/providers`, `/api/models`) return "not found"; use the Models page.
- Confirm no secret leaked: `grep -niE "sk-|ghp_|gsk_|[a-z0-9]{32,}" settings.yaml` → empty.
