package effectivejava.item78_81;

import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/**
 * Item 78: Synchronize access to shared mutable data
 * Item 79: Avoid excessive synchronization
 * Item 80: Prefer executors, tasks, and streams to threads
 * Item 81: Prefer ConcurrentHashMap to Collections.synchronizedMap
 */
public class ConcurrencyExamples {

    // Item 78: Use volatile for simple reads/writes
    private static volatile boolean stopRequested = false;

    // Item 78: Use AtomicLong for compound actions
    private static final AtomicLong nextSerialNum = new AtomicLong();

    public static long generateSerialNumber() {
        return nextSerialNum.getAndIncrement();
    }

    // Item 80: Executor framework
    public static void executorExample() {
        ExecutorService executor = Executors.newFixedThreadPool(4);

        Future<Integer> future = executor.submit(() -> {
            TimeUnit.SECONDS.sleep(1);
            return 42;
        });

        try {
            Integer result = future.get();
            System.out.println("Result: " + result);
        } catch (Exception e) {
            e.printStackTrace();
        }

        executor.shutdown();
    }

    // Item 81: ConcurrentHashMap
    public static void concurrentMapExample() {
        ConcurrentHashMap<String, Long> map = new ConcurrentHashMap<>();
        map.put("key1", 1L);
        map.merge("key1", 1L, Long::sum); // Atomic merge operation
        System.out.println("Value: " + map.get("key1"));
    }

    public static void main(String[] args) throws InterruptedException {
        // Volatile example
        Thread backgroundThread = new Thread(() -> {
            int i = 0;
            while (!stopRequested)
                i++;
            System.out.println("Stopped at: " + i);
        });
        backgroundThread.start();

        TimeUnit.MILLISECONDS.sleep(100);
        stopRequested = true;
        backgroundThread.join();

        // Serial number generation
        System.out.println("Serial numbers: " + generateSerialNumber() + ", " + generateSerialNumber());

        // Executor example
        executorExample();

        // ConcurrentMap example
        concurrentMapExample();
    }
}
