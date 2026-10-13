# Telethon counting + ground-truth delivery verification (reference)

## Instant source total (no scan)
```python
_zero = await client.get_messages(src, limit=0)
src_total = getattr(_zero, "total", None) or getattr(src, "message_count", None)
```

## Ground-truth delivered set (scan TARGET, not source)
```python
from telethon.tl.types import PeerUser
delivered = set()
async for m in client.iter_messages(target, limit=30000):
    fwd = getattr(m, "fwd_from", None)
    if fwd and getattr(fwd, "saved_from_peer", None) == PeerUser(src.id):
        sf = getattr(fwd, "saved_from_msg_id", None)
        if sf:
            delivered.add(sf)
# delivered == ids that ACTUALLY arrived in target
```

## Cache rebuild API (overwrite done-set with truth)
```python
# in cache.py
def rebuild_done_set(self, source_id, target_id, delivered_ids: set[int]) -> int:
    cur = self.conn.execute(
        "DELETE FROM forwarded WHERE source_id=? AND target_id=?",
        (source_id, target_id),
    )
    deleted = cur.rowcount
    if delivered_ids:
        ts = datetime.now(timezone.utc).isoformat()
        self.conn.executemany(
            "INSERT INTO forwarded (source_id, source_msg_id, target_id, "
            "target_msg_id, file_name, timestamp, status) VALUES (?,?,?,?,?,?,?)",
            [(source_id, mid, target_id, None, None, ts, "ok") for mid in delivered_ids],
        )
    self.conn.commit()
    return deleted
```

## Regression test (proves inflated cache is replaced by truth)
```python
def test_cache_rebuild_done_set_replaces_inflated_cache(tmp_path):
    db = tmp_path / "fwd.db"
    c = ForwardCache(db)
    c.mark_many([{"source_id": 10, "source_msg_id": i, "target_id": 20}
                 for i in range(1, 101)])      # inflated: 100 marked, 3 real
    assert c.stats()["forwarded"] == 100
    removed = c.rebuild_done_set(10, 20, {5, 6, 7})  # ground truth
    assert removed == 100
    assert c.stats()["forwarded"] == 3
    assert c.load_done_set(10, 20) == {5, 6, 7}
    assert not c.is_done(10, 1, 20)   # false positive gone
    assert c.is_done(10, 5, 20)       # truth kept
    c.close()
```

## Why this matters (the failure that spawned this skill)
A forwarder marked `done` the moment `forward_messages()` returned truthy. With a
deleted-account source peer, many returns were hollow, so the SQLite cache claimed
8,255 delivered while only 2,910 actually landed in Saved Messages. Every resume then
skipped the 5,345 missing messages and printed "Done". The fix: rebuild cache from the
target's `fwd_from` before forwarding, and print `VERIFIED in target: N / source total: T`
at the end — never trust the cache count as proof.
