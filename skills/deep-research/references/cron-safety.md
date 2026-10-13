# Cron Safety — deep-research

## Context Blowup Pattern

**Problem:** This skill's SKILL.md is 130KB+ (1,709 lines). When attached to a Hermes cron job, the combined system prompt + skill exceeds the model's context window (4K-10K tokens), causing "Context length exceeded" errors.

**Symptoms:**
- `RuntimeError: Context length exceeded (10,026 tokens). Cannot compress further.`
- Cron job fails with model errors, especially when combined with other skills like `gws-gmail`

**Root Cause:**
- Hermes loads the full SKILL.md of every skill listed in the cron job's `skills` array into the system prompt
- Skills with large SKILL.md files (100KB+) blow up context even before the prompt runs
- The `last30days` skill and `deep-research` skill are the two worst offenders

**Fix:**
1. Set `skills: []` (empty) on cron jobs that need to run reliably
2. Use direct tool calls in the cron prompt instead of relying on skill loading
3. For research tasks in cron, use `delegate_task` to spawn a subagent with the skill attached (isolates context cost)

**Working pattern for cron jobs:**
```
skills: []  ← empty, no skill loading
prompt: "Use web_search and web_extract directly to find..."
```

**Anti-pattern (causes failures):**
```
skills: ["deep-research"]  ← this will blow up context
prompt: "Research..."
```

## Model-Specific Limits

| Model | Context Limit | Safe Skill Budget |
|---|---|---|
| nvidia/nemotron-mini-4b-instruct | 4K tokens | 0 skills (use direct prompts) |
| openrouter/owl-alpha | 8K tokens | 1 small skill max |
| claude-sonnet-4 | 200K tokens | 2-3 skills OK |

**Rule of thumb:** If a skill's SKILL.md > 10KB, never attach it to a cron job.