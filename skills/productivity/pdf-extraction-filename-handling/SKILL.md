---
name: pdf-extraction-filename-handling
description: "Best practices for extracting text from PDFs when filenames contain spaces or special characters."
version: 1.0.0
category: productivity
---

# PDF Text Extraction – Handling Filenames with Spaces and Special Characters

When extracting text from PDFs whose filenames contain spaces, parentheses, or other special characters, naive command‑line calls can fail because the shell splits the name on whitespace.

## Recommended Approaches

### 1. Quote the filename in shell commands
Always wrap the path in quotes when invoking tools directly:

```bash
pdftotext "/path/to/file with spaces.pdf" -
```

### 2. Use the helper scripts from the `ocr-and-documents` skill
The helper scripts `extract_pymupdf.py` and `extract_marker.py` already accept a path argument and handle quoting internally, but you must still quote the argument when calling them from a shell:

```bash
python /path/to/extract_pymupdf.py "/path/to/file with spaces.pdf"
```

### 3. When invoking from Python (e.g., via `execute_code`)
Pass the string as‑is; no extra quoting is needed:

```python
import subprocess
subprocess.run(["pdftotext", "/path/to/file with spaces.pdf", "-"], capture_output=True, text=True)
```

### 4. Alternative: Use `web_extract` for URLs
If the PDF is accessible via a URL, prefer `web_extract` which avoids filesystem quoting issues entirely.

### 5. Troubleshooting
If you still see `FileNotFoundError`, verify:
- The file exists at the exact path (use `ls -l` to confirm).
- There are no hidden trailing spaces.
- You have read permissions.

## Related Skills
- `ocr-and-documents` – core PDF/text extraction (pymupdf, marker-pdf)
- `powerpoint` – PPTX extraction via python-pptx
- `docx` – DOCX extraction via python-docx (see note in ocr-and-documents)

## References
- Session-specific notes: see `references/session-2026-07-01.md` (created after this session).