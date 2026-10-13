#!/usr/bin/env python3
"""MANDATORY pre-step before bulk-injecting test panels.

Re-indents every column-0 `self.` line to 8 spaces across ALL scene files.
A `self.` line at column 0 is syntactically valid Python (only NameErrors at
render time), and a `git revert`/`git checkout` cannot fix it because generated
scenes are usually UNTRACKED. Running this first prevents the silent anchor-strip
pitfall that otherwise breaks scenes at render time.

Usage: python3 reindent_col0.py <scenes_dir>
"""
import glob, os

HELPERS = {"dsa_style", "template", "_template", "helpers", "graph_tree_style", "shapes3d"}

def main(scenes_dir):
    n = 0
    for f in sorted(glob.glob(os.path.join(scenes_dir, "*.py"))):
        b = os.path.splitext(os.path.basename(f))[0].lower()
        if b in HELPERS:
            continue
        lines = open(f).read().splitlines(keepends=True)
        new = [("        " + ln.lstrip() if (ln[:1] not in " \t" and ln.strip().startswith("self.")) else ln)
               for ln in lines]
        if new != lines:
            open(f, "w").write("".join(new))
            n += 1
    print(f"re-indented {n} files")

if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
