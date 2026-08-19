#!/usr/bin/env python3
"""Migrate old trick_*.py scenes to a validated base-class format.

Reads each old scene file's class attributes (TITLE, INPUT_DATA, INSIGHT_TEXT,
NAIVE_CODE, IDIOMATIC_CODE, @staticmethod bf_complexity/opt_complexity) and
rewrites a clean file that:
  - imports from the CURRENT base module (dsa_style), not an old 'template'
  - defines run_naive / run_idiomatic (the method names the base actually calls)
  - uses module-level complexity helpers (lin/quad/cubic/const_mult) instead of
    @staticmethod (which is the Python-3.14 bound-method crash from Pitfall 1)

NO deletion — overwrites the file in place only after ast.parse succeeds.
"""
import ast, os, re

REDO = os.path.dirname(os.path.abspath(__file__))

def complexity_expr(body_src: str) -> str:
    s = body_src.strip()
    if s == "return t":
        return "lin"
    if s == "return t ** 2":
        return "quad"
    if s == "return t ** 3":
        return "cubic"
    if s == "return 1":
        return "const_mult(1)"
    m = re.match(r"return t \* (\d+)", s)
    if m:
        return f"const_mult({m.group(1)})"
    m = re.match(r"return (\d+)", s)
    if m:
        return f"const_mult({m.group(1)})"
    return "lin"

def extract_class_attrs(path):
    src = open(path).read()
    tree = ast.parse(src)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    attrs, static = {}, {}
    for n in cls.body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    try:
                        attrs[t.id] = ast.literal_eval(n.value)
                    except Exception:
                        attrs[t.id] = None
        if isinstance(n, ast.FunctionDef):
            deco = [d.id for d in n.decorator_list if isinstance(d, ast.Name)]
            if "staticmethod" in deco and n.name in ("bf_complexity", "opt_complexity"):
                for b in n.body:
                    if isinstance(b, ast.Return):
                        static[n.name] = ast.unparse(b.value)
    return attrs, static

for fname in sorted(os.listdir(REDO)):
    if not (fname.startswith("trick_") and fname.endswith(".py")):
        continue
    path = os.path.join(REDO, fname)
    try:
        attrs, static = extract_class_attrs(path)
    except Exception as e:
        print(f"SKIP {fname}: parse error {e}")
        continue
    title = attrs.get("TITLE", fname)
    input_data = attrs.get("INPUT_DATA", [])
    insight = attrs.get("INSIGHT_TEXT", "")
    naive = attrs.get("NAIVE_CODE", "")
    idiomatic = attrs.get("IDIOMATIC_CODE", "")
    bf = complexity_expr(static.get("bf_complexity", "return t"))
    opt = complexity_expr(static.get("opt_complexity", "return t"))
    if naive is None or idiomatic is None:
        print(f"SKIP {fname}: missing code")
        continue

    cls_name = fname[:-3]
    m = re.match(r"trick_(\d+)_(.+)", cls_name)
    if m:
        cls_name = "Trick" + m.group(1) + re.sub(r"_", " ", m.group(2)).title().replace(" ", "")
    else:
        cls_name = "Trick" + cls_name[6:]

    out = f'''"""
{title.strip()}
"""
from manim import *
from dsa_style import TrickScene, lin, quad, cubic, const_mult

class {cls_name}(TrickScene):
    TITLE = {title!r}
    INPUT_DATA = {input_data!r}
    INSIGHT_TEXT = {insight!r}
    BF_COMPLEXITY = {bf}
    OPT_COMPLEXITY = {opt}

    NAIVE_CODE = {naive!r}

    IDIOMATIC_CODE = {idiomatic!r}

    def run_naive(self):
        lines = self.naive_code.code_lines.submobjects
        for i in range(min(len(lines), 8)):
            self.play(self.naive_hl.animate.move_to(lines[i]), run_time=0.25)
        self.wait(0.5)

    def run_idiomatic(self):
        lines = self.idiomatic_code.code_lines.submobjects
        for i in range(min(len(lines), 8)):
            self.play(self.idiomatic_hl.animate.move_to(lines[i]), run_time=0.25)
        self.wait(0.5)


if __name__ == "__main__":
    pass
'''
    tmp = path + ".new"
    open(tmp, "w").write(out)
    try:
        ast.parse(out)
        os.replace(tmp, path)
        print(f"MIGRATED {fname} -> {cls_name}")
    except SyntaxError as e:
        print(f"PARSE FAIL {fname}: {e}")
        os.remove(tmp)
