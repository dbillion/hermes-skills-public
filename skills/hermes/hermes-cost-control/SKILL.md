---
name: hermes-cost-control
description: Track and cap Hermes Agent token/cost spend; budget plugin.
version: 1.0.0
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags: [hermes, cost, tokens, budget, telemetry, plugins]
    related_skills: [hermes-use-case-impl]
---

# Hermes Cost Control

## When to Use
- User wants to track token usage, cut their token bill, or see a cost breakdown.
- User references hermesatlas use case 04 ("Cut your token bill").
- User wants a budget guardrail / hard spend cap on Hermes (autonomous, cron, or paid models).
- Before installing any community cost/telemetry tool — audit native coverage first.

Two layers: **measure** (native, zero-install) and **enforce** (community plugin).
Do measurement first — most "bill shock" is fixed per-call overhead, not useful work.

## 1. Measure first (native, no install)
These already exist in Hermes Agent — use them before pulling external tools:
- `hermes insights` — 30-day usage analytics (sessions, tokens, models, cost).
- `hermes --usage-file <path> -z "<prompt>"` — one-shot JSON cost/token report.
- `hermes prompt-size` — measures the fixed prompt/system/tool-schema overhead
  (the "73% of every call is fixed overhead" problem the community talks about).
- `hermes doctor`, `hermes monitoring` — built-in health/monitoring.

## 2. Enforce with a plugin (use case 04)
`hermes-telemetry` (nujovich) is a real Hermes plugin that adds a **hard budget
ceiling** native tooling lacks. Install via the supported path (do NOT hand-copy):
```
hermes plugins install nujovich/hermes-telemetry
hermes plugins enable hermes-telemetry
hermes plugins doctor hermes-telemetry   # validate against runtime contracts
```
- `doctor` must pass (12 hooks, no privileged tool-override needed). If it offers
  `--allow-tool-override`, decline unless you explicitly want interception.
- Restart the gateway for hooks to take effect: `hermes gateway restart`
  (cannot be done from inside a gateway-connected session — run from a real terminal).

## 3. Budget config
Write `~/.hermes/telemetry/budget.yaml` (see templates/budget.yaml). Key points:
- Scopes: `global` (catches everything, incl. delegated subagent spend),
  `per_cron_job`, `per_sender`, `per_profile`.
- `global` is the real catch-all — per-cron-job budgets EXCLUDE `delegate_task`
  subagent cost, so rely on `global` for a true ceiling.
- `thresholds.soft_pct` (warn) / `hard_pct` (enforce). `on_estimated: warn_only`
  keeps estimate-based spend from hard-cutting real work.

## 4. Verify (don't assume it works)
```
hermes plugins doctor hermes-telemetry     # structural validation
hermes plugins show hermes-telemetry        # confirms enabled + exposes /stats /budget
python3 -c "import yaml; yaml.safe_load(open('/home/deeone/.hermes/telemetry/budget.yaml'))"
```
Live enforcement is exercised by the plugin's own `check('global')` at the next
session; a benign `status='ok'` verdict with `spent=0.0` proves the path is live.

## Pitfalls
- **Hard cap is a tool-gate, not a mid-call abort.** An in-flight model stream
  still completes and is billed; further tool-driven work is blocked at the next
  tool boundary; cron jobs are paused. Set the cap knowing this.
- **Don't install heavy redundant trackers.** `tokscale` (Rust/bun, Docker,
  global leaderboard) duplicates `hermes insights` for personal use — skip it
  unless you need cross-agent fleet accounting.
- **Write large reference docs in chunks.** A `write_file` of a very large body can
  time out the stream; write a small first chunk, then `patch`-append the rest
  (keep each call < ~8K tokens). Applies to skill files too.

## References
- references/hermes-telemetry-verify.md — verification recipe details.
- templates/budget.yaml — known-good budget config to copy/modify.
