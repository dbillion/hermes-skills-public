# Cron Job Context Overflow — Error Transcript & Fix

## Error (2026-05-20)

```
Streaming failed before delivery: Error code: 400 - {'error': "This model's maximum context length is 4096 tokens. However, you requested 39399 tokens (23015 in the messages, 16384 in the completion)."}
...
Context length exceeded: 6,620 tokens. Cannot compress further.
```

**Job:** Morning Business AI Briefing (cefc4f0be230)
**Model:** nvidia/nemotron-mini-4b-instruct (4,096 token context limit)
**Root cause:** System prompt + tool schemas = ~6,620 tokens, exceeding the model's 4,096 limit before any work began.
**Failed fix attempt:** Removed skills, shortened prompt — still failed because the base system prompt alone exceeds 4K.
**Working fix:** Switched cron job model to `openrouter/owl-alpha` which has a larger context window.

## Key Lesson

RTK and qmd optimize *tool output* tokens. They cannot reduce the *system prompt* tokens. If the model's context window is smaller than the system prompt, the only fix is to switch to a model with a larger context window.

## How to Diagnose

1. Check the error log: `grep "Context length exceeded" ~/.hermes/logs/agent.log`
2. Check model context limit in the error message (e.g., "maximum context length is 4096 tokens")
3. Compare to system prompt size (typically 6,000-10,000 tokens for Hermes with full tool schemas)
4. If model limit < system prompt size → switch models, don't try to optimize the prompt

## How to Fix in Cron Job Config

Set model explicitly in the cron job:
```
model: { provider: "openrouter", model: "openrouter/owl-alpha" }
```
(Or any model with 32K+ context window.)

## What NOT to Do

- Do NOT attach large skills (last30days = 130KB) to cron jobs
- Do NOT rely on RTK/qmd to fix a too-small model context window
- Do NOT keep retrying with the same model after "Cannot compress further" error
