#!/usr/bin/env python3
"""Assemble many per-topic cheatsheet PDFs into one navigable book.

Produces:
  - A cover page
  - A Table of Contents page (page numbers + section grouping)
  - Native PDF outline bookmarks (sidebar navigator): Section -> Algorithm
  - Each topic chapter kept intact (its own pages)

Dependencies: reportlab + pypdf (install into the venv you run this from).
Usage:
  python build_book.py --root /path/to/cheatsheets --out out --dest Book.pdf
  # --root holds a manifest.json [{id,title,section}] and an out/ dir of <id>_cheatsheet.pdf
"""
import json, os, datetime, argparse
from xml.sax.saxutils import escape

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle)

# Section grouping by id prefix; override set for cross-prefix topics.
SECTION_NAMES = {
    "A": "Sorting & Classic Algorithms",
    "Q": "Coding Interview Questions",
    "S": "Data Structures & Algorithms",
}
GRAPH_IDS = {
    "Astar", "BellmanFord", "FloodFill", "FloydWarshall",
    "S03_BFS", "S09_DFS", "S10_UnionFind", "S11_Kruskal", "S12_TopoSort",
    "S13_NumIslands", "S14_Dijkstra", "S15_CycleUndirected", "S16_Bipartite",
    "S17_ConnectedComponents", "S18_Bridges",
}

def section_for(aid):
    if aid in GRAPH_IDS:
        return "Graph Algorithms"
    return SECTION_NAMES.get(aid[0], "Other")


def build_cover(dest_pdf, n_algo, n_ids):
    styles = getSampleStyleSheet()
    cover_style = ParagraphStyle("cover", parent=styles["Title"], fontSize=26,
                                 alignment=TA_CENTER, spaceAfter=14)
    sub_style = ParagraphStyle("sub", parent=styles["Normal"], fontSize=13,
                               alignment=TA_CENTER, textColor="#444444")
    today = datetime.date.today().isoformat()
    doc = SimpleDocTemplate(dest_pdf, pagesize=letter)
    el = [
        Spacer(1, 2.0 * inch),
        Paragraph("DSA Cheat Sheet Book", cover_style),
        Spacer(1, 0.2 * inch),
        Paragraph(f"{n_ids} algorithms &middot; {n_algo} pages", sub_style),
        Spacer(1, 0.15 * inch),
        Paragraph(f"Generated {today}", sub_style),
    ]
    doc.build(el)


def build_toc(dest_pdf, entries):
    styles = getSampleStyleSheet()
    toc_title_style = ParagraphStyle("toct", parent=styles["Title"], fontSize=18,
                                     spaceAfter=10)
    sec_style = ParagraphStyle("sec", parent=styles["Heading2"], fontSize=13,
                               spaceBefore=10, spaceAfter=4, textColor="#1a3e6e")
    doc = SimpleDocTemplate(dest_pdf, pagesize=letter,
                            topMargin=0.7 * inch, bottomMargin=0.6 * inch,
                            leftMargin=0.9 * inch, rightMargin=0.9 * inch)
    el = [Paragraph("Table of Contents", toc_title_style)]
    seen, grouped = [], {}
    for sec, atitle, pg in entries:
        grouped.setdefault(sec, []).append((atitle, pg))
        if sec not in seen:
            seen.append(sec)
    for sec in seen:
        el.append(Paragraph(escape(sec), sec_style))
        rows = [[escape(t), str(p)] for t, p in grouped[sec]]
        t = Table(rows, colWidths=[5.4 * inch, 0.7 * inch])
        t.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -1), 0.25, "#dddddd"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ]))
        el.append(t)
    doc.build(el)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/home/deeone/dsa-cheatsheets")
    ap.add_argument("--out", default="out")
    ap.add_argument("--dest", default="DSA_Cheatsheet_Book.pdf")
    a = ap.parse_args()

    OUT = os.path.join(a.root, a.out)
    canon = json.load(open(os.path.join(a.root, "manifest.json")))
    ids = [r["id"] for r in canon]
    titles = {r["id"]: r["title"] for r in canon}

    pdf_paths = []
    for i in ids:
        p = os.path.join(OUT, f"{i}_cheatsheet.pdf")
        if not os.path.exists(p):
            raise SystemExit(f"MISSING PDF for {i}")
        pdf_paths.append(p)

    # merge topic PDFs into one writer (PdfReader has no add_page)
    algo_writer = PdfWriter()
    algo_start = {ids[0]: 0}
    for k, p in enumerate(pdf_paths):
        r = PdfReader(p)
        if k > 0:
            algo_start[ids[k]] = len(algo_writer.pages)
        for pg in r.pages:
            algo_writer.add_page(pg)
    n_algo = len(algo_writer.pages)
    print(f"Merged {len(ids)} PDFs -> {n_algo} algorithm pages")

    # two-pass TOC: placeholder first to learn n_toc, then real page numbers
    placeholder = [(section_for(i), titles[i], 0) for i in ids]
    tmp_toc = "/tmp/_toc.pdf"
    build_toc(tmp_toc, placeholder)
    n_toc = len(PdfReader(tmp_toc).pages)

    final_page = {}
    for i in ids:
        final_page[i] = 1 + n_toc + algo_start[i] + 1   # 1-based
    real_entries = [(section_for(i), titles[i], final_page[i]) for i in ids]
    build_toc(tmp_toc, real_entries)
    assert len(PdfReader(tmp_toc).pages) == n_toc, "TOC page count shifted"

    writer = PdfWriter()
    build_cover("/tmp/_cover.pdf", n_algo, len(ids))
    for pg in PdfReader("/tmp/_cover.pdf").pages:
        writer.add_page(pg)
    for pg in PdfReader(tmp_toc).pages:
        writer.add_page(pg)
    for pg in algo_writer.pages:
        writer.add_page(pg)

    # outline bookmarks
    writer.add_outline_item("Cover", 0)
    toc_item = writer.add_outline_item("Table of Contents", 1)
    last_sec = None
    sec_items = {}
    for i in ids:
        sec = section_for(i)
        if sec != last_sec:
            dest0 = 1 + n_toc + algo_start[i]
            sec_items[sec] = writer.add_outline_item(sec, dest0, parent=toc_item)
            last_sec = sec
        writer.add_outline_item(titles[i], 1 + n_toc + algo_start[i],
                                parent=sec_items[sec])

    writer.add_metadata({
        "/Title": "Cheat Sheet Book",
        "/Author": "pdf-book-builder",
        "/CreationDate": datetime.datetime.now().strftime("D:%Y%m%d%H%M%S"),
    })
    with open(os.path.join(a.root, a.dest), "wb") as f:
        writer.write(f)
    print(f"WROTE {os.path.join(a.root, a.dest)} | total pages {len(writer.pages)}")


if __name__ == "__main__":
    main()
