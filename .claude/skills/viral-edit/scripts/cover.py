#!/usr/bin/env python3
"""
Dikey kapak görseli (1080x1920) üretir.

Shorts akışında video otomatik oynuyor, ama kapak kanal sayfasında ve Shorts
rafında görünüyor — orada **150 piksel genişliğinde** okunması gerekiyor.
Kural: tek fikir, iki-üç kelime, kalın kontur.

Çizim `overlay.py` ile aynı: aynı font, aynı kontur, aynı kırmızı ok. Kapakla
videonun ilk karesi aynı dili konuşmalı.

    python3 cover.py --frame kare.png --spec kapak.json --out kapak.png

kapak.json
----------
{
  "headline": "NEDEN|KAÇMIYOR?",     // | satır kırar
  "headline_y": 0.115,
  "headline_size": 150,
  "labels": [
    {"text": "2 TON",   "x": 0.80, "y": 0.32, "size": 92,  "color": "yellow"},
    {"text": "80 KİLO", "x": 0.25, "y": 0.78, "size": 92,  "color": "yellow"}
  ],
  "arrows": [
    {"x": 0.285, "y": 0.545, "angle": 135, "len": 300}
  ],
  "top_shade": 0.30                  // üstte koyulaştırma (yazı okunsun)
}
"""

import argparse, json, os, sys
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overlay import load_font, stroked_text, arrow_polygon, PALETTE, RED, BLACK, WHITE

W, H = 1080, 1920


def shade_top(im, strength, frac=0.34):
    """Üstte yumuşak koyulaştırma. Açık gökyüzünde beyaz yazı kayboluyor."""
    if strength <= 0:
        return im
    a = np.asarray(im).astype(np.float32)
    n = int(H * frac)
    ramp = np.linspace(1.0 - strength, 1.0, n)[:, None, None]
    a[:n] *= ramp
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def build(frame, spec, out):
    im = Image.open(frame).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    im = shade_top(im, spec.get("top_shade", 0.30))
    d = ImageDraw.Draw(im)

    for a in spec.get("arrows", []):
        ln = a.get("len", 300)
        poly = arrow_polygon(a["x"] * W, a["y"] * H, a["angle"], ln)
        d.polygon(poly, fill=RED, outline=BLACK, width=max(8, int(ln * 0.05)))

    for l in spec.get("labels", []):
        f = load_font(l.get("size", 92))
        stroked_text(d, (l["x"] * W, l["y"] * H), l["text"], f,
                     PALETTE.get(l.get("color", "white"), WHITE), BLACK,
                     max(6, f.size // 8))

    hl = spec.get("headline")
    if hl:
        f = load_font(spec.get("headline_size", 150))
        lines = hl.split("|")
        lh = int(f.size * 1.02)
        y0 = spec.get("headline_y", 0.115) * H
        for k, line in enumerate(lines):
            stroked_text(d, (W // 2, y0 + k * lh), line, f,
                         PALETTE.get(spec.get("headline_color", "white"), WHITE),
                         BLACK, max(8, f.size // 9))

    im.save(out, quality=95)
    print(f"{out}  ·  {im.size[0]}x{im.size[1]}")
    # Okunabilirlik kontrolü: 150px genişliğe indirgeyip yazı hâlâ seçiliyor mu?
    small = im.resize((150, 267), Image.LANCZOS)
    small.save(os.path.splitext(out)[0] + "_150px.png")
    print(f"   kontrol: {os.path.splitext(out)[0]}_150px.png "
          f"(Shorts rafında bu boyutta görünüyor)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    build(a.frame, json.load(open(a.spec, encoding="utf-8")), a.out)


if __name__ == "__main__":
    main()
