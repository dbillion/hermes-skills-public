# NotebookLM (`nlm` CLI) for evidence-based skill upgrades

Tool: `nlm` (uv tool `notebooklm-mcp-cli`). Auth uses saved browser cookies/CSRF,
NOT a token you type. Default profile in this env: `oludayo35` (63 cookies present).
Multiple profiles available (`nlm login` to switch).

## Discover + mine sources
```
# deep research (~5 min, ~40 sources) — ALWAYS background it, it exceeds 60s cap
nlm research start "<query>" --source web --mode deep \
    --notebook-id <NB_ID> --auto-import --force

# poll (also slow ~60s; the start with --auto-import imports on completion)
nlm research status <NB_ID>

# once imported, mine the actual content
nlm notebook list
nlm source list <NB_ID>
nlm source describe <SOURCE_ID>      # AI summary + keywords
nlm source content  <SOURCE_ID>      # raw text
nlm notebook query <NB_ID> "how do you encode X visually"
```

## Picking a notebook
List with `nlm notebook list`. Reuse an existing topic notebook instead of
spawning a new one. For DSA work the existing notebook
`DSA Java QA Harness - 60 Algorithms` (id `1bc17870-421c-4f46-bbe2-1fa4d544a236`)
is the natural home. A new one can be created with `nlm notebook create -t "<title>"`.

## Why use it
Don't invent color/encoding conventions for explainer skills — search real sources
(scientific viz color-mapping, 3b1b/Veritasium motion language) and CITE them when
patching the skill's grammar. Evidence beats opinion for durable conventions.

## Pitfalls
- `research start --mode deep` ~5 min: run with `terminal(background=true,
  notify_on_complete=true)`; never foreground (60s cap kills it).
- `research status` itself can hit the 60s cap; query a specific notebook_id.
- `--auto-import` imports discovered sources into the notebook when the task finishes.
