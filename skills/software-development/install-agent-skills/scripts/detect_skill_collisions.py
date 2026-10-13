#!/usr/bin/env python3
"""Detect Hermes Agent skill name collisions.

The skill loader keys on the frontmatter `name:` of each SKILL.md, NOT the
directory name. Two skill directories that resolve to *different real paths*
but share the same `name:` collide -> the loader refuses to load either
("Ambiguous skill name ... Refusing to guess").

Usage:
  python3 detect_skill_collisions.py                 # scan ~/.hermes/skills
  python3 detect_skill_collisions.py --root /path    # scan a custom root
  python3 detect_skill_collisions.py --candidates a/skills b/skills \
        --root ~/.hermes/skills                       # pre-test cloned repo skills

With --candidates, the script maps each candidate skill (by its frontmatter
name) and flags any name that already exists under --root, so you know which
clones are UPDATE vs NEW before you copy anything.

Exit code: 0 if no pre-existing collisions among installed skills; 1 if a
collision exists. (When --candidates is given, exit code reflects whether any
candidate name is already installed, not overall library health.)
"""
import os
import re
import sys
import argparse

SKILLS_ROOT_DEFAULT = os.path.expanduser("~/.hermes/skills")


def get_name(skill_dir):
    md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(md):
        return None
    try:
        txt = open(md, encoding="utf-8").read()
    except OSError:
        return None
    m = re.search(r"^name:\s*(.+)$", txt, re.M)
    return m.group(1).strip() if m else None


def walk_skills(root):
    """Yield (name, realpath) for every SKILL.md under root. Resolves symlinks."""
    found = []
    for cur, _dirs, files in os.walk(root):
        if "SKILL.md" in files:
            real = os.path.realpath(cur)
            nm = get_name(cur)
            if nm is not None:
                found.append((nm, real))
    return found


def report_collisions(entries, label):
    by_name = {}
    for nm, real in entries:
        by_name.setdefault(nm, set()).add(real)
    collisions = {n: ps for n, ps in by_name.items() if len(ps) > 1}
    if not collisions:
        print(f"[{label}] NO COLLISIONS ({len(entries)} skills, "
              f"{len(by_name)} unique names)")
        return 0
    print(f"[{label}] COLLISIONS FOUND:")
    for n, ps in sorted(collisions.items()):
        print(f"  name={n!r}:")
        for p in sorted(ps):
            print(f"    - {p}")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=SKILLS_ROOT_DEFAULT,
                    help="installed library root (default ~/.hermes/skills)")
    ap.add_argument("--candidates", nargs="+", default=[],
                    help="one or more cloned repo skill dirs to pre-test")
    args = ap.parse_args()

    installed = walk_skills(args.root)
    rc = report_collisions(installed, "installed")

    if args.candidates:
        cands = []
        for d in args.candidates:
            if os.path.isdir(d):
                cands.extend(walk_skills(d))
            else:
                print(f"[candidates] skip (not a dir): {d}")
        # map installed names for cross-check
        installed_names = {n for n, _ in installed}
        print(f"[candidates] {len(cands)} candidate skills:")
        for nm, real in sorted(cands):
            tag = "UPDATE" if nm in installed_names else "NEW"
            print(f"  {tag:7} name={nm!r}  <- {real}")
        # flag candidates that already exist (collision risk on copy)
        dup = [nm for nm, _ in cands if nm in installed_names]
        if dup:
            print(f"[candidates] these names already installed -> refresh "
                  f"canonical realpath, do NOT create a parallel dir: {dup}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
