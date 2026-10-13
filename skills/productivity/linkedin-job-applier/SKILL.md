---
name: linkedin-job-applier
description: "AI-powered LinkedIn job application bot using Playwright browser automation, LLM-based job evaluation, and Easy Apply automation."
metadata: {"requires": {"bins": ["uv", "python3"], "env": ["llm_api_key", "linkedin_email", "linkedin_password", "li_at"], "quota_warnings": ["Gemini free tier: 20 req/day (gemini-3-flash-preview) or 1,500 req/day (gemini-2.0-flash)"]}}
---

# LinkedIn AI Job Applier Ultimate

AI-powered job application bot for LinkedIn that automates job search, evaluation, and Easy Apply submissions using Playwright browser automation and LLM-based form filling.

Repo: https://github.com/beatwad/LinkedIn-AI-Job-Applier-Ultimate

## Setup

### 1. Clone and Install

```bash
cd /home/deeone
git clone https://github.com/beatwad/LinkedIn-AI-Job-Applier-Ultimate.git
cd LinkedIn-AI-Job-Applier-Ultimate
uv sync
```

### 2. Configure `.env`

```bash
# LinkedIn Credentials
li_at=<your_li_at_cookie>
linkedin_email=<your_email>
linkedin_password=<your_password>

# LLM Provider (choose one)
# Option A: Gemini 2.0 Flash (1,500 req/day free tier)
LLM_PROVIDER=gemini
llm_api_key=<your_gemini_key>
LLM_MODEL=gemini-2.0-flash

# Option B: OpenRouter (paid credits, no daily limit)
# LLM_PROVIDER=openrouter
# OPENROUTER_API_KEY=<your_openrouter_key>
# OPENROUTER_MODEL=google/gemini-2.0-flash-001

# Telegram (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

### 3. Add Your Resume

Place your resume PDF at: `data/resumes/resume.pdf`

The bot will parse it with LLM and generate a structured JSON with fields for:
- Personal info (name, email, phone, location)
- Education (institutions, degrees, dates)
- Experience (positions, companies, dates, responsibilities)
- Skills, projects, certifications, languages

### 4. Configure Search Parameters

Edit `config/search_config.yaml`:

```yaml
positions:
  - Senior Software Engineer
  - Java Developer
  - Backend Engineer
  - Full Stack Developer

remote: true
hybrid: true
onsite: false

experience_level:
  internship: false
  entry: false
  associate: false
  mid_senior: true
  director: false
  executive: false

job_types:
  full_time: true
  contract: true
  part_time: false
  temporary: false
  voluntary: false
  internship: false

date:
  all_time: false
  month: true
  week: false
  24_hours: false

with_company: []
with_date: []

blacklist:
  positions: []
  companies: []
  locations: []
```

### 5. Run the Bot

```bash
cd /home/deeone/LinkedIn-AI-Job-Applier-Ultimate
uv run python main.py
```

📚 **Troubleshooting Guide:** See `references/troubleshooting-2026-05-27.md` for detailed debugging patterns, LLM provider comparison (OpenRouter vs Gemini quotas), and LinkedIn bot detection workarounds. **Critical:** OpenRouter requires $1-2 credits for large token requests; Gemini free tier often shows `limit: 0` despite documentation.

## Configuration Flags (`config/app_config.py`)

- `JOB_SITE`: "linkedin" or "indeed"
- `MAX_APPLIES_NUM`: Maximum applications per run (default: 20)
- `HEADLESS_MODE`: Run browser without UI
- `EASY_APPLY_ONLY_MODE`: Only apply to Easy Apply jobs
- `TEST_MODE`: Simulate without submitting
- `DEBUG_MODE`: Save screenshots/HTML on errors
- `MONKEY_MODE`: Randomize typing speed (anti-bot detection)

## LLM Provider Selection (CRITICAL: Know the Difference!)

### **DIRECT Google Gemini API** (Recommended for Free Tier)

Uses your Google AI Studio API key directly (`AIzaSy...`). **NOT the same as OpenRouter's Gemini proxy!**

**Free tier quotas (2026 verified):**
- `gemini-1.5-flash`: 1,500 requests/day, 60,000 input tokens/minute ✅ **WORKING**
- `gemini-2.0-flash`: 1,500 requests/day OR `limit: 0` (unreliable, many users report exhausted quota) ⚠️

**Configuration:**
```env
# .env
LLM_MODEL_TYPE=gemini  # NOT "openrouter"
llm_api_key=AIzaSy...   # Your DIRECT key from https://aistudio.google.com/app/apikey (39 chars)
EASY_APPLY_MODEL=gemini-1.5-flash  # Most reliable free model

# DO NOT set OPENROUTER_API_KEY when using direct Gemini
```

```python
# config/app_config.py
LLM_MODEL_TYPE = "gemini"  # Uses direct Google API
EASY_APPLY_MODEL = "gemini-1.5-flash"  # NOT gemini-2.0-flash (often shows limit: 0)
```

**⚠️ Common Mistake:** Using `gemini-2.0-flash` through OpenRouter (`LLM_MODEL_TYPE=openrouter`) instead of direct Google API. This causes:
- Quota errors from OpenRouter credit limits, not Google's free tier
- Confusion between "402 Insufficient Credits" (OpenRouter) vs "429 RESOURCE_EXHAUSTED" (Google direct)

**Troubleshooting:**
- If you see `RESOURCE_EXHAUSTED` with `limit: 0`, your Google API key's free tier is exhausted for that model → Switch to `gemini-1.5-flash`
- If you see `Error 402: insufficient credits`, you're using OpenRouter → Add credits or switch to direct Gemini

### **OpenRouter** (Pay-per-token, No Daily Limits)

Uses your OpenRouter API key (`sk-or-...`). Proxies multiple models including Gemini, but uses YOUR OpenRouter credits, NOT Google's free tier.

**Minimum credit requirement:** $1-2 provides 2,000-5,000+ requests for cheap models.

**CRITICAL: Your OpenRouter account must have sufficient credits BEFORE running.** The bot's LangChain `ChatOpenAI` defaults to 65,536 token capacity per call. OpenRouter checks if you can afford the MAX potential cost, not the actual usage.

**Session 2026-05-27 findings:** User `user_2t4v40CDUd9EGGAo0wqYfBcZi7c` repeatedly hit `Error 402: You requested up to 65536 tokens, but can only afford 223` across multiple models (`owl/alpha-72b`, `~google/gemini-flash-latest`, `google/gemini-3.5-flash`, `openrouter/pareto-code`). **Reducing `max_tokens` parameter to 8192 did NOT fix the issue** — OpenRouter's credit check uses the model's inherent maximum output capacity, not your runtime parameter.

**Fix:** Add credits at https://openrouter.ai/settings/credits BEFORE running. There is no workaround for insufficient credits.

**Verified FREE/LOW-COST models on OpenRouter:**
- `openrouter/owl-alpha` — Free, 128K context ✅ **RECOMMENDED FREE MODEL**
- `openrouter/pareto-code` — Free/Negative cost (they pay YOU!) but still requires minimum credit buffer
- `openrouter/google/gemini-flash-1.5` — Low cost ($0.000075/$0.0003 per 1K tokens)

**INVALID model IDs (DO NOT USE):**
- `owl/alpha-72b` — ❌ Invalid! Correct ID is `openrouter/owl-alpha`
- `google/gemini-3.5-flash` — ❌ Often returns 404 or requires excessive credits

**Configuration:**
```env
# .env
OPENROUTER_API_KEY=sk-or-...  # From https://openrouter.ai/keys
LLM_MODEL_TYPE=openrouter
EASY_APPLY_MODEL=openrouter/owl-alpha  # Correct ID, NOT owl/alpha-72b
```

```python
# config/app_config.py
LLM_MODEL_TYPE = "openrouter"
EASY_APPLY_MODEL = "openrouter/owl-alpha"
```

### **Groq** (Free, Super Fast)

Uses Groq API for Llama models. Fast inference, good for quick evaluations.

**Free models:**
- `groq/llama-3.1-8b-instant` — 8B params, 128K context, very fast
- `groq/llama-3.3-70b-versatile` — 70B params, better quality

**Configuration:**
```env
# .env
GROQ_API_KEY=gsk_...  # From https://console.groq.com/keys
LLM_MODEL_TYPE=groq
EASY_APPLY_MODEL=llama-3.3-70b-versatile
```

---

## Comparison: Direct Gemini vs OpenRouter

| Aspect | Direct Gemini API | OpenRouter |
|--------|-------------------|------------|
| **API Key** | `AIzaSy...` (Google AI Studio) | `sk-or-...` (OpenRouter) |
| **Free Tier** | ✅ 1,500 req/day (gemini-1.5-flash) | ❌ No free tier (pay per token) |
| **Rate Limits** | Per-minute & per-day quotas | No daily limits, only credit balance |
| **Error Codes** | 429 RESOURCE_EXHAUSTED | 402 Insufficient Credits |
| **Token Limits** | Model-specific (e.g., 1M for Gemini 1.5) | Checked against your credit balance |
| **Best For** | Free tier users, high volume | Users with credits, need model variety |
| **Reliability** | ✅ `gemini-1.5-flash` very reliable | ⚠️ Requires $1-2 minimum credits |

**Decision Tree:**
1. **Want completely free?** → Use **Direct Gemini** with `gemini-1.5-flash`
2. **Have OpenRouter credits?** → Use `openrouter/owl-alpha` (free model on OR)
3. **Need fastest inference?** → Use **Groq** with `llama-3.3-70b-versatile`
4. **Hit Google quota?** → Add OpenRouter credits or wait 24h for reset

---

### OpenRouter Token Limit Patch (If You Have Minimal Credits)

If you have OpenRouter credits but keep hitting 402 errors, you can try reducing the token limit. **Warning:** This does NOT guarantee success if your balance is too low. OpenRouter may still block based on the model's inherent max output capacity.

```python
# src/llm/llm_manager.py — OpenRouterModel.__init__
self.model = ChatOpenAI(
    model_name=self.model_name,
    openai_api_key=api_key,
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=TEMPERATURE,
    timeout=60,
    max_tokens=8192,  # Reduced from 65536 — may help with marginal credit balances
)
```

---

### Automatic Fallback Pattern

If you want to use Direct Gemini but fallback to OpenRouter on rate limits:

```python
# src/llm/llm_manager.py — wrap Gemini invoke:
try:
    response = self.model.invoke(prompt_messages)
except ChatGoogleGenerativeAIError as e:
    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
        logger.warning("Gemini rate limited, falling back to OpenRouter with owl-alpha")
        # Switch to OpenRouter
        self.model_type = "openrouter"
        self.easy_apply_model = "openrouter/owl-alpha"
        api_key = os.getenv("OPENROUTER_API_KEY")
        from openrouter_model import OpenRouterModel  # Your implementation
        self.model = OpenRouterModel(api_key, self.easy_apply_model)
        response = self.model.invoke(prompt_messages)
    else:
        raise
```

## Output Files

- `data/output/linkedin/success.yaml` — Successful applications
- `data/output/linkedin/failed.yaml` — Failed applications with reasons
- `data/output/linkedin/skipped.yaml` — Skipped jobs with LLM reasoning
- `data/output/linkedin/interesting_jobs.yaml` — High-score jobs worth manual review
- `data/output/linkedin/resume_recommendations.txt` — Resume gaps identified by LLM
- `logs/app.log` — Full runtime log
- `data/debug/*.png` — Screenshots on errors (if DEBUG_MODE=true)

## Common Issues

### LLM Rate Limit (429 or RESOURCE_EXHAUSTED)
**Symptom:** "You exceeded your current quota" or "20 requests/day limit"

**Fix:** Switch to `gemini-2.0-flash` (1,500 req/day) or use OpenRouter:
```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash
```

### Invalid API Key
**Symptom:** "API key not valid. Please pass a valid API key."

**Cause:** The `.env` file has a masked/corrupted key (e.g., literally `AIzaSy...YzKU`)

**Fix:** Re-enter the actual API key (39 chars for Gemini, starts with `AIzaSy`)

### apply_job Returns None / TypeError
**Symptom:** `TypeError: cannot unpack non-iterable NoneType object`

**Cause:** The `apply_job()` method returns `None` when Easy Apply dialog fails to open or LLM returns malformed response.

**Fix:** Check `data/debug/` for screenshots. Common causes:
- LinkedIn UI changed (selectors outdated)
- LLM response parsing failed (add `str()` wrapper for `parsed_reply`)
- Easy Apply button not found (job doesn't support Easy Apply)

### Company Already Encountered
**Symptom:** "The company has already been encountered and the setting is not to apply again"

**Cause:** Bot tracks companies to avoid duplicate applications in the same run.

**Fix:** This is intentional. To apply to multiple jobs at the same company, disable the duplicate check in `config/app_config.py`.

### Resume Parsing Gaps
**Symptom:** "Found 42 missing or placeholder fields"

**Cause:** LLM couldn't extract all fields from your resume. Normal for optional fields (date of birth, grades, etc.).

**Fix:** Review `data/output/linkedin/resume_recommendations.txt` for gaps. The bot will fill "No info" for missing fields during application.

## Pitfalls

**CRITICAL: LinkedIn Bot Detection**

If you see `TimeoutError: Page.goto: Timeout 30000ms exceeded` when navigating to the jobs search page, LinkedIn is blocking the headless browser. This is the most common failure mode.

**Solutions (in order of effectiveness):**

1. **Use authenticated Chrome session** (BEST):
   ```python
   # In main.py or browser_utils.py, replace:
   # browser = await chromium.launch(headless=True)
   
   # With persistent context using your real Chrome profile:
   from playwright.async_api import async_playwright
   
   async with async_playwright() as p:
       browser = await p.chromium.launch_persistent_context(
           user_data_dir="/home/deeone/.config/google-chrome",
           headless=False,  # Must be False to avoid detection
       )
   ```
   This reuses your actual Chrome cookies, browsing history, and fingerprint.

2. **Switch to Indeed**:
   ```python
   # config/app_config.py
   JOB_SITE = "indeed"  # Less aggressive bot detection
   ```

3. **Semi-automated approach**:
   - Run bot with `TEST_MODE = True` to discover/score jobs without applying
   - Review `data/output/linkedin/interesting_jobs.yaml`
   - Apply manually to high-score jobs

**Other Pitfalls:**

1. **Don't use gemini-3-flash-preview** — Only 20 req/day, will hit limit after parsing resume + ~5 jobs
2. **Cookies alone aren't enough** — The bot needs email/password for the actual login flow. The `li_at` cookie helps but LinkedIn may still challenge with CAPTCHA
3. **Easy Apply dialog quirks** — Some jobs have multi-step Easy Apply (3-5 screens). The bot handles most but may fail on custom questions
4. **Rate limiting by LinkedIn** — Applying too fast (>10/min) may trigger bot detection. The bot uses human-like delays but don't push it
5. **Resume quality matters** — Garbage in, garbage out. The LLM parses your resume once and uses that JSON for all applications. If it misses key skills, every application will be weak

## Monitoring

Watch the log for:
- "Login successful" — Auth worked
- "Filters applied" — Search configured
- "Found X job elements" — Jobs discovered
- "Applied to [Job] at [Company]" — Success!
- "Skipping [Job]" — LLM decided not to apply (check `skipped.yaml`)

Check `data/output/linkedin/last_run.yaml` for summary stats.

## Advanced: Automatic Fallback to OpenRouter

To auto-fallback when Gemini rate limits:

1. Edit `src/llm/llm_manager.py`
2. Wrap Gemini invoke in try/except
3. On 429 error, instantiate OpenRouterModel and retry

Or set `LLM_PROVIDER=openrouter` from the start (no rate limits, pay per token).

## Authors
- Original: beatwad (GitHub)
- Setup guide: bornofGod session (2026-05-27)