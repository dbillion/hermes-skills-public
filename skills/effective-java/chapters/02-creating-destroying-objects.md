# Chapter 2: Creating and Destroying Objects (Items 1–9)

---

## Item 1: Consider static factory methods instead of constructors

### Why Use Static Factory Methods?

| Advantage | Explanation |
|-----------|-------------|
| **Named** | Unlike constructors, they have names that describe what they create |
| **Instance Control** | Not required to return a *new* object — allows caching, singletons, flyweights |
| **Subtype Return** | Can return an object of any subtype of their return type |
| **Varying Classes** | Class of returned object can vary from call to call based on input |
| **SPI Basis** | Class need not exist when the containing class is written (Service Provider Frameworks) |

### Disadvantages

- No public/protected constructor means the class **cannot be subclassed**
- Harder for programmers to find (not obvious in API docs)

### Common Naming Conventions

```java
// Type conversion
LocalDate date = LocalDate.from(temporal);

// Aggregation
Set<String> set = Set.of("a", "b", "c");

// More verbose alternative
Boolean b = Boolean.valueOf("true");

// Returns instance (possibly cached)
Runtime rt = Runtime.getInstance();

// Returns guaranteed new instance
Object obj = Array.newInstance(String.class, 0);

// If in a different class
BufferedReader br = Files.newBufferedReader(path);

// Concise alternative
List<String> list = Collections.list(enumeration);
```

---

## Item 2: Consider a builder when faced with many constructor parameters

### The Problem with Telescoping Constructors

```java
// Hard to read, doesn't scale
public NutritionFacts(int servingSize, int servings) { ... }
public NutritionFacts(int servingSize, int servings, int calories) { ... }
public NutritionFacts(int servingSize, int servings, int calories, int fat) { ... }
```

### The Problem with JavaBeans Pattern

```java
// Allows inconsistency, mandates mutability
NutritionFacts cocaCola = new NutritionFacts();
cocaCola.setServingSize(240);
cocaCola.setServings(8);
cocaCola.setCalories(100);
// What if someone uses the object before all setters are called?
```

### The Builder Pattern Solution

```java
public class NutritionFacts {
    private final int servingSize;
    private final int servings;
    private final int calories;
    private final int fat;
    private final int sodium;
    private final int carbohydrate;

    public static class Builder {
        // Required parameters
        private final int servingSize;
        private final int servings;

        // Optional parameters - initialized to default values
        private int calories = 0;
        private int fat = 0;
        private int sodium = 0;
        private int carbohydrate = 0;

        public Builder(int servingSize, int servings) {
            this.servingSize = servingSize;
            this.servings = servings;
        }

        public Builder calories(int val) {
            calories = val;
            return this;
        }

        public Builder fat(int val) {
            fat = val;
            return this;
        }

        public Builder sodium(int val) {
            sodium = val;
            return this;
        }

        public Builder carbohydrate(int val) {
            carbohydrate = val;
            return this;
        }

        public NutritionFacts build() {
            return new NutritionFacts(this);
        }
    }

    private NutritionFacts(Builder builder) {
        servingSize = builder.servingSize;
        servings = builder.servings;
        calories = builder.calories;
        fat = builder.fat;
        sodium = builder.sodium;
        carbohydrate = builder.carbohydrate;
    }
}

// Usage
NutritionFacts cocaCola = new NutritionFacts.Builder(240, 8)
    .calories(100)
    .sodium(35)
    .carbohydrate(27)
    .build();
```

### Key Points
- Simulates named parameters from Python
- Well-suited to class hierarchies (can have abstract builder)
- Downside: must create Builder objects first

---

## Item 3: Enforce the singleton property with a private constructor or an enum type

### The Enum Singleton (Best Way)

```java
public enum Elvis {
    INSTANCE;

    public void leaveTheBuilding() { ... }
}

// Usage
Elvis.INSTANCE.leaveTheBuilding();
```

### Why Enum is Best
- Thread-safe by default
- Serialization handled automatically
- Reflection-safe

### Alternative: Private Constructor with Static Factory

```java
public class Elvis {
    private static final Elvis INSTANCE = new Elvis();
    private Elvis() { ... }
    public static Elvis getInstance() { return INSTANCE; }
}
```

---

## Item 4: Enforce noninstantiability with a private constructor

```java
public class UtilityClass {
    // Suppress default constructor for noninstantiability
    private UtilityClass() {
        throw new AssertionError("Cannot instantiate utility class");
    }

    public static void utilityMethod() { ... }
}
```

- Making a class `abstract` does NOT prevent instantiation (can be subclassed)
- Private constructor is the only reliable way

---

## Item 5: Prefer dependency injection to hardwiring resources

### Bad: Static Utility Class

```java
public class SpellChecker {
    private static final Lexicon dictionary = ...; // Hardwired!
    private SpellChecker() {} // Noninstantiable

    public static boolean isValid(String word) { ... }
}
```

### Bad: Singleton

```java
public class SpellChecker {
    private final Lexicon dictionary = ...; // Hardwired!
    private SpellChecker(...) {}
    public static SpellChecker INSTANCE = new SpellChecker(...);
}
```

### Good: Dependency Injection

```java
public class SpellChecker {
    private final Lexicon dictionary;

    public SpellChecker(Lexicon dictionary) {
        this.dictionary = Objects.requireNonNull(dictionary);
    }

    public boolean isValid(String word) { ... }
}

// Usage
SpellChecker sc = new SpellChecker(new EnglishLexicon());
```

- Provides testability and flexibility
- Consider dependency injection frameworks (Spring, Dagger, Guice)

---

## Item 6: Avoid creating unnecessary objects

### Reuse Immutable Objects

```java
// BAD - creates a new String each time
String s = new String("bikini"); // DON'T DO THIS

// GOOD - uses the same instance
String s = "bikini";
```

### Use Static Factory Methods

```java
// BAD
Boolean b = new Boolean("true"); // Deprecated in Java 9

// GOOD
Boolean b = Boolean.valueOf("true"); // Reuses TRUE/FALSE instances
```

### Prefer Primitives to Boxed Primitives

```java
// BAD - unintentional autoboxing
Long sum = 0L;
for (long i = 0; i <= Integer.MAX_VALUE; i++) {
    sum += i; // Autoboxing on every iteration!
}

// GOOD
long sum = 0L;
for (long i = 0; i <= Integer.MAX_VALUE; i++) {
    sum += i; // No autoboxing
}
```

### Expensive Objects: Cache and Reuse

```java
// BAD - creates new Pattern every time
static boolean isRomanNumeral(String s) {
    return s.matches("^(?=.)M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})$");
}

// GOOD - compile once, reuse
public class RomanNumerals {
    private static final Pattern ROMAN = Pattern.compile(
        "^(?=.)M*(C[MD]|D?C{0,3})(X[CL]|L?X{0,3})(I[XV]|V?I{0,3})$");

    static boolean isRomanNumeral(String s) {
        return ROMAN.matcher(s).matches();
    }
}
```

---

## Item 7: Eliminate obsolete object references

### Memory Leaks in Custom Data Structures

```java
public class Stack {
    private Object[] elements;
    private int size = 0;
    private static final int DEFAULT_INITIAL_CAPACITY = 16;

    public Stack() {
        elements = new Object[DEFAULT_INITIAL_CAPACITY];
    }

    public void push(Object e) {
        ensureCapacity();
        elements[size++] = e;
    }

    public Object pop() {
        if (size == 0)
            throw new EmptyStackException();
        Object result = elements[--size];
        elements[size] = null; // Eliminate obsolete reference!
        return result;
    }

    private void ensureCapacity() {
        if (elements.length == size)
            elements = Arrays.copyOf(elements, 2 * size + 1);
    }
}
```

### When to Null Out References
- **Do** null out references when you are "managing memory manually" (e.g., custom data structures)
- **Don't** null out references routinely — let the garbage collector do its job

### Other Sources of Memory Leaks
1. **Caches** — use `WeakHashMap` or scheduled cleanup
2. **Listeners and callbacks** — deregister when no longer needed

---

## Item 8: Avoid finalizers and cleaners

### Why Finalizers Are Dangerous

- Unpredictable when they'll run
- No guarantee they'll run at all
- Severe performance penalty
- Can cause security issues

### What to Do Instead

```java
// Provide explicit termination method
try {
    // Use the resource
} finally {
    resource.close(); // Explicit cleanup
}
```

### Try-with-Resources (Item 9)

```java
try (BufferedReader br = new BufferedReader(new FileReader(path))) {
    return br.readLine();
}
```

### Valid Uses of Finalizers/Cleaners (Rare)
1. Safety net if explicit termination is forgotten
2. Objects with native peers

---

## Item 9: Always use try-with-resources in preference to try-finally

### try-finally (Verbose and Error-Prone)

```java
// Ugly when using multiple resources!
static String firstLineOfFile(String path) throws IOException {
    BufferedReader br = new BufferedReader(new FileReader(path));
    try {
        return br.readLine();
    } finally {
        br.close();
    }
}
```

### try-with-resources (Clean and Correct)

```java
static String firstLineOfFile(String path) throws IOException {
    try (BufferedReader br = new BufferedReader(new FileReader(path))) {
        return br.readLine();
    }
}
```

### Multiple Resources

```java
try (InputStream in = new FileInputStream(src);
     OutputStream out = new FileOutputStream(dst)) {
    byte[] buf = new byte[BUFFER_SIZE];
    int n;
    while ((n = in.read(buf)) >= 0)
        out.write(buf, 0, n);
}
```

### Key Benefits
- Shorter and cleaner code
- Better exception handling (suppressed exceptions preserved)
- Works with any `AutoCloseable` resource
