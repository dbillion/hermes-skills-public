# Additive code augmentation: adding variants without touching tested code

Scope: the user asks for a SECOND version of existing functions — "modern
rewrite", "Java 25 version", "stream version", "optimised alternative" — to sit
alongside the originals in a published doc.

For building the 83 packs themselves see
`references/per_algorithm_markdown_packs.md` (parser pitfalls, PNG_FIX map,
validation gate). This file is only about ADDING variants safely.

Repo scripts: `scripts/inject_rewrites.py` (injector), idempotent — it skips any
block already carrying the rewrite heading.

## The user's explicit rule: additive, never in-place
Verbatim correction: *"you are not altering the present function, you are just
writing another one below it."*

The tested original stays byte-identical; the variant goes in a NEW fenced block
directly beneath it. Prove it mechanically before reporting success — do not
eyeball a diff:

```python
import difflib
removed = [l for l in difflib.ndiff(before.splitlines(), after.splitlines())
           if l.startswith('-')]
assert not removed                     # purely additive, 0 lines lost
assert after.count("```") % 2 == 0     # fence parity intact
```
Write a `README.md.bak_rewrites` backup before the write.

Insertion point = end of the LAST ``` fence inside the `**Function ...**`
section; fall back to just before `**Unit test**` when that section has no fence.

## Verify variants by execution; never assert equivalence
Do NOT hand-wave "this stream version is equivalent" — that is fabricated
verification. Put variants in a SEPARATE source file so the tested class is
never edited, then randomised-diff every variant against its original:

- `src/main/java/dsa/Rewrites.java` — the variants (calls into the original
  class for shared types: `Algorithms.SubarrayResult`, `Algorithms.UnionFind`).
- `src/main/java/dsa/RewriteVerify.java` — a `main` looping seeded random inputs,
  comparing original vs variant, printing `PASS=<n> FAIL=<n>` and exiting 1 on
  failure.

```bash
javac -d /tmp/rwout src/main/java/dsa/{Algorithms,Rewrites,RewriteVerify}.java
java -cp /tmp/rwout dsa.RewriteVerify     # -> PASS=4780 FAIL=0
```
Gotchas that make a green run meaningless: deep-copy `int[][]` inputs between the
two calls (`Arrays.stream(a).map(int[]::clone)`) since several algorithms sort in
place; compare thrown exceptions too (`twoSum` throws when no solution exists);
for "missing number" build a true `0..n` permutation minus one element, or the
XOR identity doesn't hold.

Then confirm the real suite still passes. `./gradlew test -q` prints NOTHING on
success, so don't read silence as proof — count from the XML:

```bash
./gradlew clean test --offline
python3 -c "
import glob,re
tot=f=0
for p in glob.glob('build/test-results/test/*.xml'):
    m=re.search(r'tests=\"(\d+)\".*?failures=\"(\d+)\".*?errors=\"(\d+)\"',open(p).read())
    if m: tot+=int(m.group(1)); f+=int(m.group(2))+int(m.group(3))
print('TESTS',tot,'FAILURES',f)"     # -> TESTS 97 FAILURES 0
```

## Push back: "streams are faster" is false
The user requested rewrites *"since stream is faster"*. In Java that premise is
wrong — for primitive `int[]` work streams are typically SLOWER (boxing, lambda
dispatch, no bounds-check elision). They win on clarity, immutability and
parallelism. Say this plainly rather than shipping slower code under a
performance claim the comments will correct.

Grade each candidate instead of converting all of them:
- **Genuine wins**: pure reductions (XOR `missingNumber`); rolling-`record` DP
  dropping an O(n) memo to O(1) (`fib`); `new PriorityQueue<>(coll)` (O(n)
  heapify vs repeated offer); non-mutating sort (`kruskal` — the original
  `Arrays.sort` mutates the CALLER's array); arrow `switch` replacing an
  if/else-if chain plus its helper (`isValidParentheses`).
- **Label regressions in-place**: `mergeTwoSorted` as `concat().sorted()` is
  O((n+m) log(n+m)) and throws away the sorted precondition. Ship it only with an
  explicit "keep the original" note, or not at all.
- **Refuse where the contract forbids it**: in-place mutation returning a length
  (`removeDuplicates`) cannot be a stream without allocating.
- **Leave alone** (~68 of 83): recursive tree/graph traversals, in-place sorts,
  two-pointer scans, DP grids. A stream bubble sort is worse code, not modern.

Give each emitted block a one-line verdict above the fence so the reader knows
whether it's an improvement, a trade-off, or a deliberate counter-example.

## Check the real JDK before writing "Java 25"
The README advertises Java 25 LTS; the machine runs JDK 21 (`java -version`).
Write 21-safe syntax and flag the mismatch rather than emitting code that won't
compile locally. Java 21 already covers records, `var`, arrow/pattern `switch`,
`.toList()` — which is everything these rewrites need.
