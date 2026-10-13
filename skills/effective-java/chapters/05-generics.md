# Chapter 5: Generics (Items 26–33)

---

## Item 26: Don't use raw types

```java
// BAD - raw type
private final Collection stamps = ...;
stamps.add(new Coin(...)); // Compiles, but error at runtime!

// GOOD - parameterized type
private final Collection<Stamp> stamps = ...;
stamps.add(new Coin(...)); // Compile-time error!
```

### Exceptions (Rare)
- `Class` literals must use raw types: `List.class` (not `List<String>.class`)
- `instanceof` with raw types: `o instanceof Set`

---

## Item 27: Eliminate unchecked warnings

```java
@SuppressWarnings("unchecked")
public <T> T[] toArray(T[] a) {
    if (a.length < size) {
        // This cast is correct because the array we're creating
        // is of the same type as the one passed in, which is T[].
        return (T[]) Arrays.copyOf(elements, size, a.getClass());
    }
    ...
}
```

### Rules
- Eliminate **every** unchecked warning you can
- If you can't eliminate it, prove it's typesafe, then suppress with `@SuppressWarnings("unchecked")`
- Apply annotation to the **smallest scope possible**
- **Always** add a comment explaining why it's safe

---

## Item 28: Prefer lists to arrays

### Arrays vs Generics

| Feature | Arrays | Generics |
|---------|--------|----------|
| Covariance | `Object[]` is supertype of `String[]` | `List<Object>` is NOT supertype of `List<String>` |
| Reification | Enforce type at runtime | Type erasure (compile-time only) |

### The Problem

```java
// Fails at runtime!
Object[] objectArray = new Long[1];
objectArray[0] = "I don't fit in"; // ArrayStoreException

// Fails at compile time (good!)
List<Object> ol = new ArrayList<Long>(); // Incompatible types
ol.add("I don't fit in");
```

### Arrays and Generics Don't Mix

```java
// All illegal!
new List<E>[]
new List<String>[]
new E[]
```

### Use Lists Instead

```java
// BAD - array-based
public class Chooser {
    private final Object[] choiceArray;

    public Chooser(Collection choices) {
        choiceArray = choices.toArray();
    }

    public Object choose() {
        Random rnd = ThreadLocalRandom.current();
        return choiceArray[rnd.nextInt(choiceArray.length)];
    }
}

// GOOD - list-based
public class Chooser<T> {
    private final List<T> choiceList;

    public Chooser(Collection<T> choices) {
        choiceList = new ArrayList<>(choices);
    }

    public T choose() {
        Random rnd = ThreadLocalRandom.current();
        return choiceList.get(rnd.nextInt(choiceList.size()));
    }
}
```

---

## Item 29: Favor generic types

```java
// Before generification
public class Stack {
    private Object[] elements;
    private int size = 0;
    ...
    public void push(Object e) { ... }
    public Object pop() { ... }
}

// After generification
public class Stack<E> {
    private E[] elements;
    private int size = 0;
    ...
    public void push(E e) { ... }
    public E pop() { ... }
}
```

### Handling Array Creation

```java
// Option 1: Suppress warning (common practice)
@SuppressWarnings("unchecked")
public Stack() {
    elements = (E[]) new Object[DEFAULT_INITIAL_CAPACITY];
}

// Option 2: Use Object array and cast on every access
private Object[] elements;
public E pop() {
    E result = (E) elements[--size];
    ...
}
```

---

## Item 30: Favor generic methods

```java
// Generic singleton factory
private static UnaryOperator<Object> IDENTITY_FN = (t) -> t;

@SuppressWarnings("unchecked")
public static <T> UnaryOperator<T> identityFunction() {
    return (UnaryOperator<T>) IDENTITY_FN;
}

// Recursive type bound
public static <E extends Comparable<E>> E max(Collection<E> c) {
    if (c.isEmpty())
        throw new IllegalArgumentException("Empty collection");

    E result = null;
    for (E e : c)
        if (result == null || e.compareTo(result) > 0)
            result = e;

    return result;
}
```

---

## Item 31: Use bounded wildcards to increase API flexibility

### PECS: Producer-`extends`, Consumer-`super`

```java
// Producer - uses extends
public void pushAll(Iterable<? extends E> src) {
    for (E e : src)
        push(e);
}

// Consumer - uses super
public void popAll(Collection<? super E> dst) {
    while (!isEmpty())
        dst.add(pop());
}
```

### Don't Use Wildcards as Return Types

```java
// BAD - forces clients to think about wildcards
public static <E extends Comparable<? super E>> E max(List<? extends E> list)

// GOOD - clients don't see wildcards
public static <E extends Comparable<E>> E max(List<E> list)
```

### Comparable and Comparator

```java
// Always use bounded wildcards for comparables
public static <T extends Comparable<? super T>> T max(List<? extends T> list)

// Same for comparators
public static <T> T max(List<? extends T> list, Comparator<? super T> comp)
```

---

## Item 32: Combine generics and varargs judiciously

### The Problem: Heap Pollution

```java
// Dangerous - heap pollution!
static void dangerous(List<String>... stringLists) {
    List<Integer> intList = List.of(42);
    Object[] objects = stringLists;
    objects[0] = intList; // Heap pollution
    String s = stringLists[0].get(0); // ClassCastException!
}
```

### Safe Varargs Annotation

```java
@SafeVarargs
static <T> List<T> flatten(List<? extends T>... lists) {
    List<T> result = new ArrayList<>();
    for (List<? extends T> list : lists)
        result.addAll(list);
    return result;
}
```

---

## Item 33: Consider typesafe heterogeneous containers

```java
public class Favorites {
    private Map<Class<?>, Object> favorites = new HashMap<>();

    public <T> void putFavorite(Class<T> type, T instance) {
        favorites.put(Objects.requireNonNull(type), type.cast(instance));
    }

    public <T> T getFavorite(Class<T> type) {
        return type.cast(favorites.get(type));
    }
}

// Usage
Favorites f = new Favorites();
f.putFavorite(String.class, "Java");
f.putFavorite(Integer.class, 0xcafebabe);
f.putFavorite(Class.class, Favorites.class);

String favoriteString = f.getFavorite(String.class);
```

### Limitations
- Cannot use with non-reifiable types (e.g., `List<String>.class` is illegal)
- Can use supertype tokens to work around this
