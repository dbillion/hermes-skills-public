# Effective Java — Quick Reference Cheatsheet
## All 90 Items at a Glance

---

## Chapter 2: Creating and Destroying Objects (Items 1–9)

| Item | Rule | Key Takeaway |
|------|------|-------------|
| 1 | Static factory methods | Use `of()`, `from()`, `valueOf()`, `getInstance()`, `newInstance()` |
| 2 | Builder pattern | Use for >4 constructor parameters; immutable, readable |
| 3 | Enum singleton | `public enum Elvis { INSTANCE; }` — thread-safe, serializable |
| 4 | Non-instantiable | `private Constructor() { throw AssertionError(); }` |
| 5 | Dependency injection | Pass resources via constructor, not hardwiring |
| 6 | Reuse objects | Cache expensive objects; prefer primitives over boxed |
| 7 | Null references | Null out obsolete references in custom data structures |
| 8 | Finalizers | **Never** use finalizers or cleaners; use try-with-resources |
| 9 | Try-with-resources | Always use over try-finally; works with `AutoCloseable` |

---

## Chapter 3: Methods Common to All Objects (Items 10–14)

| Item | Rule | Key Takeaway |
|------|------|-------------|
| 10 | equals contract | Reflexive, symmetric, transitive, consistent, non-null |
| 11 | hashCode | **Always** override with equals; use `31 * result + field` |
| 12 | toString | Always override; include all interesting fields |
| 13 | clone | Prefer copy constructors/factories over `Cloneable` |
| 14 | Comparable | Implement for value classes; use `Comparator.comparingInt` |

---

## Chapter 4: Classes and Interfaces (Items 15–25)

| Item | Rule | Key Takeaway |
|------|------|-------------|
| 15 | Accessibility | Make classes/members as inaccessible as possible |
| 16 | Accessor methods | Never expose public fields in public classes |
| 17 | Immutability | 5 rules: no setters, final class, final fields, private, defensive copies |
| 18 | Composition | Favor composition over inheritance; use forwarding classes |
| 19 | Inheritance | Design for it or prohibit it; don't call overridables in constructors |
| 20 | Interfaces | Prefer interfaces to abstract classes; use skeletal implementations |
| 21 | Interface design | Design for posterity; can't change once released |
| 22 | Interface types | Use interfaces only to define types (not constant interfaces) |
| 23 | Class hierarchies | Replace tagged classes with class hierarchies |
| 24 | Static member classes | Favor static over nonstatic member classes |
| 25 | One class per file | Never put multiple top-level classes in one file |

---

## Chapter 5: Generics (Items 26–33)

| Item | Rule | Key Takeaway |
|------|------|-------------|
| 26 | No raw types | Never use raw types; `List<Object>` ≠ `List<String>` |
| 27 | Unchecked warnings | Eliminate all unchecked warnings; suppress with comment if safe |
| 28 | Lists vs arrays | Prefer `List` to arrays (arrays are reified, covariant) |
| 29 | Generic types | Favor generic types; use `@SuppressWarnings("unchecked")` for arrays |
| 30 | Generic methods | Use for type-safe utility methods; recursive type bounds |
| 31 | Bounded wildcards | **PECS**: Producer-`extends`, Consumer-`super` |
| 32 | Varargs + generics | Combine judiciously; use `@SafeVarargs` |
| 33 | Heterogeneous containers | Use `Class<T>` keys for typesafe containers |

---

## Chapter 6: Enums and Annotations (Items 34–41)

| Item | Rule | Key Takeaway |
|------|------|-------------|
| 34 | Enums over ints | Never use `int`/`String` constants; enums are full classes |
| 35 | Instance fields | Use instance fields, not `ordinal()` |
| 36 | EnumSet | Use `EnumSet` instead of bit fields |
| 37 | EnumMap | Use `EnumMap` instead of ordinal indexing |
| 38 | Extensible enums | Emulate with interfaces |
| 39 | Annotations | Prefer annotations to naming patterns |
| 40 | @Override | Always use `@Override` on every method declaration |
| 41 | Marker interfaces | Use marker interfaces to define types; annotations for reflection |

---

## Chapter 7: Lambdas and Streams (Items 42–48)

| Item | Rule | Key Takeaway |
|------|------|-------------|
| 42 | Lambdas | Prefer lambdas to anonymous classes; keep short |
| 43 | Method references | Prefer method references to lambdas when clearer |
| 44 | Standard functional interfaces | Use `Predicate`, `Function`, `Supplier`, `Consumer`, etc. |
| 45 | Streams judiciously | Use for uniform transforms, filtering, combining |
| 46 | Side-effect-free | Never use `forEach` to compute; use `collect` |
| 47 | Return Collection | Prefer `Collection` to `Stream` as return type |
| 48 | Parallel streams | Use caution; measure; right data structures matter |

---

## Chapter 8: Methods (Items 49–56)

| Item | Rule | Key Takeaway |
|------|------|-------------|
| 49 | Parameter validation | Check parameters at method start; use `Objects.requireNonNull` |
| 50 | Defensive copies | Copy before validation; use immutable types when possible |
| 51 | Method signatures | ≤4 parameters; favor interfaces; use enums over booleans |
| 52 | Overloading | Selection is static; use overriding instead |
| 53 | Varargs | Use judiciously; provide overloads for 0–3 args |
| 54 | Empty collections | Return empty collections, never `null` |
| 55 | Optional | Return `Optional` judiciously; never return `null` for Optional |
| 56 | Doc comments | Document `@param`, `@return`, `@throws` for all public APIs |

---

## Chapter 9: General Programming (Items 57–68)

| Item | Rule | Key Takeaway |
|------|------|-------------|
| 57 | Local variable scope | Declare where first used; prefer for-loops |
| 58 | for-each loops | Prefer to traditional for-loops |
| 59 | Libraries | Know and use `java.util`, `java.util.concurrent`, `java.time` |
| 60 | BigDecimal | Avoid `float`/`double` for exact answers |
| 61 | Primitives | Prefer primitives to boxed primitives |
| 62 | Strings | Don't use strings for aggregate types or enums |
| 63 | String concatenation | Use `StringBuilder` in loops |
| 64 | Interface types | Refer to objects by interfaces, not classes |
| 65 | Reflection | Prefer interfaces to reflection |
| 66 | Native methods | Use judiciously; often not worth it |
| 67 | Optimization | Don't optimize prematurely; measure first |
| 68 | Naming conventions | Follow Java naming conventions strictly |

---

## Chapter 10: Exceptions (Items 69–77)

| Item | Rule | Key Takeaway |
|------|------|-------------|
| 69 | Exceptions for exceptional | Don't use exceptions for control flow |
| 70 | Checked vs unchecked | Checked = recoverable; unchecked = programming error |
| 71 | Unnecessary checked | Avoid checked exceptions when possible |
| 72 | Standard exceptions | Reuse `IllegalArgumentException`, `IllegalStateException`, etc. |
| 73 | Exception translation | Translate low-level to high-level exceptions |
| 74 | Document exceptions | Document all exceptions with `@throws` |
| 75 | Detail messages | Include failure-capture info in exception messages |
| 76 | Failure atomicity | Failed method should leave object in prior state |
| 77 | Don't ignore | Never ignore exceptions; at minimum, log them |

---

## Chapter 11: Concurrency (Items 78–84)

| Item | Rule | Key Takeaway |
|------|------|-------------|
| 78 | Synchronization | Synchronize access to shared mutable data; use `volatile` carefully |
| 79 | Excessive sync | Don't call alien methods from synchronized blocks |
| 80 | Executors | Prefer `ExecutorService` to raw threads |
| 81 | ConcurrentHashMap | Prefer to `Collections.synchronizedMap` |
| 82 | Thread safety docs | Document thread safety of every class |
| 83 | Lazy initialization | Holder class idiom for static; double-check for instance |
| 84 | Thread scheduler | Don't depend on thread scheduler |

---

## Chapter 12: Serialization (Items 85–90)

| Item | Rule | Key Takeaway |
|------|------|-------------|
| 85 | Alternatives | Prefer JSON, Protobuf over Java serialization |
| 86 | Serializable caution | Implement with great caution; released forever |
| 87 | Custom serialized form | Use `transient` and custom `writeObject`/`readObject` |
| 88 | Defensive readObject | Make defensive copies; validate invariants |
| 89 | readResolve | Use for instance control (singletons) |
| 90 | Serialization proxies | Use proxy pattern for maximum safety |
