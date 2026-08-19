# Gateway-specific notes & verification recipes

## Omniroute (diegosouzapw/OmniRoute)
- Open-source OpenAI-compatible AI gateway. One endpoint, 290+ providers, 90+ free tiers.
- Default local endpoint: `http://localhost:20128/v1` (listens on `0.0.0.0:20128`).
- Hermes Agent is in Omniroute's list of officially-supported clients.
- Process appears as `omniroute` (node). Must be running for Hermes to reach it.
- `model: auto` works with **zero upstream credentials** — auto-routes across free tiers
  (observed landing on `gpt-oss-120b-medium`). Direct models (`gpt-4o-mini`, `claude-*`)
  need the gateway's own upstream keys and fail with OpenRouter 402 / "No active credentials".

### Hermes config for Omniroute (profile `omniroute`)
```yaml
model:
  default: auto
  provider: custom
  base_url: http://localhost:20128/v1
  api_key: sk-omniroute-local   # dummy; Omniroute ignores it for auto
```

### Direct probe (what Hermes will actually send: bearer present)
```bash
B=http://localhost:20128
# auto + dummy bearer -> "content":"OK"
curl -s -m 35 "$B/v1/chat/completions" -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-omniroute-local" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Reply with exactly the word: OK"}]}' \
  | grep -o '"content":"[^"]*"'
# /v1/models needs the bearer: 200 in ~0.07s WITH it, 000 WITHOUT it
curl -s -m 30 "$B/v1/models" -H "Authorization: Bearer sk-omniroute-local" \
  -o /dev/null -w "HTTP %{http_code}\n"
```

### Live Hermes round-trip (the proof)
```bash
# background, generous timeout — auto routing is slow (~9s, first call slower)
timeout 120 hermes chat -q "Say exactly: OMNIROUTE_OK" --profile omniroute -v > /tmp/hermes_omni.log 2>&1
grep -nE "API call #1|model=auto provider=custom|OMNIROUTE_OK" /tmp/hermes_omni.log
```
Observed success output:
```
agent.conversation_loop - INFO - API call #1: model=auto provider=custom in=33216 out=170 total=33386 latency=8.9s
OMNIROUTE_OK
```
Note: a 60–90s probe budget is too short — Omniroute `auto` free-tier routing takes longer
and the first startup call is slowest. Use `timeout 120`+. The trailing asyncio "Event loop is
closed" errors on exit are harmless shutdown noise from MCP tasks, not a failure.

## Generic OpenAI-compatible gateway (LiteLLM / Ollama / vLLM / self-hosted proxy)
- Same config contract: `provider: custom` + `base_url` (include `/v1`) + any `api_key`.
- If the gateway has no auth, still set `api_key` to a non-empty dummy — Hermes always sends
  `Authorization: Bearer <api_key>`.
- Verify with the same Step 4 live round-trip; replace `auto` with the gateway's real model id.
