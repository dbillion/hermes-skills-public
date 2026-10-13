# Voyage embed throttle playbook (`gbrain embed --stale`)

Observed on a 152-page / ~305-chunk brain, embedding model `voyage:voyage-4`:

- Full default run: 132 chunks embedded, then 172 failed with
  `[embed(voyage:voyage-4)] Too Many Requests` (HTTP 429, per-burst limit).
- Retry after ~3 min cooldown: +38 chunks, 134 still 429.
- Retry after ~5 min cooldown with `--batch-size 5`: sustained writes, no stall
  (wchar climbing ~1MB/3min). Smaller batches stay under the burst limit.

Recipe:

1. Probe: `time gbrain embed <one-small-slug>` — confirms key/network work (~20s).
2. `gbrain embed --stale` in background. On 429-heavy failure, wait, rerun — reruns
   only touch stale chunks, so each pass is cheaper than the last.
3. If 429s persist, drop to `gbrain embed --stale --batch-size 5` with a 3–5 min
   cooldown (`sleep 300` prefix in the background command).
4. Keyword search (`gbrain search`, tsvector) works WITHOUT embeddings — the brain is
   usable after step 1 of the import split even while vectors catch up. Hybrid
   `query` needs vectors + expansion model.
5. Watch the bun WORKER's `/proc/<pid>/io` wchar (see SKILL.md), not the wrapper.
