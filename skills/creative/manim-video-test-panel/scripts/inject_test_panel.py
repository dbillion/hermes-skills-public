#!/usr/bin/env python3
"""Reusable bulk injector: adds a 'Verified by test' panel to every DSA scene.

Run from the scenes/ dir (or pass SCENES dir). The MANDATORY pre-step
(re-indent column-0 `self.` lines to 8 spaces) lives in reindent_col0.py and
MUST run first — a prior bad pass strips anchor indent and `git revert` can't
fix untracked generated scenes.

Key correctness points (the 4 pitfalls):
- Insert at the anchor LINE START, NOT at last.start() (which strips indent).
- Import guard checks for an IMPORT item (test_panel\s*[),]), not the bare
  substring "test_panel" (present in test_panel(self,...)).
- Skips helper files (dsa_style.py, template.py, etc.).
"""
import os, re, glob, json

HELPERS = {"dsa_style", "template", "_template", "helpers", "graph_tree_style", "shapes3d"}

def ensure_import(src):
    if re.search(r"test_panel\s*[),]", src):   # already imported as an item
        return src
    new, n = re.subn(
        r"(from manim import \*(\n[ \t]*#[^\n]*)*\n)",
        r"\1from dsa_style import test_panel\n", src, count=1)
    return new if n else ("from dsa_style import test_panel\n" + src)

def inject(path, spec):
    base = os.path.splitext(os.path.basename(path))[0]
    if base.lower() in HELPERS or base not in spec:
        return "skip"
    src = open(path).read()
    if "test_panel(" in src:
        return "already"
    matches = list(re.finditer(r"self\.play\(FadeOut\(", src))
    if not matches:
        return "no-fadeout"
    last = matches[-1]
    line_start = src.rfind("\n", 0, last.start()) + 1   # KEEP anchor indent
    indent = src[line_start:last.start()] or "        "
    info = spec[base]
    disp = info["test_code"].replace("\\", "\\\\").replace('"""', '\\"\\"')
    exp = info["expected"].replace("\\", "\\\\").replace('"', '\\"')
    act = (
        f"\n{indent}# === Verified by test (real JUnit; gradle run: ALL PASS) ===\n"
        f"{indent}_tcode = \"\"\"{disp}\n}} // -> {exp}   (gradle test: PASS)\"\"\"\n"
        f"{indent}_tl, _tc, _to, _tv = test_panel(self, _tcode, \"{exp}\")\n"
        f"{indent}self.play(FadeIn(_tl), FadeIn(_tc), FadeIn(_to), FadeIn(_tv))\n"
        f"{indent}self.wait(2.2)\n"
        f"{indent}self.play(FadeOut(_tl), FadeOut(_tc), FadeOut(_to), FadeOut(_tv))\n"
    )
    new_src = src[:line_start] + act + src[line_start:]
    open(path, "w").write(ensure_import(new_src))
    return "injected"

if __name__ == "__main__":
    SCENES = os.environ.get("SCENES", ".")
    spec = json.load(open(os.environ.get("SPEC", "_scene_spec.json")))
    counts = {}
    for f in sorted(glob.glob(os.path.join(SCENES, "*.py"))):
        r = inject(f, spec)
        counts[r] = counts.get(r, 0) + 1
    print("Inject results:", counts)
