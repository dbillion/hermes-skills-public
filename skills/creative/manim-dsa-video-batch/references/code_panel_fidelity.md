# Code-panel fidelity — the quicksort trap

## Symptom the user reported (two rounds)
Round 1: "the picture functions just placed quicksort as quicksort, it didnt
show the implementation." The scene's `CODE` block held only the 1-line public
wrapper, and the animation ran a simplified pivot-last partition that did NOT
match the repo's real `partition()`.

Round 2 (after the first fix): the user noticed the FINAL on-screen arrangement
didn't match the caption. The fix had shown real code but animated only ONE
partition on `[5,2,8,1,9]` with pivot=9 (already largest) → cubes never moved,
ended at `[5,2,8,1,9]`, while the payoff text said `[1,2,5,8,9]`. User: "i
thought the final solution will be the arrangement... the animation differs."

Both are fidelity defects. The rule: **the code panel must show the real
implementation, AND the animation must run to completion so the visible
elements end in the state the caption claims.**

## Real source (Algorithms.java, verbatim — what the panel MUST show)
```java
public static void quickSort(int[] a) { quickSort(a, 0, a.length - 1); }
private static void quickSort(int[] a, int lo, int hi) {
    if (lo >= hi) return;
    int p = partition(a, lo, hi);
    quickSort(a, lo, p - 1);
    quickSort(a, p + 1, hi);
}
private static int partition(int[] a, int lo, int hi) {
    int pivot = a[hi];
    int i = lo;
    for (int j = lo; j < hi; j++)
        if (a[j] <= pivot) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; }
    int t = a[i]; a[i] = a[hi]; a[hi] = t;
    return i;
}
```

## Fix applied (a3_quick_sort.py) — full recursion
1. `CODE` = the 3-method block above (verbatim).
2. Animation runs the FULL recursive sort, tracking cube positions by an `order`
   array so swaps are animated and the cubes END sorted:
   - `recurse(lo, hi)`: highlight pivot (a[hi]), i = lo, j scans, swap a[i]/a[j]
     via an `order` permutation, final swap i<->hi locks pivot (GOOD), then
     recurse left `recurse(lo, p-1)` and right `recurse(p+1, hi)`.
   - Because `order` mirrors the real algorithm's swaps, after `recurse(0,4)` the
     cubes read `[1,2,5,8,9]` left-to-right — matching the caption.
   - Tracing check: final `val_at(pos) = arr[order[pos]]` must equal the claimed
     sorted output. Write this as an assertion in a scratch run if unsure.
3. Guard self-swaps (`if i != j`) and the final `i != hi` swap so the animation
   doesn't replay no-op moves.
4. Re-render that one file and `cp -f` over the stale final_videos mp4 (the
   batch skip-logic won't overwrite an existing >1KB file).

## Audit recipe (run BEFORE the full batch)
`python3 scripts/audit_stubs.py <scenes_dir>` — reports any scene whose `CODE`
block is <=2 lines or a single wrapper.
ALSO check the end-state-vs-caption match:
- Grep scenes whose payoff/result `Text(...)` states a final arrangement
  (sorted list, found index, DP value).
- Confirm the animation logic reaches that state (full recursion / full DP fill,
  not a partial step). The quicksort Round-2 bug slipped past audit_stubs.py
  because the CODE block was correct — only the animation depth was wrong.
- Manually grep for scenes whose animation references a helper (`partition`/
  `merge`/`dfs`) that is ABSENT from the code panel — that's the silent-
  divergence smell.

## Why subagents do this
They interpret "use real source" as "paste the public method signature" and then
invent a simpler walkthrough because the real helper is long; or they animate
only the first step and assume the viewer infers the rest. The fix is in the
brief: demand the FULL method body + helper bodies, require the animation to
step through the real helper on the real test sample, AND state that the visible
final state must equal the captioned result.
