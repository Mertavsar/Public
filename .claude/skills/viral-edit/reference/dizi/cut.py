#!/usr/bin/env python3
"""Son Yaz – Canan: 3:2 kaynaktan çekim başına 9:16 kesit, yeni hikâye sırası.
Yazısız 'clean' video + kaynaktaki eski altyazıların çıktı zaman/dikdörtgen listesi."""
import json, os, subprocess
import numpy as np, cv2

S = os.path.dirname(os.path.abspath(__file__))
SRC = f"{S}/in/src.mp4"
SW, SH, SFPS = 3240, 2160, 60
W, H, FPS = 1080, 1920, 30
CW = int(round(SH * W / H))                     # 1215
# (kaynak t0, t1, hız, merkez x %) — hikâye: mezar -> mutlu anlar -> araba -> kayıp -> anı
PLAN = [(23.75, 25.95, 0.85, 72),    # 0 mezar taşı "CANAN" (hook)
        (4.15, 6.25, 0.9, 45),       # 1 Canan güneşte
        (2.50, 4.05, 1.0, 38),       # 2 "tamam aşkım, kontrol ettim."
        (8.55, 9.85, 0.8, 58),       # 3 arabada: "Selim."
        (10.90, 15.45, 0.8, 45),     # 4 "Anahtar saksının altında…"
        (15.55, 18.35, 0.9, 50),     # 5 "Yağmur, ambulans! Yağmur!"
        (19.65, 21.15, 0.75, 45),    # 6 sarılı kalıyor (sessizlik)
        (21.25, 22.15, 0.8, 70),     # 7 çerçevedeki fotoğraf
        (34.85, 36.70, 0.8, 60)]     # 8 "Ayrılık vakti…" gülümseme
# kaynakta eski altyazının durduğu aralıklar (sn) ve satır y-bandı
OLDCAP = [(2.45, 3.95, 1010, 1150), (8.95, 9.75, 1010, 1150), (10.95, 15.55, 1010, 1150),
          (16.45, 18.40, 1010, 1150), (34.95, 36.10, 1010, 1150)]

seq, rects, t = [], [], 0.0
for (s0, s1, sp, xc) in PLAN:
    d = (s1 - s0) / sp
    n = int(round((t + d) * FPS)) - int(round(t * FPS))
    x0 = int(np.clip(xc / 100 * SW - CW / 2, 0, SW - CW))
    for k in range(n):
        seq.append((s0 + (s1 - s0) * k / n, x0))
    # eski altyazı -> çıktı zamanı + kesit koordinatı
    for c0, c1, y0, y1 in OLDCAP:
        a, b = max(s0, c0), min(s1, c1)
        if a < b:
            o0, o1 = t + (a - s0) / sp, t + (b - s0) / sp
            sc = W / CW
            rects.append([round(o0 - 0.05, 2), round(o1 + 0.05, 2), int(y0 * sc) - 10, int(y1 * sc) + 10, 40, W - 40])
    t += d
DUR = len(seq) / FPS
json.dump({"dur": DUR, "rects": rects, "cuts": [0] + list(np.cumsum([(p[1] - p[0]) / p[2] for p in PLAN]))},
          open(f"{S}/w/plan.json", "w"))
print(f"süre {DUR:.2f}", rects)

need = {}
for s, x0 in seq:
    for i in (int(s * SFPS), int(s * SFPS) + 1):
        need.setdefault(i, set()).add(x0)
store = {}
d = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
k = 0
while True:
    b = d.stdout.read(SW * SH * 3)
    if len(b) < SW * SH * 3:
        break
    if k in need:
        f = np.frombuffer(b, np.uint8).reshape(SH, SW, 3)
        for x0 in need[k]:
            z = cv2.resize(f[:, x0:x0 + CW], (W, H), interpolation=cv2.INTER_AREA)
            store[(k, x0)] = cv2.imencode(".jpg", z, [cv2.IMWRITE_JPEG_QUALITY, 96])[1]
    k += 1
d.wait()
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p",
                        f"{S}/w/clean_raw.mp4"], stdin=subprocess.PIPE)
for s, x0 in seq:
    i = int(s * SFPS); w_ = s * SFPS - i
    a = cv2.imdecode(store[(i, x0)], cv2.IMREAD_COLOR)
    if w_ > 0.05 and (i + 1, x0) in store:
        a = cv2.addWeighted(a, 1 - w_, cv2.imdecode(store[(i + 1, x0)], cv2.IMREAD_COLOR), w_, 0)
    enc.stdin.write(a.tobytes())
enc.stdin.close(); enc.wait()
print("tamam")
