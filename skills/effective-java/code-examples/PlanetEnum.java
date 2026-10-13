package effectivejava.item34;

/**
 * Item 34: Use enums instead of int constants
 * Item 35: Use instance fields instead of ordinals
 */
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

    public static void main(String[] args) {
        double earthWeight = 185; // lbs
        double mass = earthWeight / EARTH.surfaceGravity();
        for (Planet p : Planet.values())
            System.out.printf("Weight on %s is %.2f lbs%n",
                p, p.surfaceWeight(mass));
    }
}
