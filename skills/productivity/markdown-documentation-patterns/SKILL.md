---
name: markdown-documentation-patterns
description: Use for technical READMEs with mermaid diagrams and GIFs.
category: productivity
---

# Markdown Documentation Patterns

Reusable patterns for technical READMEs and markdown documentation that embed media (GIFs, videos), mermaid diagrams, and code blocks without layout issues.

## Core Patterns

### 1. Full-Width Code Blocks (Prevent Overflow)
**Problem**: Narrow table columns cause code overflow when embedding multi-line functions/tests.
**Solution**: Use full-width fenced code blocks instead of table cells.

```markdown
### Q1. Find the maximum sum subarray...

| Diagram | Topic / Scene |
|---|---|
| ![diagram](docs/diagrams/Q1_maxSumSubarray.png) | **Arrays_Subarrays** `q1_max_sum_subarray` |

**Function (Algorithms.java):**

```java
public static SubarrayResult maxSumSubarray(int[] nums) {
    // ... full method body
}
```

**Unit test (JUnit 5):**

```java
assertEquals(6, Algorithms.maxSumSubarray(new int[]{-2,1,-3,4,-1,2,1,-5,4}).sum());
```

![Q1 animation](explainer_videos/gifs/Q1_MaxSumSubarray.gif)
```

**Key**: Each code block is full-width (not in a table cell), preventing horizontal overflow.

### 2. Mermaid Diagram PNG Reference Management
**Problem**: Diagram PNG filenames use question-text naming (e.g., `Q10_lengthOfLongestSubstring.png`) but GIFs use abbreviated names (e.g., `Q10_LongestSubstring.gif`). Direct filename mapping fails.

**Solution**: Build a prefix-to-PNG map from actual files, then rewrite references.

```python
# Build prefix -> PNG mapping from actual files
prefix_to_png = {}
for f in os.listdir("docs/diagrams"):
    if f.endswith(".png"):
        m = re.match(r"^([QASF]\d+)_(.+)\.png$", f)
        if m:
            prefix = m.group(1)
            if prefix not in prefix_to_png:
                prefix_to_png[prefix] = f

# Fix all <img> tags
def fix_img_tag(match):
    tag = match.group(0)
    m = re.search(r'docs/diagrams/([^"]+\.png)', tag)
    if m:
        old = m.group(1)
        m2 = re.match(r"^([QASF]\d+)", old)
        if m2 and m2.group(1) in prefix_to_png:
            return tag.replace(old, prefix_to_png[m2.group(1)])
    return tag

fixed = re.sub(r"<img[^>]*docs/diagrams/[^\"]+\.png[^>]*>", 
               lambda m: fix_img(m), content)
```

**Key**: Map by prefix (Q10, A2, etc.) not full filename. Handle template placeholders in code blocks separately.

### 3. Embedded Media (GIFs) - Full Width
```markdown
<p align="center">
  <img src="explainer_videos/gifs/Q01_MaxSumSubarray.gif" 
       alt="Q01_MaxSumSubarray" width="100%">
</p>
```

- Use `width="100%"` for responsive full-width
- `align="center"` for centered display
- Alt text matches filename for accessibility

### 4. Category Ordering by Test Prefix
**Problem**: Scene filenames (e.g., `s06_valid_parentheses`) don't match question prefixes (`Q13_isValidParentheses`).
**Solution**: Categorize by test_name prefix, not scene filename.

```python
def catn(test_name):
    m = re.match(r'^([QASF])(\d+)', test_name)
    if m: return m.group(1), int(m.group(2))
    # Graph extras without numbers
    t = test_name.split('_', 1)[1] if '_' in test_name else test_name
    if 'flood' in t.lower() or 'floyd' in t.lower(): return 'G', 0
    if 'bellman' in t.lower() or 'astar' in t.lower(): return 'G', 0
    return 'G', 0

# Results in: Interview Questions (Q) -> Algorithms (A) -> Graph Extras (G)
```

### 5. Combining Reference Docs with Main README
**Pattern**: Prepend reference doc content (REf.md) to main README, deduplicate sections.

```markdown
# Main Title

> Tagline with context.

[Reference doc categorized content...]

## Start here — architecture & coverage
[Mermaid diagram]

## Quick start
[Commands]

---

## Index
[Auto-generated from blocks]

---

## Interview Questions
[Per-question blocks]

---

## Algorithms
[Per-algorithm blocks]

---

## Graph Extras
[Graph algorithm blocks]

---

## Testing
[Testing instructions]

## Layout
[Project structure]

## Tech & conventions
[Tech stack]
```

**Deduplication**: Check for existing sections before appending tail sections.

### 6. Clean Question Name Generation
```python
def clean_name(test_name):
    """Convert Q13_isValidParentheses -> 'Is Valid Parentheses'"""
    part = test_name.split('_', 1)[1] if '_' in test_name else ''
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', part)  # lower->Upper
    s = re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', ' ', s)  # XAbc -> X Abc
    words = s.split()
    if len(words) == 1:
        words = re.sub(r'(?<!^)(?=[A-Z])', ' ', part).split()
    return " ".join(w.capitalize() if i==0 else (w if w.isupper() else w.capitalize()) 
                    for i,w in enumerate(words))
```

## Pitfalls to Avoid

| Pitfall | Solution |
|---------|----------|
| Code overflow in table cells | Use full-width fenced code blocks |
| Wrong diagram PNG filenames | Map by prefix, not GIF name |
| Duplicate sections (Layout/Tech) | Check before appending tail sections |
| Wrong category (s06 to Single-Path) | Use test_name prefix, not scene filename |
| Python sentences in Java README | Strip language-specific mentions (e.g., "walrus operator") |
| Mangled names ("is valid b s t") | Use proper camelCase splitter |

## When to Use

- Technical READMEs with embedded diagrams/GIFs
- Documentation with mixed code/visual content
- Projects with auto-generated mermaid diagrams
- Any markdown with embedded media that breaks in narrow columns

## Related Skills

- `manim-dsa-storytelling` (for video generation patterns)
- `manim-explainer-animations` (for animation structure)
- `manim-brilliance-explainer` (for combined video patterns)

---

*Patterns derived from dsa-java-gradleqa README rewrite (2026-08-08). Generalizable to any technical documentation with embedded media and mermaid diagrams.*