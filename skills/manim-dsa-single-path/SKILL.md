---
name: manim-dsa-single-path
description: Build narrative-driven Manim explainer videos for a single algorithm or data structure that has no meaningful brute-force-vs-optimized split (sorting, graph traversal/shortest-path, tree operations, single-pass DP, string algorithms, data-structure mechanics, bit tricks). Companion to manim-dsa-storytelling (which is only for algorithms that have two competing approaches) -- use THIS skill instead whenever there is exactly one algorithm to walk through, not two to compare. Shares the same 3D-solid vocabulary and code-duality rules as manim-dsa-storytelling for visual consistency across a mixed batch of videos.
---

# Manim DSA Single-Path Walkthrough

## Relationship to the other two skills

Read `manim-explainer-animations/SKILL.md` first (owns the mobject/animation API surface), then
`manim-dsa-storytelling/SKILL.md` for the full 3D-solid vocabulary table and the code-duality rules
(real source in a `Code` mobject, synced `SurroundingRectangle` highlight, `add_fixed_in_frame_mobjects`
for HUD text) -- this file only overrides the **narrative shape**, since a single-path video has one
walkthrough instead of a brute-vs-optimized comparison. Reuse the solid vocabulary and code-duality
rules verbatim; do not reinvent them here.

## When to use this instead of manim-dsa-storytelling

Use this skill when the target is one of:
- A sort, traversal, or search with one standard approach (bubble/merge/quick/heap sort, BFS, DFS,
  Dijkstra, topological sort, MST algorithms)
- A tree or graph operation (max depth, LCA, diameter, cycle detection, bipartite check)
- A single-pass or single-table DP (fibonacci, climb stairs, knapsack, LCS) where there isn't a
  genuinely worse baseline worth animating
- A data structure's core mechanics (linked list reversal, stack/queue built from arrays, trie,
  segment tree, union-find)
- A bit trick or simple math routine (XOR tricks, sieve of Eratosthenes, GCD, fast exponentiation)

If a genuine brute-force baseline exists AND the complexity gap is real and instructive, use
`manim-dsa-storytelling` instead -- don't force a two-path video into this one-path skill just
because it's less work, and don't force a single-path video into a fake "brute force" frame just
to reuse the comparison skill.

## The narrative shape (4 acts, ~30-50s total)

1. **Cold open -- the structure, spatially.** Build the data structure/space with the solid from
   the vocabulary table (same table as manim-dsa-storytelling) before any code appears.
2. **The walkthrough -- code and motion together.** Bring in the real source in a `Code` mobject
   (real, verbatim) with a synced highlight tracking the active line, while a particle/marker moves
   through the 3D structure performing the algorithm. This is the largest act. For anything beyond
   ~8-10 elements/nodes/steps, subsample or use `ChangeSpeed`/run_time compression.
3. **The key property.** A short beat naming *why* this approach works -- loop invariant, structural
   guarantee, base case. Give it a real breath (Write + wait).
4. **Payoff -- the result, held.** Show the final state clearly (sorted array, shortest path traced
   in the accent color, returned value, built structure). Optionally caption the complexity as a
   fixed-in-frame label.

## Solid vocabulary for structure types not already covered

The comparison skill's table covers arrays (cube row), cyclic structures (torus), sets (sphere
cluster), trees/recursion (cone/pyramid stack), and 2D DP grids (mesh grid). This adds:

| Solid | Use for |
|---|---|
| Dot/Sphere nodes + Line/Arrow edges | Graphs (BFS/DFS/Dijkstra/MST/bipartite/cycle-detection) |
| Cone/pyramid stack, tree layout (root at top) | Binary trees (depth, LCA, diameter, mirror) |
| Cube row, vertical, with a "top" marker | Stacks |
| Cube row bent into ring, head/tail markers | Queues, circular buffers |
| Cube row + floating "current" pointer + growing second row | Linked lists |
| Nested cube grid branching downward | Tries |

For sorting: array cube-row, height = value, animate swaps as real `.animate.move_to(...)` so the
array visibly becomes sorted.

## Workflow

1. Read the real source -- never invent behavior; prefer the repo's own test file for sample input.
2. Pick one solid matching the structure's actual shape -- keep it for the whole video.
3. Storyboard the 4 acts as comments before writing `self.play()` calls.
4. Build the code panel once (no swap -- only one algorithm), same `Code`/`SurroundingRectangle`
   synced-highlight idiom as the comparison skill.
5. Render `-pql` first, check pacing and the "text lying flat on the floor" pitfall, then `-pqh`.

## Common pitfalls

- **Padding a trivial algorithm into a full video.** A one-line bit trick doesn't need 4 full acts --
  compress acts 1+2, spend most runtime on the key-property beat instead.
- **Forcing a fake "brute force" comparison** when there's no instructive worse baseline.
- **Graphs without a stable layout.** Fix node positions once, don't let them jump between acts.
- **Skipping the key-property beat** just because there's no brute-force to contrast against.
