---
name: java-bloch-audit
description: "Audit Java vs Effective Java and verify refactors compile."
version: 1
author: hermes
license: MIT
metadata:
  tags: [java, effective-java, code-review, bloch, audit]
  related_skills: [java-springboot-projects, java-21-springboot-projects]
---

# Java Bloch Audit

## When to Use
- Reviewing Java code for Effective-Java compliance.
- Responding to an "expert" review note claiming static methods are bad / interfaces preferred.
- Auditing a repo (e.g. a DSA/Gradle Java project) before a rewrite.
- Triggers: "audit this Java", "is this static method bad", "Bloch says prefer
  interface", "review the DSA repo", "is this class design wrong".

Use when reviewing Java code, responding to an "expert" Java review note, or
auditing a repo for Effective-Java compliance. Triggers: "audit this Java",
"is this static method bad", "Bloch says prefer interface", "review the DSA
repo", "is this class design wrong".

## The #1 misdiagnosis to catch

A reviewer says: *"A static method isn't the best implementation. A functional
interface is better. Interfaces are preferred to static methods."*

**This is a misreading of Bloch.** Do NOT blindly apply it. Map the claim to
the actual Items before changing code:

| Bloch Item | What it actually says | Implication |
|---|---|---|
| **Item 4** — Enforce noninstantiability with a private constructor | A class that is *only* stateless functions should have a `private` constructor (or be `final`). | **Endorses** the `final class X { private X(){} ... static methods ... }` utility pattern. Not a smell. |
| **Item 20** — Prefer interfaces to abstract classes | When you have a *family of polymorphic implementations* of a **type**, use an interface (+ skeletal impl) so existing classes can adopt it. | Governs **type hierarchies**, NOT "ban static methods". A `twoSum` with one correct behavior gains nothing from an interface. |
| **Item 22** — Use interfaces only to define types | Don't use interfaces for constants / dumping grounds. | Reinforces: don't manufacture phantom interfaces for pure functions. |
| **Item 44** — Favor standard functional interfaces | Where a **variation of behavior** exists (ordering, comparison, a strategy), pass `Comparator` / `Predicate` / `Function` instead of hard-coding it. | **The one real win.** Apply only where a strategy truly varies. |

**Rule of thumb:** Stateless, single-behavior functions STAY `static` (Item 4).
Introduce an interface/functional interface ONLY where a *variation* exists
(graph representation, sort order, a pluggable algorithm).

## Real, verified wins (from a dsa-java-gradleqa audit)

1. **Graph as interface, not `int[][] edges`.** `dijkstra`/`bfs`/`dfs`/`topoSort`/
   `kruskal`/`prim`/etc. all take a raw edge list. A `WeightedGraph` interface
   lets any representation plug in; the *algorithm method stays static* (the
   algorithm is fixed, the data varies). → Items 20/44.
2. **Generic `Comparator`-parameterized sort.** `mergeSort(int[])` →
   `<T> T[] mergeSort(T[], Comparator<? super T>)`. One impl serves every type. → Item 44.
3. **Dijkstra comparator overflow.** `new PriorityQueue<int[]>((a,b)->a[1]-b[1])`
   overflows on large weights. Use `Integer.compare(a[1], b[1])`. → Items 42/44.

See [references/bloch_static_vs_interface.md](references/bloch_static_vs_interface.md)
for the full audit write-up and the verified refactor source pattern.

## Methodology (verify, don't assert)

- **Argue back rigorously.** Before refactoring, cite the specific Bloch Item.
  The reviewer may be wrong in general but right in specific spots — separate the two.
- **Compile + run before claiming improvement.** Prototype the refactor in a
  standalone `.java`, `javac` it, run `main()` with sanity assertions.
- **Don't break existing tests.** Run the project's suite (`gradlew test` /
  `mvn test` / `./mvnw test`) and confirm BUILD SUCCESSFUL before reporting.
- **Distinguish "code is wrong" from "review note over-generalized".** If the
  repo's tests already pass, the audit is about the *note*, not the code — say so.

## Pitfalls

- Assuming a tool/integration is "not wired" without checking. Before reporting
  an MCP/server/pipeline as unavailable, actually invoke it (e.g. `mcp-cli call
  <server> <tool>`). A skill-*name* collision can block loading and look like
  "not installed" — resolve the collision instead of assuming absence.
- Turning a Bloch audit into a rewrite. Keep stateless functions static; add
  interfaces only at the genuine variation points.
