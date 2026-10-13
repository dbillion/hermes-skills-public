---
name: hermes-custom-provider
description: "Wire Hermes to a custom OpenAI-compatible model gateway."
version: 1.0.0
author: agent
license: MIT
platforms: [linux, macos]
---

# Hermes ↔ Custom OpenAI-Compatible Model Gateway

Hermes supports custom OpenAI-compatible endpoints natively: set `model.provider: custom`
plus `model.base_url` (and any non-empty `model.api_key`) in `config.yaml`. No plugin
needed. This skill covers the *correct* way to do it and the two traps that make it look
broken when it isn't.

## When to use
- User says "use Omniroute / LiteLLM / my local Ollama / this /v1 endpoint with Hermes".
- User wants Hermes to route through a free-tier aggregator or a proxy they run.
- Any request to point Hermes at a non-native provider via `base_url`.

## Step 1 — Probe the gateway directly BEFORE configuring Hermes
Confirm the endpoint actually serves completions. Send the **same bearer Hermes will send**
(a non-empty dummy is fine if the gateway ignores auth):
```bash
B=http://localhost:20128   # replace with the real base (no /v1 suffix here)
curl -s -m 35 "$B/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-dummy" \
  -d '{"model":"<model-or-auto>","messages":[{"role":"user","content":"Reply with exactly: OK"}]}'
```
- Got `{"content":"OK"}` (or streamed SSE chunks)? Gateway works — proceed.
- Got an upstream billing/404 error (e.g. OpenRouter 402, "No active credentials")? The
  gateway is alive but the *specific model* needs upstream keys. Switch to the gateway's
  free/auto route (Omniroute: model `auto` works zero-cred) or add keys to the gateway.
- `HTTP 000` / timeout on a *no-auth* `/v1/models` call is NOT proof the gateway is down —
  many gateways require a bearer on the models endpoint (see Pitfall 2).

## Step 2 — Isolate in a dedicated PROFILE (do not edit `default`)
Keep the working setup untouched; clone a profile and patch only it:
```bash
hermes profile create <name> --clone     # e.g. omniroute
# then edit ~/.hermes/profiles/<name>/config.yaml
```
(Editing `default` is fine only if the user explicitly wants everything through the gateway.)

## Step 3 — The config block
In `~/.hermes/profiles/<name>/config.yaml`:
```yaml
model:
  default: auto            # or a concrete model the gateway can serve
  provider: custom
  base_url: http://localhost:20128/v1   # must include /v1
  api_key: sk-dummy-local  # any non-empty string; sent as Bearer
```
`provider: custom` + `base_url` + `api_key` is the whole contract. Hermes builds an
OpenAI-compatible client against `base_url` and sends `Authorization: Bearer <api_key>`.

## Step 4 — Live verification (the real proof)
A curl success is not enough — verify Hermes actually drives the gateway end-to-end:
```bash
# background + generous timeout: free-tier routing is SLOW (see Pitfall 1)
timeout 120 hermes chat -q "Say exactly: OMNIROUTE_OK" --profile <name> -v > /tmp/h.log 2>&1
grep -nE "API call #1|model=.+ provider=custom|<expected text>" /tmp/h.log
```
Success looks like:
```
agent.conversation_loop - INFO - API call #1: model=auto provider=custom in=... out=... latency=8.9s
OMNIROUTE_OK
```

## Pitfalls

### Pitfall 1 — Slow free-tier / auto routing masquerades as a hang
Gateways like Omniroute `auto` fan out across free providers and emit reasoning tokens;
a single request can take **8–15s**, and the *first* call after startup can be much slower.
A `hermes chat` that returns nothing in 30–60s is usually just slow, NOT broken.
- Do NOT conclude failure inside a short probe budget. Use `timeout 120`+ and run in background.
- If you must sanity-check latency, the direct curl in Step 1 with `-w "%{time_total}s"` tells
  you the real per-request time before you blame Hermes.

### Pitfall 2 — `/v1/models` may 000 without a bearer
Some gateways (Omniroute) return HTTP 000 / hang on `/v1/models` when called with **no**
`Authorization` header, but 200 in ~0.07s *with* a bearer. Hermes may call `/v1/models`
at startup. If Hermes seems to stall at boot, send a dummy bearer on the models probe:
```bash
curl -s -m 30 "$B/v1/models" -H "Authorization: Bearer sk-dummy" -o /dev/null -w "HTTP %{http_code}\n"
```
If that 200s fast, Hermes's startup fetch is fine and the stall is Pitfall 1, not the models call.

### Pitfall 3 — Direct models need upstream keys
`gpt-4o-mini`, `claude-*`, etc. through a proxy often require the proxy's own upstream API
key. The proxy's *aggregated/auto* route is what works with zero creds. Prefer `auto` (or the
gateway's documented free model) for a credential-less Hermes setup.

## Switch / use
- CLI: `hermes chat -p <name> -q "..."`
- Gateway/Telegram: restart the gateway on the profile (`hermes gateway ...` with `-p <name>`),
  or promote to `default` if the user wants all traffic through the gateway.
- The gateway process must be running for Hermes to reach it (local process / container).

## References
- `references/gateways.md` — provider-specific notes (Omniroute recipe, endpoint, supported
  clients) and the exact verification command set used to prove a live Hermes↔gateway round trip.
