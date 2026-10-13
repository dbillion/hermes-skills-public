#!/usr/bin/env python3
"""Known-good NotebookLM deck pipeline template (distilled from a real DSA-quiz run).

Fixes captured as pitfalls in SKILL.md:
  * Code dropped by NotebookLM -> feed method+test as IMAGE sources, force verbatim embed.
  * Merge silently fails -> call pdfunite via RAW subprocess.run (never through an nlm-prepending helper).
  * Stale partial re-merge -> support selective re-run via job-index arg so you can rebuild ONE
    partial without trusting an old sibling PDF.

Usage:
  python3 gen_deck_pipeline.py            # run all JOBS, merge all
  python3 gen_deck_pipeline.py 3          # run only JOBS[3] (then manually re-merge + compress)

Env assumptions:
  * `nlm` CLI on PATH, profiles pre-logged (mentora/trinity/glorious/...).
  * code-card PNGs already rendered into CARDDIR via render_code_cards.py.
"""
import subprocess, json, os, time, sys

OUT = "/home/deeone/Desktop/quiz"
STYLE = "/home/deeone/Desktop/template/master-sketchnote-skill.md"
TMPL = "/home/deeone/Desktop/template/template-one.jpg"
SRCDIR = f"{OUT}/sources"
CARDDIR = f"{OUT}/codecards"

FOCUS = ("Create a quiz slide deck from the per-question sources. "
         "RULES: (1) ONE question per slide, in source order. "
         "(2) Print the exact question verbatim as the slide heading. "
         "(3) CODE IS SUPPLIED AS READY-MADE IMAGES (qNN_method / qNN_test). "
         "You MUST place BOTH images onto the slide EXACTLY as given — do NOT redraw, retype, "
         "paraphrase, or omit any code. This is mandatory. "
         "(4) Sketchnote aesthetic: pastel boxes, numbered sections, Follow/Share/Comment/Save footer. "
         "(5) Sections: Problem, Why it matters, Complexity, Common mistakes (X), Checklist (check), SAVE CTA. "
         "(6) Short bullets (<=8 words).")

# (profile, notebook_name, qrange, out_pdf)
JOBS = [
    ("mentora",  "DSA-Q-A", range(1, 19),   f"{OUT}/deck_a.pdf"),
    ("trinity",  "DSA-Q-B", range(19, 37),  f"{OUT}/deck_b.pdf"),
    ("glorious", "DSA-Q-C", range(37, 49),  f"{OUT}/deck_c.pdf"),
    ("mentora",  "DSA-Q-D", range(49, 56),  f"{OUT}/deck4_1.pdf"),  # enable for q49-55
]

ONLY = int(sys.argv[1]) if len(sys.argv) > 1 else None

def run(args, retries=10):
    delay = 20
    for _ in range(1, retries + 1):
        r = subprocess.run(["nlm"] + args, capture_output=True, text=True)
        msg = (r.stderr or r.stdout).strip()
        if "RESOURCE_EXHAUSTED" in msg or "rate limit" in msg.lower():
            time.sleep(delay); delay = min(delay * 2, 300); continue
        if r.returncode == 0 and r.stdout.strip():
            return r
        time.sleep(10)
    return r

def j(o):
    try: return json.loads(o.stdout)
    except Exception: return None

def switch(p):
    run(["login", "switch", p]); print(f"switched to {p}")

def nb_id(name, profile):
    switch(profile)
    d = j(run(["notebook", "list", "--profile", profile, "--json"]))
    if d:
        for n in d:
            if n["title"] == name:
                print(f"  reuse {name} {n['id']}"); return n["id"]
    d = j(run(["notebook", "create", name, "--json"]))
    return d["notebook_id"] if d else None

def src_ids(nb):
    for _ in range(5):
        d = j(run(["source", "list", nb, "--json"]))
        if d is not None:
            return {s["title"].split()[0]: s["id"] for s in d if "question" in s["title"]}
        time.sleep(15)
    return {}

def gen(name, qrange, out_pdf, profile):
    nb = nb_id(name, profile)
    if not nb: print(f"[{name}] no notebook"); return False
    have = src_ids(nb)
    if "Sketchnote" not in have:
        run(["source", "add", nb, "--file", STYLE, "--title", "Sketchnote Style Skill", "--wait"])
    if "Template" not in have:
        run(["source", "add", nb, "--file", TMPL, "--title", "Template Reference", "--wait"])
    have = src_ids(nb)
    for n in qrange:
        key = f"q{n:02d}"
        if key not in have:
            run(["source", "add", nb, "--file", f"{SRCDIR}/{key}.md", "--title", f"{key} question", "--wait"])
        for k in (f"{key}_method", f"{key}_test"):
            if k not in have and os.path.exists(f"{CARDDIR}/{k}.png"):
                run(["source", "add", nb, "--file", f"{CARDDIR}/{k}.png", "--title", f"{k} code (verbatim image)", "--wait"])
    have = src_ids(nb)
    ids = [have[f"q{n:02d}"] for n in qrange]
    for n in qrange:
        for k in (f"q{n:02d}_method", f"q{n:02d}_test"):
            if k in have: ids.append(have[k])
    r = run(["slides", "create", nb, "--format", "detailed_deck", "--length", "default",
             "--confirm", "--source-ids", ",".join(ids), "--focus", FOCUS, "--json"])
    d = j(r)
    if not d or "artifact_id" not in d:
        print(f"[{name}] FAIL {r.stdout[:160]}"); return False
    art = d["artifact_id"]; print(f"[{name}] art {art}")
    for i in range(90):
        st = j(run(["studio", "status", nb, "--json"]))
        s = st[0]["status"] if isinstance(st, list) else (st or {}).get("status")
        if s == "completed":
            print(f"[{name}] done ~{i*20}s"); break
        time.sleep(20)
    run(["download", "slide-deck", nb, "--id", art, "--output", out_pdf])
    return os.path.exists(out_pdf)

pdfs = []
for profile, name, qrange, pdf in (JOBS if ONLY is None else [JOBS[ONLY]]):
    (pdfs.append(pdf) if gen(name, qrange, pdf, profile) else print(f"!! {name} failed"))

if ONLY is not None:
    print(f"JOB {ONLY} done -> {pdfs}"); sys.exit(0)

if len(pdfs) == len(JOBS):
    all4 = [f"{OUT}/deck_a.pdf", f"{OUT}/deck_b.pdf", f"{OUT}/deck_c.pdf", f"{OUT}/deck4_1.pdf"]
    subprocess.run(["pdfunite"] + all4 + [f"{OUT}/dsa-java-quiz-deck.pdf"], check=True)  # RAW, not via run()
    info = subprocess.run(["pdfinfo", f"{OUT}/dsa-java-quiz-deck.pdf"], capture_output=True, text=True).stdout
    print("MERGED", [l for l in info.splitlines() if l.startswith("Pages")])
else:
    print("ONLY", len(pdfs), "decks:", pdfs)
