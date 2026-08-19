# PECS Cheat Sheet
## Producer-Extends, Consumer-Super

---

## The Rule

> **PECS**: **P**roducer-**E**xtends, **C**onsumer-**S**uper

| Role | Wildcard | Mnemonic |
|------|----------|----------|
| **Producer** (reads from) | `? extends T` | You "extend" what you produce |
| **Consumer** (writes to) | `? super T` | You "super" what you consume |

---

## Examples

### Producer — `? extends T`

```java
// src produces E (we read from it)
public void pushAll(Iterable<? extends E> src) {
    for (E e : src)
        push(e);
}

// Usage
Stack<Number> numberStack = new Stack<>();
Iterable<Integer> integers = List.of(1, 2, 3);
numberStack.pushAll(integers); // OK: Integer extends Number
```

### Consumer — `? super T`

```java
// dst consumes E (we write to it)
public void popAll(Collection<? super E> dst) {
    while (!isEmpty())
        dst.add(pop());
}

// Usage
Stack<Number> numberStack = new Stack<>();
Collection<Object> objects = new ArrayList<>();
numberStack.popAll(objects); // OK: Object is super of Number
```

---

## Comparable and Comparator

```java
// Always use bounded wildcards for comparables
public static <T extends Comparable<? super T>> T max(List<? extends T> list)

// Same for comparators
public static <T> T max(List<? extends T> list, Comparator<? super T> comp)
```

### Why `Comparable<? super T>`?

```java
// If LocalDate implements ChronoLocalDate which extends Comparable<ChronoLocalDate>
// Then LocalDate implements Comparable<? super LocalDate> ✓
// But NOT Comparable<LocalDate> ✗
```

---

## Quick Decision Tree

```
Do you need to READ from the parameter?
  → YES → Use ? extends T (Producer)
  → NO → Do you need to WRITE to the parameter?
      → YES → Use ? super T (Consumer)
      → NO → Use T (or don't use generics)
```

---

## Common Mistakes

```java
// BAD - forces client to think about wildcards
public static <E extends Comparable<? super E>> E max(List<? extends E> list)

// GOOD - client doesn't see wildcards
public static <E extends Comparable<E>> E max(List<E> list)
```

### Don't Use Wildcards as Return Types

```java
// BAD
public static <E extends Comparable<? super E>> List<? extends E> sort(List<E> list)

// GOOD
public static <E extends Comparable<E>> List<E> sort(List<E> list)
```
