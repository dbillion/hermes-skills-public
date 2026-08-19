---
name: resume-cv-creation
description: "Create, tailor, and format CVs/resumes for specific purposes — visa applications, job applications, career changes. Includes PDF generation pipeline with fpdf2."
triggers:
  - cv
  - resume
  - visa cv
  - cover letter
  - application document
  - tailored resume
  - immigration document
---

# Resume & CV Creation

Create purpose-tailored CV/resume documents and deliver them as formatted PDFs.

## Core Workflow

### 1. Determine Purpose

Ask (or infer from context) what the CV is for:

| Purpose | Key Requirements |
|---------|-----------------|
| **Job application** | Match job posting keywords, quantify achievements, relevant experience only |
| **Visa / immigration** | EU-format personal details (DOB, nationality, photo placeholder), employer name + dates, clear work history, match visa category (work, entrepreneur, etc.) |
| **Career change** | Emphasize transferable skills, reframe experience for new domain |
| **Academic** | Research focus, publications, education first, longer format OK |

### 2. Gather Content

Extract relevant experience from:
- Existing CV files (check `career-ops/cv.md` or user's working directory)
- User-provided details (dates, roles, companies, metrics)
- LinkedIn profile or past session context

**Rules:**
- Never fabricate dates, titles, or employers
- If user says "focus on X from year A to B", filter experience accordingly
- Quantify where possible (orders delivered, revenue impact, team size, %)
- For visa CVs: include standard EU personal details at top

### 3. Structure & Tailor

**Standard sections (order varies by purpose):**

1. Contact header (name, DOB, nationality, phone, email, address) — required for visa
2. Professional Summary (2-3 sentences, tailored to purpose)
3. Work Experience (reverse chronological, most relevant first)
4. Education
5. Skills / Technical Stack
6. Languages
7. Additional Info (driving licence, availability, etc.)

**Tailoring tactics:**
- Lead with the most relevant experience for the target
- Remove or minimize irrelevant roles
- Use keywords from the specific job posting or visa category
- For food-delivery visa: emphasize logistics, food safety, customer ratings, peak-period volume
- For tech roles: emphasize technologies, scale, architecture decisions

### 4. Generate PDF

Use the `fpdf2` pipeline. See [references/pdf-generation.md](references/pdf-generation.md) for the exact setup and script.

**Default build command:**
```bash
python3 <hermes_home>/skills/resume-cv-creation/scripts/cv-to_pdf.py <input.md> <output.pdf>
```

The script uses fpdf2 with DejaVu fonts (system TTF) for clean output.

**Font setup (one-time system dependency):**
```bash
# Install fpdf2
pip3 install --break-system-packages fpdf2

# Verify DejaVu fonts exist (usually pre-installed on Arch/Ubuntu)
ls /usr/share/fonts/TTF/DejaVuSans*.ttf
```

If DejaVu fonts are missing, the script falls back to Helvetica but output quality decreases for non-ASCII characters.

### 5. Deliver & Iterate

- Upload the PDF via MEDIA path
- Confirm the user can open it
- Iterate immediately on content/layout changes — visa CVs often need multiple rounds
- Remind user to fill in any placeholder fields (DOB, photo if applicable)

## EU Visa CV Format

When creating a visa/immigration CV (Poland, Germany, etc.):

**Required personal details (top of page):**
- Full legal name
- Date of birth (DD/MM/YYYY format)
- Nationality
- Gender (some countries require)
- Passport number (if requested)

**Work experience format:**
- Company name + location + dates (Month YYYY – Month YYYY or Present)
- Job title
- Key responsibilities as bullet points (6-10 per role)
- Quantified achievements where relevant

**Language:** Standard English unless the consulate requires the local language

**Common visa categories and their CV emphasis:**
- **Work visa (Poland):** Match the job offer description, show relevant experience duration
- **Entrepreneur/business visa:** Show business ownership, revenue, employees, permits
- **Student visa:** Education focus, enrollment proof, relevant work

## Pitfalls

- **Don't fabricate experience** — if user says "I worked at X from 2022-2026", use exactly that. Don't invent metrics unless user provides them.
- **Don't use the wrong Python** — fpdf2 may be installed in the Hermes venv (`~/.hermes/hermes-agent/venv/bin/python3`), not system python3. Always use the venv python or the dedicated script.
- **Don't forget placeholder reminders** — visa CVs often have `[DD/MM/YYYY]` or `[Address]` fields the user must fill in manually. Always flag these.
- **Don't over-format** — visa officers prefer clean, scannable layouts. Avoid columns, graphics, or fancy formatting. Simple section headers with lines work best.
- **Don't assume dates** — if user says "2022 to 2026", confirm whether it's inclusive or if they're still working there ("Present").
- **Don't skip the summary** — a 2-3 sentence professional summary at the top frames the entire document. Tailor it to the specific visa/job purpose.

## Templates

See [templates/cv-poland-food-delivery.md](templates/cv-poland-food-delivery.md) for a ready-to-use Poland food-delivery visa CV template (Wolt/Bolt Food format).

## Related Skills

- `interview-prep` — for job application follow-up after CV is done
- `ocr-and-documents` — for extracting text from existing PDF CVs
- `nano-pdf` — for editing text in generated PDFs
