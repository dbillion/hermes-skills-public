#!/usr/bin/env python3
"""Audit Manim scene files for stub/truncated/wrapper-only CODE panels.

A subagent "using real source" sometimes pastes only the public wrapper:
    CODE = """public static void f(X x) { f(x, 0, n); }"""
...and animates a simplified algorithm. This scanner flags those so you catch
them BEFORE the (slow) render batch.

It ALSO flags scenes whose payoff/result text claims a final arrangement
(sorted list, found index, computed DP value) so a human verifies the
animation runs to COMPLETION and the visible elements actually reach that
state. (Static completion-checking isn't feasible; this is a manual-review
nudge — the quicksort Round-2 bug had a correct code panel but only animated
one partition, so cubes ended unsorted while the caption said sorted.)

Usage:
    python3 audit_stubs.py <scenes_dir> [--verbose]

Exit 0 always; prints findings.
"""
import os
import re
import sys

WRAPPER_RE = re.compile(
    r"public\s+static\s+\w+\s+\w+\s*\([^)]*\)\s*\{\s*\w+\s*\([^)]*\)\s*;\s*\}",
    re.S,
)

# Result text that states a final arrangement the animation must reach.
ENDSTATE_RE = re.compile(
    r'Text\(\s*[^\n]*?(\[[^\]]*\]|index\s*=\s*\d+|=>\s*\d+|is\s+\w+)\s*[^\n]*?\)',
    re.I,
)


def audit(scenes_dir, verbose=False):
    files = [
        f for f in os.listdir(scenes_dir)
        if f.endswith(".py")
        and not f.startswith(("dsa_style", "graph_tree_style", "shapes3d"))
    ]
    issues = []
    endstate_flags = []
    checked = 0
    for fn in sorted(files):
        path = os.path.join(scenes_dir, fn)
        src = open(path, encoding="utf-8", errors="ignore").read()
        blocks = re.findall(r'CODE\s*=\s*"""(.*?)"""', src, re.S)
        if not blocks:
            issues.append((fn, "NO CODE BLOCK"))
            continue
        code = blocks[0].strip()
        checked += 1
        lines = [l for l in code.splitlines() if l.strip()]
        # stub: 1-2 lines with no control flow / no braces
        has_body = any(k in code for k in
                       ["for", "while", "if ", "if(", "return", "{", "}"]) or len(lines) >= 3
        if len(lines) <= 2 and not has_body:
            issues.append((fn, f"STUB {len(lines)}L: {code[:50]!r}"))
        elif WRAPPER_RE.search(code):
            issues.append((fn, f"WRAPPER-ONLY: {code[:60]!r}"))
        # end-state claim -> manual verification nudge
        if ENDSTATE_RE.search(src):
            endstate_flags.append(fn)
    print(f"Checked {checked} scene files. Stub/wrapper issues: {len(issues)}")
    for fn, note in issues:
        print(f"  {fn}: {note}")
        if verbose:
            print(f"     (full CODE block in {fn})")
    if endstate_flags:
        print(f"\nEND-STATE CHECK (manual): {len(endstate_flags)} scene(s) state a "
              f"final result in text — verify the animation runs to completion:")
        for fn in endstate_flags:
            print(f"  - {fn}")
        print("  Rule: if the caption says sorted/found/computed, the visible "
              "elements must actually END in that state (full recursion / full "
              "DP fill), not a partial step. See references/code_panel_fidelity.md.")
    return issues


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: audit_stubs.py <scenes_dir> [--verbose]")
        sys.exit(2)
    audit(sys.argv[1], verbose="--verbose" in sys.argv)
