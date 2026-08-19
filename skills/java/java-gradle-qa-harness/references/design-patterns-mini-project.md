# Design patterns as runnable mini-projects (GoF, 23 patterns)

User asked: "for the design patterns, do small mini projects inside the main project,
that can run separately from the main project, and run the test till it works."

## Layout (proven: dsa-design-patterns, 23 test files, all green)
One Gradle build, root `settings.gradle` + `build.gradle` with `application` plugin.
Each pattern = one subpackage under `src/main/java/dp/<group>/<Pattern>Demo.java`
with its own `public static void main(String[] args)` AND a `*Test.java` in
`src/test/java/dp/<group>/`.

```
dp/
  creational/   singleton/ factorymethod/ abstractfactory/ builder/ prototype/
  structural/   adapter/ bridge/ composite/ decorator/ facade/ flyweight/ proxy/
  behavioral/   chain/ command/ interpreter/ iterator/ mediator/ memento/
                observer/ state/ strategy/ template/ visitor/
```
23 patterns = 5 creational + 7 structural + 11 behavioral.

## Each pattern file shape
```java
package dp.creational.singleton;
public final class SingletonDemo {
    public enum Singleton { INSTANCE; }            // Josh Bloch enum singleton
    public static void main(String[] args) {
        var a = Singleton.INSTANCE, b = Singleton.INSTANCE;
        System.out.println("same instance? " + (a == b));
    }
}
```
```java
package dp.creational.singleton;
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
class SingletonDemoTest {
    @Test void sameInstance() {
        assertSame(SingletonDemo.Singleton.INSTANCE, SingletonDemo.Singleton.INSTANCE);
    }
}
```

## Modern Java used per pattern
- `sealed interface` + `permits` for state/visitor/chain variants (StateDemo, VisitorDemo, ChainDemo).
- `record` for immutable value types (Email in Builder, Glyph in Flyweight, Shape in Bridge).
- Pattern-matching `switch` for factory dispatch (FactoryMethod, AbstractFactory).
- Functional interfaces: `Consumer` (Observer), `Comparator` (Strategy).
- `List.copyOf` for immutable snapshots returned from builders/facades/mediators.

## Run one mini-project independently
```
./gradlew run --args='dp.creational.singleton.SingletonDemo'
./gradlew run --args='dp.structural.decorator.DecoratorDemo'
```
The `application` plugin's `run` task takes `--args`. Do NOT set a single `mainClass`
in build.gradle — with 23 mains it would break. Verify with one `run --args` before
claiming "each runs separately".

## Test-import gotchas (hit in the real build)
- Test sources do NOT auto-import `java.util.*`. Add explicit:
  `import java.util.List;`, `import java.util.Comparator;`, `import java.util.Map;`.
- `Observer` main uses `Consumer` → needs `import java.util.function.*;` in MAIN source too.
- Raw nested type in a test: `Coffee c = new DecoratorDemo.WithSugar(...)` fails — qualify
  as `DecoratorDemo.Coffee c` (or import the nested type).

## Test + push
`./gradlew test --console=plain` → BUILD SUCCESSFUL, 23 files, 0 failures.
Commit green state, then `gh repo create dsa-design-patterns --public` + push main.
