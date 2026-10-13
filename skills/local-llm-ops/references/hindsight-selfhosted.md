# Hindsight self-hosted (no paid key) — session notes 2026-09-03

Repo studied: vectorize-io/hindsight (`hermes-ecosystem-staging/10/hindsight/`), via read-only subagent recon.

## What it is
Agent memory system (world facts / experience facts / mental models). Interfaces: REST `/v1/...`, native MCP server (FastMCP HTTP, tools `retain, sync_retain, recall, reflect`), Python/JS SDKs, LiteLLM wrapper. Hermes has no native provider for it — wire via MCP endpoint or REST from a skill/cron; keep banks distinct from gbrain.

## No-Docker path (used here; Docker daemon was approval-gated)

```
pipx install hindsight-embed          # gives hindsight-embed + pulls hindsight CLI
# profiles live in ~/.hindsight/profiles/<name>.env  (tool's own store, key redacted in output)
hindsight-embed profile create hermes --port 8888 --env HINDSIGHT_API_LLM_PROVIDER=openai \
  --env HINDSIGHT_API_LLM_BASE_URL=http://127.0.0.1:20128/v1 \
  --env HINDSIGHT_API_LLM_MODEL=<working-model-id>
hindsight-embed profile set-env hermes HINDSIGHT_API_LLM_API_KEY "$KEY"  # in-memory only
hindsight-embed -p hermes daemon start     # first start downloads embed models; background it
curl -s -m 10 -o /dev/null -w "%{http_code}" http://localhost:8888/health  # expect 200
hindsight-embed -p hermes bank create <bank>
hindsight-embed -p hermes memory retain <bank> "<fact>"
```

Logs: `~/.hindsight/profiles/<name>.log`. DB: embedded pg0 under `~/.pg0/instances/`. Embeddings default LOCAL (`BAAI/bge-small-en-v1.5`, reranker MiniLM) — no key needed. Only the LLM leg needs a key.

## LLM via generic `openai` provider + BASE_URL

Supported providers include `openai, anthropic, gemini, groq, ollama, lmstudio, ...`. The `openai` provider takes any `BASE_URL`, so a local OpenAI-compatible gateway works — but the key var must be NON-EMPTY even if the backend would ignore it. Daemon needs a restart to pick up `set-env` changes.

## Observed failure modes (OmniRoute gateway)

- Missing `oc/`-style prefix or wrong id → HTTP 400 "Model 'X' is not available in the active live catalog for provider 'Y'". The `/v1/models` LISTING still shows the id — listing is stale, smoke-test instead.
- Free-tier pools exhaust → HTTP 429 `ProviderRateLimitResetError` with a `retry at` timestamp; the reset keeps sliding under load. Fix tried: switch provider prefix pool (`oc/` → `opencode/` → `openrouter/`), one daemon-restart cycle per attempt.
- `memory retain` 500s are almost always the LLM leg — read the daemon log tail (`Fact extraction failed`, `API error after 4 attempts`), not the CLI wrapper text.
- Bare `hindsight-embed` with no subcommand prints usage and exits — it needs `profile create` + `daemon start` first; `bank create` before `retain`.

## Resource footprint (box: 31GB RAM, Intel iGPU, no NVIDIA)

Daemon + local embed models run CPU-only, ~1–3GB RAM idle. No GPU needed. Docker single-image alternative (`ghcr.io/vectorize-io/hindsight:latest`, :8888 API + :9999 UI) estimated ~5–8GB image — unverified here.
