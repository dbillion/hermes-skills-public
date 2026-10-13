# Verified-by-test panel — injector + Gradle ground-truth recipe

## 1. Capture real test results via Gradle (read-only, safe)
```bash
cd <repo>
./gradlew test --console=plain > _gradle_test.log 2>&1
# produces build/test-results/test/TEST-dsa.AlgorithmsTest.xml
```
Parse the XML (name attr has `()` — strip it):
```python
import xml.etree.ElementTree as ET, glob, re, json
results = {}
for fx in glob.glob("build/test-results/test/TEST-*.xml"):
    root = ET.parse(fx).getroot()
    for tc in root.findall("testcase"):
        raw = tc.get("name")                 # e.g. "A3_quickSort()"
        method = re.sub(r"\(\)?$", "", raw)
        f = tc.find("failure") or tc.find("error")
        results[method] = {"status": "FAIL" if f is not None else "PASS",
                           "message": (f.get("message") or "") if f is not None else ""}
```

## 2. Extract real @Test bodies (balanced-brace scan)
```python
def extract_tests(path):
    src = open(path).read()
    tests = {}
    for m in re.finditer(r'@Test\s+void\s+(\w+)\(\)\s*\{', src):
        name = m.group(1); start = m.end() - 1; depth = 0; i = start
        while i < len(src):
            if src[i] == '{': depth += 1
            elif src[i] == '}':
                depth -= 1
                if depth == 0: break
            i += 1
        tests[name] = src[start+1:i].strip()
    return tests
```

## 3. Derive expected-output caption from assertion (real verified value)
```python
def grab_array(s, start):
    depth=0; i=start
    while i < len(s):
        if s[i]=='{': depth+=1
        elif s[i]=='}':
            depth-=1
            if depth==0: return s[start:i+1]
        i+=1
    return ""
def caption(body):
    m = re.search(r'assertArrayEquals\(\s*(?:new\s+\w+(?:\[\])?\s*)?(\{)', body)
    if m: return grab_array(body, m.start(1)).replace('{','[').replace('}',']')
    m = re.search(r'assertEquals\(\s*([^,]+),', body)
    if m: return m.group(1).strip()
    if 'assertTrue'  in body: return "true"
    if 'assertFalse' in body: return "false"
    return "PASS"
```

## 4. The test_panel helper (in dsa_style.py)
Returns 4 mobjects — unpack all four:
```python
def test_panel(scene, test_code, expected_text, label="Verified by test (JUnit)"):
    label = Text(label, color=GOOD).scale(0.4)
    scene.add_fixed_in_frame_mobjects(label)
    label.to_corner(UL).shift(DOWN*0.7)
    code = Code(code_string=test_code, language="java", formatter_style="native",
                background="window", add_line_numbers=True,
                paragraph_config={"font_size": 14})
    scene.add_fixed_in_frame_mobjects(code)
    code.scale(0.34).to_edge(LEFT, buff=0.3).shift(UP*0.15)
    out = Text("✓ Expected output:", color=WHITE).scale(0.42)
    scene.add_fixed_in_frame_mobjects(out); out.to_edge(DOWN, buff=1.0)
    val = Text(expected_text, color=GOOD, weight=BOLD).scale(0.55)
    scene.add_fixed_in_frame_mobjects(val); val.next_to(out, DOWN, buff=0.15)
    return label, code, out, val
```
Usage in construct (final act, before teardown):
```python
_tl, _tc, _to, _tv = test_panel(self, _tcode, "1,2,5,8,9")
self.play(FadeIn(_tl), FadeIn(_tc), FadeIn(_to), FadeIn(_tv))
self.wait(2.2)
self.play(FadeOut(_tl), FadeOut(_tc), FadeOut(_to), FadeOut(_tv))
```

## 5. Bulk injector (PITFALLS — burned a full session)
```python
def ensure_import(src):
    if re.search(r"test_panel\s*[),]", src):   # import item, NOT the call
        return src
    new, n = re.subn(r"(from manim import \*(\n[ \t]*#[^\n]*)*\n)",
                      r"\1from dsa_style import test_panel\n", src, count=1)
    return new if n else "from dsa_style import test_panel\n" + src

def inject(path, spec):
    base = os.path.splitext(os.path.basename(path))[0]
    if base.lower() in HELPERS or base not in spec: return "skip"
    src = open(path).read()
    if "test_panel(" in src: return "already"
    matches = list(re.finditer(r"self\.play\(FadeOut\(", src))
    if not matches: return "no-fadeout"
    last = matches[-1]
    line_start = src.rfind("\n", 0, last.start()) + 1   # KEEP anchor indent
    indent = src[line_start:last.start()] or "        "
    act = (f"\n{indent}# === Verified by test ===\n"
           f"{indent}_tcode = \"\"\"{display}\"\"\"\n"
           f"{indent}_tl,_tc,_to,_tv = test_panel(self,_tcode,\"{exp}\")\n"
           f"{indent}self.play(FadeIn(_tl),FadeIn(_tc),FadeIn(_to),FadeIn(_tv))\n"
           f"{indent}self.wait(2.2)\n"
           f"{indent}self.play(FadeOut(_tl),FadeOut(_tc),FadeOut(_to),FadeOut(_tv))\n")
    new = src[:line_start] + act + src[line_start:]   # NOT last.start()
    open(path,"w").write(ensure_import(new))
```
Pre-pass (normalize broken teardowns): any column-0 line starting with `self.`
-> re-indent to 8 (do NOT touch the module docstring `"""`). Verify by counting
column-0 `self.` lines (must be 0) — `ast.parse` alone misses the bug because
`self.play(...)` at col 0 is syntactically valid (NameError is runtime).

## 6. Render-test before full batch
Render 2-3 scenes (one multiline-import, one originally-broken). Confirm exit 0
+ mp4 exists. THEN launch all 83 (sequential is faster per-scene than N=3
concurrent on a 4-thread iGPU because 3 concurrent starve each other).
