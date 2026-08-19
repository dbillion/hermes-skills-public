#!/usr/bin/env python3
"""Audit Manim DSA scene files for out-of-range code_lines[] indices.

ast.parse will NOT catch these -- an index past the end of the CODE panel
only raises at render time. Run this after ANY edit to a CODE string.

Usage:
    python3 check_code_line_indices.py [DIR_OR_FILES...]

Exit code 0 = all indices in range; 1 = at least one file is out of range.
"""
import ast
import glob
import os
import re
import sys

CODE_VAR = re.compile(r"^(?:[A-Z_]*CODE)$")
IDX = re.compile(r"code_lines\[(\d+)\]")


def audit(path):
    src = open(path).read()
    tree = ast.parse(src)
    counts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and CODE_VAR.match(t.id):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        counts[t.id] = len(node.value.value.split("\n"))
    if not counts:
        return None
    # Conservative: an index is safe only if it fits the SMALLEST code panel,
    # since a file may hold both BRUTE_CODE and OPT_CODE.
    limit = min(counts.values())
    bad = sorted({int(m) for m in IDX.findall(src) if int(m) >= limit})
    return counts, limit, bad


def main(argv):
    targets = argv[1:] or ["."]
    files = []
    for t in targets:
        files.extend(sorted(glob.glob(os.path.join(t, "*.py"))) if os.path.isdir(t) else [t])
    failed = False
    for f in files:
        try:
            res = audit(f)
        except SyntaxError as e:
            print(f"{os.path.basename(f)}: SYNTAX ERROR {e}")
            failed = True
            continue
        if res is None:
            continue
        counts, limit, bad = res
        name = os.path.basename(f)
        if bad:
            failed = True
            print(f"{name}: OUT OF RANGE {bad} (panels={counts}, min lines={limit})")
        else:
            print(f"{name}: ok (panels={counts})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
