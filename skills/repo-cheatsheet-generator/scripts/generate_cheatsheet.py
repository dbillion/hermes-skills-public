#!/usr/bin/env python3
"""
Generate a printable repo/library cheat sheet (PDF + companion markdown)
from a cheatsheet.json file (see references/template_schema.md).

Usage:
    python3 generate_cheatsheet.py --data cheatsheet.json --out cheatsheet.pdf
"""
import argparse
import json
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, KeepTogether
)
from reportlab.lib.enums import TA_LEFT

# Fixed accent color palette, cycled per section
PALETTE = [
    colors.HexColor("#1B4F72"),  # navy
    colors.HexColor("#117864"),  # teal
    colors.HexColor("#7D3C98"),  # purple
    colors.HexColor("#B9770E"),  # amber
    colors.HexColor("#A93226"),  # rust
    colors.HexColor("#2874A6"),  # blue
]
CODE_BG = colors.HexColor("#F4F4F4")
TIP_BG = colors.HexColor("#FEF9E7")
TABLE_HEADER_BG = colors.HexColor("#EAECEE")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("Body9", parent=styles["BodyText"], fontSize=9.5, leading=13))
styles.add(ParagraphStyle("CodeBox", parent=styles["Code"], fontSize=8.5, leading=11,
                           backColor=CODE_BG, borderPadding=6))
styles.add(ParagraphStyle("Tagline", parent=styles["BodyText"], fontSize=11,
                           textColor=colors.HexColor("#555555")))


def section_header(text, color):
    style = ParagraphStyle(
        f"H_{text}", parent=styles["Heading2"], textColor=colors.white,
        backColor=color, borderPadding=(6, 8, 6, 8), fontSize=13,
        spaceAfter=8, spaceBefore=14,
    )
    return Paragraph(text, style)


def bullet_list(items):
    return ListFlowable(
        [ListItem(Paragraph(i, styles["Body9"]), leftIndent=10) for i in items],
        bulletType="bullet", start="•", leftIndent=14,
    )


def table_from_rows(headers, rows, col_widths):
    data = [headers] + rows
    wrapped = [[Paragraph(str(c), styles["Body9"]) for c in row] for row in data]
    t = Table(wrapped, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_BG),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDBDBD")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def code_block(code):
    escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    escaped = escaped.replace("\n", "<br/>")
    box = Table([[Paragraph(escaped, styles["CodeBox"])]], colWidths=[6.9 * inch])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return box


def tip_box(text):
    box = Table([[Paragraph(f"<b>Tip:</b> {text}", styles["Body9"])]], colWidths=[6.9 * inch])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TIP_BG),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#F1C40F")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return box


def build_pdf(data, out_path):
    doc = SimpleDocTemplate(
        out_path, pagesize=letter,
        topMargin=0.5 * inch, bottomMargin=0.5 * inch,
        leftMargin=0.55 * inch, rightMargin=0.55 * inch,
    )
    story = []
    colors_cycle = iter(PALETTE * 10)

    # Title
    story.append(Paragraph(data["title"], ParagraphStyle(
        "Title", parent=styles["Title"], fontSize=24, textColor=PALETTE[0])))
    story.append(Paragraph(data["tagline"], styles["Tagline"]))
    story.append(Spacer(1, 10))

    # 1. Overview
    story.append(section_header("1. OVERVIEW", next(colors_cycle)))
    story.append(bullet_list(data["overview_bullets"]))
    story.append(Spacer(1, 6))
    story.append(tip_box(data["analogy"]))

    # 2. Core components
    story.append(section_header("2. CORE COMPONENTS", next(colors_cycle)))
    rows = [[c["name"], c["purpose"], c["example"]] for c in data["components"]]
    story.append(table_from_rows(
        ["Name", "Purpose", "Example"], rows,
        [1.3 * inch, 2.8 * inch, 2.8 * inch]))

    # 3. Examples
    story.append(section_header("3. CODE EXAMPLES", next(colors_cycle)))
    for ex in data["examples"]:
        block = [Paragraph(f"<b>{ex['label']}</b>", styles["Body9"]),
                 Spacer(1, 2), code_block(ex["code"]), Spacer(1, 6)]
        story.append(KeepTogether(block))

    # 4. Conventions
    story.append(section_header("4. CONVENTIONS", next(colors_cycle)))
    rows = [[c["pattern"], c["example"]] for c in data["conventions"]]
    story.append(table_from_rows(["Pattern", "Example"], rows,
                                  [2.2 * inch, 4.7 * inch]))

    # 5. Setup
    story.append(section_header("5. SETUP", next(colors_cycle)))
    story.append(code_block(data["setup_code"]))

    # 6. Resolution order (optional)
    if data.get("resolution_order"):
        story.append(section_header("6. HOW IT RESOLVES THINGS", next(colors_cycle)))
        items = [f"{i+1}. {step}" for i, step in enumerate(data["resolution_order"])]
        story.append(bullet_list(items))

    # 7. Best practices
    story.append(section_header("7. BEST PRACTICES", next(colors_cycle)))
    story.append(bullet_list(data["best_practices"]))

    # 8. Common errors
    story.append(section_header("8. COMMON ERRORS & SOLUTIONS", next(colors_cycle)))
    rows = [[e["error"], e["cause"], e["fix"]] for e in data["common_errors"]]
    story.append(table_from_rows(["Error", "Cause", "Fix"], rows,
                                  [1.6 * inch, 2.5 * inch, 2.8 * inch]))

    # 9. Quick revision
    story.append(section_header("9. QUICK REVISION CHECKLIST", next(colors_cycle)))
    story.append(bullet_list([f"\u2610 {item}" for item in data["quick_revision"]]))

    doc.build(story)


def build_markdown(data, out_path):
    lines = [f"# {data['title']}", f"_{data['tagline']}_", ""]
    lines.append("## 1. Overview")
    lines += [f"- {b}" for b in data["overview_bullets"]]
    lines.append(f"\n> **Analogy:** {data['analogy']}\n")

    lines.append("## 2. Core Components")
    lines.append("| Name | Purpose | Example |")
    lines.append("|---|---|---|")
    for c in data["components"]:
        lines.append(f"| {c['name']} | {c['purpose']} | `{c['example']}` |")

    lines.append("\n## 3. Code Examples")
    for ex in data["examples"]:
        lines.append(f"**{ex['label']}**")
        lines.append(f"```\n{ex['code']}\n```")

    lines.append("## 4. Conventions")
    lines.append("| Pattern | Example |")
    lines.append("|---|---|")
    for c in data["conventions"]:
        lines.append(f"| {c['pattern']} | {c['example']} |")

    lines.append(f"\n## 5. Setup\n```\n{data['setup_code']}\n```")

    if data.get("resolution_order"):
        lines.append("\n## 6. How It Resolves Things")
        for i, step in enumerate(data["resolution_order"], 1):
            lines.append(f"{i}. {step}")

    lines.append("\n## 7. Best Practices")
    lines += [f"- {b}" for b in data["best_practices"]]

    lines.append("\n## 8. Common Errors & Solutions")
    lines.append("| Error | Cause | Fix |")
    lines.append("|---|---|---|")
    for e in data["common_errors"]:
        lines.append(f"| {e['error']} | {e['cause']} | {e['fix']} |")

    lines.append("\n## 9. Quick Revision Checklist")
    lines += [f"- [ ] {q}" for q in data["quick_revision"]]

    Path(out_path).write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True, help="Output .pdf path")
    args = ap.parse_args()

    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)

    required = ["title", "tagline", "overview_bullets", "analogy", "components",
                "examples", "conventions", "setup_code", "best_practices",
                "common_errors", "quick_revision"]
    missing = [k for k in required if k not in data or data[k] in ([], "", None)]
    if missing:
        sys.exit(f"cheatsheet.json missing required fields: {missing}")

    out_pdf = args.out
    out_md = str(Path(args.out).with_suffix(".md"))

    build_pdf(data, out_pdf)
    build_markdown(data, out_md)
    print(f"Wrote {out_pdf} and {out_md}")


if __name__ == "__main__":
    main()
