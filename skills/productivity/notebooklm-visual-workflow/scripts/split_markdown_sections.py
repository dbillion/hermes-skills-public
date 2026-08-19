#!/usr/bin/env python3
"""Split a markdown doc into one .md per section header.

Usage:
  split_markdown_sections.py <in.md> <out_dir> [--level 3] [--between "## Start" "## End"]

Splits on headers of the given level (default ###). If --between is given, only
the region between the two level-2 headers is processed. Output files are named
by the header slug. HTML entities are unescaped.

Good for carving a big README into per-question sources so NotebookLM renders
each one faithfully in a one-item-per-page / quiz deck (see
references/quiz-deck-recipe.md).
"""
import html, re, os, sys, argparse


def slug(s):
    s = re.sub(r'[^A-Za-z0-9 ]+', '', s).strip().lower().replace(' ', '-')
    return s[:60] or 'item'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp')
    ap.add_argument('out')
    ap.add_argument('--level', type=int, default=3)
    ap.add_argument('--between', nargs=2, default=None,
                    metavar=('START', 'END'))
    args = ap.parse_args()

    lines = open(args.inp, encoding='utf-8').read().splitlines()
    os.makedirs(args.out, exist_ok=True)

    if args.between:
        start_txt, end_txt = args.between
        si = next((i for i, l in enumerate(lines) if l.strip().startswith(start_txt)), 0)
        ei = next((i for i in range(si + 1, len(lines)) if lines[i].startswith('## ')), len(lines))
        lines = lines[si:ei]

    hashes = '#' * args.level
    blocks, cur = [], None
    for l in lines:
        if l.startswith(hashes + ' '):
            if cur:
                blocks.append(cur)
            cur = [html.unescape(l[args.level + 1:].strip())]
        elif cur is not None:
            cur.append(html.unescape(l))
    if cur:
        blocks.append(cur)

    for b in blocks:
        fn = os.path.join(args.out, slug(b[0]) + '.md')
        open(fn, 'w', encoding='utf-8').write('\n'.join(b) + '\n')
    print(f"wrote {len(blocks)} section files to {args.out}")


if __name__ == '__main__':
    main()
