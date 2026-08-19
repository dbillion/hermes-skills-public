package effectivejava.item5;

import java.util.Objects;

/**
 * Item 5: Prefer dependency injection to hardwiring resources
 * 
 * Dependency injection makes it easy to substitute different implementations
 * for testing or different environments.
 */
public class SpellChecker {
    private final Lexicon dictionary;

    public SpellChecker(Lexicon dictionary) {
        this.dictionary = Objects.requireNonNull(dictionary);
    }

    public boolean isValid(String word) {
        return dictionary.contains(word);
    }

    // Lexicon interface
    public interface Lexicon {
        boolean contains(String word);
    }

    // Implementation
    public static class EnglishLexicon implements Lexicon {
        @Override
        public boolean contains(String word) {
            // Simplified check
            return word != null && !word.isEmpty();
        }
    }

    public static void main(String[] args) {
        SpellChecker checker = new SpellChecker(new EnglishLexicon());
        System.out.println("Is 'hello' valid? " + checker.isValid("hello"));
    }
}
