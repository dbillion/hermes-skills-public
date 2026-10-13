# Verifying a Java/Gradle solution before/after NLM upload

When the digest task includes "the final solution" (a Java repo you must
build + test), the Gradle wrapper version often predates the system JDK:

- Symptom: `./gradlew ...` fails with
  `BUG! exception ... Unsupported class file major version 68`
  (major 68 = Java 24; Gradle 8.2 supports <= Java 20).
- Fix: switch to an older JDK via sdkman, then run gradle on that JDK:
  ```bash
  export JAVA_HOME="$HOME/.sdkman/candidates/java/17.0.12-graal"
  export PATH="$JAVA_HOME/bin:$PATH"
  cd <repo>
  ./gradlew test --console=plain
  ```
  sdkman Java 17 + Gradle 8.2 is a fully supported combo.
- First run needs network (downloads Jackson/JUnit from mavenCentral) — give it a
  300s+ timeout or it interrupts mid-download.
- Real verification = read the test XML, not just "BUILD SUCCESSFUL":
  `find build/test-results -name "*.xml" -exec grep -oE 'tests="[0-9]+" skipped="[0-9]+" failures="[0-9]+" errors="[0-9]+"' {} \;`
- Compile-first to get actionable errors: `./gradlew compileJava 2>&1 | grep -iE "error:|BUILD"`

## Lesson from a real bug
The agent's first draft compiled with 3 errors the *green test caught* (a
generic-cache type clash + 2 unhandled `JsonProcessingException`). Reasoning
alone missed them. Always run the test; treat BUILD SUCCESS + 0 failures/errors
as the gate before claiming the solution works.
