#!/usr/bin/env python3
"""
Kaynağa gömülü, SÜREKLİ DEĞİŞEN altyazıyı (kelime kelime yazı, renkli vurgu
kutusu) her karede ayrı tespit edip siler.

dewatermark.py sabit filigran içindir ("karelerin %80'inde aynı yerde").
Buradaki yazı her saniye değiştiği için o yöntem çalışmaz: maske her karede
renkten çıkarılıyor — beyaz dolgu (düşük doygunluk, yüksek parlaklık) +
vurgu kutusu rengi — sadece yazı bandının içinde. Harf gölgesi genişletmeyle
kapsanıyor. Harf alanı Telea ile, büyük vurgu kutusu satır/sütun geçişiyle
dolduruluyor (Telea büyük alanda renk sürüklüyor).

    python3 detext.py in.mp4 out.mp4 --band 610,790 --hl-hue 118,150 --until 36

--band: yazının durduğu y aralığı. --hl-hue: vurgu kutusu tonu (OpenCV 0-180;
mor ≈ 118–150). --extra t0,t1,y0,y1,x0,x1: o zaman/alan içindeki kırmızı
çizimleri (gömülü ok vb.) de sil. Sonra önce/sonra karşılaştırmasına BAK.
"""
import argparse, subprocess, numpy as np, cv2, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dewatermark import probe, fill_smooth


def text_mask(f, y0, y1, hue, white_min, grow=15):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    mn = f.min(2).astype(int); mx = f.max(2).astype(int)
    white = (mn > white_min) & ((mx - mn) < 45)
    hl = (hsv[..., 0] >= hue[0]) & (hsv[..., 0] <= hue[1]) & (hsv[..., 1] > 70) & (hsv[..., 2] > 80)
    m = np.zeros(f.shape[:2], np.uint8)
    m[y0:y1] = ((white | hl)[y0:y1]) * 255
    # tek tük parlak piksel (su parıltısı, pul) yazı değil: yatay yoğunluk ara
    dens = cv2.blur((m > 0).astype(np.float32), (41, 9))
    m[dens < 0.12] = 0
    hlm = np.zeros_like(m); hlm[y0:y1] = hl[y0:y1] * 255
    hlm[dens < 0.12] = 0
    hlm = cv2.morphologyEx(hlm, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    # Harf gölgesi 5–6 px dışarı taşıyor; 9 px'lik genişletme onu kaçırıp
    # noktalı bir hayalet bıraktı (ay balığı klibi). Kelimeler arası boşluk da
    # kapatılıyor ki satır tek parça dolsun.
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 21), np.uint8))
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (grow, grow)))
    return m, cv2.dilate(hlm, np.ones((11, 11), np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--band", default="610,790")
    ap.add_argument("--hl-hue", default="118,150")
    ap.add_argument("--white-min", type=int, default=195)
    ap.add_argument("--grow", type=int, default=15, help="harf gölgesini kapsayan genişletme (px)")
    ap.add_argument("--until", type=float, default=1e9)
    ap.add_argument("--extra", action="append", default=[])
    a = ap.parse_args()
    W, H, fps = probe(a.src)
    y0, y1 = (int(v) for v in a.band.split(",")); hue = [int(v) for v in a.hl_hue.split(",")]
    extras = [[float(v) for v in e.split(",")] for e in a.extra]
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-", "-i", a.src, "-map", "0:v", "-map", "1:a?",
                            "-c:v", "libx264", "-crf", "12", "-preset", "slow", "-pix_fmt", "yuv420p",
                            "-c:a", "copy", a.out], stdin=subprocess.PIPE)
    # Yazı belirirken/kaybolurken (fade) harfler yarı saydam ve beyaz eşiğinin
    # altında kalıyor; ay balığı klibinin ilk 0.3 saniyesinde İngilizce yazı
    # bu yüzden silinmedi. Her kareye komşu karelerin maskesi de eklenir:
    # [-back, +ahead] penceresindeki maskelerin birleşimi.
    from collections import deque
    back, ahead = 6, 10
    frames, masks, times = deque(), deque(), deque()
    red_cfg = extras

    def mask_for(f, t):
        if t >= a.until:
            return np.zeros(f.shape[:2], np.uint8)
        m, hlm = text_mask(f, y0, y1, hue, a.white_min, a.grow)
        m |= hlm
        for t0, t1, ey0, ey1, ex0, ex1 in red_cfg:
            if t0 <= t <= t1:
                hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
                red = ((hsv[..., 0] < 12) | (hsv[..., 0] > 168)) & (hsv[..., 1] > 90) & (hsv[..., 2] > 60)
                r = np.zeros_like(m)
                r[int(ey0):int(ey1), int(ex0):int(ex1)] = red[int(ey0):int(ey1), int(ex0):int(ex1)] * 255
                m |= cv2.dilate(r, np.ones((11, 11), np.uint8))
        return m

    hist = deque(maxlen=back)
    i = 0; eof = False

    def emit():
        f = frames.popleft(); m0 = masks[0]; t = times.popleft()
        u = m0.copy()
        for k in list(masks)[1:ahead + 1]:
            u |= k
        for k in hist:
            u |= k
        if t < a.until and u.any():
            f = cv2.inpaint(f, u, 7, cv2.INPAINT_TELEA)
        hist.append(masks.popleft())
        enc.stdin.write(f.tobytes())

    while True:
        b = dec.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        f = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(); t = i / fps
        frames.append(f); times.append(t); masks.append(mask_for(f, t)); i += 1
        if len(frames) > ahead:
            emit()
    while frames:
        emit()
    enc.stdin.close(); enc.wait()
    print(f"{i} kare -> {a.out}")


if __name__ == "__main__":
    main()
