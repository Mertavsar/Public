#!/usr/bin/env python3
"""MythBusters – kızartma yağıyla araba (resmi Shorts, dikey 1080x1920 25fps, gömülü beyaz altyazı y≈1391–1447).
Seslendirme boşluksuz ~7 hece/sn (votight --gap 0.04). Kullanılan 15 aralık sel.mp4'te birleştirildi, altyazı
şeridi (y 1216–1600) ProPainter ile silinip geri yapıştırılıyor. Oklar/etiketler kelimeye oturur.
Ses: seslendirme + kaynağın kendi altyapısı (MDX inst) kesintisiz, konuşmanın ~15 LU altında. Sentetik müzik/efekt yok."""
import json, os, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

S = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT") or f"{S}/out/kizartma_yagi.mp4"
W, H, FPS, SFPS = 1080, 1920, 30, 25
STRIP_Y = 1216
ANTON = "/home/user/Public/.claude/skills/viral-edit/fonts/Anton-Regular.ttf"
caps = json.load(open(f"{S}/w/cap.json", encoding="utf-8"))
MAP = json.load(open(f"{S}/w/sel_map.json"))
VOD = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{S}/w/vo_v.wav"],
                           capture_output=True, text=True).stdout)
ws = lambda i: round(caps[i]["s"] - 0.05, 2)
END = VOD + 1.1


def sel_t(t):                                            # orijinal kaynak zamanı -> sel.mp4 zamanı
    for a, b, c in MAP:
        if a - 0.02 <= t <= b + 0.02:
            return c + min(max(t - a, 0), b - a - 0.04)
    raise ValueError(f"{t} seçili aralıkta değil")


SEG = [(0.00, 0.65, 3.20),      # SOĞUK AÇILIŞ: altın kızartma yağı akıyor + "KIZARTMA YAĞI" oku
       (2.10, 55.45, 57.20),    # "USED COOKING OIL" bidonu
       (3.30, 6.75, 8.60),      # Adam & Jamie arabada
       (4.50, 58.20, 59.85),    # "hiçbir değişiklik yapmadan çalışır" Jamie şüpheli yakın
       (ws(15), 8.60, 10.75),   # "Mantık şu" arabada (KIVILCIM ✗ / SIKIŞTIRMA ✓)
       (7.95, 13.95, 15.50),    # yakıt filtresi
       (ws(24), 15.60, 17.45),  # "Efsane Avcıları" gülüyorlar
       (11.05, 25.25, 26.33),   # "kızartma yağını" arabaya bağlı yağ bidonu (ok)
       (12.05, 20.95, 22.40),   # "Mercedes'in deposuna"
       (13.05, 10.85, 12.15),   # "kontağı çevirdi" anahtar (daire)
       (14.30, 12.12, 12.12),   # DONMA + "?"
       (ws(37), 12.25, 13.90),  # "Motor sorunsuz çalıştı" ızgara + ÇALIŞTI damgası
       (ws(40), 32.85, 35.20),  # "Pistte turlar"
       (17.40, 35.30, 37.15),   # jant
       (18.40, 27.15, 29.45),   # önden araba (7,8 L göstergesi)
       (ws(51), 42.75, 46.20),  # "%10" konuşma (çubuklar)
       (22.85, 37.25, 39.30),   # "bedava" gülüyorlar (0 TL)
       (ws(62), 48.45, 50.85),  # "Ama dikkat" Jamie
       (25.85, 14.40, 15.50),   # "tıkayıp zarar" filtre (kırmızı daire)
       (ws(72), 64.98, 67.60)]  # "efsane doğru çıktı" araba geliyor + DOĞRU ÇIKTI
B = [s[0] for s in SEG] + [END]
FREEZE = (B[10], B[11])
seq = []
for k, (t0, a, b) in enumerate(SEG):
    n = int(round(B[k + 1] * FPS)) - int(round(t0 * FPS))
    seq += [(a + (b - a) * j / max(n, 1), k) for j in range(n)]
DUR = len(seq) / FPS
print(f"süre {DUR:.2f}  hızlar", [round((b - a) / (B[k + 1] - B[k]), 2) for k, (_, a, b) in enumerate(SEG)])

need = set()
for s, _ in seq:
    i = sel_t(s) * SFPS; need.update({int(i), int(i) + 1})


def frames(p, w, h):
    d = subprocess.Popen(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    while True:
        b = d.stdout.read(w * h * 3)
        if len(b) < w * h * 3:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)
    d.wait()


BAR = os.environ.get("BAR") == "1"                      # hızlı sürüm: silme yerine altyazı bandı İngilizceyi örter
strip_src = f"{S}/w/strip_clean.mp4" if (os.path.exists(f"{S}/w/strip_clean.mp4") and not BAR) else None
store = {}
sg = frames(strip_src, W, 384) if strip_src else None
for k, f in enumerate(frames(f"{S}/w/sel.mp4", W, H)):
    st = next(sg, None) if sg else None
    if k in need:
        f = f.copy()
        if st is not None:
            f[STRIP_Y:STRIP_Y + 384] = st
        store[k] = cv2.imencode(".jpg", f, [cv2.IMWRITE_JPEG_QUALITY, 94])[1]
last = max(store)


def grade(f):
    f = f.astype(np.float32); g = f.mean(2, keepdims=True); f = g + (f - g) * 1.18
    return np.clip(128 + (f - 128) * 1.08, 0, 255).astype(np.uint8)


def get(s):
    t = sel_t(s) * SFPS; i0 = min(int(t), last); w_ = t - int(t)
    a = cv2.imdecode(store[i0], cv2.IMREAD_COLOR)
    if 0.15 < w_ < 0.85 and i0 + 1 in store:
        a = cv2.addWeighted(a, 1 - w_, cv2.imdecode(store[i0 + 1], cv2.IMREAD_COLOR), w_, 0)
    return grade(a)


def zoom(f, z, cx=W / 2, cy=H / 2):
    return cv2.warpAffine(f, np.float32([[z, 0, cx * (1 - z)], [0, z, cy * (1 - z)]]), (W, H), borderMode=cv2.BORDER_REFLECT)


_F = {}
font = lambda s: _F.setdefault(s, ImageFont.truetype(ANTON, int(s)))
WHITE, YELLOW, RED, GREEN, BLACK = (255, 255, 255), (255, 214, 0), (235, 40, 45), (40, 200, 80), (0, 0, 0)


def pop(tt, t0, d=0.15, a=0.35):
    u = (tt - t0) / d
    return 1.0 if u >= 1 else 1 + a - a * (1 - (1 - max(u, 0)) ** 3)


def ease(tt, t0, d=0.18):
    return float(np.clip((tt - t0) / d, 0, 1)) ** 0.6


def stroke(dl, xy, s, f, col, st=10):
    dl.text((xy[0] + 5, xy[1] + 8), s, font=f, fill=(0, 0, 0, 160), stroke_width=st, stroke_fill=(0, 0, 0, 160))
    dl.text(xy, s, font=f, fill=col + (255,), stroke_width=st, stroke_fill=(0, 0, 0, 255))


def tag(lay, txt, cx, cy, size, bg, fg=WHITE, sc=1.0, angle=0):
    L = Image.new("RGBA", lay.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(L); f = font(size * sc)
    tw = dl.textlength(txt, font=f); bb = dl.textbbox((0, 0), txt, font=f); th = bb[3] - bb[1]; p = 22 * sc
    dl.rounded_rectangle([cx - tw / 2 - p, cy - th / 2 - p, cx + tw / 2 + p, cy + th / 2 + p], radius=18 * sc,
                         fill=bg + (255,), outline=BLACK + (255,), width=int(7 * sc))
    dl.text((cx - tw / 2, cy - th / 2 - bb[1]), txt, font=f, fill=fg + (255,))
    lay.alpha_composite(L.rotate(angle, resample=Image.BICUBIC, center=(cx, cy)) if angle else L)


def arrow(dl, x0, y0, x1, y1, e, col=RED):
    if e <= 0:
        return
    x1, y1 = x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
    ang = np.arctan2(y1 - y0, x1 - x0); hl = 70
    bx, by = x1 - hl * 0.8 * np.cos(ang), y1 - hl * 0.8 * np.sin(ang)
    head = [(x1, y1), (x1 - hl * np.cos(ang - 0.5), y1 - hl * np.sin(ang - 0.5)), (x1 - hl * np.cos(ang + 0.5), y1 - hl * np.sin(ang + 0.5))]
    dl.line([x0, y0, bx, by], fill=BLACK + (255,), width=34); dl.polygon(head, fill=BLACK + (255,), outline=BLACK + (255,), width=12)
    dl.line([x0, y0, bx, by], fill=col + (255,), width=22); dl.polygon(head, fill=col + (255,))


def ring(dl, cx, cy, rx, ry, e, col=RED):
    if e <= 0:
        return
    box = [cx - rx, cy - ry, cx + rx, cy + ry]
    dl.arc(box, -90, -90 + 360 * e, fill=BLACK + (255,), width=26); dl.arc(box, -90, -90 + 360 * e, fill=col + (255,), width=16)


def stamp(lay, txt, col, cx, cy, tt, t0, size=170, angle=-8):
    sc = pop(tt, t0, 0.18, 0.6)
    f = font(size); tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = tmp.textlength(txt, font=f); w, h = int(tw + 120), int(size * 1.45)
    S_ = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ds = ImageDraw.Draw(S_)
    ds.rounded_rectangle([10, 10, w - 10, h - 10], radius=28, outline=col + (255,), width=20, fill=(0, 0, 0, 90))
    ds.text((w / 2 - tw / 2, h / 2 - size * 0.66), txt, font=f, fill=col + (255,), stroke_width=5, stroke_fill=(0, 0, 0, 255))
    S_ = S_.resize((max(1, int(w * sc)), max(1, int(h * sc)))).rotate(angle, resample=Image.BICUBIC, expand=True)
    lay.alpha_composite(S_, (int(cx - S_.size[0] / 2), int(cy - S_.size[1] / 2)))


chunks, cur = [], []
for w in caps:
    cur.append(w)
    if len(cur) >= 3 or w["w"].endswith((".", ",", ":")):
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)
EMPH = {"kızartma", "yağını", "dizel", "hiçbir", "değişiklik", "kıvılcımla", "sıkıştırmayla", "kontağı", "çalıştı.", "7,8",
        "%10", "bedava.", "dikkat:", "zarar", "doğru", "efsane", "mercedes'in"}
REDW = {"değil,", "dikkat:", "zarar", "tıkayıp"}

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", f"{S}/w/video.mp4"],
                       stdin=subprocess.PIPE)
T_START = B[11]
for n, (s, si) in enumerate(seq):
    tt = n / FPS
    f = get(s)
    if FREEZE[0] <= tt < FREEZE[1]:                       # kontak dondu: yakınlaş + karart
        e = (tt - FREEZE[0]) / (FREEZE[1] - FREEZE[0])
        f = zoom(f, 1 + 0.25 * e ** 0.7, 540, 720)
        f = (f * (1 - 0.35 * e)).astype(np.uint8)
    for c in B[1:-1]:                                     # kesim: giren plan büyükten oturur
        if 0 <= tt - c < 0.16 and abs(c - FREEZE[0]) > 0.01:
            f = zoom(f, 1 + 0.08 * (1 - (tt - c) / 0.16) ** 2)
    if 0 <= tt - T_START < 0.45:                          # motor çalıştı: flaş + titreşim
        e = 1 - (tt - T_START) / 0.45; a = 14 * e * (1 if n % 2 else -1)
        f = cv2.warpAffine(f, np.float32([[1, 0, a], [0, 1, a * 0.6]]), (W, H), borderMode=cv2.BORDER_REFLECT)
        if tt - T_START < 0.08:
            f = cv2.addWeighted(f, 0.5, np.full_like(f, 255), 0.5, 0)
    img = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA")
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    # --- oklar, etiketler, grafikler ---
    if 0.10 <= tt < B[1]:
        arrow(dl, 380, 760, 560, 900, ease(tt, 0.10)); tag(lay, "KIZARTMA YAĞI", 300, 660, 92, RED, sc=pop(tt, 0.10))
    if ws(20) <= tt < B[6]:
        tag(lay, "KIVILCIM", 540, 480, 110, (70, 70, 70), sc=pop(tt, ws(20)))
        dl = ImageDraw.Draw(lay)
        if tt >= ws(21):
            e = ease(tt, ws(21), 0.15); dl.line([300, 480, 300 + 480 * e, 480], fill=RED + (255,), width=18)
        if tt >= ws(22):
            tag(lay, "SIKIŞTIRMA ✓".replace(" ✓", ""), 540, 650, 120, GREEN, sc=pop(tt, ws(22)))
    if B[7] + 0.05 <= tt < B[8]:
        arrow(dl, 400, 830, 760, 880, ease(tt, B[7] + 0.05)); tag(lay, "YAKIT: KIZARTMA YAĞI", 400, 720, 78, RED, sc=pop(tt, B[7] + 0.05))
    dl = ImageDraw.Draw(lay)
    if ws(35) <= tt < FREEZE[1]:
        ring(dl, 470, 800, 170, 150, ease(tt, ws(35), 0.25))
    if FREEZE[0] <= tt < FREEZE[1]:
        fq = font(520 * pop(tt, FREEZE[0], 0.12, 0.4)); qw = dl.textlength("?", font=fq)
        stroke(dl, (540 - qw / 2, 960 - fq.size * 0.62), "?", fq, RED, 16)
    if ws(39) + 0.25 <= tt < ws(45):                      # cevap verildi -> hemen yeni soru (yeniden kanca)
        sc = pop(tt, ws(39) + 0.25, 0.16, 0.35); fq = font(118 * sc)
        for j, line in enumerate(["PEKİ KAÇ LİTRE", "YAKTI?"]):
            lw = dl.textlength(line, font=fq); stroke(dl, (540 - lw / 2, 560 + j * fq.size * 1.08), line, fq, YELLOW, 12)
    dl = ImageDraw.Draw(lay)
    if ws(45) <= tt < B[15]:                              # 100 km = 7,8 L
        sc = pop(tt, ws(45), 0.16, 0.35); fb = font(230 * sc); fu = font(78 * sc); fs = font(70 * sc)
        v = "7,8"; tw = dl.textlength(v, font=fb); uw = dl.textlength("LİTRE", font=fu)
        x = 540 - (tw + 20 + uw) / 2; y = 470
        stroke(dl, (540 - dl.textlength("100 KM'DE", font=fs) / 2, y - 95 * sc), "100 KM'DE", fs, WHITE, 8)
        stroke(dl, (x, y), v, fb, YELLOW, 14); stroke(dl, (x + tw + 20, y + fb.size * 0.6), "LİTRE", fu, WHITE, 8)
    if ws(55) <= tt < ws(59):                             # verim çubukları
        e = ease(tt, ws(55), 0.35)
        dl.rounded_rectangle([90, 400, 990, 790], radius=30, fill=(0, 0, 0, 175))
        for j, (lab, pct, col) in enumerate([("MAZOT", 1.0, WHITE), ("KIZARTMA YAĞI", 0.9, YELLOW)]):
            y = 450 + j * 170; fL = font(64)
            stroke(dl, (130, y), lab, fL, col, 6)
            dl.rounded_rectangle([130, y + 85, 130 + 720 * pct * e, y + 140], radius=14, fill=col + (255,))
            stroke(dl, (130 + 720 * pct * e + 18, y + 72), f"%{int(round(pct * 100 * e))}", font(70), col, 7)
    if ws(59) <= tt < B[17]:
        stamp(lay, "YAKIT: 0 TL", GREEN, 540, 600, tt, ws(59), size=150, angle=-6)
    if ws(62) <= tt < B[18]:
        tag(lay, "DİKKAT!", 540, 520, 140, YELLOW, fg=BLACK, sc=pop(tt, ws(62)), angle=-4)
    dl = ImageDraw.Draw(lay)
    if B[18] <= tt < B[19]:
        ring(dl, 660, 760, 190, 430, ease(tt, B[18], 0.3))
        if tt >= ws(69):
            tag(lay, "TIKANABİLİR", 540, 1270, 100, RED, sc=pop(tt, ws(69)))
    if tt >= ws(75):
        stamp(lay, "DOĞRU ÇIKTI", GREEN, 540, 760, tt, ws(75), size=160)
        if tt >= ws(75) + 0.45:
            tag(lay, "UZUN VADEDE MOTORA ZARAR VEREBİLİR", 540, 900, 52, (30, 30, 30), fg=YELLOW, sc=pop(tt, ws(75) + 0.45, 0.15, 0.2))
        dl = ImageDraw.Draw(lay)
    dl = ImageDraw.Draw(lay)
    # --- 3 soruluk kontrol listesi (vaat + yeniden kanca) ---
    if tt >= B[1]:
        Q = [("ÇALIŞIR MI?", ws(39), "EVET", GREEN), ("KAÇ LİTRE YAKAR?", ws(48), "7,8 L", GREEN),
             ("MOTORA ZARARI VAR MI?", ws(69), "OLABİLİR", RED)]
        sc0 = pop(tt, B[1], 0.18, 0.25); x0, y0 = 70, 70
        dl.rounded_rectangle([x0 - 20, y0 - 18, 1010, y0 + 3 * 92 - 4], radius=24, fill=(0, 0, 0, 185), outline=(255, 255, 255, 90), width=3)
        for j, (q, tq, ans, col) in enumerate(Q):
            y = y0 + j * 92; done = tt >= tq; s_ = pop(tt, tq, 0.18, 0.45) if done else 1.0
            bx = [x0, y + 8, x0 + 58, y + 66]
            dl.rounded_rectangle(bx, radius=10, fill=(col if done else (40, 40, 40)) + (255,), outline=WHITE + (255,), width=4)
            if done and col == GREEN:
                dl.line([x0 + 12, y + 38, x0 + 25, y + 52, x0 + 47, y + 20], fill=WHITE + (255,), width=9, joint="curve")
            elif done:
                fx_ = font(52); dl.text((x0 + 29 - dl.textlength("!", font=fx_) / 2, y + 6), "!", font=fx_, fill=WHITE + (255,))
            fq = font(58 * (s_ if done else 1)); stroke(dl, (x0 + 80, y + 4), q, fq, WHITE if not done else (200, 200, 200), 6)
            if done:
                fa = font(58 * s_); aw = dl.textlength(ans, font=fa); stroke(dl, (990 - aw, y + 4), ans, fa, col, 7)
    # --- altyazı ---
    if BAR:
        for (y0, y1, a) in [(1336, 1352, 130), (1352, 1366, 215), (1366, 1478, 255), (1478, 1492, 215), (1492, 1508, 130)]:
            dl.rectangle([0, y0, W, y1], fill=(8, 8, 10, a))
    for ch in chunks:
        if ch[0]["s"] <= tt < ch[-1]["e"] + 0.12:
            fo = font(104); full = " ".join(w["w"] for w in ch)
            while dl.textlength(full, font=fo) > W - 80:
                fo = font(fo.size - 4)
            x = W / 2 - dl.textlength(full, font=fo) / 2; y = 1420 - fo.size * 0.55
            for w in ch:
                if w["s"] > tt:
                    break
                key = w["w"].lower()
                col = RED if key in REDW else (YELLOW if (key in EMPH or tt < w["e"]) else WHITE)
                stroke(dl, (x, y), w["w"], fo, col, 11)
                x += dl.textlength(w["w"] + " ", font=fo)
            break
    img.alpha_composite(lay)
    enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
enc.stdin.close(); enc.wait()

# ---- ses: seslendirme + kaynağın kendi altyapısı (kesintisiz) ----
SR = 44100; N = int(round(DUR * SR))
rd = lambda p, af="anull": np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-af", af, "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"],
                                                        capture_output=True).stdout, np.float32).copy()
vo = rd(f"{S}/w/vo_v.wav", "highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80")
bed = rd(f"{S}/w/src_inst.wav")
voc = np.zeros(N); voc[:min(N, len(vo))] = vo[:N]
m = np.zeros(N); m[:min(N, len(bed))] = bed[:N]
rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 1e-4] ** 2) + 1e-12)
m = m * (rms(voc) / rms(m)) * 10 ** (-14 / 20)
env = np.convolve(np.abs(voc), np.ones(int(0.05 * SR)) / int(0.05 * SR), mode="same")
duck = 1 - 0.35 * np.clip(env / (np.percentile(env, 90) + 1e-9), 0, 1)
duck = np.convolve(duck, np.ones(int(0.2 * SR)) / int(0.2 * SR), mode="same")
mix = voc + m * duck
mix.astype(np.float32).tofile(f"{S}/w/mix.f32")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", f"{S}/w/mix.f32",
                "-af", f"afade=t=out:st={DUR - 0.4:.2f}:d=0.4,loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "2", f"{S}/w/audio.wav"], check=True)
os.remove(f"{S}/w/mix.f32")
vk = int(min(14000, 27 * 8 * 1024 / DUR - 200)); pl = f"{S}/w/pass"
c = ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{vk}k", "-maxrate", f"{int(vk * 1.4)}k", "-bufsize", f"{vk * 2}k", "-passlogfile", pl]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/w/video.mp4", *c, "-pass", "1", "-an", "-f", "null", "/dev/null"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/w/video.mp4", "-i", f"{S}/w/audio.wav", "-map", "0:v", "-map", "1:a",
                *c, "-pass", "2", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", OUT], check=True)
print(f"{OUT}: {os.path.getsize(OUT) / 1e6:.1f} MB, {DUR:.2f} sn")
