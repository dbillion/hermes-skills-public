package effectivejava.item45_46;

import java.util.*;
import java.util.stream.*;

import static java.util.stream.Collectors.*;

/**
 * Item 45: Use streams judiciously
 * Item 46: Prefer side-effect-free functions in streams
 */
public class StreamExamples {

    // BAD - side effects in forEach
    public static Map<String, Long> badWordFreq(List<String> words) {
        Map<String, Long> freq = new HashMap<>();
        words.forEach(word -> {
            freq.merge(word.toLowerCase(), 1L, Long::sum);
        });
        return freq;
    }

    // GOOD - pure function pipeline
    public static Map<String, Long> goodWordFreq(List<String> words) {
        return words.stream()
            .collect(groupingBy(String::toLowerCase, counting()));
    }

    // Anagrams example
    public static List<List<String>> anagrams(List<String> words) {
        return words.stream()
            .collect(groupingBy(word -> word.chars().sorted()
                .collect(StringBuilder::new, StringBuilder::appendCodePoint, StringBuilder::append)
                .toString()))
            .values().stream()
            .filter(group -> group.size() >= 2)
            .collect(toList());
    }

    public static void main(String[] args) {
        List<String> words = Arrays.asList("hello", "world", "hello", "java", "world", "hello");

        System.out.println("Word frequencies (good): " + goodWordFreq(words));

        List<String> anagramWords = Arrays.asList("staple", "pleats", "elapse", "palest", "hello");
        System.out.println("Anagrams: " + anagrams(anagramWords));
    }
}
