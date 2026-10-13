#!/usr/bin/env python3
"""Validate a DSA Manim README before commit/push.
Checks: balanced HTML tables, every gif/diagram ref resolves on disk.
Usage: python3 validate_readme.py <README.md> <repo_root>
"""
import re, os, sys

def main():
    md = sys.argv[1]
    root = sys.argv[2] if len(sys.argv) > 2 else "."
    t = open(md).read()
    tables = t.count("<table>"); tclose = t.count("</table>")
    tr = t.count("<tr>"); trc = t.count("</tr>")
    pre = t.count("<pre>"); prec = t.count("</pre>")
    print(f"tables open/close: {tables}/{tclose}  tr: {tr}/{trc}  pre: {pre}/{prec}")
    ok = (tables == tclose and tr == trc and pre == prec)
    gifs = re.findall(r'explainer_videos/gifs/([^"]+\.gif)', t)
    diags = re.findall(r'docs/diagrams/([^"]+\.png)', t)
    gif_bad = [g for g in gifs if not os.path.exists(os.path.join(root, "explainer_videos/gifs", g))]
    diag_bad = [d for d in diags if not os.path.exists(os.path.join(root, "docs/diagrams", d))]
    print(f"gif refs: {len(gifs)} broken: {gif_bad}")
    print(f"diag refs: {len(diags)} broken: {diag_bad}")
    if gif_bad or diag_bad:
        ok = False
    # cell count sanity: each table should have a colspan=3 gif row for 83 blocks
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
