# Chapter 4: Classes and Interfaces (Items 15–25)

---

## Item 15: Minimize the accessibility of classes and members

### Accessibility Levels

| Modifier | Access |
|----------|--------|
| `private` | Only within the top-level class |
| *package-private* (default) | Any class in the same package |
| `protected` | Subclasses + same package |
| `public` | Anywhere |

### Rules
- Make each class/member as **inaccessible as possible**
- Instance fields of public classes should **rarely** be public
- Public mutable fields are **not thread-safe**
- Never have `public static final` array fields (or accessors returning them)

```java
// BROKEN - mutable public array
public static final Thing[] VALUES = { ... };

// FIXED - private array, public immutable list
private static final Thing[] PRIVATE_VALUES = { ... };
public static final List<Thing> VALUES =
    Collections.unmodifiableList(Arrays.asList(PRIVATE_VALUES));

// ALTERNATIVE - return a copy
private static final Thing[] PRIVATE_VALUES = { ... };
public static final Thing[] values() {
    return PRIVATE_VALUES.clone();
}
```

---

## Item 16: In public classes, use accessor methods, not public fields

```java
// BAD - public fields
class Point {
    public double x;
    public double y;
}

// GOOD - accessor methods
class Point {
    private double x;
    private double y;

    public Point(double x, double y) {
        this.x = x;
        this.y = y;
    }

    public double getX() { return x; }
    public double getY() { return y; }
    public void setX(double x) { this.x = x; }
    public void setY(double y) { this.y = y; }
}
```

- If a class is package-private or private nested, exposing fields is fine
- Public classes must maintain encapsulation

---

## Item 17: Minimize mutability

### The 5 Rules for Immutable Classes

1. Don't provide mutators (setters)
2. Ensure the class can't be extended (`final` or private constructor)
3. Make all fields `final`
4. Make all fields `private`
5. Ensure exclusive access to any mutable components (defensive copies)

```java
public final class Complex {
    private final double re;
    private final double im;

    public Complex(double re, double im) {
        this.re = re;
        this.im = im;
    }

    // No setters!
    public double realPart() { return re; }
    public double imaginaryPart() { return im; }

    public Complex plus(Complex c) {
        return new Complex(re + c.re, im + c.im);
    }

    public Complex minus(Complex c) {
        return new Complex(re - c.re, im - c.im);
    }

    // ... times, dividedBy

    @Override
    public boolean equals(Object o) { ... }

    @Override
    public int hashCode() { ... }

    @Override
    public String toString() { return "(" + re + " + " + im + "i)"; }
}
```

### Advantages of Immutability
- **Simple:** Only one state — the one it was created in
- **Thread-safe:** No synchronization needed
- **Can be shared freely:** No defensive copies needed
- **Great building blocks:** Perfect for map keys, set elements
- **Failure atomicity:** Free for immutable objects

### Disadvantage
- Requires a separate object for each distinct value (can be costly for large objects)

---

## Item 18: Favor composition over inheritance

### The Problem with Inheritance

```java
// BROKEN - Inappropriate use of inheritance!
public class InstrumentedHashSet<E> extends HashSet<E> {
    private int addCount = 0;

    @Override
    public boolean add(E e) {
        addCount++;
        return super.add(e);
    }

    @Override
    public boolean addAll(Collection<? extends E> c) {
        addCount += c.size();
        return super.addAll(c);
    }
}

// HashSet's addAll calls add() internally!
// So addCount gets incremented twice for each element
```

### The Composition Solution

```java
public class InstrumentedSet<E> extends ForwardingSet<E> {
    private int addCount = 0;

    public InstrumentedSet(Set<E> s) {
        super(s);
    }

    @Override
    public boolean add(E e) {
        addCount++;
        return super.add(e);
    }

    @Override
    public boolean addAll(Collection<? extends E> c) {
        addCount += c.size();
        return super.addAll(c);
    }

    public int getAddCount() {
        return addCount;
    }
}

// Reusable forwarding class
public class ForwardingSet<E> implements Set<E> {
    private final Set<E> s;
    public ForwardingSet(Set<E> s) { this.s = s; }

    public void clear() { s.clear(); }
    public boolean contains(Object o) { return s.contains(o); }
    public boolean isEmpty() { return s.isEmpty(); }
    public int size() { return s.size(); }
    public Iterator<E> iterator() { return s.iterator(); }
    public boolean add(E e) { return s.add(e); }
    public boolean remove(Object o) { return s.remove(o); }
    public boolean containsAll(Collection<?> c) { return s.containsAll(c); }
    public boolean addAll(Collection<? extends E> c) { return s.addAll(c); }
    public boolean removeAll(Collection<?> c) { return s.removeAll(c); }
    public boolean retainAll(Collection<?> c) { return s.retainAll(c); }
    public Object[] toArray() { return s.toArray(); }
    public <T> T[] toArray(T[] a) { return s.toArray(a); }
    @Override
    public boolean equals(Object o) { return s.equals(o); }
    @Override
    public int hashCode() { return s.hashCode(); }
    @Override
    public String toString() { return s.toString(); }
}
```

### Key Points
- Inheritance violates encapsulation (superclass internals can change)
- Composition = "has-a" instead of "is-a"
- Known as the **Decorator pattern**
- Disadvantage: Not suited for callback frameworks (SELF problem)

---

## Item 19: Design and document for inheritance or else prohibit it

### If You Design for Inheritance

1. **Document self-use of overridable methods**
2. **Provide hooks** (protected methods)
3. **Test by writing subclasses** (~3) before releasing
4. **Constructors must not invoke overridable methods**

```java
public class Super {
    public Super() {
        overrideMe(); // DANGEROUS!
    }
    public void overrideMe() {}
}

public class Sub extends Super {
    private final Instant instant;

    Sub() {
        instant = Instant.now();
    }

    @Override
    public void overrideMe() {
        System.out.println(instant); // instant is null here!
    }
}
```

### Prohibiting Inheritance

```java
// Make class final
public final class UtilityClass { ... }

// Or make constructor private
public class UtilityClass {
    private UtilityClass() { throw new AssertionError(); }
}
```

---

## Item 20: Prefer interfaces to abstract classes

### Why Interfaces Are Better
- Existing classes can be easily retrofitted to implement a new interface
- Interfaces are ideal for defining mixins
- Interfaces allow construction of nonhierarchical type frameworks

```java
// Singer and Songwriter are both interfaces
public interface Singer {
    AudioClip sing(Song s);
}

public interface Songwriter {
    Song compose(int chartPosition);
}

// Can implement both!
public interface SingerSongwriter extends Singer, Songwriter {
    AudioClip strum();
    void actSensitive();
}
```

### Skeletal Implementation Pattern

```java
// Interface
public interface Collection<E> { ... }

// Abstract skeletal implementation
public abstract class AbstractCollection<E> implements Collection<E> { ... }

// Concrete implementation
public class ArrayList<E> extends AbstractCollection<E> implements List<E> { ... }
```

---

## Item 21: Design interfaces for posterity

- Once an interface is released and widely implemented, it's nearly impossible to change
- Java 8+ default methods help but are not a panacea
- Document the thread-safety and behavioral contracts

---

## Item 22: Use interfaces only to define types

```java
// BAD - Constant interface antipattern
public interface PhysicalConstants {
    static final double AVOGADROS_NUMBER = 6.022_140_857e23;
    static final double BOLTZMANN_CONSTANT = 1.380_648_52e-23;
    static final double ELECTRON_MASS = 9.109_383_56e-31;
}

// GOOD - Utility class with static imports
public class PhysicalConstants {
    private PhysicalConstants() {} // Prevent instantiation

    public static final double AVOGADROS_NUMBER = 6.022_140_857e23;
    public static final double BOLTZMANN_CONSTANT = 1.380_648_52e-23;
    public static final double ELECTRON_MASS = 9.109_383_56e-31;
}

// Usage
import static com.example.PhysicalConstants.*;
```

---

## Item 23: Prefer class hierarchies to tagged classes

### Tagged Class (Bad)

```java
class Figure {
    enum Shape { RECTANGLE, CIRCLE };

    final Shape shape;

    // Rectangle fields
    double length;
    double width;

    // Circle fields
    double radius;

    Figure(double radius) {
        shape = Shape.CIRCLE;
        this.radius = radius;
    }

    Figure(double length, double width) {
        shape = Shape.RECTANGLE;
        this.length = length;
        this.width = width;
    }

    double area() {
        switch (shape) {
            case RECTANGLE: return length * width;
            case CIRCLE: return Math.PI * (radius * radius);
            default: throw new AssertionError(shape);
        }
    }
}
```

### Class Hierarchy (Good)

```java
abstract class Figure {
    abstract double area();
}

class Circle extends Figure {
    final double radius;

    Circle(double radius) { this.radius = radius; }

    @Override
    double area() { return Math.PI * (radius * radius); }
}

class Rectangle extends Figure {
    final double length;
    final double width;

    Rectangle(double length, double width) {
        this.length = length;
        this.width = width;
    }

    @Override
    double area() { return length * width; }
}
```

---

## Item 24: Favor static member classes over nonstatic

### Static Member Class

```java
public class Calculator {
    public enum Operation { PLUS, MINUS, TIMES, DIVIDE }
    ...
}
```

### Nonstatic Member Class (Inner Class)

```java
public class MySet<E> extends AbstractSet<E> {
    // Nonstatic member class - each instance is bound to enclosing instance
    private class MyIterator implements Iterator<E> {
        // Can access MySet's fields directly
    }
}
```

### Key Rule

> If a member class does not require access to an enclosing instance, **always** make it `static`.

- Nonstatic member classes hold an implicit reference to the enclosing instance
- This costs time, space, and can cause memory leaks
- Anonymous classes: keep them short (<10 lines)

---

## Item 25: Limit source files to a single top-level class

```java
// NEVER DO THIS - multiple top-level classes in one file
class Utensil {
    static final String NAME = "pan";
}

class Dessert {
    static final String NAME = "cake";
}
```

- Can provide multiple definitions (if same class exists in another file)
- Behavior depends on order files are passed to compiler!
- **Never** put multiple top-level classes/interfaces in one source file
