#!/usr/bin/env python3
"""Reusable code-card PNG generator for NotebookLM decks.

NotebookLM `detailed_deck` rasterizes slides and DROPS prose-requested code. The fix: render each
question's exact method + JUnit test as a PNG, add it as an IMAGE source, and force the FOCUS prompt
to embed it verbatim. This script produces those PNGs.

Usage:
  python3 render_code_cards.py --src sources --out codecards

It expects each source file (qNN.md) to contain ```java method block then a ```java test block.
If a file has only ONE java fence (test only), it renders the test and warns (you must backfill the
method from the real .java first).

Dependencies: Pillow. Font: JetBrains Mono ExtraBold (override with --font).
"""
import re, os, argparse, textwrap
from PIL import Image, ImageDraw, ImageFont

def load_font(size, path):
    return ImageFont.truetype(path, size)

def extract_java_fences(path):
    txt = open(path, encoding="utf-8").read()
    return re.findall(r"```java\s*\n(.*?)```", txt, re.DOTALL)

def render_card(title, code, out_path, font_path, title_color=(0x2A, 0x6F, 0xDB)):
    pad = 28
    title_h = 46
    line_h = 32
    lines = []
    for raw in code.strip().splitlines():
        if len(raw) <= 52:
            lines.append(raw)
        else:
            lines.extend(textwrap.wrap(raw, width=52) or [raw])
    W = 1140
    H = pad * 2 + title_h + len(lines) * line_h + 12
    img = Image.new("RGB", (W, H), (245, 247, 250))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, title_h], fill=title_color)
    d.text((pad, 8), title, font=load_font(22, font_path), fill=(255, 255, 255))
    d.rectangle([pad, title_h + 8, W - pad, H - pad], outline=(210, 216, 224), width=2,
                fill=(255, 255, 255))
    y = title_h + 18
    mono = load_font(20, font_path)
    for ln in lines:
        d.text((pad + 12, y), ln, font=mono, fill=(33, 37, 41))
        y += line_h
    img.save(out_path, "PNG")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="dir with qNN.md source files")
    ap.add_argument("--out", required=True, help="output dir for code-card PNGs")
    ap.add_argument("--font", default="/usr/share/fonts/TTF/JetBrainsMono-ExtraBold.ttf")
    ap.add_argument("--count", type=int, default=55, help="number of questions")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rendered = 0
    for n in range(1, a.count + 1):
        key = f"q{n:02d}"
        path = f"{a.src}/{key}.md"
        if not os.path.exists(path):
            print("MISSING", path); continue
        fences = extract_java_fences(path)
        if len(fences) < 2:
            print(f"{key}: only {len(fences)} java fence(s) — backfill method from .java first")
            if fences:
                render_card(f"{key.upper()} JUnit 5 Test", fences[0], f"{a.out}/{key}_test.png", a.font)
            continue
        method, test = fences[0], fences[1]
        q = open(path).readline().strip()
        render_card(f"{key.upper()} Method - {q[:60]}", method, f"{a.out}/{key}_method.png", a.font)
        render_card(f"{key.upper()} JUnit 5 Test", test, f"{a.out}/{key}_test.png", a.font)
        rendered += 1
    print(f"rendered {rendered} questions -> {a.out}")

if __name__ == "__main__":
    main()
