# Chapter 7: Lambdas and Streams (Items 42–48)

---

## Item 42: Prefer lambdas to anonymous classes

### Anonymous Class (Verbose)

```java
// Old way
Collections.sort(words, new Comparator<String>() {
    public int compare(String s1, String s2) {
        return Integer.compare(s1.length(), s2.length());
    }
});
```

### Lambda (Concise)

```java
Collections.sort(words, (s1, s2) -> Integer.compare(s1.length(), s2.length()));
```

### Method Reference (Even Better — see Item 43)

```java
Collections.sort(words, comparingInt(String::length));
```

### Key Points
- Omit types when the compiler can infer them
- Omit parentheses for single inferred-type parameter
- Omit braces and `return` for single-expression lambdas
- Don't use lambdas where they make code less clear
- Lambdas lack names and documentation — keep them short (few lines)

---

## Item 43: Prefer method references to lambdas

```java
// Lambda
map.merge(key, 1, (count, incr) -> count + incr);

// Method reference - cleaner!
map.merge(key, 1, Integer::sum);
```

### Method Reference Types

| Type | Example | Lambda Equivalent |
|------|---------|-------------------|
| Static | `Integer::parseInt` | `str -> Integer.parseInt(str)` |
| Bound | `Instant.now()::isAfter` | `Instant then = Instant.now(); t -> then.isAfter(t)` |
| Unbound | `String::toLowerCase` | `str -> str.toLowerCase()` |
| Class Constructor | `TreeMap<K,V>::new` | `() -> new TreeMap<K,V>()` |
| Array Constructor | `int[]::new` | `len -> new int[len]` |

### When to Use Lambdas Instead
- When the method name doesn't describe the operation well
- When the lambda is shorter than the method reference
- When parameters need transformation

---

## Item 44: Favor the use of standard functional interfaces

### Key Standard Interfaces

| Interface | Signature | Example |
|-----------|-----------|---------|
| `UnaryOperator<T>` | `T apply(T t)` | `String::toLowerCase` |
| `BinaryOperator<T>` | `T apply(T t1, T t2)` | `BigInteger::add` |
| `Predicate<T>` | `boolean test(T t)` | `Collection::isEmpty` |
| `Function<T,R>` | `R apply(T t)` | `Arrays::asList` |
| `Supplier<T>` | `T get()` | `Instant::now` |
| `Consumer<T>` | `void accept(T t)` | `System.out::println` |

### Rules
- Use standard interfaces when possible
- Don't add `@FunctionalInterface` unless you want multiple interfaces
- Provide specialized primitive interfaces (`IntPredicate`, `LongBinaryOperator`) to avoid boxing

---

## Item 45: Use streams judiciously

### When to Use Streams
- Uniformly transform sequences of elements
- Filter sequences
- Combine sequences using a single operation
- Accumulate sequences into a collection
- Search a sequence for an element satisfying a criterion

### When NOT to Use Streams
- When readability suffers
- When you need access to indices
- When you need to modify local variables
- When you need `break`/`continue`/`return` from enclosing method

```java
// GOOD - streams shine here
Map<String, Long> freq = words.stream()
    .collect(groupingBy(String::toLowerCase, counting()));

// BAD - streams make this worse
for (int i = 0; i < values.size(); i++) {
    // Need index - streams don't help
}
```

---

## Item 46: Prefer side-effect-free functions in streams

### The Pure Function Principle

```java
// BAD - side effects in forEach!
Map<String, Long> freq = new HashMap<>();
words.forEach(word -> {
    freq.merge(word.toLowerCase(), 1L, Long::sum); // Mutating external state!
});

// GOOD - pure function pipeline
Map<String, Long> freq = words.stream()
    .collect(groupingBy(String::toLowerCase, counting()));
```

### Key Collectors

```java
// toList, toSet, toMap
List<String> result = stream.collect(toList());

// groupingBy
Map<String, List<Album>> albumsByArtist = albums.stream()
    .collect(groupingBy(Album::getArtist));

// joining
String joined = stream.map(Object::toString).collect(joining(", "));

// counting, summing, averaging
long count = stream.collect(counting());
```

### Important Rules
- `forEach` should only present results, not compute them
- Never say `collect(counting())` — use `count()` directly
- Static import `Collectors` members for readability

---

## Item 47: Prefer Collection to Stream as a return type

### The Problem

```java
// Stream doesn't extend Iterable - can't use for-each!
Stream<String> stream = ...;
for (String s : stream) { ... } // ERROR!
```

### Solution: Return Collection

```java
// Collection provides both iteration and stream access
public Collection<String> getWords() { ... }

// Usage
for (String word : getWords()) { ... }        // Iteration
getWords().stream().filter(...).collect(...); // Stream
```

### When Stream is Appropriate
- Sequence is too large to store in memory
- Sequence is computed lazily (infinite streams)

---

## Item 48: Use caution when making streams parallel

### When Parallel Helps
- Large data sources
- Computationally intensive pipelines
- Correct source (ArrayList, arrays, IntStream.range, HashMap, etc.)

### When Parallel Hurts
- Stream source is `Stream.iterate` or `Stream.iterate`
- Terminal operation is `limit` or `findFirst`
- Small data sources
- Pipeline relies on encounter order

```java
// BAD - wrong source, wrong terminal operation
long sum = Stream.iterate(1L, i -> i + 1)
    .limit(n)
    .parallel()
    .reduce(0L, Long::sum);

// GOOD - right source, right terminal operation
long sum = LongStream.rangeClosed(1, n)
    .parallel()
    .sum();
```

### Performance Tips
- Measure before and after parallelizing
- Ensure correct data structures (`IntStream.range` > `Stream.iterate`)
- Avoid boxing in parallel streams
