#!/usr/bin/env python3
"""
Kesimlere görsel geçiş: zoom-punch ve whip-pan (hareket bulanıklığıyla).

build.py'nin beyaz flaş + sarsıntısı kullanıcıya "berbat" geldi. Bunlar flaş
kullanmaz; hareket kesimin iki yanına yayılır (çıkan plan hızlanarak gider,
giren plan yavaşlayarak oturur), göz kesimi hissetmez.

    python3 transitions.py content.mp4 content_fx.mp4 \
        --at 2.35:zoom 4.10:whip 13.00:big ...

zoom  çıkan plan merkeze doğru büyür, giren plan büyükten oturur (radyal blur)
big   zoom'un güçlüsü (anlatının döndüğü an)
whip  çıkan ve giren plan yan yana tek şerit gibi sola kayar (yatay blur).
      İlk sürüm kenarı aynalayarak dolduruyordu: kayma anında aynı yüz iki
      kez göründü. Şimdi boşluğu karşı planın gerçek karesi dolduruyor.
Altyazı/ok katmanı bundan SONRA bindirilir — yazılar sarsılmaz.
"""
import argparse, subprocess
import numpy as np, cv2


def probe(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate", "-of", "csv=p=0", p],
                       capture_output=True, text=True).stdout.strip().split(",")
    n, d = o[2].split("/")
    return int(o[0]), int(o[1]), float(n) / float(d)


def zoom(f, s, blur):
    """merkezden s kat büyüt; blur>0 ise birkaç ölçeği karıştır (radyal bulanıklık)"""
    H, W = f.shape[:2]
    scales = [s] if blur <= 0 else list(np.linspace(s, s * (1 + blur), 5))
    acc = np.zeros_like(f, np.float32)
    for sc in scales:
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, sc)
        acc += cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return (acc / len(scales)).astype(np.uint8)


def shift(f, dx, blur):
    H, W = f.shape[:2]
    M = np.float32([[1, 0, dx], [0, 1, 0]])
    g = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    k = int(blur)
    return cv2.blur(g, (k, 1)) if k > 1 else g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--at", nargs="+", required=True, help="zaman:tür (zoom|big|whip)")
    ap.add_argument("--frames", type=int, default=5, help="kesimin her yanında kaç kare")
    a = ap.parse_args()
    W, H, fps = probe(a.src)
    ev = []
    for s in a.at:
        t, k = s.split(":")
        ev.append((int(round(float(t) * fps)), k))
    N = a.frames

    def fx(i, f):
        for c, kind in ev:
            d = i - c                      # <0 çıkan plan, >=0 giren plan
            if -N <= d < N:
                p = (N + d) / N if d < 0 else (N - d) / N   # kesime yaklaştıkça 1
                p = p * p                  # kesime doğru hızlanır / sonra yavaşlar
                if kind in ("zoom", "big"):
                    A = 0.45 if kind == "big" else 0.22
                    return zoom(f, 1 + A * p, 0.10 * p if kind == "big" else 0.06 * p)
                if kind == "whip":
                    u = (d + N + 0.5) / (2 * N)             # 0..1 kesim boyunca
                    e = 0.5 - 0.5 * np.cos(np.pi * u)       # yumuşak başla/bit
                    a_, b_ = (f, still[c][1]) if d < 0 else (still[c][0], f)
                    strip = np.concatenate([a_, b_], 1)
                    x = int(round(e * W))
                    g = np.ascontiguousarray(strip[:, x:x + W])
                    k = int(1 + 160 * np.sin(np.pi * u))
                    return cv2.blur(g, (k, 1)) if k > 1 else g
        return f

    # whip için kesimin iki yanındaki sabit kareler (çıkanın sonu, girenin başı)
    still = {}
    for c, kind in ev:
        if kind == "whip":
            fr = []
            for j in (c - 1, c):
                b = subprocess.run(["ffmpeg", "-v", "error", "-i", a.src, "-vf",
                                    f"select=eq(n\\,{j})", "-frames:v", "1", "-f", "rawvideo",
                                    "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
                fr.append(np.frombuffer(b, np.uint8).reshape(H, W, 3))
            still[c] = fr

    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-f", "rawvideo", "-pix_fmt",
                            "bgr24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-", "-c:v", "libx264",
                            "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", a.out],
                           stdin=subprocess.PIPE)
    i = 0
    while True:
        b = dec.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        enc.stdin.write(fx(i, f).tobytes())
        i += 1
    enc.stdin.close(); enc.wait()
    print(f"{i} kare, {len(ev)} geçiş -> {a.out}")


if __name__ == "__main__":
    main()
