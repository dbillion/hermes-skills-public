# Static Methods vs Interfaces — The Bloch Correction

## The claim that triggered this audit
An expert reviewer told the user: *"A static method isn't the best
implementation. A functional interface is better. Interfaces are preferred to
static methods."* — while reviewing `dsa-java-gradleqa` (`Algorithms.java`, a
`final` class of `public static` methods + `private Algorithms() {}`).

## Why the claim is wrong (in general)
- **Bloch Item 4** literally *recommends* the private-constructor + static-method
  utility class for stateless operations. The repo was already compliant.
- **Bloch Item 20** ("prefer interfaces to abstract classes") is about *type
  hierarchies with multiple polymorphic implementations*, not about eliminating
  static methods. Confusing "interface vs abstract class" with "interface vs
  static method" is the core error.
- **Bloch Item 22**: don't use interfaces as dumping grounds for constants/functions.

## Where the claim is RIGHT (narrow)
**Bloch Item 44** — where a *variation of behavior* exists, pass a standard
functional interface instead of hard-coding it. Three real wins found:

### Win A — Graph as an interface
Before: every graph algorithm took `int[][] edges`, hard-coding an edge-list.
```java
public interface WeightedGraph {
    int vertexCount();
    List<int[]> neighbors(int v); // {toVertex, weight}
}
public static final class EdgeListGraph implements WeightedGraph { /* ... */ }
public static int dijkstra(WeightedGraph g, int src, int dst) { /* stays static */ }
```
Algorithm method stays `static`; the *data* varies polymorphically.

### Win B — Generic Comparator-parameterized sort
Before: `public static void mergeSort(int[] a)` (int-only).
After: `public static <T> T[] mergeSort(T[] a, Comparator<? super T> cmp)`.
Ordering is a functional interface; one impl serves every type.

### Win C — Dijkstra comparator overflow
Before: `new PriorityQueue<int[]>((a,b) -> a[1]-b[1])` — overflows on large weights.
After: `Integer.compare(a[1], b[1])` (Item 42/44).

## Verification done (real, not asserted)
- Prototype `AlgorithmsBlochAppendix.java` compiled with `javac -Xlint:all` on
  OpenJDK 21 and ran; output:
  `twoSum=[0,1]; binarySearch=2; dijkstra(0->2)=6; mergeSort=[1,2,4,5,8]`.
- Original repo `./gradlew test` → BUILD SUCCESSFUL (AlgorithmsTest + SmokeTest
  all PASSED). Conclusion: code was NOT broken; the *review note* over-generalized.

## How to argue back (reusable)
1. Quote the specific Bloch Item the reviewer's claim maps to.
2. Separate "wrong in general / right in specific spots."
3. Keep stateless single-behavior functions static; add interfaces only at real
   variation points.
4. Never report a refactor as "improved" without compiling + running it and
   keeping the existing test suite green.
