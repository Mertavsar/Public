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


def build_mask(F, box, W, H, grow=7, halo_min=140):
    y0, y1, x0, x1 = box
    mn = F.min(axis=3).astype(int); mx = F.max(axis=3).astype(int)
    hsv = np.stack([cv2.cvtColor(f, cv2.COLOR_BGR2HSV) for f in F])
    core = ((mn > 195) & ((mx - mn) < 40)).mean(0) > 0.8
    halo = ((mn > halo_min) & ((mx - mn) < 60)).mean(0) > 0.7
    h_ = hsv[..., 0]
    icon = ((hsv[..., 1] > 55) & (hsv[..., 2] > 110) &
            (((h_ > 78) & (h_ < 105)) | (h_ > 155) | (h_ < 10))).mean(0) > 0.6
    near = cv2.dilate(((core | icon) * 255).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    logo = cv2.dilate((core * 255).astype(np.uint8), np.ones((41, 41), np.uint8)) > 0
    sel = core | (halo & near) | (icon & logo)
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = sel[y0:y1, x0:x1] * 255
    return cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (grow, grow)))


def static_text_mask(F, box, W, H, thr=16, grow=9):
    """Videonun TAMAMINDA duran gömülü yazı (kaynağın kendi başlığı) — düz
    zemin üstünde. Zaman medyanından arka plan satır satır kenarlardan
    doğrusal kestiriliyor; ondan sapan her şey (beyaz harf, renkli kutu) maske.
    Fil klibinde İngilizce başlık + pembe kutular + kanal adı böyle silindi."""
    y0, y1, x0, x1 = box
    M = np.median(F[:, y0:y1, x0:x1].astype(np.float32), axis=0)
    g = M.mean(2)
    edge = max(6, (x1 - x0) // 20)
    left = np.median(g[:, :edge], axis=1); right = np.median(g[:, -edge:], axis=1)
    xs = np.linspace(0, 1, x1 - x0)[None, :]
    bg = left[:, None] * (1 - xs) + right[:, None] * xs
    hsv = cv2.cvtColor(M.astype(np.uint8), cv2.COLOR_BGR2HSV)
    h_ = hsv[..., 0]
    pink = (hsv[..., 1] > 30) & ((h_ > 150) | (h_ < 12))          # vurgu kutuları
    sel = (np.abs(g - bg) > thr) | pink
    m = np.zeros((H, W), np.uint8)
    m[y0:y1, x0:x1] = sel * 255
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (grow, grow)))
    # harflerin arasındaki temiz adacıklar dolguda leke bırakıyor: bloğu kapat
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))


def fill_smooth(f, m, k=0):
    """Büyük maske için dolgu: her satırda maskenin solundaki ve sağındaki
    temiz pikseller arasında doğrusal geçiş, sonra hafif yumuşatma.

    Neden: Telea büyük alanda renk sürüklüyor (fil klibinde pembe/turkuaz
    leke bıraktı), Gauss tabanlı normalize dolgu çekirdekten büyük maskede
    ortayı siyah bırakıyor. Gömülü başlıklar genelde yukarıdan aşağı değişen,
    yatayda düz bir sis/gradyan zemin üstünde — satır satır doğrusal geçiş o
    zemini olduğu gibi taşıyor."""
    src = f.astype(np.float32)
    sel = m > 0

    def interp(img, mask):
        o = img.copy(); xs = np.arange(img.shape[1])
        for y in np.nonzero(mask.any(1))[0]:
            ok = ~mask[y]
            if ok.sum() < 2:
                continue
            for c in range(3):
                o[y, ~ok, c] = np.interp(xs[~ok], xs[ok], img[y, ok, c])
        return o
    # yatay geçiş kenardaki vinyeti taşır (açık bant), dikey geçiş üstteki
    # görüntüyü aşağı akıtır — ortalamaları ikisinin de izini yarıya indiriyor
    row = interp(src, sel)
    # dikey geçişi doğrudan pikselden alırsan üstteki doku (çakıl, ray) aşağı
    # çizgi çizgi akıyor — fil klibinde dikey şeritler bıraktı. Önce maskeyi
    # dışarıda tutarak yatayda geniş yumuşat, sütunlara sadece ton taşınsın.
    valid = (~sel).astype(np.float32)
    kx = (81, 1)
    num = cv2.blur(src * valid[..., None], kx); den = cv2.blur(valid, kx)[..., None]
    srcH = np.where(den > 1e-3, num / np.maximum(den, 1e-3), src)
    col = interp(srcH.transpose(1, 0, 2), sel.T).transpose(1, 0, 2)
    out = src.copy(); out[sel] = (0.5 * row + 0.5 * col)[sel]
    sm = cv2.GaussianBlur(out, (0, 0), 3)
    out[sel] = sm[sel]
    # kenarı orijinale yumuşak geçir: düz dolgu keskin kenarlı bir dikdörtgen
    # gibi seçiliyordu. İçerisi (kenardan ~10 px içeri) tamamen dolgu kalır.
    a = np.clip(cv2.GaussianBlur(sel.astype(np.float32), (0, 0), 10) * 1.8, 0, 1)[..., None]
    out = a * out + (1 - a) * src
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--switch", type=float, required=True, help="filigranın köşe değiştirdiği an")
    ap.add_argument("--box-a", required=True); ap.add_argument("--box-b", required=True)
    ap.add_argument("--until", type=float, default=1e9, help="kapanış kartı başlangıcı")
    ap.add_argument("--static-box", action="append", default=[],
                    help="videonun tamamında duran gömülü yazı kutusu y0,y1,x0,x1 (tekrarlanabilir)")
    ap.add_argument("--grow", type=int, default=7,
                    help="maske genişletme (px). Kalın/parlak filigranda hayalet kalırsa 11-13")
    ap.add_argument("--halo-min", type=int, default=140,
                    help="hâle eşiği; parlak filtreli kaynakta hayalet kalırsa düşür (110-120)")
    a = ap.parse_args()
    W, H, fps = probe(a.src)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.src, "-t", f"{min(a.until, 1e6)}",
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    F = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3); sw = int(a.switch * fps)
    ba = [int(v) for v in a.box_a.split(",")]; bb = [int(v) for v in a.box_b.split(",")]
    mA = build_mask(F[:sw], ba, W, H, a.grow, a.halo_min); mB = build_mask(F[sw:], bb, W, H, a.grow, a.halo_min)
    mS = np.zeros((H, W), np.uint8)
    for sb in a.static_box:
        mS = mS | static_text_mask(F, [int(v) for v in sb.split(",")], W, H)
    if a.static_box:
        print(f"sabit yazi maskesi {int((mS>0).sum())} px")
    # sabit bloğun çevresi: filigranın bu bölgeye taşan kısmı da satır dolgusuna girer
    mSz = cv2.dilate(mS, np.ones((61, 61), np.uint8))
    mU = mA | mB
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
        if a.static_box:
            # sabit bloğa değen filigran pikselleri dolguya kaynak olmasın
            mm = mS if m is None else (mS | (cv2.dilate(m, np.ones((15, 15), np.uint8)) & mSz))
            f = fill_smooth(f, mm)
        if m is not None:
            m = cv2.bitwise_and(m, cv2.bitwise_not(mS))
            f = cv2.inpaint(f, m, 4, cv2.INPAINT_TELEA)
        enc.stdin.write(f.tobytes()); i += 1
    enc.stdin.close(); enc.wait()
    print(f"{i} kare -> {a.out}")


if __name__ == "__main__":
    main()
