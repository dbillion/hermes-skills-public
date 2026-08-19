# Chapter 12: Serialization (Items 85–90)

---

## Item 85: Prefer alternatives to Java serialization

### The Dangers of Java Serialization
- **Security vulnerabilities** — deserialization of untrusted data is inherently dangerous
- **Remote Code Execution (RCE)** — many exploits via serialization
- **Brittleness** — serialized form becomes part of the API
- **Performance** — slow and space-inefficient

### Recommended Alternatives

| Format | Use Case |
|--------|----------|
| **JSON** | Web APIs, configuration, human-readable |
| **Protocol Buffers (protobuf)** | Cross-language, high performance |
| **FlatBuffers** | Zero-copy deserialization |
| **MessagePack** | Binary JSON |
| **Kryo** | Java-specific, fast |
| **Avro** | Big data, schema evolution |

### Example: JSON with Jackson

```java
// Serialize
ObjectMapper mapper = new ObjectMapper();
String json = mapper.writeValueAsString(myObject);

// Deserialize
MyObject obj = mapper.readValue(json, MyObject.class);
```

### If You Must Use Serialization
- Never deserialize untrusted data
- Use serialization filtering (Java 9+ `ObjectInputFilter`)
- Prefer whitelisting over blacklisting

---

## Item 86: Implement Serializable with great caution

### Costs of Implementing Serializable
- **Released forever** — serialized form becomes part of the API
- **Security holes** — deserialization attacks
- **Testing burden** — must test compatibility across versions
- **Performance** — slower than custom formats
- **Increased responsibility** — must ensure `readObject` invariants

### Rules
- Don't implement `Serializable` lightly
- Consider using a custom serialized form
- Consider serialization proxies
- Inner classes should not implement `Serializable`

---

## Item 87: Consider using a custom serialized form

### Default Serialized Form
- Captures all non-transient, non-static fields
- May expose implementation details
- May be bloated

### Custom Serialized Form

```java
public final class StringList implements Serializable {
    private transient int size = 0;
    private transient Entry head = null;

    // No longer serializable!
    private static class Entry {
        String data;
        Entry next;
        Entry previous;
    }

    // Custom serialization
    private void writeObject(ObjectOutputStream s) throws IOException {
        s.defaultWriteObject();
        s.writeInt(size);

        // Write out all elements in proper sequence
        for (Entry e = head; e != null; e = e.next)
            s.writeObject(e.data);
    }

    private void readObject(ObjectInputStream s)
            throws IOException, ClassNotFoundException {
        s.defaultReadObject();
        int numElements = s.readInt();

        // Read in all elements and insert them in list
        for (int i = 0; i < numElements; i++)
            add((String) s.readObject());
    }

    // ... add, remove, etc.
}
```

### Rules
- Declare fields you don't want serialized as `transient`
- Write a `readObject` that performs defensive copies
- Write a `readObject` that checks invariants
- Write a `readObject` that makes defensive copies of mutable transient fields

---

## Item 88: Write readObject methods defensively

### The Bogus Byte-Stream Attack

```java
// A hostile stream could create a mutable Date!
public final class Period {
    private final Date start;
    private final Date end;

    private void readObject(ObjectInputStream s)
            throws IOException, ClassNotFoundException {
        s.defaultReadObject();

        // Defensive copies - MUST be done!
        start = new Date(start.getTime());
        end = new Date(end.getTime());

        // Validate invariants
        if (start.compareTo(end) > 0)
            throw new InvalidObjectException(start + " after " + end);
    }
}
```

### Rules for Defensive readObject
1. Call `defaultReadObject()` first
2. Make defensive copies of all mutable fields
3. Validate invariants
4. If validation fails, throw `InvalidObjectException`

---

## Item 89: For instance control, prefer readResolve to readObject

### The Singleton Problem

```java
public class Elvis implements Serializable {
    public static final Elvis INSTANCE = new Elvis();
    private Elvis() { ... }

    // Without readResolve, deserialization creates a new instance!

    private Object readResolve() {
        return INSTANCE; // Return the canonical instance
    }
}
```

### readResolve for Immutable Serializable Classes

```java
private Object readResolve() {
    return new Period(start, end); // Use public constructor
}
```

---

## Item 90: Consider serialization proxies instead of serialized instances

### The Serialization Proxy Pattern

```java
public final class Period implements Serializable {
    private final Date start;
    private final Date end;

    public Period(Date start, Date end) {
        this.start = new Date(start.getTime());
        this.end = new Date(end.getTime());
        if (this.start.compareTo(this.end) > 0)
            throw new IllegalArgumentException(start + " after " + end);
    }

    // Serialization proxy
    private static class SerializationProxy implements Serializable {
        private final Date start;
        private final Date end;

        SerializationProxy(Period p) {
            this.start = p.start;
            this.end = p.end;
        }

        private Object readResolve() {
            return new Period(start, end); // Uses public constructor
        }

        private static final long serialVersionUID = ...;
    }

    // Write proxy instead of real object
    private Object writeReplace() {
        return new SerializationProxy(this);
    }

    // Prevent normal deserialization
    private void readObject(ObjectInputStream stream)
            throws InvalidObjectException {
        throw new InvalidObjectException("Proxy required");
    }
}
```

### Benefits
- Greatly reduces the scope of attack surface
- Doesn't require defensive copying in `readObject`
- Provides perfect encapsulation
- Can change internal representation without affecting serialized form

### When to Use
- When you must use Java serialization
- For classes with complex invariants
- For classes that need instance control (singletons, etc.)
