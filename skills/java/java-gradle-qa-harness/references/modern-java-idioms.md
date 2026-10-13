# Modern Java idioms (from javaevolved.github.io) — Java 17 build constraint

The user pointed at https://javaevolved.github.io/ for "modern ideas". The site's
homepage lists idioms to prefer. Most are available on Java 17; a few need Java 21.

## Safe on Java 17 (use freely)
- `record` value types — immutable, generated accessors (`r.x()`), `equals/hashCode/toString`.
- `sealed` interface/class + `permits` — closed subtype set, enables exhaustive `switch`.
- Pattern-matching `switch` (on sealed types / enums / `Integer` etc.):
  `return switch (kind) { case "a" -> new A(); default -> throw new IllegalArgumentException(kind); };`
- Enhanced `instanceof` pattern: `if (x instanceof String s) { use s; }`
- `var` local inference (NOT in compound declarations, NOT for lambda params on Java 17).
- `Stream.toList()` (immutable) instead of `collect(Collectors.toList())`.
- `Collectors.toCollection(ArrayDeque::new)` — explicit collection type.
- `Optional` chaining (`map`/`flatMap`/`filter`/`orElse`), `OptionalInt` for primitives.
- `List.copyOf` / `Map.copyOf` / `Set.copyOf` — immutable snapshots.
- Functional interfaces as args: `Comparator.naturalOrder()`, `Consumer<String>`, `Function`.
- `String` APIs: `strip()`, `isBlank()`, `repeat(n)`, `lines()`, `transform(f)`.

## Requires Java 21 (DO NOT use on the configured Java 17)
- `SequencedCollection.reversed()` — on 17 use `Collections.reverse(new ArrayList<>(list))`.
- `Stream.mapMulti((e, sink) -> ...)` — on 17 use `flatMap` or explicit loops.
- `switch` with unnamed pattern `_` (Java 21 preview) — on 17 keep `default`.
- `Math.clamp` — on 17 use `Math.max(lo, Math.min(hi, v))`.
- Virtual threads (`Thread.ofVirtual()`) — on 17 use `ExecutorService` + platform threads.

## Why this matters
The build runs on Java 17.0.12-graal via sdkman. Gradle 8.2.1 will NOT run on system
Java 21/24. A `p.reversed()` call compiles on a Java 21 JDK but fails on the Java 17
toolchain with "cannot find symbol". Always write for Java 17 unless the user upgrades
the sdkman candidate and the Gradle version together.

## Applying idioms in a study-guide / algorithm project
- Return complex results as `record` (e.g. `record Subarray(int sum, int[] arr){}`).
- Model a problem's variants as a `sealed` hierarchy + pattern-matching `switch` for
  dispatch (replaces brittle `instanceof` chains and the Visitor boilerplate).
- Prefer `List.copyOf` for immutability in Builder/flyweight returns.
- Use `IntStream.range(0,n).boxed().collect(...)` to build index lists (suffix array).
- `ConcurrentHashMap.computeIfAbsend` for flyweight caches.
