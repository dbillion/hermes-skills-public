---
name: python-modularization
description: Split Python god files by concern; no monoliths.
---

# Python Modularization (anti-god-file)

## When to use
- Writing a new Python module/CLI that could grow past ~200 lines.
- Refactoring an existing file that has become a monolith (the user will call it out: "why are you creating a god file", "can it be modularized", "why is X 358 lines?").
- After any refactor, before declaring done — split AND verify.

## Hard rule (user mandate — non-negotiable)
NO 400-line monoliths. One concern per module. If a file exceeds ~200-400 lines or mixes unrelated responsibilities, split it. The user corrected this twice in one session; treat it as a hard rule, not optional polish. A file that accumulates logic "for now" and gets split later is explicitly rejected — modularize as you build.

## Preferred structure (proven on a Telethon Click CLI)
Three layers:
1. **Thin entry layer** (`cli.py`, ~100-120 lines): only Click decorators + options, wired to call command bodies. No logic.
2. **Command bodies** (`commands.py` or per-command modules): the async/sync implementations. Keep each command's body its own function. If one function embeds a second near-parallel pipeline (e.g. a COPY-mode branch inside forward), extract it to its own module.
3. **Pure primitives** (`peer.py`, `copy_mode.py`, `login.py`, `dedupe.py`, ...): importable + unit-testable without network/IO.

Real sizes after a refactor (all ≤224 lines): cli 116, peer 219, commands 224, login 62, dedupe 52, copy_mode 101.

## Test splitting
Mirror the source layout: one `test_<module>.py` per source module. Do NOT keep a single `test_offline.py` god file (it hit 353 lines). Each test file covers exactly its module's concern.

## Pitfalls
- Accumulating logic into one file "for now" then splitting later is rejected — modularize from the start.
- Don't use `__import__("time")` / `__import__("asyncio")` hacks inside functions; hoist to real top-level imports.
- Moving a symbol (e.g. `_is_from_source` cli → peer) breaks test imports — update them; that break is the proof the extraction landed.
- Stray placeholder lines (`console = click.Utils`) or unused imports left during a split fail lint — clean before committing.
- A file UNDER the line cap can still violate the rule if it embeds a second near-parallel pipeline. Example: `commands.py` at 358 lines had `forward_run` containing BOTH native-forward and a COPY-mode download→upload→delete loop (~67 lines of duplicate pipeline). The user flagged it with "why is commands 358? can it be modularized". Fix: extract the branch to its own module (`copy_mode.py`) with a clean return tuple `(count, max_id, run_forwarded)` so the orchestrator keeps its resume state. Size alone is not the pass criterion — one concern per file is.
- Split as its own git commit so it's revertable independently of any logic change.

## Verify after splitting
Run the suite. For network code you can't hit live, verify with a stubbed async client — see references/stubbed-async-client-testing.md.

## Quick checklist
- [ ] Every module ≤ ~224 lines (most <120)?
- [ ] One concern per file (no embedded second pipeline)?
- [ ] CLI layer is thin (options → call body, no logic)?
- [ ] One test file per source module (no `test_offline.py` god file)?
- [ ] Real imports hoisted (no `__import__` hacks)?
- [ ] Suite green after the split?
