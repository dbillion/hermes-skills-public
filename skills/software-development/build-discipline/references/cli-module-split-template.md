# CLI / module split template (Click / Telethon / any command-driven module)

Worked pattern from the `tgforwarder` refactor (branch `fix/channel-peer-dedup`).
Three progressive splits, all behavior-preserving. Use whenever a command module
or its test file grows past ~200 lines.

## Split 1 — `cli.py` 694 → 116 lines

The monolith held Click decorators AND pure forwarding primitives AND async
command bodies. Extract by concern:

- `<pkg>/peer.py` (pure primitives, NO Click, NO network to import): `WorkItem`
  dataclass, `retry`/`timer` helpers, `iter_undone`, `iter_source_ids_recency`/
  `_full`, `content_hash_of`, `_is_from_source`, `verify_ids_exist`,
  `_forward_messages`, `_forward_batch`.
- `<pkg>/commands.py` (async `*_run` bodies only — no `@click.option`): `forward_run`,
  `score_run`, `test_ocr_run`, `interactive_menu`.
- `<pkg>/cli.py` (thin layer ~100-150 lines): each `@cli.command()` declares options
  and calls the matching `*_run` via `asyncio.run(...)`.

Late-import sibling deps inside functions to avoid circular imports
(e.g. `from .forward import original_filename` inside the function body).

**Gotcha after any move:** tests importing a moved symbol break — fix them.
`_is_from_source` moved `cli -> peer`, so
`from tgforwarder.cli import _is_from_source` → `from tgforwarder.peer import _is_from_source`.
That breakage is the proof the extraction landed.

## Split 2 — `commands.py` 358 → 224 (a hidden god FUNCTION)

`forward_run` was a 200-line function embedding TWO pipelines: native forward plus
a ~67-line COPY-mode (download→upload→delete) loop. Extract the copy loop into its
own module with a clean RETURN tuple so the orchestrator keeps its state:

- `copy_mode.py`: `run_copy_mode(client, src, tgts, *, order, rebuild_cache, offset_id,
  batch_size, delay, limit, process_all, done_by_target, cache, logger, count, max_id,
  run_forwarded) -> (count, max_id, run_forwarded)`.
- `login.py`: `login_run` (auth + 2FA / invalid-creds handling).
- `dedupe.py`: `dedupe_run` (scan + chunked delete).
- `commands.py` (~224): orchestrator; delegates COPY work to `copy_mode`, else keeps
  `score_run`/`test_ocr_run`/`interactive_menu`.

The `(count, max_id, run_forwarded)` tuple lets the orchestrator persist resume
state unchanged — no behavior shift. Lesson: when a function has a near-parallel
second pipeline, that's a hidden god function; extract it.

## Split 3 — `test_offline.py` 353 → 7 focused test files

A god test file covering 6 unrelated modules is rejected the same as a god source
file. **Mirror the source layout, one `test_<module>.py` per source module, then
delete the god file:**

`test_forward.py` (3), `test_score.py` (4), `test_cache.py` (7), `test_state.py`
(1), `test_report.py` (3), `test_peer.py` (1), `test_client.py` (2). Plus new
`test_copy_mode.py` (4) for the extracted pipeline. Total: 24 passing (20 migrated
+ 4 new). Keep each test file small and focused; relocate shared fixtures into the
matching module (tiny `tests/conftest.py` only if truly cross-cutting).

## Async unit tests WITHOUT adding pytest-asyncio

If the repo has no `pytest-asyncio` dependency, do NOT introduce one just to test
coroutines. Write a plain sync function and drive the coroutine with `asyncio.run`:

```python
import asyncio
from types import SimpleNamespace
from tgforwarder.cache import ForwardCache
from tgforwarder.copy_mode import run_copy_mode
from tgforwarder.report import ForwardLogger

class _StubClient:
    def iter_messages(self, src, *, min_id=0, reverse=False):
        async def gen():
            for m in self._messages:
                if m.id >= min_id:
                    yield m
        return gen()
    async def send_message(self, target, *, message, file=None):
        self.send_id += 1
        self.sent.append((target.id, message, file))
        return SimpleNamespace(id=self.send_id)

def test_copy_mode_dedups_by_content_hash_within_target(tmp_path):
    src = SimpleNamespace(id=-1001961116802, title="src")
    t1 = SimpleNamespace(id=11, title="tgt11")
    msgs = [_StubMsg(1, "dup"), _StubMsg(2, "dup")]
    client = _StubClient(msgs)
    _, _, run_forwarded = asyncio.run(run_copy_mode(
        client, src, [t1], order="oldest", rebuild_cache=False, offset_id=0,
        batch_size=25, delay=0, limit=50, process_all=False,
        done_by_target={t1.id: set()}, cache=ForwardCache(tmp_path / "c.db"),
        logger=ForwardLogger(), count=0, max_id=0, run_forwarded=0))
    assert run_forwarded == 1
```

Stub gotcha: `original_filename()` reads `message.media.document.attributes[0].file_name`,
so stub media must carry `document = SimpleNamespace(size=…, attributes=[SimpleNamespace(file_name=…)])`,
not just `size`.

## Guardrail (the actual lesson)

The monolith crept up over several small edits, each under the LOC radar. Rule:
**after every edit that adds lines to a module, check its LOC. If it exceeds
~200, split before the next edit.** Don't wait for the user to flag it — a
694-line `cli.py` and a 358-line `commands.py` and a 353-line `test_offline.py`
were each a failure of this rule, not one-time slips.

## Verification checklist after any such split

- `python -c "import <pkg>.<all new modules>"` succeeds.
- CLI `--help` lists every command (no command lost in the move).
- `wc -l <pkg>/*.py` — every file ≤ ~224; none a monolith.
- `wc -l tests/*.py` — no god test file.
- Test runner green (for tgforwarder: `.venv/bin/python -m pytest -q` — NOT bare
  `pytest`, which collects nothing in this repo).
