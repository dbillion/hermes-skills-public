#!/usr/bin/env python3
"""Convert local .md / .py source files into Colab-ready .ipynb notebooks.

Key techniques learned (DS-A study-notebook generation):
- .md  -> split on fenced ```lang blocks: prose=markdown cell, ```python/py/(none)=CODE cell,
         other langs (bash/json)=markdown literal.
- .py  -> one CODE cell per top-level def/class.
- Every code cell that is a bare definition gets a RUNNABLE DEMO appended so the
  implementation is visibly exercised (user requirement: "make the implementation visible").
  Demo = a call with sample args + print(...), wrapped in try/except so a cell
  never hard-crashes. Classes needing constructor args print "demo skipped (needs args)".
- Write nbformat-4 JSON. Colab's `download` returns NON-valid JSON (wire format);
  keep these locally-built files as the canonical artifact.

CRITICAL nbformat rule (cost a full debug cycle once):
  source must be a list of lines where EVERY line except the LAST ends with '\n'.
  If you use c.split('\n') directly, lines have NO trailing newline and Jupyter/Colab
  MERGES them into one line -> SyntaxError that passes a local '\n'.join()+compile() test
  but FAILS real per-cell Colab execution (colab exec -f). ALWAYS route source through
  to_source() below.

Usage:
  python3 md_to_colab_notebook.py FILE1.md FILE2.py ...
  -> writes <basename>.ipynb next to each source (or in --out DIR).
"""
import json, os, re, ast, sys

SAMPLES = {
    "nums": "[-2, 1, -3, 4, -1, 2, 1, -5, 4]", "num": "10", "arr": "[1,2,3,4,5]",
    "array": "[1,2,3,4,5]", "s": "'racecar'", "text": "'hello world'", "string": "'abcde'",
    "n": "5", "k": "3", "target": "9", "lst": "[3,1,4,1,5,9,2,6]",
    "list": "[3,1,4,1,5,9,2,6]", "a": "[1,2,3]", "b": "[2,3,4]",
    "graph": "{0:[1,2],1:[2],2:[]}", "edges": "[(0,1),(1,2)]",
}
def to_source(text):
    """nbformat RULE: source is a list of lines; every line EXCEPT the last MUST end
    with '\\n'. Without trailing newlines, Jupyter/Colab MERGES adjacent lines into one
    (e.g. 'from x import yimport time@contextmanagerdef f...') -> SyntaxError.
    This is invisible to local '\\n'.join()+compile() tests but FAILS real per-cell Colab
    execution (colab exec -f). Always build source lists through this helper."""
    lines = text.split("\n")
    if not lines:
        return [""]
    out = []
    for i, ln in enumerate(lines):
        out.append(ln if i == len(lines) - 1 else ln + "\n")
    return out

def sample_for(name):
    ln = name.lower()
    for k, v in SAMPLES.items():
        if k in ln: return v
    return "None"

def build_demo(code):
    try: tree = ast.parse(code)
    except SyntaxError: return ""
    if re.search(r"^\s*\w+\s*\(.*\)\s*$", code, re.M): return ""  # already has a call
    defs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    if defs:
        fn = defs[0]; args = [a.arg for a in fn.args.args]
        call = f"{fn.name}()" if not args else f"{fn.name}({', '.join(sample_for(a) for a in args)})"
        return (f"\n# --- demo ---\ntry:\n    _r = {call}\n    print('{fn.name}(...) ->', _r)\n"
                f"except Exception as _e:\n    print('demo skipped:', _e)\n")
    if classes:
        cl = classes[0]
        return (f"\n# --- demo ---\ntry:\n    _inst = {cl.name}()\n    print('{cl.name} instantiated:', _inst)\n"
                f"except Exception as _e:\n    print('demo skipped (needs args):', _e)\n")
    return ""

def add_demo_if_def(code):
    if not re.search(r"^\s*(def |class |async def )", code, re.M): return code
    d = build_demo(code)
    if d and "# --- demo ---" not in code: return code.rstrip() + "\n" + d
    return code

FENCE = re.compile(r"```([a-zA-Z0-9_+-]*?)\s*\n")
def md_cells(text):
    cells, buf, i, n = [], [], 0, len(text)
    while i < n:
        m = FENCE.search(text, i)
        if not m: buf.append(text[i:]); break
        if text[i:m.start()].strip(): buf.append(text[i:m.start()].strip())
        close = text.find("```", m.end())
        if close == -1: buf.append(text[m.end():].strip()); break
        lang = (m.group(1) or "").lower(); body = text[m.end():close]
        if lang in ("python", "py", "python3", ""):
            if buf: cells.append(("md", "\n\n".join(buf))); buf = []
            cells.append(("code", add_demo_if_def(body.rstrip("\n"))))
        else:
            if buf: cells.append(("md", "\n\n".join(buf))); buf = []
            cells.append(("md", f"```{lang}\n{body.rstrip(chr(10))}\n```"))
        i = close + 3
    if buf: cells.append(("md", "\n\n".join(buf)))
    return [{"cell_type": t, "metadata": {}, "source": to_source(c)} if t == "md"
            else {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": to_source(c)}
            for t, c in cells]

def py_cells(text):
    lines, cells, cur, started = text.split("\n"), [], [], [], False
    ind = lambda s: len(s) - len(s.lstrip(" "))
    for ln in lines:
        if re.match(r"^(def |class |async def )", ln) and (not started or ind(ln) == 0):
            if cur: cells.append("\n".join(cur).strip()); cur = []
            started = True
        cur.append(ln)
    if cur: cells.append("\n".join(cur).strip())
    return [add_demo_if_def(c) for c in cells if c.strip()]

def build(path, out_dir=None):
    name = os.path.basename(path)
    txt = open(path, encoding="utf-8").read()
    cells = md_cells(txt) if name.endswith(".md") else \
        [{"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": to_source(c)}
         for c in py_cells(txt)]
    nb = {"cells": cells, "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "colab": {"provenance": [], "toc_visible": True}}, "nbformat": 4, "nbformat_minor": 0}
    out = os.path.join(out_dir or os.path.dirname(path) or ".",
                     name.rsplit(".", 1)[0] + ".ipynb")
    json.dump(nb, open(out, "w"), indent=1, ensure_ascii=False)
    demos = sum(1 for c in cells if c["cell_type"] == "code" and "# --- demo ---" in "".join(c["source"]))
    print(f"wrote {out}  cells={len(cells)} demos={demos}")

if __name__ == "__main__":
    out = None
    files = sys.argv[1:]
    if "--out" in files:
        i = files.index("--out"); out = files[i+1]; files = files[:i] + files[i+2:]
    for f in files: build(f, out)
