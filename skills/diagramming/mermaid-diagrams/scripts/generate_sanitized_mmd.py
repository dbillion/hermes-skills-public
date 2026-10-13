#!/usr/bin/env python3
"""
Generate one mermaid .mmd per unit (question/algorithm/module) with node text
auto-sanitized so mmdc never hits the parser pitfalls (no [ ] ( ) = ' " : / etc.
in labels). Pair with the batch-render loop in SKILL.md.

Usage:
    python3 generate_sanitized_mmd.py --out docs/diagrams

Define UNITS = { "Q1_twoSum": ("Title", ["step1","step2",...]), ... }
Each unit becomes a vertical graph TD flowchart: START -> N0 -> N1 -> ... -> END.
END is a fixed "assert passes in JUnit" caption so the diagram ties to a test.

Why this exists: hand-writing 90 .mmd files invites apostrophe/`=`/bracket parse
errors. Centralizing the sanitizer means the diagrams are reproducible and safe.
This is exactly how the dsa-java-gradleqa repo got 90 per-method diagrams with
zero render failures.
"""
import os
import argparse

# method -> (display title, [flow steps])   # replace with your real units
UNITS = {
    "Q1_twoSum": ("Two Sum", ["Put num to index in map", "For each x look for target minus x",
                              "If found return pair", "Else store x"]),
    "A1_bubbleSort": ("Bubble sort", ["For i in n", "For j in n-i-1",
                                       "Swap if a j greater a j plus 1", "Repeat passes"]),
}

FORBIDDEN = ["[", "]", "{", "}", "(", ")", "=", '"', "'", ":", "/", "\\", "#", "@",
             "*", "+", "&", "|", "<", ">", "%", "$"]


def sanitize(s: str) -> str:
    for ch in FORBIDDEN:
        s = s.replace(ch, " ")
    return " ".join(s.split())


def build(units: dict, out_dir: str) -> int:
    os.makedirs(out_dir, exist_ok=True)
    n = 0
    for method, (title, steps) in units.items():
        lines = ["graph TD", f'    START["{sanitize(title)}"]']
        prev = "START"
        for i, st in enumerate(steps):
            node = f"N{i}"
            lines.append(f'    {node}["{sanitize(st)}"]')
            lines.append(f"    {prev} --> {node}")
            prev = node
        lines.append(f'    {prev} --> END["assert passes in JUnit"]')
        with open(os.path.join(out_dir, method + ".mmd"), "w") as f:
            f.write("\n".join(lines) + "\n")
        n += 1
    return n


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/diagrams")
    args = ap.parse_args()
    count = build(UNITS, args.out)
    print(f"wrote {count} mermaid sources to {args.out}")
