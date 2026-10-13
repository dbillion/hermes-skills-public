# LinkedIn Job Applier Troubleshooting Guide

**Session Date:** 2026-05-27  
**Status:** Partially working — LLM evaluation works, but LinkedIn navigation and Easy Apply dialog opening are unreliable.

## Quick Diagnostic Flow

```
1. Check LLM provider → Is API key valid? → Test with simple prompt
2. Check credits/quota → OpenRouter: $1+ balance? Gemini: 429 errors?
3. Check LinkedIn auth → Email/password or cookies valid? → Try manual login
4. Check for bot detection → Timeout on jobs page? → Use persistent Chrome profile
```

## Error Patterns & Solutions

### 1. LLM Error 402 (OpenRouter Insufficient Credits)

**Symptom:**
```
openai.APIStatusError: Error code: 402 - {'error': {'message': 
'This request requires more credits, or fewer max_tokens. 
You requested up to 65536 tokens, but can only afford 223.'}}
```

**Root Cause:** OpenRouter account has insufficient credits for large token requests.

**Solution:**
1. Visit https://openrouter.ai/settings/credits
2. Add $1-2 (provides thousands of Gemini Flash requests)
3. Or reduce `max_tokens` in LLM config (not recommended — affects response quality)

**Verification:**
```bash
curl -H "Authorization: Bearer *** \
  https://openrouter.ai/api/v1/credit
```

---

### 2. Gemini Error 429 (Quota Exhausted)

**Symptom A — Standard quota:**
```
google.api_core.exceptions.ResourceExhausted: 429 Resource exhausted
You exceeded your current quota, please check your plan and billing details.
limit: 20, current: 21
```

**Symptom B — Zero quota (reported by many users):**
```
google.api_core.exceptions.ResourceExhausted: 429
limit: 0, current: 1
```

**Root Cause:** 
- `gemini-3-flash-preview`: Only 20 requests/day (exhausted after resume parsing + ~5 jobs)
- `gemini-2.0-flash`: Documented as 1,500/day but many users get `limit: 0`

**Solution:**
1. **Immediate:** Switch to OpenRouter (see Error 402 solution above)
2. **Alternative:** Change to `gemini-2.0-flash` if you have confirmed free tier access
   ```env
   LLM_PROVIDER=gemini
   LLM_MODEL=gemini-2.0-flash
   ```

**Verification:**
```python
import google.generativeai as genai
genai.configure(api_key="AIzaSy...")
model = genai.GenerativeModel("gemini-2.0-flash")
print(model.generate_content("Hello").text)
```

---

### 3. LinkedIn Navigation Timeout (Bot Detection)

**Symptom:**
```
TimeoutError: Page.goto: Timeout 30000ms exceeded
URL: https://www.linkedin.com/jobs/search/...
```

**Root Cause:** LinkedIn detects and blocks headless browsers (even with `patchright` stealth).

**Solutions (in order of effectiveness):**

#### A. Use Persistent Chrome Profile (BEST)

Reuse your actual Chrome browser session with real cookies:

```python
# In src/utils/browser_utils.py or main.py
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch_persistent_context(
        user_data_dir="/home/deeone/.config/google-chrome",
        headless=False,  # MUST be False to avoid detection
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
        ],
    )
    page = browser.pages[0] if browser.pages else await browser.new_page()
```

**Why this works:** LinkedIn sees real Chrome fingerprint, browsing history, and authenticated session cookies.

#### B. Switch to Indeed

```python
# config/app_config.py
JOB_SITE = "indeed"  # Less aggressive bot detection
```

#### C. Semi-Automated Mode

Run bot to find/score jobs, then apply manually:

```python
# config/app_config.py
TEST_MODE = True  # Don't submit applications, just evaluate
MAX_APPLIES_NUM = 20
```

Then review `data/output/linkedin/interesting_jobs.yaml` and apply manually.

---

### 4. Easy Apply Dialog Not Opening

**Symptom:**
```json
{
  "company_name": "Ideawise Group",
  "job_title": "Operations Engineer",
  "interest_reason": "Could not apply to Operations Engineer at Ideawise Group. Reason: Easy Apply dialog did not open",
  "interest_score": 70
}
```

**Root Cause:** 
- LinkedIn UI changed (selectors outdated)
- Job doesn't actually support Easy Apply (button leads to external site)
- Click handler failed (network issue, modal blocked)

**Debugging Steps:**

1. **Enable debug mode:**
   ```python
   # config/app_config.py
   DEBUG_MODE = True
   ```

2. **Check screenshots:**
   ```bash
   ls -lt data/debug/*.png | head -5
   feh data/debug/$(ls -t data/debug/*.png | head -1)
   ```

3. **Check HTML capture:**
   ```bash
   ls -lt data/debug/*.html | head -5
   ```

4. **Manual verification:**
   - Open the job URL in your real browser
   - Check if "Easy Apply" button exists
   - Check if it opens a modal or redirects externally

**Solution:** 
- Bot already skips these jobs (added to `interesting_jobs.yaml`)
- Apply manually to high-score jobs from this list
- No automated fix available (LinkedIn UI changes frequently)

---

### 5. TypeError: Cannot unpack NoneType

**Symptom:**
```
TypeError: cannot unpack non-iterable NoneType object
  File "job_manager_linkedin.py", line 327, in apply_job
    (job_is_interesting, score, reasoning) = self.llm_answerer_component.job_is_interesting(...)
```

**Root Cause:** LLM evaluation returned `None` instead of a tuple (usually due to API error or malformed response).

**Solution:** Already patched with error handling:

```python
# src/job_manager/linkedin/job_manager_linkedin.py (line 327+)
try:
    result = self.llm_answerer_component.job_is_interesting(job.model_dump())
    if result is None or not isinstance(result, tuple) or len(result) != 3:
        logger.warning(f"LLM evaluation returned invalid result: {result}, defaulting to interested")
        job_is_interesting, score, reasoning = True, 50, "LLM evaluation failed, defaulting to interested"
    else:
        job_is_interesting, score, reasoning = result
except Exception as e:
    logger.warning(f"LLM evaluation error: {e}, defaulting to interested")
    job_is_interesting, score, reasoning = True, 50, "LLM evaluation error, defaulting to interested"
```

**Verification:**
```bash
cd /home/deeone/LinkedIn-AI-Job-Applier-Ultimate
grep -A10 "result = self.llm_answerer_component.job_is_interesting" src/job_manager/linkedin/job_manager_linkedin.py
```

---

### 6. Resume Parsing Gaps

**Symptom:**
```
Resume parsing completed with 42 missing or placeholder fields
```

**Root Cause:** LLM couldn't extract all fields from your resume (normal for optional fields like date of birth, grades, references).

**Impact:** Bot will fill "No info" for missing fields during Easy Apply. Some applications may fail if LinkedIn requires specific fields.

**Solution:**
1. **Review recommendations:**
   ```bash
   cat data/output/linkedin/resume_recommendations.txt
   ```

2. **Optional:** Manually edit the parsed resume JSON:
   ```bash
   cat data/output/linkedin/parsed_resume.json
   # Edit to fill gaps
   ```

3. **Better:** Update your actual resume PDF with missing key info (skills, dates, education)

---

### 7. Invalid API Key (Masked/Corrupted)

**Symptom:**
```
google.api_core.exceptions.InvalidArgument: 400 API key not valid. Please pass a valid API key.
```

**Root Cause:** The `.env` file contains a literally masked key like `AIzaSy...YzKU` instead of the full 39-character key.

**Diagnosis:**
```bash
cd /home/deeone/LinkedIn-AI-Job-Applier-Ultimate
grep "^llm_api_key=" .env
# Should be 39 chars for Gemini (starts with AIzaSy)
# Should be 73 chars for OpenRouter (starts with sk-or-v1-)
```

**Solution:**
1. Get the real key from source:
   - **Gemini:** https://aistudio.google.com/app/apikey
   - **OpenRouter:** https://openrouter.ai/keys

2. Update `.env`:
   ```bash
   cd /home/deeone/LinkedIn-AI-Job-Applier-Ultimate
   # Edit .env manually or use:
   python3 -c "
   with open('.env', 'r') as f:
       lines = f.readlines()
   with open('.env', 'w') as f:
       for line in lines:
           if line.startswith('llm_api_key='):
               f.write('llm_api_key=YOUR_ACTUAL_KEY_HERE\n')
           else:
               f.write(line)
   "
   ```

3. **Verify length:**
   ```bash
   grep "^llm_api_key=" .env | cut -d'=' -f2 | wc -c
   # Gemini: 40 (39 + newline)
   # OpenRouter: 74 (73 + newline)
   ```

---

## LLM Provider Comparison (2026-05-27)

| Provider | Model | Quota/Limit | Cost | Reliability | Recommendation |
|----------|-------|-------------|------|-------------|----------------|
| **OpenRouter** | `~google/gemini-flash-latest` | No daily limit | ~$0.0001/request | ⭐⭐⭐⭐⭐ | **BEST** — Add $1-2 credits |
| **Gemini** | `gemini-2.0-flash` | 1,500/day (or `limit: 0` for some users) | Free | ⭐⭐ | Unreliable — many report `limit: 0` |
| **Gemini** | `gemini-3-flash-preview` | 20/day | Free | ⭐ | Too low — exhausts after ~5 jobs |

**Conclusion:** Use OpenRouter with $1-2 credits for production job applying. Gemini free tier is unreliable for this use case.

---

## Monitoring & Success Metrics

### What to Watch For

**Good signs:**
- ✅ "Login successful"
- ✅ "Filters applied"
- ✅ "Found X job elements"
- ✅ "LLM evaluation completed in X seconds"
- ✅ "Applied to [Job] at [Company]"

**Warning signs:**
- ⚠️ "LLM evaluation returned invalid result" (handled, but suboptimal)
- ⚠️ "Skipping [Job] — score below threshold" (normal, but check `interesting_jobs.yaml`)
- ⚠️ "Easy Apply dialog did not open" (LinkedIn UI issue)

**Critical errors:**
- ❌ "TimeoutError: Page.goto" (bot detection — use persistent Chrome)
- ❌ "Error 402" (OpenRouter credits — add funds)
- ❌ "Error 429" (Gemini quota — switch to OpenRouter)
- ❌ "Invalid API key" (masked key — update with real key)

### Output Files to Check

After each run:

```bash
cd /home/deeone/LinkedIn-AI-Job-Applier-Ultimate

# Success count
echo "Applications sent:"
grep -c "company_name:" data/output/linkedin/success.yaml || echo "0"

# Interesting jobs (high score but couldn't auto-apply)
echo "Interesting jobs (manual apply recommended):"
cat data/output/linkedin/interesting_jobs.yaml | grep "company_name:" | wc -l

# Skip reasons
echo "Top skip reasons:"
grep "skip_reason:" data/output/linkedin/skipped.yaml | sort | uniq -c | sort -rn | head -5

# Latest errors
echo "Latest errors:"
tail -100 logs/app.log | grep -i "error\|fail\|timeout" | tail -10
```

---

## Session-Specific Fixes Applied

1. **Model selection:** Changed from `gemini-3-flash-preview` (20/day) to `~google/gemini-flash-latest` via OpenRouter
2. **Error handling:** Patched `apply_job()` to handle `None` returns gracefully
3. **Cache clearing:** Added cache clear before runs to avoid stale bytecode
4. **Key management:** Script to copy OpenRouter key from `~/.hermes/.env` to project `.env`

---

## When to Give Up on Automation

**Signs it's time to switch to manual:**

1. **Persistent navigation timeouts** even with persistent Chrome profile
2. **LinkedIn account restrictions** (CAPTCHAs, temporary bans)
3. **More time debugging than applying** (>1 hour setup for <5 applications)
4. **UI changes breaking selectors** (requires code updates)

**Alternative workflow:**
1. Run bot in `TEST_MODE = True` to discover/score jobs
2. Review `interesting_jobs.yaml` for high-score matches
3. Apply manually to top 10-20 jobs
4. This gives you LLM-powered job discovery without the fragility of automated applying

---

## Contact & Updates

If LinkedIn changes their UI or new error patterns emerge, update this reference file with:
- Error message
- Root cause analysis
- Solution steps
- Verification commands

**Last updated:** 2026-05-27  
**Bot version:** LinkedIn-AI-Job-Applier-Ultimate (beatwad/LinkedIn-AI-Job-Applier-Ultimate)