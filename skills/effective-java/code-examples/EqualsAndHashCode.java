package effectivejava.item10_11;

import java.util.Objects;

/**
 * Item 10: Obey the general contract when overriding equals
 * Item 11: Always override hashCode when you override equals
 */
public final class PhoneNumber {
    private final short areaCode, prefix, lineNum;

    public PhoneNumber(int areaCode, int prefix, int lineNum) {
        this.areaCode = rangeCheck(areaCode, 999, "area code");
        this.prefix = rangeCheck(prefix, 999, "prefix");
        this.lineNum = rangeCheck(lineNum, 9999, "line num");
    }

    private static short rangeCheck(int val, int max, String arg) {
        if (val < 0 || val > max)
            throw new IllegalArgumentException(arg + ": " + val);
        return (short) val;
    }

    @Override
    public boolean equals(Object o) {
        if (o == this)
            return true;
        if (!(o instanceof PhoneNumber))
            return false;
        PhoneNumber pn = (PhoneNumber) o;
        return pn.lineNum == lineNum
            && pn.prefix == prefix
            && pn.areaCode == areaCode;
    }

    @Override
    public int hashCode() {
        int result = Short.hashCode(areaCode);
        result = 31 * result + Short.hashCode(prefix);
        result = 31 * result + Short.hashCode(lineNum);
        return result;
    }

    // Using Objects.hash (slower but cleaner)
    // @Override
    // public int hashCode() {
    //     return Objects.hash(lineNum, prefix, areaCode);
    // }

    @Override
    public String toString() {
        return String.format("(%03d) %03d-%04d", areaCode, prefix, lineNum);
    }

    public static void main(String[] args) {
        PhoneNumber pn1 = new PhoneNumber(707, 867, 5309);
        PhoneNumber pn2 = new PhoneNumber(707, 867, 5309);
        PhoneNumber pn3 = new PhoneNumber(650, 555, 1212);

        System.out.println("pn1.equals(pn2): " + pn1.equals(pn2)); // true
        System.out.println("pn1.equals(pn3): " + pn1.equals(pn3)); // false
        System.out.println("pn1.hashCode() == pn2.hashCode(): " + (pn1.hashCode() == pn2.hashCode())); // true
        System.out.println("pn1: " + pn1);
    }
}
