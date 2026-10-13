# Chapter 10: Exceptions (Items 69–77)

---

## Item 69: Use exceptions only for exceptional conditions

```java
// BAD - using exception for control flow
try {
    int i = 0;
    while (true)
        range[i++].climb();
} catch (ArrayIndexOutOfBoundsException e) {
    // "Expected" end of loop
}

// GOOD - standard idiom
for (Mountain m : range)
    m.climb();
```

### Rules
- Exceptions are for exceptional conditions, not ordinary control flow
- A well-designed API must not force clients to use exceptions for control flow
- Provide state-testing methods or return distinguished values

---

## Item 70: Use checked exceptions for recoverable conditions and runtime exceptions for programming errors

### Checked Exceptions
- Use for conditions from which the caller can reasonably recover
- Confront the user with a mandate to recover

### Unchecked Exceptions (RuntimeException, Error)
- Use to indicate programming errors
- Most runtime exceptions indicate precondition violations

```java
// Checked - caller can recover
public void readFile(String path) throws IOException { ... }

// Unchecked - programming error
if (obj == null)
    throw new NullPointerException("obj must not be null");
```

---

## Item 71: Avoid unnecessary use of checked exceptions

### When Checked Exceptions Are Justified
- The exceptional condition cannot be prevented by proper use of the API
- The programmer using the API can take useful action once confronted

### Eliminating Checked Exceptions

```java
// Before - checked exception
String readFile(String path) throws FileNotFoundException {
    ...
}

// After - return Optional
Optional<String> readFile(String path) {
    ...
}
```

---

## Item 72: Favor the use of standard exceptions

### Most Commonly Reused Exceptions

| Exception | Use Case |
|-----------|----------|
| `IllegalArgumentException` | Non-null parameter value is inappropriate |
| `IllegalStateException` | Object state is inappropriate for method invocation |
| `NullPointerException` | Parameter value is null where prohibited |
| `IndexOutOfBoundsException` | Index parameter value is out of range |
| `ConcurrentModificationException` | Concurrent modification detected |
| `UnsupportedOperationException` | Object does not support method |

### Rules
- Reuse standard exceptions when possible
- Don't reuse `Exception`, `RuntimeException`, `Throwable`, or `Error`
- Document all exceptions thrown

---

## Item 73: Throw exceptions appropriate to the abstraction

### Exception Translation

```java
try {
    // Low-level abstraction
    ...
} catch (LowerLevelException e) {
    // Translate to higher-level abstraction
    throw new HigherLevelException(...);
}
```

### Example

```java
/**
 * Returns the element at the specified position in this list.
 * @throws IndexOutOfBoundsException if index is out of range
 */
public E get(int index) {
    ListIterator<E> i = listIterator(index);
    try {
        return i.next();
    } catch (NoSuchElementException e) {
        throw new IndexOutOfBoundsException("Index: " + index);
    }
}
```

### Exception Chaining

```java
try {
    ...
} catch (LowerLevelException cause) {
    throw new HigherLevelException(cause);
}
```

---

## Item 74: Document all exceptions thrown by each method

```java
/**
 * Registers the specified listener to receive action events
 * from this button. If the listener is null, no exception is
 * thrown and no action is performed.
 *
 * @param listener the action listener to be added
 * @throws NullPointerException if listener is null
 */
public void addActionListener(ActionListener listener) {
    ...
}
```

### Rules
- Always declare checked exceptions individually
- Document precisely the conditions under which each is thrown
- Use `@throws` for ALL exceptions, but `throws` keyword only for checked
- If many methods throw the same exception for the same reason, document in class comment

---

## Item 75: Include failure-capture information in detail messages

```java
// BAD - uninformative
throw new IndexOutOfBoundsException("Illegal index");

// GOOD - captures failure details
public IndexOutOfBoundsException(int lowerBound, int upperBound, int index) {
    super(String.format(
        "Lower bound: %d, Upper bound: %d, Index: %d",
        lowerBound, upperBound, index));
    this.lowerBound = lowerBound;
    this.upperBound = upperBound;
    this.index = index;
}
```

### Rules
- Include values of all parameters/fields that contributed to the exception
- Don't include passwords, encryption keys, or sensitive data
- Consider providing accessor methods for exception fields

---

## Item 76: Strive for failure atomicity

### Definition
A failed method invocation should leave the object in the state it was in prior to the invocation.

### Techniques

```java
// 1. Immutable objects - free failure atomicity
public class String { ... } // Always safe

// 2. Check parameters before making changes
public void addAll(int index, Collection<? extends E> c) {
    if (index < 0 || index > size)
        throw new IndexOutOfBoundsException();
    ... // Now safe to modify
}

// 3. Perform operation on temporary copy
public List<E> sort() {
    List<E> copy = new ArrayList<>(this);
    Collections.sort(copy);
    return copy; // Only return if successful
}

// 4. Recovery code (rare)
try {
    ...
} catch (Exception e) {
    rollback(); // Restore invariants
    throw e;
}
```

---

## Item 77: Don't ignore exceptions

```java
// BAD - empty catch block
try {
    ...
} catch (SomeException e) {
    // EMPTY - silently ignores the exception!
}

// GOOD - at minimum, log it
try {
    ...
} catch (SomeException e) {
    logger.log(Level.SEVERE, "...", e);
}

// If truly appropriate to ignore, document why
try {
    ...
} catch (SomeException ignored) {
    // This exception is expected when the file doesn't exist yet.
    // We will create it on the next write.
}
```
