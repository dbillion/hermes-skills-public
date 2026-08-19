# Data extraction recipe (DSA Manim README publish)

One record per scene. Source files (in `explainer_videos/`):
- `_scene_spec.json` → per base: `test_name` (e.g. `Q3_twoSum`), `expected`.
- `_tests.json`      → per `test_name`: the REAL @Test body string (use as the
  "unit test" column). Keys like `Q1_maxSumSubarray`, `A3_quickSort`.
- `_render_map_full.json` → per base: `final` = gif filename (e.g.
  `Q03_TwoSum.mp4`). Strip `.mp4` → gif base. AUTHORITATIVE for gif name.
- `src/main/java/dsa/Algorithms.java` → extract the real method source for the
  "function(s) used" column.
- `organized/<Topic>/<gif>.mp4` → symlinks; walk them to map gif → Topic.

## gif name from base (robust)
```python
import json, re, glob, os
rmap = json.load(open("explainer_videos/_render_map_full.json"))
gif_files = {os.path.basename(p)[:-4] for p in glob.glob("explainer_videos/gifs/*.gif")}
def gif_for(base):
    if base in rmap and rmap[base].get("final"):
        c = rmap[base]["final"][:-4]
        if c in gif_files: return c
    n = re.sub(r"[^a-z0-9]","", base.lower())          # normalized compare
    for g in gif_files:
        if re.sub(r"[^a-z0-9]","", g.lower()) == n: return g
    return None
```

## topic from organized/ (use os.walk, NOT glob)
```python
import os
tb = {}
for root, dirs, files in os.walk("explainer_videos/organized"):
    for f in files:
        p = os.path.join(root, f)
        if os.path.islink(p):
            tb[f[:-4]] = os.path.basename(root)        # gif name -> Topic
# assign: r['topic'] = tb.get(r['gif']) or 'Other'
# ALWAYS include a 'Misc' fallback so every record emits a block.
```
Glob `organized/*/*` returns NOTHING when `organized/` holds symlinks to other
dirs — os.walk + os.path.islink is required.

## function source extraction (brace-match)
```python
src = open("src/main/java/dsa/Algorithms.java").read()
def extract_method(name):
    if not name: return None
    idx = src.find(f"public static {name}(")
    if idx < 0: idx = src.find(f" {name}(")
    if idx < 0:
        m = re.search(r"\b"+re.escape(name)+r"\s*\(", src); idx = m.start() if m else -1
    if idx < 0: return None
    start = src.rfind("public static", 0, idx)
    if start < 0: start = idx
    b = src.find("{", idx); depth=0; i=b
    while i < len(src):
        if src[i]=="{": depth+=1
        elif src[i]=="}":
            depth-=1
            if depth==0: end=i+1; break
        i+=1
    return src[start:end]
```
Method name: take it from the @Test call `Algorithms.<method>(` if present, else
`test_name.split("_",1)[1]` camelCased. Stack-impl methods (MinStack, MaxStack,
QueueWithStacks, LCA) may have NO top-level `public static` — show the @Test call
text instead, don't fake source.

## diagram PNG path conversion
`Q05_MissingNumber.gif` → `docs/diagrams/Q5_missingNumber.png`
(no zero-pad on the number; first letter of the word part lowercased):
```python
def diag_for(gif):
    m = re.match(r"^([QASF])(\d+)_([A-Za-z0-9]+)$", gif)
    if m:
        pre, num, word = m.group(1), int(m.group(2)), m.group(3)
        return f"{pre}{num}_{word[0].lower()+word[1:]}"
    return gif[0].lower()+gif[1:] if gif else ""
```
If `docs/diagrams/<d>.png` does NOT exist on disk, emit a `—` cell, never a
broken `<img>`. (Single-path S* and graph-extras often have no diagram PNG.)
