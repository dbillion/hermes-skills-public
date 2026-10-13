#!/usr/bin/env python3
"""Safe revert of a bulk test-panel injection when scenes are UNTRACKED.

git checkout / git revert are NO-OPS on untracked generated scenes, so this
python script is the only safe cleanup. It removes the injected act block and
the standalone `from dsa_style import test_panel` import line.

Usage: python3 revert_injection.py <scenes_dir>
"""
import glob, os, re

def revert(path):
    src = open(path).read()
    # remove the injected act block (from the comment line through its final FadeOut)
    src, n = re.subn(
        r"[ \t]*# === Verified by test.*?self\.play\(FadeOut\(_tl\), FadeOut\(_tc\), FadeOut\(_to\), FadeOut\(_tv\)\)\n",
        "", src, flags=re.DOTALL)
    # remove standalone import line, and any ", test_panel" / "test_panel," in an existing import
    src = re.sub(r"from dsa_style import test_panel\n", "", src)
    src = src.replace(", test_panel", "").replace(" test_panel,", "")
    open(path, "w").write(src)
    return n

if __name__ == "__main__":
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else "."
    c = 0
    for f in glob.glob(os.path.join(d, "*.py")):
        c += revert(f)
    print(f"reverted {c} inject blocks")
