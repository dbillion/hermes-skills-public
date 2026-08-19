# Effective Java — Complete Learning Skill

## Overview
Master the 90 items from Joshua Bloch's *Effective Java* (3rd Edition) to write robust, maintainable, and efficient Java code.

---

## Learning Path

### Phase 1: Foundations (Items 1–25)
**Goal:** Understand object creation, core methods, and class design.

| Week | Items | Topics |
|------|-------|--------|
| 1 | 1–9 | Static factories, Builder pattern, Singletons, Dependency Injection, Object reuse, Try-with-resources |
| 2 | 10–14 | `equals`, `hashCode`, `toString`, `clone`, `Comparable` contracts |
| 3 | 15–25 | Accessibility, Immutability, Composition vs Inheritance, Class hierarchies, Nested classes |

**Deliverable:** Build a small library applying these patterns.

### Phase 2: Advanced Types (Items 26–48)
**Goal:** Master generics, enums, lambdas, and streams.

| Week | Items | Topics |
|------|-------|--------|
| 4 | 26–33 | Generics, wildcards, PECS, varargs safety |
| 5 | 34–41 | Enum patterns, EnumSet, EnumMap, Annotations, Marker interfaces |
| 6 | 42–48 | Lambdas, Method references, Stream best practices, Collectors |

**Deliverable:** Refactor an existing project using streams and generics properly.

### Phase 3: Professional Practices (Items 49–90)
**Goal:** Handle methods, exceptions, concurrency, and serialization safely.

| Week | Items | Topics |
|------|-------|--------|
| 7 | 49–56 | Parameter validation, Defensive copies, Method signatures, Overloading |
| 8 | 57–68 | Local variables, Libraries, `BigDecimal`, Reflection, Native methods |
| 9 | 69–77 | Exception design, Checked vs Unchecked, Failure atomicity |
| 10 | 78–84 | Concurrency, Synchronization, Executors, Lazy initialization |
| 11 | 85–90 | Serialization dangers, Serialization proxies, Alternatives (JSON, Protobuf) |

**Deliverable:** Code review a project applying all 90 items.

---

## Key Principles Summary

### 1. Creating and Destroying Objects
- **Item 1:** Use static factory methods (`of()`, `from()`, `valueOf()`, `getInstance()`)
- **Item 2:** Use Builder pattern for many constructor parameters
- **Item 3:** Singletons via `enum` (not `private static final`)
- **Item 4:** Non-instantiable classes need `private` constructor
- **Item 5:** Prefer dependency injection over hardwiring
- **Item 6:** Reuse immutable objects; prefer primitives over boxed types
- **Item 7:** Null out obsolete references in custom data structures
- **Item 8:** Avoid finalizers and cleaners
- **Item 9:** Always use try-with-resources

### 2. Methods Common to All Objects
- **Item 10:** Override `equals` only when necessary; follow the contract (reflexive, symmetric, transitive, consistent)
- **Item 11:** Always override `hashCode` when overriding `equals`
- **Item 12:** Always override `toString`
- **Item 13:** Prefer copy constructors over `Cloneable`
- **Item 14:** Implement `Comparable` for value classes

### 3. Classes and Interfaces
- **Item 15:** Minimize accessibility (prefer `private`)
- **Item 16:** Use accessor methods, not public fields
- **Item 17:** Minimize mutability — immutable objects are thread-safe
- **Item 18:** Favor composition over inheritance
- **Item 19:** Design for inheritance or prohibit it
- **Item 20:** Prefer interfaces to abstract classes
- **Item 21:** Design interfaces for posterity
- **Item 22:** Use interfaces only to define types
- **Item 23:** Prefer class hierarchies to tagged classes
- **Item 24:** Favor static member classes
- **Item 25:** One top-level class per source file

### 4. Generics
- **Item 26:** Don't use raw types
- **Item 27:** Eliminate unchecked warnings
- **Item 28:** Prefer `List` to arrays
- **Item 29:** Favor generic types
- **Item 30:** Favor generic methods
- **Item 31:** Use bounded wildcards (PECS: Producer-`extends`, Consumer-`super`)
- **Item 32:** Combine generics and varargs judiciously
- **Item 33:** Consider typesafe heterogeneous containers

### 5. Enums and Annotations
- **Item 34:** Use enums instead of `int` constants
- **Item 35:** Use instance fields, not ordinals
- **Item 36:** Use `EnumSet`, not bit fields
- **Item 37:** Use `EnumMap`, not ordinal indexing
- **Item 38:** Emulate extensible enums with interfaces
- **Item 39:** Prefer annotations to naming patterns
- **Item 40:** Consistently use `@Override`
- **Item 41:** Use marker interfaces to define types

### 6. Lambdas and Streams
- **Item 42:** Prefer lambdas to anonymous classes
- **Item 43:** Prefer method references to lambdas
- **Item 44:** Favor standard functional interfaces
- **Item 45:** Use streams judiciously
- **Item 46:** Prefer side-effect-free functions in streams
- **Item 47:** Prefer `Collection` to `Stream` as return type
- **Item 48:** Use caution when making streams parallel

### 7. Methods
- **Item 49:** Check parameters for validity
- **Item 50:** Make defensive copies when needed
- **Item 51:** Design method signatures carefully
- **Item 52:** Use overloading judiciously
- **Item 53:** Use varargs judiciously
- **Item 54:** Return empty collections, not `null`
- **Item 55:** Return `Optional` judiciously
- **Item 56:** Write doc comments for all exposed API elements

### 8. General Programming
- **Item 57:** Minimize scope of local variables
- **Item 58:** Prefer for-each loops
- **Item 59:** Know and use the libraries
- **Item 60:** Avoid `float`/`double` for exact answers (use `BigDecimal`)
- **Item 61:** Prefer primitive types to boxed primitives
- **Item 62:** Avoid strings where other types are appropriate
- **Item 63:** Beware the performance of string concatenation
- **Item 64:** Refer to objects by their interfaces
- **Item 65:** Prefer interfaces to reflection
- **Item 66:** Use native methods judiciously
- **Item 67:** Optimize judiciously
- **Item 68:** Adhere to generally accepted naming conventions

### 9. Exceptions
- **Item 69:** Use exceptions only for exceptional conditions
- **Item 70:** Checked exceptions for recoverable, runtime for programming errors
- **Item 71:** Avoid unnecessary checked exceptions
- **Item 72:** Favor standard exceptions
- **Item 73:** Throw exceptions appropriate to the abstraction
- **Item 74:** Document all exceptions thrown
- **Item 75:** Include failure-capture info in detail messages
- **Item 76:** Strive for failure atomicity
- **Item 77:** Don't ignore exceptions

### 10. Concurrency
- **Item 78:** Synchronize access to shared mutable data
- **Item 79:** Avoid excessive synchronization
- **Item 80:** Prefer executors, tasks, and streams to threads
- **Item 81:** Prefer `ConcurrentHashMap` to `Collections.synchronizedMap`
- **Item 82:** Document thread safety
- **Item 83:** Use lazy initialization judiciously
- **Item 84:** Don't depend on the thread scheduler

### 11. Serialization
- **Item 85:** Prefer alternatives to Java serialization (JSON, Protobuf)
- **Item 86:** Implement `Serializable` with great caution
- **Item 87:** Consider using a custom serialized form
- **Item 88:** Write `readObject` methods defensively
- **Item 89:** For instance control, prefer `readResolve` to `readObject`
- **Item 90:** Consider serialization proxies instead of serialized instances

---

## Study Checklist

- [ ] Read all 11 chapter guides in `chapters/`
- [ ] Run all code examples in `code-examples/`
- [ ] Complete the 3-phase learning path above
- [ ] Apply at least 5 items to a real project
- [ ] Review cheatsheets before code reviews
- [ ] Read the official source code on GitHub

---

## Quick Reference: Top 10 Must-Know Items

1. **Item 2** — Builder Pattern for complex objects
2. **Item 10–11** — `equals` and `hashCode` contracts
3. **Item 17** — Make classes immutable when possible
4. **Item 18** — Favor composition over inheritance
5. **Item 31** — PECS: Producer-`extends`, Consumer-`super`
6. **Item 34** — Use enums, not `int` constants
7. **Item 43** — Prefer method references to lambdas
8. **Item 50** — Make defensive copies
9. **Item 76** — Strive for failure atomicity
10. **Item 85** — Avoid Java serialization; use JSON/Protobuf
