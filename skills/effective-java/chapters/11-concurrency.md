# Chapter 11: Concurrency (Items 78–84)

---

## Item 78: Synchronize access to shared mutable data

### The Problem

```java
// BROKEN - unsynchronized access
private static boolean stopRequested;

public static void main(String[] args) throws InterruptedException {
    Thread backgroundThread = new Thread(() -> {
        int i = 0;
        while (!stopRequested)
            i++;
    });
    backgroundThread.start();

    TimeUnit.SECONDS.sleep(1);
    stopRequested = true; // May never be seen!
}
```

### The Fix: Synchronization

```java
// Properly synchronized
private static boolean stopRequested;

private static synchronized void requestStop() {
    stopRequested = true;
}

private static synchronized boolean stopRequested() {
    return stopRequested;
}
```

### Better Fix: volatile

```java
private static volatile boolean stopRequested;
```

### But volatile is NOT enough for compound actions!

```java
// BROKEN - read-modify-write is not atomic!
private static volatile int nextSerialNumber = 0;

public static int generateSerialNumber() {
    return nextSerialNumber++; // NOT atomic!
}

// FIXED - use AtomicLong
private static final AtomicLong nextSerialNum = new AtomicLong();

public static long generateSerialNumber() {
    return nextSerialNum.getAndIncrement();
}
```

### Key Rules
- Synchronization is required for reliable communication between threads
- Synchronization ensures that each thread sees the most up-to-date value
- `volatile` is sufficient only for simple reads/writes (not compound actions)
- Prefer `java.util.concurrent.atomic` for lock-free thread-safe programming

---

## Item 79: Avoid excessive synchronization

### Don't Call Alien Methods from Synchronized Blocks

```java
// DANGEROUS - calling alien method while holding lock
public class ObservableSet<E> extends ForwardingSet<E> {
    public void addObserver(SetObserver<E> observer) {
        synchronized(observers) {
            observers.add(observer);
        }
    }

    private void notifyElementAdded(E element) {
        synchronized(observers) {
            for (SetObserver<E> observer : observers)
                observer.added(this, element); // Alien method!
        }
    }
}
```

### The Fix: Copy the Collection

```java
private void notifyElementAdded(E element) {
    List<SetObserver<E>> snapshot = null;
    synchronized(observers) {
        snapshot = new ArrayList<>(observers);
    }
    for (SetObserver<E> observer : snapshot)
        observer.added(this, element);
}
```

### Even Better: Use Concurrent Collections

```java
private final List<SetObserver<E>> observers =
    new CopyOnWriteArrayList<>();

public void addObserver(SetObserver<E> observer) {
    observers.add(observer);
}

private void notifyElementAdded(E element) {
    for (SetObserver<E> observer : observers)
        observer.added(this, element);
}
```

### Key Rules
- Never call overridable methods from synchronized regions
- Keep synchronized blocks as small as possible
- Consider `CopyOnWriteArrayList` for observer lists
- Consider `ConcurrentHashMap` for maps

---

## Item 80: Prefer executors, tasks, and streams to threads

### The Old Way

```java
// Creating threads directly - bad!
Thread thread = new Thread(task);
thread.start();
```

### The Executor Framework

```java
// Single thread executor
ExecutorService executor = Executors.newSingleThreadExecutor();

// Submit tasks
executor.execute(runnable);
Future<Integer> future = executor.submit(callable);

// Shutdown
executor.shutdown();
```

### Types of Executors

```java
Executors.newCachedThreadPool();       // Good for short-lived tasks
Executors.newFixedThreadPool(n);       // Fixed number of threads
Executors.newSingleThreadExecutor();   // Sequential execution
Executors.newScheduledThreadPool(n);     // Scheduled tasks
Executors.newWorkStealingPool();       // Java 8+ - good for parallelism
```

### Prefer CompletableFuture for Complex Workflows

```java
CompletableFuture.supplyAsync(() -> fetchPrice(productId))
    .thenApply(price -> applyDiscount(price))
    .thenAccept(discountedPrice -> displayPrice(discountedPrice));
```

---

## Item 81: Prefer ConcurrentHashMap to Collections.synchronizedMap

```java
// BAD - coarse-grained synchronization
Map<K, V> syncMap = Collections.synchronizedMap(new HashMap<>());

// GOOD - fine-grained lock striping
Map<K, V> concurrentMap = new ConcurrentHashMap<>();
```

### ConcurrentHashMap Features
- Fine-grained locking (lock striping)
- `putIfAbsent`, `compute`, `merge` atomic operations
- `ConcurrentHashMap` is faster than `HashMap` + synchronization

### Concurrent Collections

| Collection | Use Instead Of |
|------------|----------------|
| `ConcurrentHashMap` | `Collections.synchronizedMap` |
| `CopyOnWriteArrayList` | `Collections.synchronizedList` |
| `CopyOnWriteArraySet` | `Collections.synchronizedSet` |
| `ConcurrentLinkedQueue` | `Collections.synchronizedQueue` |
| `BlockingQueue` | Hand-rolled producer-consumer |

---

## Item 82: Document thread safety

### Levels of Thread Safety

```java
/**
 * This class is thread-safe.
 * Multiple threads can safely access it concurrently.
 */
public class ThreadSafeClass { ... }

/**
 * This class is immutable and therefore thread-safe.
 */
public final class ImmutableClass { ... }

/**
 * This class is NOT thread-safe.
 * External synchronization is required for concurrent access.
 */
public class NotThreadSafeClass { ... }
```

### Lock Objects

```java
/**
 * The lock object for synchronizing access to this instance.
 * This field is final and therefore safe to publish.
 */
private final Object lock = new Object();
```

---

## Item 83: Use lazy initialization judiciously

### Lazy Initialization Holder Class Idiom

```java
// Thread-safe lazy initialization without synchronization on access
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

### Double-Check Idiom (for instance fields)

```java
private volatile FieldType field;

private FieldType getField() {
    FieldType result = field;
    if (result == null) { // First check (no locking)
        synchronized(this) {
            result = field;
            if (result == null) // Second check (with locking)
                field = result = new FieldType();
        }
    }
    return result;
}
```

### Key Rules
- Don't use lazy initialization unless you need to
- For static fields, use the holder class idiom
- For instance fields, use double-check idiom
- For primitives, use `AtomicReference` or `AtomicLong`

---

## Item 84: Don't depend on the thread scheduler

### Rules
- Don't write code that depends on thread scheduling for correctness
- Thread scheduler varies across platforms
- Thread priorities are among the least portable features of Java
- Use `Thread.yield()` sparingly, if at all
- Use thread pools instead of managing threads directly
