# Chapter 8: Methods (Items 49–56)

---

## Item 49: Check parameters for validity

```java
public BigInteger mod(BigInteger m) {
    if (m.signum <= 0)
        throw new ArithmeticException("Modulus must be positive");
    ...
}
```

### Use Objects.requireNonNull

```java
// Modern Java - no manual null checks needed
this.strategy = Objects.requireNonNull(strategy, "strategy");
```

### Rules
- Check parameters at the top of the method
- Check parameters stored for later use (constructors!)
- Indiscriminate reliance on implicit checks loses **failure atomicity**

---

## Item 50: Make defensive copies when needed

### The Problem

```java
public final class Period {
    private final Date start;
    private final Date end;

    public Period(Date start, Date end) {
        if (start.compareTo(end) > 0)
            throw new IllegalArgumentException(start + " after " + end);
        this.start = start;     // DANGEROUS - aliasing!
        this.end = end;         // DANGEROUS - aliasing!
    }
}

// Attack!
Date start = new Date();
Date end = new Date();
Period p = new Period(start, end);
end.setYear(78); // Modifies internals of p!
```

### The Fix: Defensive Copies

```java
public Period(Date start, Date end) {
    // Defensive copies FIRST (before validation)
    this.start = new Date(start.getTime());
    this.end = new Date(end.getTime());

    // Validate on copies (protects against TOCTOU attacks)
    if (this.start.compareTo(this.end) > 0)
        throw new IllegalArgumentException(this.start + " after " + this.end);
}

// Also defend accessors
public Date start() {
    return new Date(start.getTime());
}
```

### Modern Java: Use Immutable Types

```java
public final class Period {
    private final Instant start;
    private final Instant end;

    public Period(Instant start, Instant end) {
        if (start.compareTo(end) > 0)
            throw new IllegalArgumentException(start + " after " + end);
        this.start = start; // Instant is immutable - safe!
        this.end = end;
    }
}
```

### Key Rules
- Make defensive copies **before** checking validity
- Don't use `clone()` for defensive copies of parameters (subclassable types)
- Return defensive copies of mutable internal fields
- **Best solution:** Use immutable objects as components

---

## Item 51: Design method signatures carefully

### Guidelines
1. **Choose method names carefully** — clear, consistent, follow conventions
2. **Don't go overboard with convenience methods** — every method should "pull its weight"
3. **Avoid long parameter lists** — aim for ≤4 parameters
   - Break method into multiple methods
   - Create helper classes to hold parameters
   - Use Builder pattern for object construction
4. **For parameter types, favor interfaces over classes**
5. **Prefer two-element enum types to boolean parameters**

```java
// BAD - boolean is unclear at call site
public void setTemperature(boolean celsius) { ... }

// GOOD - enum is self-documenting
public enum TemperatureScale { FAHRENHEIT, CELSIUS }
public void setTemperature(TemperatureScale scale) { ... }
```

---

## Item 52: Use overloading judiciously

### The Selection is Static

```java
public class CollectionClassifier {
    public static String classify(Set<?> s) { return "Set"; }
    public static String classify(List<?> lst) { return "List"; }
    public static String classify(Collection<?> c) { return "Unknown Collection"; }

    public static void main(String[] args) {
        Collection<?>[] collections = {
            new HashSet<String>(),
            new ArrayList<String>(),
            new HashMap<String, String>().values()
        };

        for (Collection<?> c : collections)
            System.out.println(classify(c)); // Always prints "Unknown Collection"!
    }
}
```

### The Fix: Use Overriding Instead

```java
class Wine {
    String name() { return "wine"; }
}

class SparklingWine extends Wine {
    @Override
    String name() { return "sparkling wine"; }
}

class Champagne extends SparklingWine {
    @Override
    String name() { return "champagne"; }
}

// Works correctly - selection is dynamic
for (Wine wine : wines)
    System.out.println(wine.name());
```

---

## Item 53: Use varargs judiciously

```java
// Every invocation requires an array allocation!
public void foo() { ... }
public void foo(int a1) { ... }
public void foo(int a1, int a2) { ... }
public void foo(int a1, int a2, int a3) { ... }
public void foo(int a1, int a2, int a3, int... rest) { ... }
```

### Varargs and Generics

```java
// Safe with @SafeVarargs
@SafeVarargs
static <T> List<T> flatten(List<? extends T>... lists) { ... }
```

---

## Item 54: Return empty collections or arrays, not nulls

```java
// BAD - forces null checks on every caller
public List<Cheese> getCheeses() {
    return cheesesInStock.isEmpty() ? null : new ArrayList<>(cheesesInStock);
}

// GOOD - empty collection is fine
public List<Cheese> getCheeses() {
    return new ArrayList<>(cheesesInStock);
}

// OPTIMIZED - reuse immutable empty collection
public List<Cheese> getCheeses() {
    return cheesesInStock.isEmpty() ? Collections.emptyList()
        : new ArrayList<>(cheesesInStock);
}
```

---

## Item 55: Return optionals judiciously

```java
// BAD - exception for control flow
public static <E extends Comparable<E>> E max(Collection<E> c) {
    if (c.isEmpty())
        throw new IllegalArgumentException("Empty collection");
    ...
}

// BETTER - return Optional
public static <E extends Comparable<E>> Optional<E> max(Collection<E> c) {
    if (c.isEmpty())
        return Optional.empty();
    ...
}

// Usage
Optional<E> max = max(collection);
max.ifPresent(System.out::println);
```

### Rules
- Never return `null` for an `Optional`-returning method
- Don't use `Optional` in fields, method parameters, or collections
- `Optional` is primarily for return types
- Prefer `OptionalInt`, `OptionalLong`, `OptionalDouble` for primitives

---

## Item 56: Write doc comments for all exposed API elements

### Javadoc Best Practices

```java
/**
 * Returns the element at the specified position in this list.
 *
 * <p>This method is <i>not</i> guaranteed to run in constant time.
 * In some implementations it may run in time proportional to the
 * element position.
 *
 * @param index index of the element to return; must be non-negative
 *              and less than the size of this list
 * @return the element at the specified position in this list
 * @throws IndexOutOfBoundsException if the index is out of range
 *         ({@code index < 0 || index >= size()})
 */
E get(int index);
```

### Key Rules
- Document every parameter with `@param`
- Document return value with `@return` (even for void)
- Document every exception with `@throws`
- Use `{@code}` for code fragments
- Use `{@literal}` for HTML metacharacters
- Provide a summary description (first sentence)
