# Effective Java — Common Patterns Quick Reference

---

## 1. Builder Pattern

```java
public class Pizza {
    public enum Topping { HAM, MUSHROOM, ONION, PEPPER, SAUSAGE }
    private final Set<Topping> toppings;

    public static class Builder {
        private final EnumSet<Topping> toppings = EnumSet.noneOf(Topping.class);

        public Builder addTopping(Topping topping) {
            toppings.add(Objects.requireNonNull(topping));
            return this;
        }

        public Pizza build() {
            return new Pizza(this);
        }
    }

    private Pizza(Builder builder) {
        toppings = builder.toppings.clone();
    }
}
```

---

## 2. Singleton (Enum)

```java
public enum Elvis {
    INSTANCE;
    private final String[] favoriteSongs = { "Hound Dog", "Heartbreak Hotel" };
    public void leaveTheBuilding() { ... }
}
```

---

## 3. Utility Class

```java
public final class UtilityClass {
    private UtilityClass() {
        throw new AssertionError("Cannot instantiate utility class");
    }
    // static methods...
}
```

---

## 4. Service Provider Framework

```java
// Service interface
public interface Service { ... }

// Provider interface
public interface Provider {
    Service newService();
}

// Noninstantiable registration class
public class Services {
    private Services() {} // Noninstantiable
    private static final Map<String, Provider> providers = new ConcurrentHashMap<>();
    private static final String DEFAULT_PROVIDER_NAME = "<def>";

    public static void registerDefaultProvider(Provider p) {
        registerProvider(DEFAULT_PROVIDER_NAME, p);
    }

    public static void registerProvider(String name, Provider p) {
        providers.put(name, p);
    }

    public static Service newInstance() {
        return newInstance(DEFAULT_PROVIDER_NAME);
    }

    public static Service newInstance(String name) {
        Provider p = providers.get(name);
        if (p == null)
            throw new IllegalArgumentException("No provider registered with name: " + name);
        return p.newService();
    }
}
```

---

## 5. Typesafe Heterogeneous Container

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
```

---

## 6. Lazy Initialization Holder Class

```java
public class FieldType {
    private FieldType() {}

    private static class FieldHolder {
        static final FieldType field = new FieldType();
    }

    public static FieldType getInstance() {
        return FieldHolder.field;
    }
}
```

---

## 7. Double-Check Idiom

```java
private volatile FieldType field;

private FieldType getField() {
    FieldType result = field;
    if (result == null) {
        synchronized(this) {
            result = field;
            if (result == null)
                field = result = new FieldType();
        }
    }
    return result;
}
```

---

## 8. Serialization Proxy Pattern

```java
private static class SerializationProxy implements Serializable {
    private final Date start;
    private final Date end;

    SerializationProxy(Period p) {
        this.start = p.start;
        this.end = p.end;
    }

    private Object readResolve() {
        return new Period(start, end);
    }
}

private Object writeReplace() {
    return new SerializationProxy(this);
}

private void readObject(ObjectInputStream stream) throws InvalidObjectException {
    throw new InvalidObjectException("Proxy required");
}
```

---

## 9. Forwarding Class (Decorator Pattern)

```java
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
    @Override public boolean equals(Object o) { return s.equals(o); }
    @Override public int hashCode() { return s.hashCode(); }
    @Override public String toString() { return s.toString(); }
}
```

---

## 10. Defensive Copy in Constructor

```java
public Period(Date start, Date end) {
    // Defensive copies BEFORE validation
    this.start = new Date(start.getTime());
    this.end = new Date(end.getTime());

    if (this.start.compareTo(this.end) > 0)
        throw new IllegalArgumentException(this.start + " after " + this.end);
}
```
