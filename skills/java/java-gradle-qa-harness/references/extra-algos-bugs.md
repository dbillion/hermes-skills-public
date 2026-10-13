# Extra-algorithms build: concrete bug fixes (dsa-extra-algos, 9 tests green)

Project covers algorithms missed in the main DSA study guide: Fenwick tree, AVL tree,
B-Tree, suffix array, Mobius function, Strongly Connected Components (Kosaraju),
articulation points (Tarjan), convex hull (Andrew monotone chain), point-in-polygon,
B-Tree search.

## Bug 1 — Mobius function misses the trailing prime factor
Wrong:
```java
for (int p = 2; p * p <= n; p++) { if (n % p == 0) { cnt++; n /= p; if (n % p == 0) { return 0; } } }
return (cnt % 2 == 0) ? 1 : -1;   // mu(2)=+1  WRONG, should be -1
```
Fix: after the loop, if `n > 1` it is a prime factor.
```java
if (n > 1) cnt++;
return (cnt % 2 == 0) ? 1 : -1;
```
mu(2)=-1, mu(6)=+1, mu(30)=-1, mu(4)=0.

## Bug 2 — Kosaraju SCC adds in pre-order (wrong component count)
Wrong: `visited[u]=true; out.add(u); for (v...) dfs(...);` → finishing order is wrong,
gives 1 component instead of 2 for {0,1,2} cycle + {3,4} cycle.
Fix: add AFTER recursing (post-order):
```java
visited[u] = true;
for (int v : adj.get(u)) if (!visited[v]) dfs(adj, v, visited, out);
out.add(u);
```

## Bug 3 — Java 17 has no SequencedCollection.reversed()
Wrong: `var upper = hullHalf(p.reversed());` → "cannot find symbol" on Java 17.
Fix:
```java
List<Point> upper = new ArrayList<>(p);
Collections.reverse(upper);
upper = hullHalf(upper);
```

## Bug 4 — suffix array reassigns a var captured by lambda
Wrong: `var rank = ...; sa.sort((a,b) -> rank.get(a) ...); rank = nrank;` →
"local variables referenced from a lambda must be final or effectively final".
Fix: hold in a final array box:
```java
final List<Integer>[] rankBox = new List[]{ initial };
... final List<Integer> rank = rankBox[0]; ... ; rankBox[0] = nrank;
```

## Bug 5 — primitive int can't call .equals
Wrong: `if (i < c.keys.size() && k.equals(c.keys.get(i))) return true;`
Fix: `if (i < c.keys.size() && k == c.keys.get(i)) return true;`

## Bug 6 — Fenwick range expectation was a test bug
`range(2,3)` of values [3@1, 2@2, 5@3] = 2+5 = 7, not 5. Verify with Debug, don't
assume the tree is wrong.

## Debug pattern (reuse from every algo project)
```java
package extra;
public class Debug {
  public static void main(String[] a) {
    var ft = new AlgorithmsExtra.Fenwick(5);
    ft.add(1,3); ft.add(2,2); ft.add(3,5);
    System.out.println("sum(3)=" + ft.sum(3) + " range(2,3)=" + ft.range(2,3));
  }
}
```
`java -cp build/classes/java/main extra.Debug` — print ACTUAL before editing the algo.
Delete Debug.java before committing.
