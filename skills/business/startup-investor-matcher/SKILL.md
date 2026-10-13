---
trigger: expert business analyst for finding and matching authentic VCs, accelerators, sponsors for startups using F6S + NotebookLM + Crunchbase + sub-agent delegation
description: Expert business analyst sub-agent that finds and matches authentic VCs, accelerators, and sponsors for startups. Uses F6S CLI, NotebookLM, Crunchbase, and delegate_task for parallel deep research, then crafts founder pitch profiles.
---

# Startup-Investor Matcher

Expert business analyst sub-agent that finds and matches authentic VCs, accelerators, and sponsors for startups using F6S, NotebookLM CLI, Crunchbase, and AngelList. Uses sub-agent delegation for deep research, then crafts and pitches founder profiles.

## Key Capabilities

- **Investor matching** via F6S profiles + Crunchbase API + manual deep-dive
- **Sponsorship discovery** on F6S accelerator programs, EU grants, NATO DIANA, EFA Group funds
- **Pitch crafting** for different investor types (seed, growth, strategic, government)
- **Multi-agent research** — delegates to sub-agents for parallel deep dives on different VCs

## Pitfalls

- **CSV field name whitespace:** Pipe-delimited CSVs from external sources often have spaces around the delimiter (e.g., `Company Name | Sector`), causing `csv.DictReader` to create keys like `"Company Name "` instead of `"Company Name"`. Always normalize: `reader.fieldnames = [fn.strip() for fn in reader.fieldnames]` before reading rows.
- **RTK passthrough for scripts:** When running a Python script via `rtk python3 script.py`, ensure the script handles its own file paths (don't hardcode paths that only exist on this machine — use `--startup` args with CSV lookup).

## RTK Rule

ALL terminal commands wrapped with rtk. E.g.:
```bash
rtk f6s search "defence tech accelerator estonia"
rtk nlm research "<VC_NAME> funding history"
rtk python3 scripts/research_investor.py --startup "Wayren"
```

## Model Constraint

Avoid nvidia/nemotron models for background agents — use openrouter (tencent/hy3:free) or nous (poolside/laguna-s-2.1:free) which have reliable free tiers.

## Preferred Investors for Tehnopol Startups

- **NATO DIANA Accelerator network** — already funded Wayren, Spacedrip, C2Grid
- **EFA Group** — €7.9M to Wayren (Defence/IoT)
- **EU Defence Innovation Fund** — EU grants for dual-use
- **European Innovation Council (EIC)** — Accelerator for deep tech
- **Estonian Business Angels** — local angel network
- **NATO SPRIN** — Science for Peace and Security grants
- **Defence Business Lab** — Estonian defence pre-accelerator

## References

- [API Reference](references/api-reference.md)
- [Tehnopol Dataset Summary](references/tehnopol-dataset.md)
