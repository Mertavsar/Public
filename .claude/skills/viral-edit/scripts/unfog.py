#!/usr/bin/env python3
"""
Kaynağa gömülü alt sis/beyaz şeridi düzeltir — KIRPMADAN.

Bazı TikTok kopyaları altyazı için alt %30–40'a beyaz bir sis/gradyan
şeridi ekliyor; altında görüntü YOK (fil klibinde 0.64 altında satır
içeriği %1–7 ölçüldü). Kullanıcı "alt taraf niye beyaz" dedi.

1. Sis yarı saydamsa (içerik ≥ %35): px = a·W + (1−a)·img tersine çevrilir;
   a satır satır zamansal oynaklıktan kestirilir (referans: üstteki temiz
   görüntü). Gerçek görüntü geri gelir.
2. Görüntünün tükendiği satırdan aşağısı: son geri kazanılan satırın rengi
   yatayda yumuşatılıp koyuya inen sinematik bir gradyana çevrilir. Beyaz
   gider, altyazı koyu zeminde okunur.

    python3 unfog.py ham_clean.mp4 ham_final.mp4 --ref 300,540 --start 0.50

--ref: temiz görüntü satırları (y0,y1). --start: sisin başladığı oran.
Önce ölç: satır başına zamansal std / referans std (SKILL.md §4).
"""
import argparse, subprocess, numpy as np, cv2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--ref", default="300,540")
    ap.add_argument("--start", type=float, default=0.50)
    ap.add_argument("--min-content", type=float, default=0.35,
                    help="bu oranın altında içerik kalan satır geri kazanılmaz, gradyana döner")
    ap.add_argument("--fade", type=float, default=0.10, help="koyuya iniş uzunluğu (kare oranı)")
    ap.add_argument("--floor", type=float, default=0.12, help="gradyan sonu parlaklık çarpanı")
    a = ap.parse_args()
    pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                         "stream=width,height,r_frame_rate", "-of", "csv=p=0", a.src],
                        capture_output=True, text=True).stdout.strip().split(",")
    W, H = int(pr[0]), int(pr[1]); n_, d_ = pr[2].split("/"); fps = float(n_) / float(d_)

    s = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", a.src, "-vf", "fps=5",
                                      "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                                     capture_output=True).stdout, np.uint8).reshape(-1, H, W, 3).astype(np.float32)
    r0, r1 = (int(v) for v in a.ref.split(","))
    sd = s.mean(3).std(0).mean(1)
    ref = sd[r0:r1].mean()
    keep = np.clip(sd / ref, 0, 1)                       # 1 - a
    keep = cv2.GaussianBlur(keep.reshape(-1, 1), (1, 0), 6).ravel() if False else np.convolve(keep, np.ones(9) / 9, "same")
    y0 = int(a.start * H)
    ys = np.arange(H)
    rec = (ys >= y0) & (keep >= a.min_content)
    y_end = int(ys[(ys >= y0) & (keep >= a.min_content)].max()) if rec.any() else y0
    alpha = np.clip(1 - keep, 0, 0.95)
    alpha[:y0] = 0
    mu = s.mean(0)                                       # H,W,3
    m_ref = mu[max(r0, y0 - 40):y0].mean(0)              # W,3 — sis üstündeki ortalama görüntü
    Wc = (mu - (1 - alpha)[:, None, None] * m_ref[None]) / np.maximum(alpha, 1e-3)[:, None, None]
    Wc = np.clip(cv2.GaussianBlur(Wc, (0, 0), 8), 0, 255)
    fade_n = max(8, int(a.fade * H))
    print(f"geri kazanılan: y {y0}–{y_end} ({y0/H:.2f}–{y_end/H:.2f}) · gradyan {y_end/H:.2f}→{min(H,y_end+fade_n)/H:.2f}")
    del s

    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-", "-i", a.src, "-map", "0:v", "-map", "1:a?",
                            "-c:v", "libx264", "-crf", "12", "-preset", "slow", "-pix_fmt", "yuv420p",
                            "-c:a", "copy", a.out], stdin=subprocess.PIPE)
    A = alpha[y0:y_end + 1, None, None]
    ramp = np.linspace(0, 1, fade_n)[:, None, None]
    i = 0
    while True:
        b = dec.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        f = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32)
        band = f[y0:y_end + 1]
        f[y0:y_end + 1] = np.clip((band - A * Wc[y0:y_end + 1]) / np.maximum(1 - A, 0.05), 0, 255)
        edge = cv2.GaussianBlur(f[y_end - 6:y_end + 1].mean(0, keepdims=True), (0, 0), sigmaX=90, sigmaY=0.1)
        tail_len = H - (y_end + 1)
        mult = np.concatenate([1 - (1 - a.floor) * ramp[:, :, 0],
                               np.full((max(0, tail_len - fade_n), 1), a.floor)])[:tail_len, :, None]
        f[y_end + 1:] = edge * mult
        # geçiş satırlarını yumuşat — kesin çizgi görünmesin
        seam = slice(max(0, y_end - 10), min(H, y_end + 12))
        f[seam] = cv2.GaussianBlur(f[seam], (0, 0), sigmaX=1, sigmaY=4)
        enc.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes()); i += 1
    enc.stdin.close(); enc.wait()
    print(f"{i} kare -> {a.out}")


if __name__ == "__main__":
    main()
