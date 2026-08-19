# Local fallback: analyze the exported notes directly when NotebookLM query quota is exhausted

## When to use
`nlm query notebook` starts returning `{"status":"error","error":"NotebookLM temporarily rejected the query because a usage limit was reached."}` (or `RESOURCE_EXHAUSTED` / `429`) and does NOT clear after retries/sleeps. This is the **daily query cap**, which in practice is shared across the `nlm` profiles (dayozoe, abiodun, and the owner account all hit the same limit in one session). Profile rotation fixes *upload/generation* 429s but NOT this daily query wall.

**Do NOT** keep retrying with longer sleeps — you'll burn the session. Pivot to local analysis of the decrypted export instead. (User preference, stated explicitly: "Pivot now: I analyze the local decrypted note export directly and build both PDFs today (no waiting)".)

## Prerequisites
You already have a decrypted, redacted markdown export from the ColorNote pipeline, e.g.:
`/home/deeone/Downloads/colornote_notes_redacted_2010-2026.md`
Each note is formatted as:
```
### <Title> _(YYYY-MM-DD HH:MM)_

<body text>
```

## Step 1 — parse notes
```python
import re
text = open(SRC, encoding="utf-8").read()
pat = re.compile(r"### (.+?) _\((\d{4}-\d{2}-\d{2})[ \d:]*\)_\s*\n(.*?)(?=\n### |\Z)", re.S)
notes = [{"title":m.group(1).strip(),"date":m.group(2),"year":int(m.group(2)[:4]),"body":m.group(3).strip()}
         for m in pat.finditer(text)]
def search(terms, years=None, limit=60):
    return [n for n in notes if (not years or n["year"] in years)
            and any(t.lower() in (n["title"]+" "+n["body"]).lower() for t in terms)][:limit]
```
(Parsed ~2,346 of 2,377 notes; ~31 multi-line edge cases dropped — acceptable.)

## Step 2 — apply frameworks against the real text
Grounded frameworks that work well on a personal-notes corpus (cite by note date):
- **VIA Character Strengths** (Peterson & Seligman) — spirituality, hope, leadership, perseverance, honesty.
- **Self-Determination Theory** (Deci & Ryan) — intrinsic/autonomy vs fear-driven ("Air Force as fail-safe") goals; internally-owned goals persisted, fear-driven abandoned.
- **Dweck Growth Mindset** — attribution style after failure (effort vs prophecy/fate vs fixed "lack of integrity").
- **Pennebaker linguistic markers** — insight/causation words, tense shifts (aspirational future vs planned future = rumination-adjacent incompletion).
- **Lazarus & Folkman coping** — problem- vs emotion- vs meaning/spiritual-reframing (notes skew heavily to spiritual reframe).
- **Gollwitzer implementation intentions** — vision ("employ thousands") vs "if-then" concrete plans; the 2019 `[V]` checkmark / "Work Done" reports ARE the proven winning pattern.
Synthesize into two deliverables: **execution/follow-through** angle and **emotional/well-being** angle.

## Step 3 — render PDFs with pandoc
`pandoc input.md -o out.pdf` works (pdflatex present). Produce:
- `colornote_psych_execution.pdf` — execution angle
- `colornote_psych_wellbeing.pdf` — well-being angle
- `colornote_psych_analysis_full.pdf` — master (all frameworks + both angles)
Verify: `file out.pdf` → "PDF document".

## Step 4 — deliver
Upload to Drive via `gws drive +upload out.pdf --name out.pdf` (gws sets `application/pdf` correctly for PDFs, unlike the octet-stream forced on other types). Share/attach to the relevant notebook if desired. Send via `MEDIA:/path`.

## Why this is durable
The export is complete and self-contained; local analysis needs no quota and produces cited, defensible output. The only loss vs NotebookLM RAG is auto-citations — mitigate by quoting note dates inline (as above).
