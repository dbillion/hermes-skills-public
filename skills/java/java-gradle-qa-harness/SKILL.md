---
name: java-gradle-qa-harness
description: Scaffold, build, and verify a runnable modern-Java project (algorithm/QA/study-guide style) with Gradle 8.x + JUnit 5, prove it green with ./gradlew test, then commit + push to GitHub. Use when the user wants a Java project they can run tests on, a DSA/algorithm study guide, or "use Gradle to run the task and upload our code so we can test it".
---

# Java Gradle QA Harness

Build a runnable modern-Java project the user can `./gradlew test` themselves. Proven on a 96-test DSA study guide (40 interview Qs + 20 core algos + filled roadmap gaps) pushed to github.com/dbillion/dsa-java-gradleqa.

## When to use
- "create a Java Gradle project we can run the tests on"
- "build me a DSA / algorithm study guide in Java"
- "use Gradle to run the task and upload our algorithm so we can start testing"
- Any ask for a runnable, test-backed Java deliverable (not a Spring Boot web app — use java-springboot-projects for that).

## Workflow (ORDER MATTERS — do not reorder)
1. **Set Java 17 via sdkman** (system Java 21/24 breaks Gradle 8.2). Export every command:
   ```
   export JAVA_HOME="$HOME/.sdkman/candidates/java/17.0.12-graal"
   export PATH="$JAVA_HOME/bin:$PATH"
   ```
2. **Scaffold dirs + Gradle files** (see templates/). Create `settings.gradle`, `build.gradle` (Java plugin, `testImplementation 'org.junit.jupiter:junit-jupiter:5.9.1'`), `gradle/wrapper/gradle-wrapper.properties` pinned to `gradle-8.2.1-bin.zip`.
3. **Generate a VALID wrapper** — `gradle wrapper` from a `gradle` on PATH writes a correct `gradlew` + `gradle-wrapper.jar`. Do NOT hand-write `gradlew` (it tries to `exec` the jar directly and dies with "Exec format error"). After generating, `chmod +x gradlew gradle/wrapper/gradle-wrapper.jar`.
4. **Add a placeholder Main + 1 smoke test, then `./gradlew test`** to prove the harness works.
5. **COMMIT the baseline first** (user's hard rule: "commit before editing so we can revert"). `git add -A && git commit`.
6. **Add the real algorithms + tests.** One `Algorithms.java` (static methods, modern Java) + `AlgorithmsTest.java` (`@Test` per algorithm).
7. **Iterate `./gradlew test` until green.** Fix compile + assertion failures (see Pitfalls). Each red run is signal, not failure.
8. **Commit the green state, then push**: `gh repo create <name> --public` → `git remote add origin ...` → `git push -u origin main`. Verify with `gh repo view` + `git log origin/main`.

## Modern Java to use (user explicitly wants this)
- `record` for return types (e.g. `record Result(int sum, int[] subarray){}`)
- Stream API: `IntStream`, `Collectors.groupingBy`, `Collectors.toCollection(ArrayDeque::new)`
- Generics + wildcards: `List<? extends Number>` (PECS), `List<? super T>` (PECS)
- `Optional` / `OptionalInt` for nullable results
- `var`, enhanced `instanceof` (`if (x instanceof String s)`), `switch` expressions
- `ArrayDeque` instead of `Stack`/`LinkedList` for stacks/queues
- **`sealed` hierarchies + `permits`** for typed dispatch without `instanceof` chains
  (e.g. `sealed interface Shape permits Circle, Rect {}`). Drives the Visitor and
  pattern-matching idioms below.
- **Pattern-matching `switch`** on sealed types / enums: `return switch (kind) { case "a" -> ...; default -> throw ...; }`
- **`List.copyOf` / `Map.copyOf`** for immutable snapshots (safe to return from builders).
- **Functional interfaces** (`Consumer`, `Comparator`) as Strategy / Observer args.
- **javaevolved.github.io idiom set** (the user pointed at this site): records, sealed,
  pattern-matching switch, `var`, `Stream.toList()`, `Collectors.teeing`, `Stream.mapMulti`,
  virtual threads, `String` APIs, `Math.clamp`, `Optional` chaining, `SequencedCollection`,
  immutable collectors. **JAVA 17 CONSTRAINT**: `SequencedCollection.reversed()` and
  `Stream.mapMulti` are Java 21 — NOT available on the configured Java 17. Use
  `Collections.reverse(list)` + `new ArrayList<>(list)` instead. (See references/modern-java-idioms.md)

## Variant: multi-project / mini-project layout
When the user asks for "separate mini-projects that can run separately from the main project":
- One Gradle build (root `settings.gradle` + `build.gradle` with `application` plugin).
- Each mini-project is a **subpackage** with its own `public static void main(String[] args)`
  that prints a result — so it runs independently via `./gradlew run --args='pkg.FooDemo'`.
- Each subpackage ALSO gets its own `*Test.java` (one `@Test` minimum) under `src/test`.
- Verified pattern: 23 GoF design patterns (5 creational / 7 structural / 11 behavioral)
  as `dp.creational.*`, `dp.structural.*`, `dp.behavioral.*` — 23 test files, all green,
  each main runnable alone. See references/design-patterns-mini-project.md.
- For "a SEPARATE project for the remaining parts": make a second standalone repo
  (own `settings.gradle`/`build.gradle`/wrapper), not a subproject of the first. Push both.

## Pitfalls (hit and fixed in the real build)
- **Lambda captures non-final var**: a `Function f = null; f = k -> f.apply(...)` self-recursive lambda fails ("local variables referenced from a lambda must be final"). Fix: iterative fill or a helper method, not a self-referential lambda.
- **`var` in compound declaration is illegal**: `var a = new ArrayList<>(), b = new ArrayList<>()` → "var is not allowed in a compound declaration". Declare separately.
- **Nested method declarations are illegal in Java**: `int h(int r,int c){...}` inside another method → "'；' expected". Extract to a `private static` helper.
- **`assertArrayEquals` needs `int[]`, not `List`**: comparing `List.of(1,2,3)` with `assertArrayEquals` fails. Use `assertEquals(List.of(...), actual)` for lists; `assertArrayEquals(new int[]{...}, actual)` only for primitive arrays.
- **NPE from enqueueing null children in BFS serialize**: `q.add(cur.left)` where left is null is fine, but polling null then `cur.val` NPEs if the null guard is missing. Guard `if (cur == null) continue;` OR only enqueue non-null children.
- **Test-expectation bugs look like algo bugs**: when a test fails, print the ACTUAL value with a throwaway `Debug.java` (`java -cp build/classes/java/main dsa.Debug`) before assuming the algorithm is wrong. In this build, 6 of 7 first-run failures were wrong test expectations, not algo errors.
- **`nlm research` / NotebookLM enrichment is a SEPARATE, flaky step** — see nlm-productivity skill. It is NOT part of the Gradle task. Do not let it block or distract from getting tests green and pushing.

## Pitfalls — extra-algorithms project (Fenwick/AVL/B-Tree/geometry/graph)
- **Möbius trailing prime**: after the `for (p=2; p*p<=n; p++)` loop, if `n>1` it is a
  remaining prime factor — `cnt++` or you get μ(prime)=+1 instead of -1. Always add
  `if (n > 1) cnt++;` after the loop.
- **Kosaraju SCC needs POST-order**: the finishing-time DFS must `out.add(u)` AFTER
  recursing into children (post-order), not before. Adding on entry gives 1 wrong
  component count. Same for any reverse-topo second pass.
- **Java 17 has no `SequencedCollection.reversed()`** (Java 21). Use
  `var upper = new ArrayList<>(pts); Collections.reverse(upper);` then `hullHalf(upper)`.
- **`rankBox` trick for suffix array**: you cannot reassign a `var` captured by a lambda.
  Hold it in `final List<Integer>[] rankBox = new List[]{...}` and reassign `rankBox[0]`.
- **`k.equals(...)` on a primitive `int k`** → "int cannot be dereferenced". Use `k == x`.
- **Fenwick range sum**: `range(l,r) = sum(r) - sum(l-1)`; a wrong expected literal
  (e.g. 5 vs 7) is a test bug, not an algo bug — verify with Debug.

## Pitfalls — design-patterns mini-project layout
- **`application` plugin + many mains**: never set a single `mainClass`. Run each
  mini-project with `./gradlew run --args='dp.creational.singleton.SingletonDemo'`.
- **Raw nested type in tests**: `Coffee c = new DecoratorDemo.WithSugar(...)` fails in the
  test file — qualify as `DecoratorDemo.Coffee c` or import the nested type.
- **Missing test imports**: test files need explicit `import java.util.List;`,
  `import java.util.Comparator;`, `import java.util.function.*;` (Consumer) — `java.util.*`
  is NOT auto-imported in test sources.
- **`Observer` main using `Consumer`**: `import java.util.function.*;` in the MAIN source too.

## Verification
- `./gradlew test --console=plain` → "BUILD SUCCESSFUL", 0 failures, exit 0.
- `git log origin/main -1` shows the push.
- User can clone + `./gradlew test` on their machine.

## Support files
- `templates/build.gradle` — minimal Java + JUnit 5.9.1 build file.
- `templates/settings.gradle` — `rootProject.name`.
- `templates/gradle-wrapper.properties` — pinned 8.2.1.
- `references/debug-loop.md` — the Debug.java + `java -cp` print-actual-value pattern for diagnosing test failures.
- `references/modern-java-idioms.md` — javaevolved.github.io idiom set, with the Java 17 vs 21 constraint calls out.
- `references/design-patterns-mini-project.md` — the 23-pattern runnable-mini-project layout (package map, run command, test-import gotchas).
- `references/extra-algos-bugs.md` — concrete bug fixes from the Fenwick/AVL/suffix/Möbius/SCC/geometry build.
