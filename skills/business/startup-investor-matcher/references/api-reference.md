# Startup-Investor Matcher — API Reference

## F6S CLI
```bash
rtk f6s search "query" --type accelerator
rtk f6s profile <f6s-id> --fields name,investments,sectors
rtk f6s programs --country estonia --sector defence
```

## Crunchbase via CLI
```bash
rtk cb search investors --region europe --sector defence-tech
rtk cb search accelerators --program-name "NATO DIANA"
```

## NotebookLM Research
```bash
nlm login --check
nlm notebook create "VC Deep Dive"  # returns notebook-id
nlm add <notebook-id> --url <url>  # add Crunchbase/F6S profile
nlm research --mode deep --query "<investor-name> funding history"
nlm export <notebook-id> --format csv
```

## Sub-Agent Delegation Pattern
```python
# Use delegate_task to spawn parallel researchers:
delegate_task(tasks=[{
    "goal": "Deep research VC firm: <Firm Name>",
    "context": "Focus on defence tech investments in Baltic/Nordic region"
}, {
    "goal": "Deep research accelerator: <Accelerator Name>",
    "context": "Focus on NATO DIANA or EU defence funding"
}])
```

## Research Script
```bash
rtk python3 scripts/research_investor.py --startup "Wayren" --sector "Defence" --tier seed
```
