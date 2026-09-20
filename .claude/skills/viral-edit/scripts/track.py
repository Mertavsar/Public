#!/usr/bin/env python3
"""
Özneyi zaman içinde takip eder ve her an için EDL'ye yazılacak `cropx` önerir.

Neden var: fil videosunda kadrajı kontakt sayfasına bakarak tahmin ettim ve
son iki planda adam kadrajın TAMAMEN dışında kaldı (166 yazmıştım, 648
olmalıydı). Gözle tahmin yerine piksel sayarak bulunca düzeldi. Bu iş artık
elle yapılmıyor.

    # kirmizi tisortlu adami takip et, 608 genisliginde pencere icin cropx uret
    python3 track.py video.mp4 --color red --win 608

    # kahverengi hayvan
    python3 track.py video.mp4 --color brown --win 438 --from 3 --to 13

    # on ayar tutmazsa baskinlik oranini gevset
    python3 track.py video.mp4 --color red --ratio 1.25 --win 608

Çıktı: `t  bulunan_piksel  merkez_x  önerilen_cropx` satırları. EDL yazarken
planın `src` anına en yakın satırın `cropx`'ini al.

Bulunamadı satırları önemli: özne o an kadrajda yok ya da örtülü demektir —
o anı plan başlangıcı yapma.
"""

import argparse, subprocess, sys
import numpy as np
from PIL import Image

# RGB oran kuralları. HSV denendi ve bu görüntülerde zayıf kaldı: doygunluk
# eşiği düşükken toprak/ten tonunu özne sanıyor, yüksekken özneyi tamamen
# kaybediyor (ölçüldü: en iyi HSV ayarında bile ortalama 200 px hata).
# Oran kuralı doğrudan "hangi kanal hangisinden ne kadar baskın" diye soruyor.
#   (v_min, r/g oranı, r/b oranı, g_max)  — kanal adları renk başına değişir
PRESETS = {
    #        v_min  ch1/ch2  ch1/ch3  ch2_max   kanallar
    "red":    dict(lo=95,  a=1.50, b=1.45, cap=175, ch=(0, 1, 2)),
    "orange": dict(lo=95,  a=1.30, b=1.60, cap=200, ch=(0, 1, 2)),
    "brown":  dict(lo=55,  a=1.18, b=1.35, cap=185, ch=(0, 1, 2)),
    "yellow": dict(lo=110, a=1.02, b=1.70, cap=255, ch=(0, 1, 2)),
    "blue":   dict(lo=70,  a=1.35, b=1.25, cap=210, ch=(2, 1, 0)),
    "green":  dict(lo=60,  a=1.20, b=1.20, cap=210, ch=(1, 0, 2)),
}


def frame(path, t):
    raw = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", path,
         "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
        capture_output=True, check=True).stdout
    import io
    return Image.open(io.BytesIO(raw)).convert("RGB")


def mask(im, pre):
    a = np.asarray(im, dtype=np.float32)
    i, j, k = pre["ch"]
    c1, c2, c3 = a[..., i], a[..., j], a[..., k]
    return (c1 > pre["lo"]) & (c1 > c2 * pre["a"]) & (c1 > c3 * pre["b"]) & (c2 < pre["cap"])


def center_x(m, bins=48):
    """Dağınık yanlış pozitifler ortalamayı çekiyor — en YOĞUN bölgeyi bul.

    x konumlarını histograma dök, en dolu kovayı seç, sadece onun çevresindeki
    pikselleri ortala. Ölçüldü: düz ortalama 200 px hata veriyordu, bu 40 px'e
    indirdi."""
    xs = np.nonzero(m)[1]
    if len(xs) == 0:
        return None
    W = m.shape[1]
    h, edges = np.histogram(xs, bins=bins, range=(0, W))
    k = int(np.argmax(h))
    c = (edges[k] + edges[k + 1]) / 2
    span = W / bins * 3
    near = xs[np.abs(xs - c) <= span]
    return float(near.mean()) if len(near) else float(c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--color", default="red", choices=sorted(PRESETS))
    ap.add_argument("--ratio", type=float, default=None,
                    help="ön ayar tutmazsa baskınlık oranını elle ver (1.2 gevşek, 1.7 sıkı)")
    ap.add_argument("--win", type=int, required=True, help="kırpma penceresi genişliği")
    ap.add_argument("--step", type=float, default=0.4)
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=None)
    ap.add_argument("--min-px", type=int, default=150, help="bu kadar pikselden azı 'yok'")
    ap.add_argument("--top", type=float, default=0.0,
                    help="üstten bu orandaki şeridi yok say (gökyüzü vb.)")
    a = ap.parse_args()

    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "format=duration", "-of", "csv=p=0", a.video],
                               capture_output=True, text=True).stdout)
    t1 = min(a.t1, dur - 0.05) if a.t1 else dur - 0.05
    pre = dict(PRESETS[a.color])
    if a.ratio:
        pre["a"] = a.ratio; pre["b"] = a.ratio

    im0 = frame(a.video, a.t0)
    W, H = im0.size
    if a.win > W:
        raise SystemExit(f"pencere {a.win} kaynaktan ({W}) geniş.")
    lo, hi = 0, W - a.win
    print(f"{a.video}  {W}x{H}  ·  renk {a.color}  ·  pencere {a.win}px  "
          f"·  cropx aralığı 0–{hi}")
    print("\n    t   piksel   merkez_x   cropx")
    miss = 0
    t = a.t0
    while t <= t1:
        m = mask(frame(a.video, t), pre)
        if a.top > 0:
            m[:int(H * a.top)] = False
        n = int(m.sum())
        cx = center_x(m) if n >= a.min_px else None
        if cx is None:
            print(f"{t:6.2f}   {n:6d}   —          —     (özne yok/örtülü)")
            miss += 1
        else:
            print(f"{t:6.2f}   {n:6d}   {cx:7.0f}   {int(min(max(cx - a.win / 2, lo), hi)):6d}")
        t += a.step

    if miss:
        print(f"\n{miss} anda özne bulunamadı. O anları plan BAŞLANGICI yapma; "
              f"tutmuyorsa --color / --min-px değiştir.")


if __name__ == "__main__":
    main()
