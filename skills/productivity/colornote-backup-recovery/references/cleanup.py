#!/usr/bin/env python3
"""Decrypt-cleanup + redacted export for a ColorNote V2 backup.

Usage:
    python3 cleanup.py <decrypted_out.json> <out_dir>

`decrypted_out.json` is the file written by:
    java -jar colornote-decrypt.jar 0000 28 < file.backup > out.json

This strips the V2 binary separators, parses each JSON note record, drops the
account/meta record (which holds auth tokens), redacts emails inside note bodies,
and writes:
    - colornote_notes_redacted.md  (full readable, one heading per note, by date)
    - colornote_notes.csv          (id,created,modified,year,month,title,body,
                                     word_count,char_count,themes,has_url,has_email)
    - colornote_notes.json         (same rows as JSON)
No ColorNote token / credential is ever written to disk.
"""
import json, re, csv, sys, datetime, os, collections

EMAIL_RE = re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", re.I)
URL_RE = re.compile(r"https?://|www\.", re.I)
THEMES = {
    "Faith/Teaching": ["pastor", "god", "bible", "church", "prayer", "jesus", "christ",
                        "lord", "spirit", "scripture", "sermon", "preach", "faith", "gospel",
                        "psalm", "papa", "rhapsody", "zeal", "holy"],
    "Goals/Plans": ["plan", "goal", "vision", "target", "ambition", "dream", "future",
                    "resolution", "strategy", "objective", "this year", "my year", "by 20"],
    "Music/Songs": ["song", "lyric", "chorus", "hymn", "music", "worship", "melody"],
    "Work/Business": ["business", "job", "work", "company", "project", "client", "income",
                      "invest", "money", "sale", "market", "startup", "brand"],
    "Personal/Reflection": ["grateful", "thankful", "tired", "fear", "worry", "anxious",
                            "my life", "i am", "i feel", "proud", "happy", "sad", "lonely"],
    "Health": ["health", "exercise", "diet", "weight", "sleep", "doctor", "sick"],
    "People/Names": ["brother", "sister", "mum", "mom", "dad", "father", "friend",
                      "uncle", "aunt"],
}
STOP = set("the a an and or to of in is was are be for on with that this it i you we they "
            "he she my our your his her as at by from not but so if then can will do does did "
            "have has had me him them us no yes".split())


def parse(raw: bytes):
    data = raw.replace(b"\n", b"X")          # newlines only appear inside binary separators
    parts = re.split(b"\x00\x00..", data)    # \x00\x00 + 2 length bytes between records
    recs = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        try:
            recs.append(json.loads(p.decode("utf-8", "replace")))
        except Exception:
            pass
    return recs


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    raw = open(sys.argv[1], "rb").read()
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)

    recs = parse(raw)
    meta = [r for r in recs if "auth_token" in r]   # DROP — holds tokens
    notes = [r for r in recs if "title" in r]
    print(f"parsed {len(recs)} records: {len(notes)} notes, {len(meta)} meta (dropped)")

    def dt(ms):
        try:
            return datetime.datetime.fromtimestamp(int(ms) / 1000)
        except Exception:
            return None

    rows = []
    for n in notes:
        d = dt(n.get("created_date") or 0)
        m = dt(n.get("modified_date") or 0)
        title = (n.get("title") or "").strip()
        body = EMAIL_RE.sub("[user-email]", (n.get("note") or "").replace("\r", ""))
        text = (title + " " + body).lower()
        themes = [t for t, kws in THEMES.items() if any(k in text for k in kws)]
        rows.append({
            "id": n.get("_id"),
            "created": d.strftime("%Y-%m-%d %H:%M") if d else "",
            "modified": m.strftime("%Y-%m-%d %H:%M") if m else "",
            "year": d.year if d else "",
            "month": f"{d.year}-{d.month:02d}" if d else "",
            "title": title,
            "body": body,
            "word_count": len(re.findall(r"\b\w[\w']+\b", body)),
            "char_count": len(body),
            "themes": ";".join(themes),
            "has_url": bool(URL_RE.search(text)),
            "has_email": "@" in text,
        })
    rows.sort(key=lambda r: r["created"])

    with open(os.path.join(out, "colornote_notes.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    with open(os.path.join(out, "colornote_notes.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=0)

    by_year = collections.defaultdict(list)
    for r in rows:
        by_year[r["year"]].append(r)
    md = ["# ColorNote Notes — Recovered & De-identified\n",
          f"Total notes: {len(rows)}\n"]
    for y in sorted(by_year):
        md.append(f"\n## {y} ({len(by_year[y])} notes)\n")
        for r in by_year[y]:
            md.append(f"### {r['title'] or '(untitled)'} ({r['created']})\n")
            if r["body"].strip():
                md.append(r["body"].strip() + "\n")
    open(os.path.join(out, "colornote_notes_redacted.md"), "w").write("\n".join(md))

    print(f"wrote {len(rows)} notes to {out}/colornote_notes.{{csv,json,redacted.md}}")


if __name__ == "__main__":
    main()
