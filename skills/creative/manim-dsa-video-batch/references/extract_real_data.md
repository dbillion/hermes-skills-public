# Extract real source + test samples from a Java DSA repo

Use to build the per-problem bundle fed to generation subagents. Pulls the
verbatim method body and the test's asserted sample input (never invent data).

```python
import re, json

java = open("src/main/java/dsa/Algorithms.java").read()
test = open("src/test/java/dsa/AlgorithmsTest.java").read()

def balanced(src, start_idx):
    depth = 0; i = start_idx
    while i < len(src):
        if src[i] == '{': depth += 1
        elif src[i] == '}':
            depth -= 1
            if depth == 0: break
        i += 1
    return src[start_idx:i+1]

def method(src, name):
    m = re.search(r'public\s+(?:static\s+)?(?:<[^>]+>\s+)?[\w<>\[\],. ]+?\s+'
                  + re.escape(name) + r'\s*\(([^)]*)\)\s*\{', src)
    return balanced(src, m.end()-1) if m else None

def inner_class(src, name):
    m = re.search(r'(?:public\s+|private\s+|static\s+)*class\s+'
                  + re.escape(name) + r'\s*[\{<]', src)
    if not m: return None
    return balanced(src, src.index('{', m.start()))

def test_body(src, testname):
    m = re.search(r'void\s+' + re.escape(testname) + r'\s*\(\s*\)\s*\{(.*?)\n\s*\}',
                  src, re.DOTALL)
    return m.group(1) if m else None

# Map test name -> method/inner-class. Strip leading Q##_ / A##_ to find the base.
# Inner classes live as Algorithms.ArrayStack etc. -> extract via inner_class().
```

Notes:
- Generic return types (e.g. `public static <T extends Comparable<? super T>> List<T> heapSort`)
  break the simple `public ... name(` regex if the `<...>` is in the return — fall back to
  `java.index("public static <T ...> List<T> heapSort")` + find first `{`.
- The test sample is in `assertEquals(expected, Algorithms.method(<real args>))` — capture the
  `<real args>` verbatim; that is what the animation must use.
