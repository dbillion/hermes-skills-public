#!/usr/bin/env python3
"""
Convert a markdown CV to a styled A4 PDF.

Usage:
    python3 cv-to_pdf.py input.md output.pdf

Dependencies:
    pip3 install --break-system-packages fpdf2

Fonts:
    DejaVu Sans (system TTF) — usually at /usr/share/fonts/TTF/
    Falls back to Helvetica if not found.
"""

import sys
import os
import re

# Add hermes venv to path if needed
venv_site = os.path.expanduser("~/.hermes/hermes-agent/venv/lib/python3.11/site-packages")
if os.path.isdir(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)

from fpdf import FPDF


def find_dejavu_fonts():
    """Locate DejaVu font files on the system."""
    search_dirs = [
        "/usr/share/fonts/TTF",
        "/usr/share/fonts/dejavu",
        "/usr/local/share/fonts",
    ]
    regular = bold = italic = None
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            fp = os.path.join(d, f)
            if "DejaVuSans.ttf" == f and "Bold" not in f and "Oblique" not in f:
                regular = fp
            elif "DejaVuSans-Bold.ttf" == f:
                bold = fp
            elif "DejaVuSans-Oblique.ttf" == f:
                italic = fp
    return regular, bold, italic


def parse_markdown_to_pdf(md_text, pdf):
    """Parse markdown and write to PDF object."""
    lines = md_text.split('\n')
    in_ul = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_ul:
                in_ul = False
            continue

        # H1 — Name / title
        if re.match(r'^# [^#]', stripped):
            if in_ul:
                in_ul = False
            text = stripped[2:].strip()
            pdf.set_font('DejaVu', 'B', 18)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.ln(2)

        # H2 — Section header
        elif stripped.startswith('## '):
            if in_ul:
                in_ul = False
            text = stripped[3:].strip()
            pdf.set_font('DejaVu', 'B', 12)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(0, 0, 0)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)

        # H3 — Job header
        elif stripped.startswith('### '):
            if in_ul:
                in_ul = False
            text = stripped[4:].strip()
            pdf.set_font('DejaVu', 'B', 10.5)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font('DejaVu', 'I', 9.5)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 5, "", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

        # Horizontal rule
        elif stripped == '---':
            if in_ul:
                in_ul = False
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(4)

        # Bullet list
        elif stripped.startswith('- '):
            if not in_ul:
                in_ul = True
            text = stripped[2:].strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            pdf.set_font('DejaVu', '', 9.5)
            pdf.set_text_color(30, 30, 30)
            x = pdf.get_x()
            pdf.cell(5, 5, chr(8226) + ' ')
            pdf.multi_cell(175, 5, text)

        # Plain paragraph
        else:
            if in_ul:
                in_ul = False
            text = stripped
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            pdf.set_font('DejaVu', '', 9.5)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 5, text)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 cv-to_pdf.py <input.md> <output.pdf>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Create PDF
    pdf = CVPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Add fonts
    reg, bold, italic = find_dejavu_fonts()
    if reg:
        pdf.add_font('DejaVu', '', reg)
        pdf.add_font('DejaVu', 'B', bold or reg)
        pdf.add_font('DejaVu', 'I', italic or reg)
    else:
        # Fallback to Helvetica
        pdf.add_font('DejaVu', '', 'Helvetica')
        pdf.add_font('DejaVu', 'B', 'Helvetica-Bold')
        pdf.add_font('DejaVu', 'I', 'Helvetica-Oblique')

    pdf.add_page()
    parse_markdown_to_pdf(md_text, pdf)
    pdf.output(output_path)
    print(f"PDF created: {output_path} ({os.path.getsize(output_path)} bytes)")


class CVPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')


if __name__ == '__main__':
    main()
