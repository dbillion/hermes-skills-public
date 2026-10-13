#!/usr/bin/env python3
"""Generate a GitHub-safe rich-media README from a JSON item list.

Each item:
  {"heading": "Q1. Find the maximum sum subarray (...)",
   "topic": "Arrays_Subarrays", "base": "q1_max_sum_subarray",
   "cat": "Q",                                                # Q/A/S/F/B grouping
   "diagram_png": "docs/diagrams/Q1_maxSumSubarray.png",      # optional, path checked
   "func": "public static int f() { ... }",                   # real source
   "test": "assertEquals(6, f());",                            # real @Test body
   "gif": "explainer_videos/gifs/Q01_MaxSumSubarray.gif"}      # optional

Usage:
  python3 generate_rich_readme.py items.json > README_NEW.md

Emits: title + Index (by sentence) + per-category blocks using HTML <table> with
<pre><code> so code renders; colspan=3 <img> for full-width gif. GFM-safe: no
mermaid / no fenced code inside Markdown table cells.
"""
import json, html, sys, os


def esc(s):
    return html.escape(s or "")


def codeblock(s, lang="java"):
    if not s:
        return "<em>(source not extracted)</em>"
    return f"<pre><code class=\"language-{lang}\">{esc(s.strip())}</code></pre>"


def block(it):
    gif = it.get("gif")
    diag = it.get("diagram_png")
    diagcell = (f'<p><img src="{esc(diag)}" alt="diagram" width="260"></p>'
                if diag and os.path.exists(diag) else '<p><em>(no diagram)</em></p>')
    gifrow = (f'<p align="center"><img src="{esc(gif)}" alt="{esc(gif)}" width="100%"></p>'
              if gif else '<p align="center"><strong>GIF: pending</strong></p>')
    return (f"\n### {esc(it['heading'])}\n\n"
            f"<p><sub>topic: <strong>{esc(it.get('topic', ''))}</strong> · "
            f"<code>{esc(it.get('base', ''))}</code></sub></p>\n\n"
            f"| Diagram | Function | Unit test |\n|---|---|---|\n"
            f"| {diagcell} | {codeblock(it.get('func'))} | {codeblock(it.get('test'))} |\n\n"
            f"{gifrow}\n")


def main():
    items = json.load(open(sys.argv[1]))
    cats = {}
    for it in items:
        c = it.get("cat") or (it["base"][0].upper() if it.get("base") else "X")
        cats.setdefault(c, []).append(it)
    order = [c for c in ["Q", "A", "S", "F", "B", "X"] if c in cats]
    cat_name = {"Q": "Interview Questions", "A": "Algorithms",
                "S": "Single-Path", "F": "Graph Extras", "B": "Graph Extras", "X": "Other"}
    out = ["# Visual Explainers\n",
           "\n> Each item shows the real problem statement, its diagram, the actual "
           "function, the unit test, then the animation.\n",
           "## Index\n"]
    for c in order:
        out.append(f"\n### {cat_name[c]}\n")
        for it in cats[c]:
            out.append(f"- {esc(it['heading'])}")
    out.append("")
    for c in order:
        out.append(f"\n## {cat_name[c]}\n")
        for it in cats[c]:
            out.append(block(it))
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
