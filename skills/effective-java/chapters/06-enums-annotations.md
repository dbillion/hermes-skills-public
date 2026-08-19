# Chapter 6: Enums and Annotations (Items 34–41)

---

## Item 34: Use enums instead of int constants

### The Old Way (Bad)

```java
public static final int APPLE_FUJI = 0;
public static final int APPLE_PIPPIN = 1;
public static final int APPLE_GRANNY_SMITH = 2;

public static final int ORANGE_NAVEL = 0;
public static final int ORANGE_TEMPLE = 1;
public static final int ORANGE_BLOOD = 2;

// Can accidentally compare apples to oranges!
```

### The Enum Way (Good)

```java
public enum Apple { FUJI, PIPPIN, GRANNY_SMITH }
public enum Orange { NAVEL, TEMPLE, BLOOD }
```

### Enums with Data and Behavior

```java
public enum Planet {
    MERCURY(3.303e+23, 2.4397e6),
    VENUS(4.869e+24, 6.0518e6),
    EARTH(5.976e+24, 6.37814e6),
    MARS(6.421e+23, 3.3972e6),
    JUPITER(1.899e+27, 7.1492e7),
    SATURN(5.688e+26, 6.0268e7),
    URANUS(8.686e+25, 2.5559e7),
    NEPTUNE(1.024e+26, 2.4746e7);

    private final double mass;   // In kilograms
    private final double radius; // In meters

    Planet(double mass, double radius) {
        this.mass = mass;
        this.radius = radius;
    }

    public double mass() { return mass; }
    public double radius() { return radius; }

    public double surfaceGravity() {
        return G * mass / (radius * radius);
    }

    public double surfaceWeight(double mass) {
        return mass * surfaceGravity();
    }

    private static final double G = 6.67300E-11;
}
```

### Constant-Specific Method Implementations

```java
public enum Operation {
    PLUS("+") {
        public double apply(double x, double y) { return x + y; }
    },
    MINUS("-") {
        public double apply(double x, double y) { return x - y; }
    },
    TIMES("*") {
        public double apply(double x, double y) { return x * y; }
    },
    DIVIDE("/") {
        public double apply(double x, double y) { return x / y; }
    };

    private final String symbol;

    Operation(String symbol) { this.symbol = symbol; }

    @Override
    public String toString() { return symbol; }

    public abstract double apply(double x, double y);
}
```

### Strategy Enum Pattern

```java
enum PayrollDay {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY,
    SATURDAY(PayType.WEEKEND), SUNDAY(PayType.WEEKEND);

    private final PayType payType;

    PayrollDay(PayType payType) { this.payType = payType; }
    PayrollDay() { this(PayType.WEEKDAY); } // Default

    int pay(int minutesWorked, int payRate) {
        return payType.pay(minutesWorked, payRate);
    }

    // Strategy enum
    private enum PayType {
        WEEKDAY {
            int overtimePay(int mins, int payRate) {
                return mins <= MINS_PER_SHIFT ? 0 : (mins - MINS_PER_SHIFT) * payRate / 2;
            }
        },
        WEEKEND {
            int overtimePay(int mins, int payRate) {
                return mins * payRate / 2;
            }
        };

        abstract int overtimePay(int mins, int payRate);

        private static final int MINS_PER_SHIFT = 8 * 60;

        int pay(int minsWorked, int payRate) {
            int basePay = minsWorked * payRate;
            return basePay + overtimePay(minsWorked, payRate);
        }
    }
}
```

---

## Item 35: Use instance fields instead of ordinals

```java
// BAD - depends on order, fragile
public enum Ensemble {
    SOLO, DUET, TRIO, QUARTET, QUINTET,
    SEXTET, SEPTET, OCTET, NONET, DECTET;

    public int numberOfMusicians() { return ordinal() + 1; }
}

// GOOD - explicit, robust
public enum Ensemble {
    SOLO(1), DUET(2), TRIO(3), QUARTET(4), QUINTET(5),
    SEXTET(6), SEPTET(7), OCTET(8), NONET(9), DECTET(10),
    TRIPLE_QUARTET(12);

    private final int numberOfMusicians;

    Ensemble(int size) { this.numberOfMusicians = size; }

    public int numberOfMusicians() { return numberOfMusicians; }
}
```

---

## Item 36: Use EnumSet instead of bit fields

```java
// OLD WAY - bit fields
public static final int STYLE_BOLD = 1 << 0;      // 1
public static final int STYLE_ITALIC = 1 << 1;    // 2
public static final int STYLE_UNDERLINE = 1 << 2; // 4

public void applyStyles(int styles) { ... }

// NEW WAY - EnumSet
public enum Style { BOLD, ITALIC, UNDERLINE, STRIKETHROUGH }

public void applyStyles(Set<Style> styles) { ... }

// Usage
applyStyles(EnumSet.of(Style.BOLD, Style.ITALIC));
```

---

## Item 37: Use EnumMap instead of ordinal indexing

```java
// BAD - ordinal indexing
Set<Plant>[] plantsByLifeCycle = (Set<Plant>[]) new Set[Plant.LifeCycle.values().length];

// GOOD - EnumMap
Map<Plant.LifeCycle, Set<Plant>> plantsByLifeCycle =
    new EnumMap<>(Plant.LifeCycle.class);

for (Plant.LifeCycle lc : Plant.LifeCycle.values())
    plantsByLifeCycle.put(lc, new HashSet<>());

for (Plant p : garden)
    plantsByLifeCycle.get(p.lifeCycle).add(p);
```

---

## Item 38: Emulate extensible enums with interfaces

```java
public interface Operation {
    double apply(double x, double y);
}

public enum BasicOperation implements Operation {
    PLUS("+") { public double apply(double x, double y) { return x + y; } },
    MINUS("-") { public double apply(double x, double y) { return x - y; } },
    TIMES("*") { public double apply(double x, double y) { return x * y; } },
    DIVIDE("/") { public double apply(double x, double y) { return x / y; } };

    private final String symbol;
    BasicOperation(String symbol) { this.symbol = symbol; }
    @Override public String toString() { return symbol; }
}

// Extensible!
public enum ExtendedOperation implements Operation {
    EXP("^") { public double apply(double x, double y) { return Math.pow(x, y); } },
    REMAINDER("%") { public double apply(double x, double y) { return x % y; } };

    private final String symbol;
    ExtendedOperation(String symbol) { this.symbol = symbol; }
    @Override public String toString() { return symbol; }
}
```

---

## Item 39: Prefer annotations to naming patterns

### Old Way: Naming Patterns

```java
// JUnit 3 - must start with "test"
public class MyTest extends TestCase {
    public void testMethod1() { ... }
    public void testMethod2() { ... }
}
```

### New Way: Annotations

```java
// JUnit 4+ - uses @Test annotation
public class MyTest {
    @Test
    public void method1() { ... }

    @Test
    public void method2() { ... }
}
```

### Defining Custom Annotations

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Test {
    // Marker annotation - no elements
}
```

---

## Item 40: Consistently use the @Override annotation

```java
// Without @Override - typo goes unnoticed
public class Bigram {
    public boolean equals(Bigram b) {  // Overloads, doesn't override!
        return b.first == first && b.second == second;
    }
}

// With @Override - compile-time error catches the bug
@Override
public boolean equals(Bigram b) {  // ERROR: does not override!
    ...
}

// Correct
@Override
public boolean equals(Object o) { ... }
```

---

## Item 41: Use marker interfaces to define types

```java
// Marker interface - defines a type
public interface Serializable {
}

// Marker annotation - does NOT define a type
public @interface Serializable {
}
```

### When to Use What
- Use **marker interfaces** when you want the type system to enforce the contract
- Use **marker annotations** when you want to use reflection to process the marker
