#!/usr/bin/env python3
"""Render each question's EXACT Java method + JUnit test as code-card PNGs.

NotebookLM paraphrases text but embeds images as-is. Feeding the real code as an
image source + forcing verbatim embedding in --focus is the reliable way to get
the code onto a slide deck (detailed_deck is image-only and restyles text).

Usage: python3 render_code_cards.py <sources_dir> <out_dir>
"""
import re, os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

def load_font(size):
    for cand in ("/usr/share/fonts/TTF/JetBrainsMono-ExtraBold.ttf",
                 "/usr/share/fonts/noto/NotoSansMono-SemiCondensedThin.ttf"):
        if os.path.exists(cand):
            return ImageFont.truetype(cand, size)
    return ImageFont.load_default()

def extract_fences(path):
    return re.findall(r"```java\s*\n(.*?)```", open(path, encoding="utf-8").read(), re.DOTALL)

def render_card(title, code, out_path, title_color=(0x2A, 0x6F, 0xDB)):
    pad = 28; title_h = 46; line_h = 32; font = load_font(24)
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
    d.text((pad, 8), title[:78], font=load_font(22), fill=(255, 255, 255))
    d.rectangle([pad, title_h + 8, W - pad, H - pad], outline=(210, 216, 224), width=2,
                fill=(255, 255, 255))
    y = title_h + 18
    mono = load_font(20)
    for ln in lines:
        d.text((pad + 12, y), ln, font=mono, fill=(33, 37, 41))
        y += line_h
    img.save(out_path, "PNG")

def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    n = 0
    for i in range(1, 999):
        key = f"q{i:02d}"
        path = f"{src}/{key}.md"
        if not os.path.exists(path):
            continue
        fences = extract_fences(path)
        if len(fences) < 1:
            print(f"{key}: no java fence"); continue
        method = fences[0] if len(fences) >= 1 else ""
        test = fences[1] if len(fences) >= 2 else ""
        q = open(path).readline().strip()
        if method:
            render_card(f"{key.upper()}  Method  —  {q[:54]}", method, f"{out}/{key}_method.png")
        if test:
            render_card(f"{key.upper()}  JUnit 5 Test", test, f"{out}/{key}_test.png")
        n += 1
    print(f"rendered {n} questions -> {out}")

if __name__ == "__main__":
    main()
