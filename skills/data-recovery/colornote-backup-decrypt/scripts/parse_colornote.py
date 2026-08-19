#!/usr/bin/env python3
"""End-to-end ColorNote backup recovery.

Usage:
    python3 parse_colornote.py <out.raw> [out.md]

Reads the raw decrypted stream (produced by colornote-decrypt.jar), splits it
into JSON note records, DROPS the account/meta record (which holds live tokens),
strips any Google token strings found in note bodies, and writes a redacted
Markdown export (one section per year) plus prints per-year counts.

It also prints a leak check: number of 'ya29' / 'NTA5ODg' matches in the
output (must be 0).
"""
import json, re, sys, datetime
from collections import defaultdict

def main():
    if len(sys.argv) < 2:
        print("usage: parse_colornote.py <out.raw> [out.md]")
        sys.exit(1)
    raw_path = sys.argv[1]
    md_path = sys.argv[2] if len(sys.argv) > 2 else raw_path + ".redacted.md"

    raw = open(raw_path, "rb").read()
    data = raw.replace(b"\n", b"X")
    parts = re.split(b"\x00\x00..", data)

    notes = []
    meta_count = 0
    for p in parts:
        p = p.strip()
        if not p:
            continue
        try:
            o = json.loads(p.decode("utf-8", "replace"))
        except Exception:
            continue
        if "auth_token" in o or "fb_access" in o:
            meta_count += 1   # account/meta record -> DROP (holds tokens)
            continue
        if "title" in o:
            notes.append(o)

    # Redact any Google tokens that leaked into note bodies
    token_re = re.compile(r"ya29\.[A-Za-z0-9_-]+|NTA5ODg[A-Za-z0-9+/=]+|1//[0-9A-Za-z_-]+")
    for n in notes:
        for k in ("note", "title"):
            if k in n and isinstance(n[k], str):
                n[k] = token_re.sub("[REDACTED-TOKEN]", n[k])

    notes.sort(key=lambda x: int(x.get("created_date") or 0))

    def dt(ms):
        try:
            return datetime.datetime.fromtimestamp(int(ms) / 1000)
        except Exception:
            return None

    out = ["# ColorNote Backup — Recovered Notes (REDACTED)\n"]
    out.append(f"_Total notes: {len(notes)} (meta records dropped: {meta_count})_\n")
    by_year = defaultdict(list)
    for n in notes:
        d = dt(n["created_date"])
        by_year[d.year if d else 0].append((d, n))
    for y in sorted(by_year):
        out.append(f"\n## {y} ({len(by_year[y])} notes)\n")
        for d, n in by_year[y]:
            title = (n.get("title") or "(untitled)").strip()
            body = (n.get("note") or "").replace("\r", "").strip()
            stamp = d.strftime("%Y-%m-%d %H:%M") if d else "?"
            out.append(f"### {title}  _({stamp})_\n")
            if body:
                out.append(body + "\n")

    text = "\n".join(out)
    open(md_path, "w").write(text)

    leaks = len(re.findall(r"ya29|NTA5ODg", text))
    print(f"notes={len(notes)} meta_dropped={meta_count} out={md_path}")
    print(f"LEAK CHECK (ya29/NTA5ODg matches in output): {leaks}  [must be 0]")

if __name__ == "__main__":
    main()
