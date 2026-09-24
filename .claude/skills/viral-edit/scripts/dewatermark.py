#!/usr/bin/env python3
"""
TikTok filigranını KIRPMADAN ve BULANIKLAŞTIRMADAN siler.

Kullanıcının kuralı: dikey kaynak kesilmez, zoom yapılmaz (SKILL.md §4).
`delogo` ve blur kutusu görünür leke bırakıyor. Burada kutu değil, yazının
kendi harf şekli maskelenip her karede çevresinden dolduruluyor (inpainting).

Maske nasıl çıkıyor: filigran EKRANDA SABİT, altındaki görüntü hareket ediyor.
"Karelerin %80'inden fazlasında aynı pikselde beyaz" olan yer filigrandır;
kuş, su, çimen hareket ettiği için elenir. Logonun camgöbeği/kırmızı kenarı
ve yazının hâlesi ayrıca ekleniyor — ilk denemede bunlar kalmış, camgöbeği
nokta ve beyaz hayalet olarak görünmüştü.

TikTok filigranı videonun ortasında köşe değiştirir. --switch o an (s);
öncesi --box-a, sonrası --box-b içinde aranır. Geçişte iki maske birleşik.

    python3 dewatermark.py ham.mp4 ham_clean.mp4 --switch 4.95 \\
        --box-a 430,580,0,210 --box-b 760,900,380,576 --until 11.6

Kutular y0,y1,x0,x1 (kaynak pikseli). Önce ölç: kontak sayfası + drawgrid.
Çıktıdan sonra 3x büyütülmüş önce/sonra karşılaştırmasına BAK.

Gereken: pip install opencv-python-headless
"""
import argparse, subprocess, numpy as np, cv2


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip().split(",")
    w, h = int(out[0]), int(out[1]); a, b = out[2].split("/")
    return w, h, float(a) / float(b)


def build_mask(F, box, W, H):
    y0, y1, x0, x1 = box
    mn = F.min(axis=3).astype(int); mx = F.max(axis=3).astype(int)
    hsv = np.stack([cv2.cvtColor(f, cv2.COLOR_BGR2HSV) for f in F])
    core = ((mn > 195) & ((mx - mn) < 40)).mean(0) > 0.8
    halo = ((mn > 140) & ((mx - mn) < 60)).mean(0) > 0.7
    h_ = hsv[..., 0]
    icon = ((hsv[..., 1] > 55) & (hsv[..., 2] > 110) &
            (((h_ > 78) & (h_ < 105)) | (h_ > 155) | (h_ < 10))).mean(0) > 0.6
    near = cv2.dilate(((core | icon) * 255).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    logo = cv2.dilate((core * 255).astype(np.uint8), np.ones((41, 41), np.uint8)) > 0
    sel = core | (halo & near) | (icon & logo)
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = sel[y0:y1, x0:x1] * 255
    return cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--switch", type=float, required=True, help="filigranın köşe değiştirdiği an")
    ap.add_argument("--box-a", required=True); ap.add_argument("--box-b", required=True)
    ap.add_argument("--until", type=float, default=1e9, help="kapanış kartı başlangıcı")
    a = ap.parse_args()
    W, H, fps = probe(a.src)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.src, "-t", f"{min(a.until, 1e6)}",
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    F = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3); sw = int(a.switch * fps)
    ba = [int(v) for v in a.box_a.split(",")]; bb = [int(v) for v in a.box_b.split(",")]
    mA = build_mask(F[:sw], ba, W, H); mB = build_mask(F[sw:], bb, W, H); mU = mA | mB
    print(f"maske A {int((mA>0).sum())} px · B {int((mB>0).sum())} px")
    del F
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-f", "rawvideo",
                            "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-", "-i", a.src,
                            "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "12",
                            "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy", a.out],
                           stdin=subprocess.PIPE)
    i = 0
    while True:
        b = dec.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        f = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(); t = i / fps
        m = mA if t < a.switch - 0.25 else (mU if t < a.switch + 0.25 else
                                            (mB if t < a.until else None))
        if m is not None:
            f = cv2.inpaint(f, m, 4, cv2.INPAINT_TELEA)
        enc.stdin.write(f.tobytes()); i += 1
    enc.stdin.close(); enc.wait()
    print(f"{i} kare -> {a.out}")


if __name__ == "__main__":
    main()
