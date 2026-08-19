# PDF Generation Pipeline

## Overview

Convert markdown CVs to styled A4 PDFs using `fpdf2` with DejaVu fonts.

## Dependencies

```bash
# Install fpdf2 (system-wide, since venv python may not be in PATH)
pip3 install --break-system-packages fpdf2

# DejaVu fonts — usually pre-installed on Arch/Ubuntu
# Verify:
ls /usr/share/fonts/TTF/DejaVuSans*.ttf
# If missing: sudo pacman -S ttf-dejavu  (Arch) or apt install fonts-dejavu (Ubuntu)
```

## Script Location

`scripts/cv-to_pdf.py` — standalone Python script that converts markdown CV to styled PDF.

## Usage

```bash
# With Hermes venv python (recommended)
~/.hermes/hermes-agent/venv/bin/python3 scripts/cv-to_pdf.py input.md output.pdf

# Or system python3 if fpdf2 is installed there
python3 scripts/cv-to_pdf.py input.md output.pdf
```

## How It Works

1. Parses markdown: `#` → name header, `##` → section headers, `###` → job headers, `-` → bullets
2. Applies A4 page format with 2cm margins
3. Uses DejaVu Sans (regular/bold/italic) for Unicode support
4. Adds page numbers in footer
5. Handles special characters: bullet (•), en-dash (—), em-dash (—)

## System-Specific Notes (Arch Linux)

- **fpdf2 install**: Must use `pip3 install --break-system-packages fpdf2` (PEP 668 enforced)
- **Python path**: The Hermes venv is at `~/.hermes/hermes-agent/venv/bin/python3`
- **Font path**: `/usr/share/fonts/TTF/DejaVuSans.ttf` and variants
- **weasyprint alternative**: Does NOT work cleanly — PIL `_image` C extension fails when installed via `--target`. Use fpdf2 instead.
- **pandoc**: Available but requires LaTeX (`texlive`) for PDF output, which is heavy. fpdf2 is pure Python.

## Output Specs

- Page: A4 (210×297mm)
- Margins: 2cm left/right, auto bottom
- Font sizes: Name 18pt, Section headers 12pt, Body 9.5pt
- Color scheme: Black headers, dark gray body (#1a1a1a / #333333)
- File size: ~35-45KB for a single-page CV
