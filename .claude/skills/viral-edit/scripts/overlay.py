#!/usr/bin/env python3
"""
Grafik katmanını üretir: kırmızı N/30 sayacı, tek kelimelik altyazı, kırmızı oklar.

Çıktı: RGBA video (.mov / qtrle). ffmpeg'de `overlay` ile kartın üstüne bindirilir.
Grafik olmayan kareler tamamen saydamdır, o yüzden dosya küçük kalır.

Kullanım
--------
    python3 overlay.py --spec spec.json --out overlay.mov

spec.json
---------
{
  "canvas": [1080, 1920],
  "fps": 30,
  "duration": 41.5,
  "card": {"x": 105, "y": 263, "w": 870, "h": 1169},

  "counter": {"total": 30, "steps": [[3.0, 1], [12.0, 6], [24.0, 12], [34.0, 24]],
              "size": 82},

  "captions": "captions.json",
  "caption_size": 74,
  "caption_y": 0.86,          // kartın içinde, üstten oran

  "arrows": [
    {"t": 15.4, "dur": 1.2, "x": 0.72, "y": 0.34, "angle": 215, "len": 340, "draw": 0.18}
  ],

  "banners": [
    {"t": 0, "dur": 1.8, "text": "GÖZÜNE BİR|SANTİM KALDI", "y": 0.22, "size": 104}
  ]
}

arrows:  x/y kart içinde 0–1 oranı (okun SİVRİ UCU oraya bakar).
         angle = okun geldiği yön, derece (0=sağdan, 90=alttan, 180=soldan, 270=üstten).
         draw  = çizilerek beliriş süresi (saniye). 0 ise anında görünür.
         pulse = tam çizildikten sonra nabız genliği (0.07 iyi çalışıyor).

banners: kare sıfırdan itibaren SABİT duran hook yazısı. Tek kelimelik altyazı
         hook için yetmez — "Gözüne" tek başına hiçbir vaat taşımaz. İzleyici ilk
         saniyede "neden izleyeyim" sorusunun cevabını arar; banner o cevaptır.
         text içinde | satır kırar. y = kart içinde 0–1 oranı.
"""

import argparse, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RED = (228, 26, 28, 255)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]


def load_font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise SystemExit("Kalın sans-serif font bulunamadı. DejaVu veya Liberation kur.")


def stroked_text(draw, xy, text, font, fill, stroke, w):
    """PIL'in stroke_width'i bazı sürümlerde zayıf; elle kalın kontur çiziyoruz."""
    x, y = xy
    for dx in range(-w, w + 1):
        for dy in range(-w, w + 1):
            if dx * dx + dy * dy <= w * w:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke, anchor="mm")
    draw.text((x, y), text, font=font, fill=fill, anchor="mm")


def arrow_polygon(tipx, tipy, angle_deg, length, head=0.42, shaft=0.30):
    """Kalın, kaba ok. Sivri uç (tipx,tipy)'de; gövde angle yönünden gelir."""
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)          # uçtan gövdeye doğru birim vektör
    px, py = -uy, ux                           # dik
    hl = length * head                         # baş uzunluğu
    hw = length * head * 0.62                  # baş yarı genişliği
    sw = length * shaft * 0.34                 # gövde yarı genişliği
    bx, by = tipx + ux * length, tipy + uy * length          # gövde sonu
    nx, ny = tipx + ux * hl, tipy + uy * hl                  # baş tabanı
    return [
        (tipx, tipy),
        (nx + px * hw, ny + py * hw),
        (nx + px * sw, ny + py * sw),
        (bx + px * sw, by + py * sw),
        (bx - px * sw, by - py * sw),
        (nx - px * sw, ny - py * sw),
        (nx - px * hw, ny - py * hw),
    ]


def clip_polygon_progress(poly, tip, frac):
    """Okun çizilerek belirmesi: uçtan gövdeye doğru açılır."""
    if frac >= 1.0:
        return poly
    cx, cy = tip
    return [(cx + (x - cx) * frac, cy + (y - cy) * frac) for x, y in poly]


def counter_value(steps, t):
    v = None
    for st, val in steps:
        if t >= st:
            v = val
    return v


def build(spec, out):
    W, H = spec["canvas"]
    fps = spec.get("fps", 30)
    nf = int(round(spec["duration"] * fps))
    card = spec["card"]

    caps = []
    if spec.get("captions"):
        caps = json.load(open(spec["captions"], encoding="utf-8"))

    cfont = load_font(spec.get("caption_size", 74))
    nfont = load_font(spec.get("counter", {}).get("size", 82))

    cap_y = card["y"] + int(card["h"] * spec.get("caption_y", 0.86))
    cnt_y = card["y"]                                  # kartın üst kenarına oturur
    cx = card["x"] + card["w"] // 2

    arrows = spec.get("arrows", [])
    counter = spec.get("counter")
    # Hook yazısı: kare sıfırdan itibaren ekranda duran, birden fazla kelimelik vaat.
    # Tek kelimelik altyazı hook için işe yaramaz — "Gözüne" tek başına hiçbir şey
    # söylemez. İzleyici ilk saniyede "bunu neden izleyeyim" sorusuna cevap arar.
    banners = spec.get("banners", [])
    bfonts = {}
    for b in banners:
        sz = b.get("size", 96)
        if sz not in bfonts:
            bfonts[sz] = load_font(sz)

    p = subprocess.Popen(
        ["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
         "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
         "-c:v", "qtrle", "-pix_fmt", "argb", out],
        stdin=subprocess.PIPE)

    blank = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ci = 0
    for f in range(nf):
        t = f / fps
        # o an bir şey çizilecek mi?
        word = None
        while ci < len(caps) and caps[ci]["e"] <= t:
            ci += 1
        if ci < len(caps) and caps[ci]["s"] <= t < caps[ci]["e"]:
            word = caps[ci]["w"]
        cval = counter_value(counter["steps"], t) if counter else None
        act = [a for a in arrows if a["t"] <= t < a["t"] + a["dur"]]
        ban = [b for b in banners if b["t"] <= t < b["t"] + b["dur"]]

        if word is None and cval is None and not act and not ban:
            p.stdin.write(blank.tobytes())
            continue

        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        for a in act:
            tipx = card["x"] + a["x"] * card["w"]
            tipy = card["y"] + a["y"] * card["h"]
            ln = a.get("len", 340)
            dr = a.get("draw", 0.0)
            frac = 1.0 if dr <= 0 else min(1.0, (t - a["t"]) / dr)
            # çizildikten sonra nabız gibi atsın — göz oku kaçırmasın
            pulse = a.get("pulse", 0.0)
            if pulse and frac >= 1.0:
                ln *= 1.0 + pulse * math.sin(2 * math.pi * a.get("pulse_hz", 3.2)
                                             * (t - a["t"] - dr))
            poly = arrow_polygon(tipx, tipy, a["angle"], ln)
            poly = clip_polygon_progress(poly, (tipx, tipy), frac)
            d.polygon(poly, fill=RED, outline=BLACK, width=max(8, int(ln * 0.045)))

        if cval is not None:
            stroked_text(d, (cx, cnt_y), f"{cval}/{counter['total']}", nfont,
                         RED, BLACK, max(4, nfont.size // 14))

        if word:
            stroked_text(d, (cx, cap_y), word, cfont,
                         WHITE, BLACK, max(5, cfont.size // 9))

        for b in ban:
            bf = bfonts[b.get("size", 96)]
            by = card["y"] + b.get("y", 0.30) * card["h"]
            lines = b["text"].split("|")          # | ile satır kır
            lh = int(bf.size * 1.18)
            y0 = by - (len(lines) - 1) * lh / 2
            for k, line in enumerate(lines):
                stroked_text(d, (cx, y0 + k * lh), line, bf,
                             b.get("color", WHITE), BLACK, max(6, bf.size // 8))

        p.stdin.write(img.tobytes())

    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg overlay yazımı başarısız.")
    print(f"{out}  ·  {nf} kare  ·  {nf/fps:.2f}s  ·  {len(caps)} kelime, "
          f"{len(arrows)} ok, sayaç: {'var' if counter else 'yok'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    build(json.load(open(a.spec, encoding="utf-8")), a.out)


if __name__ == "__main__":
    main()
