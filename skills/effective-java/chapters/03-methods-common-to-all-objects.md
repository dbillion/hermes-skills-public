# Chapter 3: Methods Common to All Objects (Items 10–14)

---

## Item 10: Obey the general contract when overriding equals

### When NOT to Override equals

- Each instance is inherently unique (e.g., `Thread`)
- No need for logical equality test (e.g., `Pattern`)
- Superclass already overrode `equals` and it still applies (e.g., `AbstractSet` → `Set`)
- Private class/package-private class where `equals` will never be invoked

### The equals Contract

1. **Reflexive:** `x.equals(x)` must return `true`
2. **Symmetric:** `x.equals(y)` iff `y.equals(x)`
3. **Transitive:** if `x.equals(y)` and `y.equals(z)`, then `x.equals(z)`
4. **Consistent:** Multiple invocations return the same result (if no mutation)
5. **Non-nullity:** `x.equals(null)` must return `false`

### Recipe for a High-Quality equals Method

```java
@Override
public boolean equals(Object o) {
    // 1. Use == for performance
    if (o == this)
        return true;

    // 2. Check type
    if (!(o instanceof PhoneNumber))
        return false;

    // 3. Cast
    PhoneNumber pn = (PhoneNumber) o;

    // 4. Check significant fields (compare cheapest/most likely to differ first)
    return pn.lineNum == lineNum
        && pn.prefix == prefix
        && pn.areaCode == areaCode;
}
```

### Important Rules
- **Always override `hashCode` when you override `equals`**
- Don't be too clever (e.g., don't use `getClass()` check unless required)
- Don't write `equals` that depends on unreliable resources (e.g., network)
- Make sure parameter is `Object` type (use `@Override` to catch mistakes)

### The Liskov Substitution Problem

```java
// BROKEN - Violates symmetry!
public final class CaseInsensitiveString {
    private final String s;

    @Override 
    public boolean equals(Object o) {
        if (o instanceof CaseInsensitiveString)
            return s.equalsIgnoreCase(((CaseInsensitiveString) o).s);
        if (o instanceof String)  // One-way interoperability!
            return s.equalsIgnoreCase((String) o);
        return false;
    }
}
```

**Fix:** Remove the `String` comparison. Only compare with same type.

---

## Item 11: Always override hashCode when you override equals

### The Contract

- Equal objects **must** have equal hash codes
- Unequal objects **should** have unequal hash codes (not required but desirable)

### A Good hashCode Implementation

```java
@Override
public int hashCode() {
    int result = Short.hashCode(areaCode);
    result = 31 * result + Short.hashCode(prefix);
    result = 31 * result + Short.hashCode(lineNum);
    return result;
}
```

### Using Objects.hash (Slower but Cleaner)

```java
@Override
public int hashCode() {
    return Objects.hash(lineNum, prefix, areaCode);
}
```

### Lazily Initialized hashCode (for Immutable Objects)

```java
private int hashCode; // Default 0

@Override
public int hashCode() {
    int result = hashCode;
    if (result == 0) {
        result = Short.hashCode(areaCode);
        result = 31 * result + Short.hashCode(prefix);
        result = 31 * result + Short.hashCode(lineNum);
        hashCode = result;
    }
    return result;
}
```

### Key Points
- Do NOT exclude significant fields for performance
- Don't provide a detailed specification of the hashCode value
- Use `31` as multiplier (it's odd prime, `31 * i == (i << 5) - i`)

---

## Item 12: Always override toString

### Why?
- Makes your class more pleasant to use
- Makes systems using the class easier to debug
- `toString` is automatically called in many contexts (logging, concatenation, `println`)

### Guidelines

```java
@Override
public String toString() {
    return "PhoneNumber{" +
        "areaCode=" + areaCode +
        ", prefix=" + prefix +
        ", lineNum=" + lineNum +
        '}';
}
```

- Return **all** interesting information contained in the object
- Document whether you specify a format (and provide a static factory to parse back)
- Provide programmatic access to the info (don't force clients to parse the string)

---

## Item 13: Override clone judiciously

### The Cloneable Interface
- `Cloneable` is a **marker interface** with no methods
- It indicates that `Object.clone()` will return field-by-field copy

### Problems with clone()

```java
// BROKEN - clone creates shared mutable state!
@Override
public Stack clone() {
    try {
        Stack result = (Stack) super.clone();
        result.elements = elements.clone(); // Deep copy needed!
        return result;
    } catch (CloneNotSupportedException e) {
        throw new AssertionError();
    }
}
```

### Better Alternative: Copy Constructor or Factory

```java
// Copy constructor
public Yum(Yum yum) { ... }

// Copy factory
public static Yum newInstance(Yum yum) { ... }
```

### Why Copy Constructors/Factories Are Better
- Don't conflict with proper use of `final` fields
- Don't throw unnecessary checked exceptions
- Don't require casting
- Can accept interface types (e.g., `new TreeSet<>(s)` works for any `Set`)

### If You Must Use clone()
- Call `super.clone()`, not constructor
- Fix any fields that need deep copying
- `clone` must never invoke overridable methods
- Public `clone` should omit `throws` clause
- New interfaces should not extend `Cloneable`

---

## Item 14: Consider implementing Comparable

### Why?
- Allows objects to be used with `TreeSet`, `TreeMap`, search/sort utilities
- Easy to specify complex field comparisons

### The compareTo Contract

1. **sgn(x.compareTo(y)) == -sgn(y.compareTo(x))** (antisymmetry)
2. **Transitive:** if `x.compareTo(y) > 0` and `y.compareTo(z) > 0`, then `x.compareTo(z) > 0`
3. **Consistent with equals:** `x.compareTo(y) == 0` implies `x.equals(y)` (recommended but not required)

### Implementation Pattern

```java
public final class PhoneNumber implements Comparable<PhoneNumber> {
    private final short areaCode, prefix, lineNum;

    @Override
    public int compareTo(PhoneNumber pn) {
        int result = Short.compare(areaCode, pn.areaCode);
        if (result == 0) {
            result = Short.compare(prefix, pn.prefix);
            if (result == 0) {
                result = Short.compare(lineNum, pn.lineNum);
            }
        }
        return result;
    }
}
```

### Java 8+ Comparator Construction

```java
private static final Comparator<PhoneNumber> COMPARATOR =
    comparingInt((PhoneNumber pn) -> pn.areaCode)
        .thenComparingInt(pn -> pn.prefix)
        .thenComparingInt(pn -> pn.lineNum);

@Override
public int compareTo(PhoneNumber pn) {
    return COMPARATOR.compare(this, pn);
}
```

### Key Points
- Use `<` and `>` for primitive fields (not subtraction — risk of overflow)
- Use `Comparator` static methods for clean, readable comparisons
