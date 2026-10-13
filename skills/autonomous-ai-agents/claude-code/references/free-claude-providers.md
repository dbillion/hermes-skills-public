# Free Claude Code — Provider API Reference

## Provider Endpoints for Dynamic Model Discovery

These endpoints are called by fcc-claude when `FCC_SMOKE_*_MODELS=""` (empty string) is set.

---

### OpenRouter

**API Key Env:** `OPENROUTER_API_KEY`
**Models Endpoint:** `https://openrouter.ai/api/v1/models`
**Auth Header:** `Authorization: Bearer $OPENROUTER_API_KEY`

**Example Request:**
```bash
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/models | jq
```

**Response Shape:**
```json
{
  "data": [
    {
      "id": "openrouter/owl-alpha",
      "name": "Owl Alpha 72B",
      "pricing": {
        "prompt": "0",
        "completion": "0",
        "image": "0",
        "request": "0"
      },
      "context_length": 32768,
      "top_provider": "together"
    }
  ]
}
```

**Free Model Detection:**
- `pricing.prompt == "0"` AND `pricing.completion == "0"` → FREE
- `pricing.prompt < 0` OR `pricing.completion < 0` → Negative cost (pays YOU!)
- Filter: `jq '.data[] | select(.pricing.prompt == "0" or .pricing.prompt < 0)'`

**Notable Free Models (as of 2026-05):**
- `openrouter/owl-alpha` — 72B, free, high quality
- `openrouter/pareto-code` — Code specialist, negative cost
- `openrouter/qwen-2.5-coder-32b-instruct` — 32B code model
- `openrouter/deepseek-v3` — 671B MoE, free tier available

---

### NVIDIA NIM

**API Key Env:** `NVIDIA_NIM_API_KEY`
**Models Endpoint:** `https://integrate.api.nvidia.com/v1/models`
**Auth Header:** `Authorization: Bearer $NVIDIA_NIM_API_KEY`

**Example Request:**
```bash
curl -H "Authorization: Bearer $NVIDIA_NIM_API_KEY" \
  https://integrate.api.nvidia.com/v1/models | jq
```

**Response Shape:**
```json
{
  "data": [
    {
      "id": "nvidia/llama-3.1-405b-instruct",
      "object": "model",
      "created": 1234567890,
      "owned_by": "nvidia"
    }
  ]
}
```

**All NVIDIA NIM Models Are FREE** — no pricing filter needed.

**Available Models (as of 2026-05):**
- `nvidia/llama-3.1-8b-instruct` — Fast, efficient
- `nvidia/llama-3.1-70b-instruct` — High quality
- `nvidia/llama-3.1-405b-instruct` — **Most powerful Llama!**
- `nvidia/mixtral-8x7b-instruct` — MoE architecture
- `nvidia/mistral-large-2-instruct` — Top-tier reasoning
- `nvidia/codellama-70b` — **Code specialist**
- `nvidia/phi-3-mini-instruct` — Small but mighty (128K context)
- `nvidia/phi-3-medium-instruct` — Balanced performance
- `nvidia/nemotron-4-340b-instruct` — **NVIDIA's flagship 340B model!**
- `nvidia/gemma-7b-instruct` — Google's efficient model
- `nvidia/llama3-chatqa-1.5-8b` — Conversational QA
- `nvidia/llama3-chatqa-1.5-70b` — Larger conversational model
- `nvidia/nemotron-mini-4b-instruct` — Tiny, fast

---

### Groq

**API Key Env:** `GROQ_API_KEY`
**Models Endpoint:** `https://api.groq.com/openai/v1/models`
**Auth Header:** `Authorization: Bearer $GROQ_API_KEY`

**Example Request:**
```bash
curl -H "Authorization: Bearer $GROQ_API_KEY" \
  https://api.groq.com/openai/v1/models | jq
```

**Response Shape:**
```json
{
  "data": [
    {
      "id": "llama-3.3-70b-versatile",
      "object": "model",
      "created": 1234567890,
      "owned_by": "groq"
    }
  ]
}
```

**All Groq Models Are FREE** (with rate limits: 30 RPM, 60k tokens/request).

**Available Models (as of 2026-05):**
- `llama-3.3-70b-versatile` — Best overall (Llama 3.3 70B)
- `llama-3.1-8b-instant` — Fastest (Llama 3.1 8B)
- `mixtral-8x7b-32768` — MoE with 32K context
- `gemma2-9b-it` — Google Gemma 2 9B
- `gemma-7b-it` — Original Gemma 7B
- `llama-guard-3-8b` — Safety classifier (not for chat)

---

### Google Gemini

**API Key Env:** `GEMINI_API_KEY` (or `GOOGLE_API_KEY`)
**Models Endpoint:** `https://generativelanguage.googleapis.com/v1beta/models`
**Auth Header:** `x-goog-api-key: $GEMINI_API_KEY`

**Example Request:**
```bash
curl -H "x-goog-api-key: $GEMINI_API_KEY" \
  "https://generativelanguage.googleapis.com/v1beta/models" | jq
```

**Response Shape:**
```json
{
  "models": [
    {
      "name": "models/gemini-2.5-flash-lite-preview-06-17",
      "displayName": "Gemini 2.5 Flash Lite",
      "inputTokenLimit": 1048576,
      "outputTokenLimit": 65536,
      "supportedGenerationMethods": ["generateContent", "countTokens"]
    }
  ]
}
```

**Free Tier:** 1,500 requests/day per model (varies by model).

**Available Models (as of 2026-05):**
- `gemini-2.5-flash-lite-preview-06-17` — Fast, efficient, 1M context
- `gemini-2.5-flash-preview-tuning-2025-09-12` — Tuning support
- `gemini-2.5-pro-preview-06-05` — High quality (limited free quota)
- `gemini-2.0-flash` — Previous gen, still fast
- `gemini-1.5-flash` — Legacy,lowest cost

**Note:** Gemini API uses a different endpoint format than OpenAI-compatible providers. fcc-claude handles this translation internally.

---

## Debugging Model Discovery

### Step 1: Verify Environment Variables

```bash
# Check if vars are set
env | grep -E "^(OPENROUTER|NVIDIA_NIM|GROQ|GEMINI)_API_KEY="

# Check discovery vars (should be empty string, not unset)
env | grep FCC_SMOKE
```

Expected output:
```
OPENROUTER_API_KEY=sk-or-...
NVIDIA_NIM_API_KEY=nvapi-...
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIzaSy...
FCC_SMOKE_OPENROUTER_FREE_MODELS=
FCC_SMOKE_NIM_MODELS=
FCC_SMOKE_GROQ_MODELS=
FCC_SMOKE_GEMINI_MODELS=
```

### Step 2: Test Provider APIs Directly

```bash
# OpenRouter
curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/models | jq '.data | length'

# NVIDIA NIM
curl -s -H "Authorization: Bearer $NVIDIA_NIM_API_KEY" \
  https://integrate.api.nvidia.com/v1/models | jq '.data | length'

# Groq
curl -s -H "Authorization: Bearer $GROQ_API_KEY" \
  https://api.groq.com/openai/v1/models | jq '.data | length'

# Gemini
curl -s -H "x-goog-api-key: $GEMINI_API_KEY" \
  "https://generativelanguage.googleapis.com/v1beta/models" | jq '.models | length'
```

Expected: Non-zero model counts (e.g., 50+, 10+, 6, 5).

### Step 3: Check fcc-claude Config File

```bash
# Verify config file exists and has correct content
cat ~/.config/free-claude-code/.env | grep -E "^FCC_SMOKE|^.*_API_KEY="

# Check file permissions (should be readable)
ls -la ~/.config/free-claude-code/.env
```

### Step 4: Test Model Tab Completion

```bash
# Start fcc-claude and try tab completion
fcc-claude --model openrouter/[TAB]
fcc-claude --model nvidia_nim/[TAB]
fcc-claude --model groq/[TAB]
```

If models appear, discovery succeeded. If not, check logs.

### Common Error Codes

| Code | Meaning | Fix |
|------|---------|-----|
| `401 Unauthorized` | Invalid API key | Check key in provider dashboard |
| `403 Forbidden` | API key lacks permission | Enable API in provider console |
| `429 Too Many Requests` | Rate limited | Wait and retry, or upgrade tier |
| `404 Not Found` | Wrong endpoint URL | Verify endpoint matches provider docs |
| `500 Internal Server Error` | Provider outage | Check provider status page |

---

## Model Selection Heuristics

When fcc-claude auto-discovers models, use these heuristics to pick the right one:

### For Code Tasks
1. **Large context (full repo):** `nvidia/llama-3.1-405b-instruct` (128K) or `groq/llama-3.3-70b-versatile`
2. **Fast iteration:** `nvidia/llama-3.1-8b-instruct` or `groq/llama-3.1-8b-instant`
3. **Code specialist:** `nvidia/codellama-70b` or `openrouter/qwen-2.5-coder-32b-instruct`
4. **Best quality:** `nvidia/nemotron-4-340b-instruct` or `openrouter/owl-alpha`

### For Writing/Content
1. **Long-form:** `gemini-2.5-flash-lite-preview-06-17` (1M context!)
2. **Creative:** `openrouter/pareto-code` (actually good at prose despite name)
3. **Fast drafts:** `groq/gemma2-9b-it`
4. **Professional tone:** `nvidia/mistral-large-2-instruct`

### For CV/Resume Tasks
1. **Tailoring to job:** `gemini-2.5-flash` (good formatting, understands structure)
2. **Keyword optimization:** `nvidia/llama-3.1-70b-instruct`
3. **ATS compatibility check:** `openrouter/owl-alpha`
4. **Quick polish:** `groq/llama-3.3-70b-versatile`

### Cost-Aware Fallback Chain
```
nvidia/nemotron-4-340b → nvidia/llama-3.1-405b → openrouter/owl-alpha → groq/llama-3.3-70b → nvidia/llama-3.1-8b
(Highest quality)                                                              (Fastest/cheapest)
```

---

## Rate Limits Summary

| Provider | Rate Limit | Notes |
|----------|-----------|-------|
| OpenRouter | Varies by model | Free models: ~20 RPM; negative cost: unlimited |
| NVIDIA NIM | 40 RPM default | Some models have 10 RPM; check per-model limits |
| Groq | 30 RPM, 60k tokens/request | Very fast inference (~500 tokens/sec) |
| Gemini | 1,500 requests/day | Per-model quota; resets at midnight PT |

**Pro tip:** For high-volume tasks (like job application bot), rotate between providers to avoid hitting any single rate limit.