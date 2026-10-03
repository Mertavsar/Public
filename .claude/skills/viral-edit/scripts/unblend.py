#!/usr/bin/env python3
"""
Sabit konumlu yarı saydam watermark'ı ters harmanlar: I = s·B + k (piksel ve
kanal başına) birçok kareden regresyonla ölçülür, B = (I − k)/s geri kazanılır.

Tek başına iz bırakır (harf kenarı); ardından aynı harf maskesiyle
`vinpaint.py --mask-img` çalıştır (SKILL.md "Büyük yarı saydam watermark").

    python3 unblend.py ham.mp4 ham_ub.mp4 --box 255,680,570,295 --mask harf.png --t0 3.4

--mask: kutu boyutunda harf maskesi (beyaz = harf). Harf içi boşlukları
KAPATMA: oradaki gerçek piksel Telea tahminini doğru tutar.
"""
import argparse, subprocess
import numpy as np, cv2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--box", required=True, help="x,y,w,h")
    ap.add_argument("--mask", required=True)
    ap.add_argument("--t0", type=float, default=0.0, help="watermark bu saniyede başlar")
    ap.add_argument("--step", type=int, default=3, help="fit için her kaçıncı kare")
    a = ap.parse_args()
    X0, Y0, WW, HH = (int(v) for v in a.box.split(","))
    P = 24
    x0, y0, w, h = X0 - P, Y0 - P, WW + 2 * P, HH + 2 * P
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate", "-of", "csv=p=0", a.src],
                       capture_output=True, text=True).stdout.strip().split(",")
    W, H = int(o[0]), int(o[1]); fps = eval(o[2])
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a.t0 + 0.3:.3f}", "-i", a.src, "-vf",
                        f"format=bgr24,crop={w}:{h}:{x0}:{y0}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                       capture_output=True).stdout
    F = np.frombuffer(b, np.uint8).reshape(-1, h, w, 3)[::a.step]
    M = np.zeros((h, w), np.uint8)
    M[P:P + HH, P:P + WW] = (cv2.imread(a.mask, cv2.IMREAD_GRAYSCALE) > 127) * 255
    M = cv2.dilate(M, np.ones((3, 3), np.uint8))
    I = F.astype(np.float32)
    B = np.stack([cv2.inpaint(f, M, 6, cv2.INPAINT_TELEA) for f in F]).astype(np.float32)
    # Telea tahmini düz zeminde güvenilir: dokulu karelerin ağırlığı düşük
    g = np.stack([cv2.GaussianBlur(np.abs(cv2.Laplacian(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
                  .astype(np.float32), cv2.CV_32F)), (0, 0), 12) for f in F])
    wt = np.exp(-g / 3.0)[..., None]
    for _ in range(6):                      # IRLS: aykırı kareler düşer
        sw = wt.sum(0) + 1e-6
        mb, mi = (wt * B).sum(0) / sw, (wt * I).sum(0) / sw
        s = np.clip((wt * (B - mb) * (I - mi)).sum(0) / ((wt * (B - mb) ** 2).sum(0) + 1e-3), 0.4, 1.05)
        k = mi - s * mb
        wt = np.exp(-g / 3.0)[..., None] / (1 + (np.abs(I - (s * B + k)) / 8) ** 2)
    print(f"{len(F)} karede fit, harf içi s medyan {np.median(s[M > 0]):.3f}")

    d = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         stdout=subprocess.PIPE)
    e = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s",
                          f"{W}x{H}", "-r", f"{fps}", "-i", "-", "-c:v", "libx264", "-crf", "10",
                          "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    i, n0 = 0, int(round(a.t0 * fps))
    while True:
        buf = d.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        if i >= n0:
            f = f.copy()
            r = f[y0:y0 + h, x0:x0 + w].astype(np.float32)
            f[y0:y0 + h, x0:x0 + w] = np.clip((r - k) / s, 0, 255).round().astype(np.uint8)
        e.stdin.write(f.tobytes()); i += 1
    e.stdin.close(); e.wait()
    print(f"{i} kare -> {a.out}")


if __name__ == "__main__":
    main()
