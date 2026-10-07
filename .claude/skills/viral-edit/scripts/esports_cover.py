#!/usr/bin/env python3
"""Esports Shorts kapağı (1080x1920): üstte en parlak oyun karesi, altta oyuncunun
yüzü, ayraçta 2 satır büyük yazı (beyaz + sarı), sol üstte rozet (TOP 4 / #1).
Kural: 150 px genişlikte okunmalı -> 2-3 kelime, kalın kontur. Blur yok.

    python3 esports_cover.py --game g.png --face c.png --l1 "KERIA'S LUX" \
        --l2 "IS ILLEGAL" --badge "TOP 4" --out kapak.jpg
"""
import cv2, numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--game", required=True, help="oyun karesi (kaynaktan kırpılmış, ör. 1080x860)")
ap.add_argument("--face", help="oyuncu kamerası karesi (yoksa oyun tüm kapağı doldurur)")
ap.add_argument("--l1", required=True); ap.add_argument("--l2", required=True)
ap.add_argument("--badge", default=""); ap.add_argument("--gx", type=int, default=60)
ap.add_argument("--ty", type=int, default=935, help="1. satırın y merkezi (2. satır +155)")
ap.add_argument("--cy", type=float, default=0.5, help="yüz yoksa: odak noktasının y oranı (0-1)")
ap.add_argument("--out", required=True)
A = ap.parse_args(); W, H = 1080, 1920
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"
def punch(f, sat=1.3, con=1.18):
    f = f.astype(np.float32); g = f.mean(2, keepdims=True)
    f = g + (f - g) * sat; f = 128 + (f - 128) * con
    return np.clip(f, 0, 255).astype(np.uint8)
g = cv2.imread(A.game)
can = np.zeros((H, W, 3), np.uint8); can[:] = (14, 8, 22)
GB = 1150 if A.face else H                      # oyunun kapladığı yükseklik
sc = max(GB / g.shape[0], W / g.shape[1])
g = cv2.resize(g, (int(round(g.shape[1] * sc)), int(round(g.shape[0] * sc))), interpolation=cv2.INTER_CUBIC)
if A.face:
    x0 = A.gx; g = punch(g[:GB, x0:x0 + W])
else:
    x0 = (g.shape[1] - W) // 2
    y0 = int(np.clip(A.cy * g.shape[0] - GB / 2, 0, g.shape[0] - GB)); g = punch(g[y0:y0 + GB, x0:x0 + W])
can[0:GB] = g
if A.face:
    c = cv2.imread(A.face)
    sc = 1.4; c = cv2.resize(c, (int(c.shape[1] * sc), int(c.shape[0] * sc)), interpolation=cv2.INTER_CUBIC)
    cx0 = (c.shape[1] - W) // 2; c = punch(c[:, cx0:cx0 + W], 1.05, 1.12)
    fy = H - c.shape[0]; can[fy:] = c[:H - fy]
    # ayraç çizgisi
    a = np.linspace(0, 1, W)[None, :, None]
    can[1146:1158] = (np.array([60, 30, 235]) * (1 - a) + np.array([40, 200, 255]) * a).astype(np.uint8)
# yazı alanı için alt/üst koyulaştırma (blur yok)
sh = np.ones((H, 1, 1), np.float32)
if A.face:
    for y in range(820, 1146): sh[y] = 1 - 0.55 * (y - 820) / 326
else:                                           # yazı çevresi yumuşak koyulaşır, kenar çizgisi yok
    yy_ = np.arange(H); sh[:, 0, 0] = 1 - 0.5 * np.exp(-((yy_ - (A.ty + 75)) / 190.0) ** 2)
for y in range(0, 330): sh[y] = 0.45 + 0.55 * (y / 330) ** 1.5
can = (can * sh).astype(np.uint8)
img = Image.fromarray(cv2.cvtColor(can, cv2.COLOR_BGR2RGB)).convert("RGBA")
lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
def txt(cx, cy, s, size, col, st=12):
    f = ImageFont.truetype(FONT, size)
    while d.textlength(s, font=f) > W - 60:
        size -= 6; f = ImageFont.truetype(FONT, size)
    tw = d.textlength(s, font=f); x, y = cx - tw / 2, cy - size * 0.62
    d.text((x + 8, y + 10), s, font=f, fill=(0, 0, 0, 170), stroke_width=st, stroke_fill=(0, 0, 0, 170))
    d.text((x, y), s, font=f, fill=col, stroke_width=st, stroke_fill=(0, 0, 0))
txt(W / 2, A.ty, A.l1, 150, (255, 255, 255))
txt(W / 2, A.ty + 155, A.l2, 190, (255, 214, 0), 14)
# TOP 4 rozeti
f = ImageFont.truetype(FONT, 78); s = A.badge; tw = d.textlength(s, font=f)
if s:
    d.rounded_rectangle([46, 150, 46 + tw + 56, 260], radius=18, fill=(235, 30, 45), outline=(0, 0, 0), width=6)
    d.text((74, 160), s, font=f, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
img.alpha_composite(lay)
img.convert("RGB").save(A.out, quality=95)
