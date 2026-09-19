#!/usr/bin/env python3
"""Poster uzerindeki grafik katmani (baslik, alt metin, ikonlar) temizlenmis
'temiz plaka' uretir. Yakin planlarda kirpilmis yazi gorunmesini onler;
kamera geri cekilirken bu ogeler tek tek geri getirilir.

Yontem: her kutunun icini, kutunun solundaki ve sagindaki temiz sutunlardan
satir bazli dogrusal enterpolasyonla doldurur, dikey yumusatma ve kaynakla
eslesen grain ekler, kenarlari yumusak gecisle karistirir.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

from boxes import INPAINT_BOXES as ELEMENTS

EDGE = 6       # kenar ornekleme genisligi
FEATHER = 16   # yumusak gecis


def inpaint_box(arr, box, rng):
    """Coons yamasi: dort kenardan cift yonlu enterpolasyon.
    Dogrusal ve capraz isik gecislerini birebir yeniden uretir, bu yuzden
    kutu sinirlarinda dikis birakmaz."""
    x0, y0, x1, y1 = box
    h, w = y1 - y0, x1 - x0

    L = np.median(arr[y0:y1, x0 - EDGE:x0], axis=1)          # (h,3)
    R = np.median(arr[y0:y1, x1:x1 + EDGE], axis=1)          # (h,3)
    Tp = np.median(arr[y0 - EDGE:y0, x0:x1], axis=0)         # (w,3)
    Bt = np.median(arr[y1:y1 + EDGE, x0:x1], axis=0)         # (w,3)

    u = np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :, None]
    v = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]

    c00, c10 = Tp[0], Tp[-1]
    c01, c11 = Bt[0], Bt[-1]

    fill = ((1 - u) * L[:, None, :] + u * R[:, None, :]
            + (1 - v) * Tp[None, :, :] + v * Bt[None, :, :]
            - ((1 - u) * (1 - v) * c00 + u * (1 - v) * c10
               + (1 - u) * v * c01 + u * v * c11))

    img = Image.fromarray(np.clip(fill, 0, 255).astype(np.uint8))
    fill = np.asarray(img.filter(ImageFilter.GaussianBlur(1.6)), np.float32)

    # cevredeki dokuyla eslesen ince grain
    ring = np.concatenate([
        arr[y0:y1, x0 - EDGE:x0].reshape(-1, 3),
        arr[y0:y1, x1:x1 + EDGE].reshape(-1, 3),
        arr[y0 - EDGE:y0, x0:x1].reshape(-1, 3),
        arr[y1:y1 + EDGE, x0:x1].reshape(-1, 3),
    ])
    sigma = float(np.clip(ring.std(axis=0).mean() * 0.14, 0.7, 2.6))
    fill += rng.normal(0, sigma, fill.shape).astype(np.float32)

    # kenar yumusatma maskesi (kosinus gecisli)
    f = min(FEATHER, w // 2, h // 2)
    ramp = (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, f))).astype(np.float32)
    m = np.ones((h, w), np.float32)
    m[:, :f] *= ramp[None, :]
    m[:, -f:] *= ramp[::-1][None, :]
    m[:f, :] *= ramp[:, None]
    m[-f:, :] *= ramp[::-1][:, None]
    m = m[..., None]

    arr[y0:y1, x0:x1] = arr[y0:y1, x0:x1] * (1 - m) + fill * m
    return arr


def main(src_path, out_path):
    src = Image.open(src_path).convert("RGB")
    arr = np.asarray(src, np.float32).copy()
    rng = np.random.default_rng(11)
    for name, *box in ELEMENTS:
        arr = inpaint_box(arr, box, rng)
    clean = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    clean.save(out_path)
    print(f"OK -> {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
