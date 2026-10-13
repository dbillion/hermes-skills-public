package effectivejava.item3;

/**
 * Item 3: Enforce the singleton property with a private constructor or an enum type
 * 
 * This approach is functionally equivalent to the public field approach,
 * except that it is more concise, provides the serialization machinery for free,
 * and provides an ironclad guarantee against multiple instantiation, even in
 * the face of sophisticated serialization or reflection attacks.
 */
public enum Elvis {
    INSTANCE;

    public void leaveTheBuilding() {
        System.out.println("Elvis has left the building!");
    }

    public static void main(String[] args) {
        Elvis.INSTANCE.leaveTheBuilding();
    }
}
