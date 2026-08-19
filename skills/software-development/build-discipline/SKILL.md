---
name: build-discipline
description: "User build rule: plan tasks, tests required, modular files."
version: 1.0.0
author: Hermes Agent (captured from user correction)
license: MIT
platforms: [linux, macos, windows]
tags: [coding-standards, testing, planning, modular, workflow, process]
related_skills: [writing-plans, test-driven-development, ponytail, code-refactoring, verification-loop]
---

# Build Discipline (dbillion — explicit, non-negotiable mandate)

Captured from a direct user correction. These rules apply to EVERY software build,
refactor, or coding task for this user. They are process-level, not language-specific.

## The Four Rules

1. **Plan, then tasks, then TICK.**
   - Write a plan. Convert it into a task list (use the `todo` tool or a written
     checklist). Mark each task `completed` the moment its work is done and verified
     — not in bulk at the end. An un-ticked task list where you did the work anyway
     is a miss; tick as you go.

2. **Unit tests are MANDATORY. No tests = FAILURE.**
   - "If you can't test what you just built, you have failed — do not claim success."
   - Plan the test for each task up front. Prefer offline / pure-logic tests; mock
     network, Telegram, filesystem where needed. Run the language's test runner
     (`pytest`, `cargo test`, `gradle test`) and confirm GREEN before reporting done.
   - A build that cannot be exercised by a test is, by this user's rule, a failed build.

3. **Break large files into modules. NEVER leave a 400-line monolithic file that
   could be modular.**
   - This user detests long unmodularized files. Split by responsibility
     (e.g. client / cache / forward / score / cli). Each unit importable and testable.
   - Before writing a file, ask: "could this be 3 smaller files?" — if yes, do it.
   - The refactor IS the build; don't write an 800-line script and "refactor later."

4. **For refactoring / code-structure work, load the `ponytail` and/or
   `code-refactoring` skills.** Write plans and rules out EXPLICITLY — never imply them.

## Workflow (concrete)

1. Write the plan (see `writing-plans` for bite-sized structure).
2. Create the task list mirroring the plan.
3. Implement + write the unit test for each task.
4. Run the test runner; confirm green. Show the pass output.
5. Tick the task `completed`.
6. Repeat until all tasks done. Only then report success.

## Pitfalls (this user's triggers — avoid)

- **Monolithic file** — rejected. Modularize as you build.
- **"It works" without a green test run** — never claim done unless the runner
  actually passed in this session. Paste/summarize the pass output.
- **Un-ticked tasks** — a plan with N items where you did some and said "done" is a miss.
- **Implied rules** — state the plan and the testing approach plainly.

### The "creeping monolith" trap (learned the hard way)
A monolith rarely appears in one edit — it creeps. Across several small
`add this function` / `add this command` edits, a module that started at 200
lines quietly grew to 600+ before anyone noticed. The user's actual words when
it surfaced: *"why are you creating a god file of over 500 lines? cant you
modularize and import them using some of the template in python tricks."*

**Active guardrail — check LOC after every edit that adds lines to a module:**
- If a source file exceeds ~200 lines, STOP and split BEFORE the next edit.
- Do not wait for the user to flag it. A 694-line `cli.py` is a failure of this
  rule, not a one-time slip.
- The codebase's own layout is the template (the user pointed at it as "the
  template in python tricks"): one concern per module — `client.py`, `cache.py`,
  `forward.py`, `score.py`, `state.py`, `report.py`. Follow that, don't invent a
  new structure.

### Test files are god files too
The rule applies to the `tests/` tree, not just source. A 353-line
`test_offline.py` covering 6 unrelated modules is a god test file and was
rejected the same way. **Mirror the source layout**: one `tests/test_<module>.py`
per source module (`test_cache.py`, `test_score.py`, `test_forward.py`,
`test_peer.py`, `test_client.py`, `test_state.py`, `test_report.py`, …). Keep
each test file focused and small; relocate shared fixtures/helpers into the
matching test module (or a tiny `tests/conftest.py` if truly cross-cutting).
Delete the god file once split.

### Click / Telegram CLI modularization template (reusable split)
When a CLI module (e.g. a Click `cli.py` driving Telegram/Telethon) balloons:
- `<pkg>/peer.py` (pure primitives): dataclasses, retry/timer helpers, lazy
  `iter_*` generators, content-hash + peer-matching helpers, batched-op
  functions. Importable + unit-testable with NO network/Telegram.
- `<pkg>/commands.py` (async command bodies): the `forward_run`, `dedupe_run`,
  `login_run`, `score_run`, `test_ocr_run`, `interactive_menu` implementations.
  No `@click.option` decorators here.
- `<pkg>/cli.py` (thin layer, ~100-150 lines): `@click.command()` decorators with
  options, each calling the matching `*_run` body via `asyncio.run(...)`.
Behavior is preserved; only the import graph changes. After splitting, update
any test imports that referenced symbols moved out of `cli` (e.g.
`tgforwarder.cli._is_from_source` → `tgforwarder.peer._is_from_source`).

### Near-parallel pipeline branch → its own module
A function is a hidden god function when it embeds TWO similar pipelines. In
`forward_run`, the COPY-mode (download→upload→delete) loop was a ~67-line
near-parallel pipeline living inside the native-forward function, inflating the
file to 358 lines. Extract it into `<pkg>/copy_mode.py` as `run_copy_mode(...)`
with a clean RETURN tuple `(count, max_id, run_forwarded)` so the orchestrator
can still persist resume state. Pass all shared collaborators (client, src, tgts,
done_by_target, cache, logger) as args. Then `commands.py` stays a thin
orchestrator (~220 lines) and `copy_mode.py` is independently unit-testable.

### Async unit tests WITHOUT adding pytest-asyncio
If the repo has no `pytest-asyncio` dependency, do NOT introduce one just to
test coroutines. Write the test as a plain sync function and drive the coroutine
with `asyncio.run(...)`:
```python
import asyncio
def test_copy_mode_dedups_by_content_hash_within_target(tmp_path):
    client = _StubClient(msgs)
    _, _, run_forwarded = asyncio.run(run_copy_mode(client, ...))
    assert run_forwarded == 1
```
This keeps the suite dependency-free while giving the async module real
coverage. Stub the async client with a class whose `iter_messages` returns a
real `async def gen()` and whose `send_message`/`download_media` are `async def`.
See `references/cli-module-split-template.md` for the full worked example.

## Verification

- Test runner exit code 0 with passing tests = proof of done.
- `todo` list shows all items `completed` = proof of tracking.
- File sizes reasonable (no single source file sprawling past ~200 lines when it
  could be split) = proof of modularity. **Check LOC after every line-adding edit,
  not just at the end — the creeping-monolith trap is the common failure mode.**

## Reference files (session-specific detail)
- `references/cli-module-split-template.md` — worked example of all three splits:
  `cli.py` 694→116 (peer/commands/cli), `commands.py` 358→224 (extract `copy_mode`,
  `login`, `dedupe`), and the `test_offline.py` 353 god-test split into per-module
  test files. Includes the async-without-pytest-asyncio stub pattern and the
  post-split verification checklist.
- `references/telegram-tg-cli-user-session.md` — fix for `tg chats` failing as a bot
  session; point kabi-tg-cli at a real user `.session` + own API creds.
- `references/hatchling-empty-wheel.md` — why `uv build` emits an empty wheel when
  modules sit at project root instead of inside `<pkg>/`, and how to verify/fix.

## Remember

```
Plan -> tasks -> TICK each as completed
Unit tests mandatory (no tests = failure; show green run)
Modular files only (no 400-line monoliths)
Load ponytail / code-refactoring for structure work
Write rules explicitly
```

## Reference files (session-specific detail)
- `references/telegram-tg-cli-user-session.md` — fix for `tg chats` failing as a bot
  session; point kabi-tg-cli at a real user `.session` + own API creds.
- `references/hatchling-empty-wheel.md` — why `uv build` emits an empty wheel when
  modules sit at project root instead of inside `<pkg>/`, and how to verify/fix.
