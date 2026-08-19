# Chapter 9: General Programming (Items 57–68)

---

## Item 57: Minimize the scope of local variables

### Techniques
1. **Declare where first used** — not at the top of the method
2. **Nearly every declaration should contain an initializer**
3. **Prefer for-loops to while-loops**
4. **Keep methods small and focused**

```java
// BAD - declared before use, no initializer
String s;
... // 50 lines later
s = someMethod();

// GOOD - declared and initialized at first use
String s = someMethod();

// BAD - while loop with variable outside scope
Iterator<Element> i = c.iterator();
while (i.hasNext()) {
    doSomething(i.next());
}
Iterator<Element> i2 = c2.iterator(); // Can accidentally use i instead of i2
while (i.hasNext()) { // BUG!
    doSomethingElse(i2.next());
}

// GOOD - for loop limits scope
for (Iterator<Element> i = c.iterator(); i.hasNext(); ) {
    doSomething(i.next());
}
for (Iterator<Element> i = c2.iterator(); i.hasNext(); ) {
    doSomethingElse(i.next());
}
```

---

## Item 58: Prefer for-each loops to traditional for-loops

```java
// Traditional for-loop - error-prone
for (Iterator<Element> i = c.iterator(); i.hasNext(); ) {
    Element e = i.next();
    ...
}

// for-each - clean and safe
for (Element e : c) {
    ...
}
```

### When You CAN'T Use for-each
1. **Destructive filtering** — use `Iterator.remove()`
2. **Transforming** — use `Iterator` or array index
3. **Parallel iteration** — use explicit iterators

---

## Item 59: Know and use the libraries

### Benefits
- Leverage expert knowledge
- Don't reinvent the wheel
- Performance improves over time

### Essential Packages
- `java.lang` — fundamentals (auto-imported)
- `java.util` — collections, dates, random
- `java.io` — I/O streams
- `java.util.concurrent` — concurrency utilities

### Modern Java Features to Know
- `ThreadLocalRandom` — preferred random number generator
- `java.time` — modern date/time API (Java 8+)

```java
// BAD - old way
Random rnd = new Random();
int random = rnd.nextInt();

// GOOD - modern way
int random = ThreadLocalRandom.current().nextInt();
```

---

## Item 60: Avoid float and double if exact answers are required

### The Problem

```java
// BAD - floating point arithmetic
System.out.println(1.03 - 0.42); // 0.6100000000000001
System.out.println(1.00 - 9 * 0.10); // 0.09999999999999998
```

### Solutions

```java
// Use BigDecimal for monetary calculations
BigDecimal total = new BigDecimal("1.00");
BigDecimal item = new BigDecimal("0.10");
total = total.subtract(item.multiply(BigDecimal.valueOf(9)));

// Or use int/long (cents)
int totalCents = 100;
int itemCents = 10;
int result = totalCents - 9 * itemCents; // 10 cents = $0.10
```

---

## Item 61: Prefer primitive types to boxed primitives

```java
// BAD - comparing boxed primitives with ==
Integer a = 127;
Integer b = 127;
System.out.println(a == b); // true (cached)

Integer c = 128;
Integer d = 128;
System.out.println(c == d); // false (different objects!)
```

### The NullPointerException Trap

```java
// BAD - auto-unboxing null
Integer i = null;
int j = i; // NullPointerException!
```

### Rules
- Use primitives wherever you have the choice
- Be careful with mixed-type operations (auto-boxing/unboxing)
- Use `==` on primitives, `equals()` on boxed types

---

## Item 62: Avoid strings where other types are more appropriate

```java
// BAD - using string to represent a compound key
String compoundKey = className + "#" + i.next();

// GOOD - use a dedicated class
public class Key {
    private final Class<?> clazz;
    private final Object arg;
    ...
}
```

### Don't Use Strings for Aggregate Types
- Use classes, enums, or dedicated types instead
- Strings are poor substitutes for enum types
- Strings are poor substitutes for aggregate types

---

## Item 63: Beware the performance of string concatenation

```java
// BAD - O(n²) time complexity!
String statement = "";
for (int i = 0; i < numItems(); i++)
    statement += lineForItem(i); // Creates new String each time!

// GOOD - O(n) time complexity
StringBuilder b = new StringBuilder(numItems() * LINE_WIDTH);
for (int i = 0; i < numItems(); i++)
    b.append(lineForItem(i));
String statement = b.toString();
```

---

## Item 64: Refer to objects by their interfaces

```java
// GOOD - interface as type
List<String> list = new ArrayList<>();
Set<String> set = new HashSet<>();

// BAD - concrete class as type
ArrayList<String> list = new ArrayList<>();
HashSet<String> set = new HashSet<>();
```

### Benefits
- Flexibility to change implementation
- Programs are more flexible
- If appropriate interface exists, use it for parameters, return values, variables, and fields

### Exceptions
- Value classes (String, BigInteger)
- Framework-specific classes (java.io)
- When additional methods are needed from concrete class

---

## Item 65: Prefer interfaces to reflection

### The Problems with Reflection
- Loses all compile-time type checking
- Code required to perform reflective access is clumsy
- Performance is worse
- Often requires runtime permissions that don't work under security managers

### The Solution
- Use reflection only for instantiation, then access via interface

```java
// Use reflection only to instantiate
Class<? extends Set<String>> cl = Class.forName(args[0]).asSubclass(Set.class);
Constructor<? extends Set<String>> cons = cl.getConstructor();
Set<String> s = cons.newInstance();

// Use normally via interface
s.addAll(Arrays.asList(args).subList(1, args.length));
```

---

## Item 66: Use native methods judiciously

### Reasons to Avoid
- Native languages are not safe (memory corruption)
- Less portable
- Harder to debug
- Can decrease performance (JNI overhead)
- Require "glue code" that's difficult to read and write

### When to Use
- Access platform-specific facilities (registry, file locks)
- Legacy code libraries
- Performance-critical code (rarely worth it)

---

## Item 67: Optimize judiciously

### Rules
1. **Don't optimize prematurely** — write good programs, not fast ones
2. **Don't optimize indiscriminately** — measure before and after
3. **Strive to write good programs rather than fast ones** — good design enables performance tuning

### Performance Tuning Tips
- Use a profiler to find the real bottlenecks
- Focus on architecture-level decisions (API design, data structures)
- Micro-optimizations are rarely worth it

---

## Item 68: Adhere to generally accepted naming conventions

### Package Names
- `com.companyname.project.component`
- All lowercase, no underscores

### Class/Interface Names
- `ClassName`, `InterfaceName`
- Nouns or noun phrases

### Method Names
- `methodName`, `toString`, `getXxx`, `setXxx`, `isXxx`
- Verbs or verb phrases

### Field Names
- `fieldName`
- Constants: `ALL_CAPS_WITH_UNDERSCORES`

### Local Variables
- Similar to field names but can be abbreviated

### Type Parameters
- `T` — arbitrary type
- `E` — element type (collections)
- `K`, `V` — key and value (maps)
- `X` — exception
- `R` — return type
