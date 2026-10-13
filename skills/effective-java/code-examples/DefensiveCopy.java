package effectivejava.item50;

import java.util.Date;

/**
 * Item 50: Make defensive copies when needed
 * 
 * You must program defensively, with the assumption that clients of your class
 * will do their best to destroy its invariants.
 */
public final class Period {
    private final Date start;
    private final Date end;

    /**
     * @param start the beginning of the period
     * @param end the end of the period; must not precede start
     * @throws IllegalArgumentException if start is after end
     * @throws NullPointerException if start or end is null
     */
    public Period(Date start, Date end) {
        // Defensive copies BEFORE validation (protects against TOCTOU attacks)
        this.start = new Date(start.getTime());
        this.end = new Date(end.getTime());

        if (this.start.compareTo(this.end) > 0)
            throw new IllegalArgumentException(this.start + " after " + this.end);
    }

    public Date start() {
        return new Date(start.getTime()); // Defensive copy
    }

    public Date end() {
        return new Date(end.getTime()); // Defensive copy
    }

    @Override
    public String toString() {
        return start + " - " + end;
    }

    public static void main(String[] args) {
        Date start = new Date();
        Date end = new Date(start.getTime() + 100000);
        Period p = new Period(start, end);

        // Try to mutate internals
        start.setTime(start.getTime() - 1000000); // Won't affect p!
        System.out.println("Period: " + p);

        // Try to mutate via accessor
        p.end().setTime(p.start().getTime() - 1); // Won't affect p!
        System.out.println("Period after attempted mutation: " + p);
    }
}
