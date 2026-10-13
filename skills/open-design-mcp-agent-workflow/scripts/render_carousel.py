#!/usr/bin/env python3
"""Render an Open Design carousel HTML deck into upload-ready assets.

Usage:
  python3 render_carousel.py

Reads the sibling index.html (a vertical .deck of .card divs, 1080x1440 / 3:4),
extracts each card into its own minimal HTML file, screenshots it with headless
Chromium, and bundles the PNGs into a multi-page PDF.

Why per-card files: the `?card=N` query-param isolation trick FAILS under headless
Chrome (it ignores the param and screenshots the same first card 8x). Building one
file per card is the reliable method.

Prereqs: chromium/chrome on PATH, Pillow (`pip install pillow`).
"""
import os
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
HTML = HERE / "index.html"
OUT = HERE / "pictures"
OUT.mkdir(exist_ok=True)
CHROME = "/usr/bin/chromium"  # fall back to "chromium"/"google-chrome" if missing
W, H = 1080, 1440


def extract_cards(html: str) -> list[str]:
    style = re.search(r"<style>.*?</style>", html, re.DOTALL).group(0)
    cards = re.findall(r'(<div class="card [^"]*">.*?</div>\s*</div>)', html, re.DOTALL)
    return [f"<!DOCTYPE html><html><head><meta charset='UTF-8'>"
            # NOTE: Tailwind CDN is loaded WITHOUT SRI by design — this mirrors Open
            # Design's card-xiaohongshu template (a local design artifact, not a
            # production web app), so CDN-compromise exposure is not a concern here.
            f"<script src='https://cdn.tailwindcss.com'></script>{style}"
            f"</head><body style='margin:0;background:#f3eee5;'>"
            f"<div class='deck'>{c}</div></body></html>" for c in cards]


def main() -> None:
    html = HTML.read_text()
    cards = extract_cards(html)
    print(f"extracted {len(cards)} cards")
    for i, doc in enumerate(cards, 1):
        card_html = OUT / f"card-{i:02d}.html"
        card_html.write_text(doc)
        raw = OUT / f"_raw-{i:02d}.png"
        subprocess.run([CHROME, "--headless", "--no-sandbox", "--hide-scrollbars",
                        f"--window-size={W},{H}", "--default-background-color=00000000",
                        f"--screenshot={raw}", f"file://{card_html}"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        with Image.open(raw) as im:
            im = im.convert("RGB")
            if im.size != (W, H):
                left = max(0, (im.width - W) // 2)
                top = max(0, (im.height - H) // 2)
                im = im.crop((left, top, left + W, top + H))
            im.save(OUT / f"card-{i:02d}.png")
        raw.unlink()
        print(f"card-{i:02d}.png done", Image.open(OUT / f'card-{i:02d}.png').size)
    # Bundle into a PDF (one card per page)
    imgs = [Image.open(OUT / f"card-{i:02d}.png").convert("RGB") for i in range(1, len(cards) + 1)]
    pdf = OUT / "travel-carousel.pdf"
    imgs[0].save(pdf, save_all=True, append_images=imgs[1:], resolution=96.0)
    print("PDF:", pdf, os.path.getsize(pdf), "bytes")


if __name__ == "__main__":
    main()
