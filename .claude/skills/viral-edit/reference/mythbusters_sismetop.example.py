#!/usr/bin/env python3
"""MythBusters – şişme top (helikopterden 300 m): TR seslendirme 1.2x, VULRAN girişi + soğuk açılış.
0–2.3 sn: Buster helikopterden atılıyor, düşüş YARIDA donup kesiliyor (sonuç saklı), sonra sunucu yüzü.
Kaynak zaten kurgulu (bulanık üst/alt + gömülü turkuaz altyazı y≈930–985): yalnız net bant (y 298–918)
kırpılıyor, altyazı bandın dışında kalıyor. Bant 2.15x büyütülüp ortaya, üst/alt koyu bar; altyazı alt barda.
Ses: seslendirme + sentetik hareketli yatak (118 BPM, konuşma altında kısılır) + iki çarpmada darbe."""
import json, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/user/Public/.claude/skills/viral-edit/scripts")
import sounddesign as sd

S = os.path.dirname(os.path.abspath(__file__))
SRC = f"{S}/w/src30.mp4"
OUT = os.environ.get("OUT") or f"{S}/out/sisme_top.mp4"
W, H, FPS, SFPS, SW, SH = 1080, 1920, 30, 30, 720, 1280
BY0, BY1 = 298, 918                       # kaynaktaki net bant
Z = 2.15; CW = int(round(W / Z))          # kırpma genişliği (502)
BH = int(round((BY1 - BY0) * Z)); OY = (H - BH) // 2   # bant yüksekliği 1333, üstten 293
ANTON = "/home/user/Public/.claude/skills/viral-edit/fonts/Anton-Regular.ttf"
VO = os.environ.get("VO") or "vo_v"                  # VULRAN hızı: 7 hece/sn, boşluk ≤0.07 sn (votight)
CAPO = json.load(open(f"{S}/w/cap_fast.json", encoding="utf-8"))   # plan zamanları bu (1.2x) sese göre yazıldı
caps = json.load(open(f"{S}/w/cap_v.json" if VO == "vo_v" else f"{S}/w/cap_fast.json", encoding="utf-8"))
_os = [0.0] + [w["s"] for w in CAPO] + [CAPO[-1]["e"] + 5]; _ns = [0.0] + [w["s"] for w in caps] + [caps[-1]["e"] + 5]
tm = lambda t: float(np.interp(t, _os, _ns))           # eski zaman -> yeni zaman
wso = lambda i: round(CAPO[i]["s"] - 0.05, 2)
VOD = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{S}/w/{VO}.wav"],
                           capture_output=True, text=True).stdout)
ws = lambda i: round(caps[i]["s"] - 0.05, 2)
END = VOD + 1.3
SEG = [(0.00, 16.80, 17.45, 450),      # SOĞUK AÇILIŞ: Buster kapıdan tekmeleniyor
       (0.70, 17.50, 17.88, 450),      # dışarı yuvarlanıyor
       (1.25, 18.03, 18.45, 330),      # tepeden: yere doğru düşüyor…
       (2.05, 18.45, 18.45, 330),      # …DONDU (düşüş yarıda kesilir, sonuç saklı)
       (2.30, 2.17, 3.00, 330),        # "helikopterden" sunucu yüzü, gülüyor
       (3.25, 25.17, 26.55, 360),      # "300 metre" helikopter + top
       (4.40, 5.10, 6.30, 360),        # "hayatta kalırsın" top gökyüzünde
       (wso(14), 10.40, 13.77, 330),    # "Mantık basit…" Adam topla yuvarlanıyor
       (wso(25), 14.60, 15.70, 360),    # "Efsane Avcıları" sensör yapıştırma
       (10.85, 15.70, 16.70, 400),     # Buster kapıda
       (11.45, 0.00, 0.72, 450),       # "topsuz attı" tekme
       (wso(31), 0.75, 1.20, 469),      # "Saatte 190" düşüş
       (13.40, 1.25, 2.10, 330),       # tepeden düşüş
       (14.20, 18.90, 20.10, 360),     # "çakıldı" YERE ÇARPMA (kaynak 18.97 → 14.27)
       (15.40, 20.20, 22.10, 360),     # "ölümcül darbe sensörleri"
       (16.80, 22.20, 23.55, 360),     # "kırmızıya döndü" WARNING/FATAL
       (wso(42), 3.00, 5.10, 360),      # "Sonra Buster'ı dev topun içine koydular."
       (wso(48), 23.60, 25.10, 360),    # top helikopterin altında
       (21.55, 28.00, 30.00, 360),     # "90" düşüyor (26.77 planında top bant dışında, alınmadı)
       (23.80, 30.40, 31.15, 420),     # yere yaklaşıyor
       (24.45, 32.45, 33.40, 251),     # "çarptığı an" TOP YERE ÇARPAR (kaynak 32.95 → 24.95)
       (25.40, 35.83, 37.30, 360),     # "sensörlerin hepsi yine kırmızı"
       (wso(64), 34.53, 35.83, 360),    # "Topun içini … doldurdular"
       (wso(69), 22.40, 23.40, 360),    # "Sonuç aynı." FATAL tekrar
       (wso(71), 32.60, 34.40, 251),    # "Çünkü 90 km = duvar" ağır çekim tekrar
       (wso(80), 37.30, 39.15, 360)]    # "kurtaramaz" + BUSTED
SEG = [(tm(t0), a, b, cx) for t0, a, b, cx in SEG]
B = [s[0] for s in SEG] + [END]
T_HIT = [tm(14.27), tm(24.95)]
FREEZE = (B[3], B[4])
seq = []
for k, (t0, a, b, cx) in enumerate(SEG):
    n = int(round(B[k + 1] * FPS)) - int(round(t0 * FPS))
    seq += [(a + (b - a) * j / max(n, 1), k) for j in range(n)]
DUR = len(seq) / FPS
print(f"süre {DUR:.2f}  hızlar", [round((b - a) / (B[k + 1] - B[k]), 2) for k, (_, a, b, _) in enumerate(SEG)])


def grade(f):
    f = f.astype(np.float32); g = f.mean(2, keepdims=True); f = g + (f - g) * 1.15
    f = 128 + (f - 128) * 1.10
    return np.clip(f, 0, 255).astype(np.uint8)


need = set()
for s, _ in seq:
    need.add(int(round(s * SFPS))); need.add(int(s * SFPS)); need.add(int(s * SFPS) + 1)
PATCH_T = (31.70, 34.70); PY0, PY1, PX0, PX1 = 460, 850, 440, 720   # "ESTIMATED VELOCITY 56 MPH" yaması
need.add(int(31.40 * SFPS))
store, k = {}, 0
d = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
patch = None
while True:
    b = d.stdout.read(SW * SH * 3)
    if len(b) < SW * SH * 3:
        break
    if k in need:
        f = np.frombuffer(b, np.uint8).reshape(SH, SW, 3).copy()
        if k == int(31.40 * SFPS):
            patch = f[PY0:PY1, PX0:PX1].copy()
        if patch is not None and PATCH_T[0] <= k / SFPS <= PATCH_T[1]:
            f[PY0:PY1, PX0:PX1] = patch
            # topa bağlı kesik çizgi: ince yatay parlak çizgi (üstü/altı karanlık) -> maske + Telea
            r = f[440:918, 330:720]; br = r.min(2) > 165
            up = np.roll(br, 5, 0); dn = np.roll(br, -5, 0)
            line = br & ~up & ~dn
            line = cv2.morphologyEx(line.astype(np.uint8), cv2.MORPH_OPEN, np.ones((1, 4), np.uint8))
            line = cv2.dilate(line, np.ones((5, 9), np.uint8)) * 255
            if line.any():
                f[440:918, 330:720] = cv2.inpaint(np.ascontiguousarray(r), line, 4, cv2.INPAINT_TELEA)
        store[k] = cv2.imencode(".jpg", f[BY0:BY1], [cv2.IMWRITE_JPEG_QUALITY, 96])[1]
    k += 1
d.wait(); last = max(store)


def get(s, cx):
    i0 = min(int(s * SFPS), last); w_ = s * SFPS - int(s * SFPS)
    a = cv2.imdecode(store[i0], cv2.IMREAD_COLOR)
    if 0.1 < w_ < 0.9 and i0 + 1 in store:
        a = cv2.addWeighted(a, 1 - w_, cv2.imdecode(store[i0 + 1], cv2.IMREAD_COLOR), w_, 0)
    x0 = int(min(max(cx - CW / 2, 0), SW - CW))
    a = cv2.resize(a[:, x0:x0 + CW], (W, BH), interpolation=cv2.INTER_LANCZOS4)
    bl = cv2.GaussianBlur(a, (0, 0), 1.6)
    return grade(cv2.addWeighted(a, 1.45, bl, -0.45, 0))


def zoom(f, z, cx=None, cy=None):
    h, w = f.shape[:2]; cx = w / 2 if cx is None else cx; cy = h / 2 if cy is None else cy
    return cv2.warpAffine(f, np.float32([[z, 0, cx * (1 - z)], [0, z, cy * (1 - z)]]), (w, h), borderMode=cv2.BORDER_REFLECT)


# koyu zemin + bant kenarlarında yumuşak geçiş
yy = np.arange(H)[:, None]
BG = np.zeros((H, W, 3), np.float32)
BG[:] = np.array([16, 12, 10], np.float32) + 10 * np.exp(-((yy - H / 2) / 900.0) ** 2)[..., None]
FEATHER = 70
alpha = np.ones((BH, 1), np.float32)
r = np.arange(FEATHER) / FEATHER
alpha[:FEATHER, 0] = r; alpha[-FEATHER:, 0] = r[::-1]
alpha = alpha[..., None]

_F = {}
font = lambda s: _F.setdefault(s, ImageFont.truetype(ANTON, s))
WHITE, YELLOW, RED = (255, 255, 255), (255, 214, 0), (255, 50, 50)
EMPH = {"şişme", "300", "hayatta", "buster'ı", "topsuz", "190", "çakıldı", "ölümcül", "kırmızıya", "90", "yine", "aynı",
        "duvara", "kurtaramaz", "efsane", "dev"}


def stroke(dl, xy, s, f, col, st):
    dl.text((xy[0] + 5, xy[1] + 8), s, font=f, fill=(0, 0, 0, 170), stroke_width=st, stroke_fill=(0, 0, 0, 170))
    dl.text(xy, s, font=f, fill=col, stroke_width=st, stroke_fill=(0, 0, 0, 255))


def pop(tt, t0, d=0.14, a=0.3):
    u = (tt - t0) / d
    return 1.0 if u >= 1 else 1 + a - a * (1 - (1 - max(u, 0)) ** 3)


chunks, cur = [], []
for w in caps:
    cur.append(w)
    if len(cur) >= 3 or w["w"].endswith((".", ",", ":")):
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)
# ekran göstergeleri: (başla, bitir, büyük, birim, renk, alt satır)
GAUGE = [(ws(8), B[7] - 0.05, "300", "METRE", WHITE, None),
         (ws(32), B[14], "190", "KM/S", RED, None),
         (ws(51), B[20], "90", "KM/S", YELLOW, None),
         (ws(73), B[25] - 0.05, "90", "KM/S", YELLOW, "= DUVARA ÇARPMAK")]
T_BUST = ws(84) + 0.55

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", f"{S}/w/video.mp4"],
                       stdin=subprocess.PIPE)
for n, (s, si) in enumerate(seq):
    tt = n / FPS
    f = get(s, SEG[si][3])
    if FREEZE[0] <= tt < FREEZE[1]:                       # donan düşüş: hızla yakınlaş + kırmızı ton
        e = (tt - FREEZE[0]) / (FREEZE[1] - FREEZE[0])
        f = zoom(f, 1 + 0.35 * e ** 0.7)
        rr = f.copy(); rr[..., 2] = np.clip(rr[..., 2].astype(int) + 90, 0, 255); rr[..., :2] = (rr[..., :2] * 0.6).astype(np.uint8)
        f = cv2.addWeighted(f, 1 - 0.6 * e ** 0.5, rr, 0.6 * e ** 0.5, 0)
        if tt - FREEZE[0] < 0.07:
            f = cv2.addWeighted(f, 0.4, np.full_like(f, 255), 0.6, 0)
    for c in B[1:-1]:                                     # kesim: giren plan büyükten oturur
        if 0 <= tt - c < 0.18 and abs(c - FREEZE[0]) > 0.01:
            f = zoom(f, 1 + 0.09 * (1 - (tt - c) / 0.18) ** 2)
    for th in T_HIT:                                      # çarpma: flaş + sarsıntı
        if 0 <= tt - th < 0.55:
            e = 1 - (tt - th) / 0.55
            f = zoom(f, 1 + 0.07 * e)
            a = 24 * e * (1 if n % 2 else -1)
            f = cv2.warpAffine(f, np.float32([[1, 0, a], [0, 1, -a * 0.7]]), (W, BH), borderMode=cv2.BORDER_REFLECT)
            if tt - th < 0.1:
                f = cv2.addWeighted(f, 0.45, np.full_like(f, 255), 0.55, 0)
    if tt >= T_BUST:
        e = min(1, (tt - T_BUST) / 0.25); rr = f.copy(); rr[..., 2] = np.clip(rr[..., 2].astype(int) + 60, 0, 255)
        f = cv2.addWeighted(f, 1 - 0.35 * e, rr, 0.35 * e, 0)
    fr = BG.copy()
    fr[OY:OY + BH] = fr[OY:OY + BH] * (1 - alpha) + f.astype(np.float32) * alpha
    img = Image.fromarray(cv2.cvtColor(fr.astype(np.uint8), cv2.COLOR_BGR2RGB)).convert("RGBA")
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    for t0, t1, v, unit, col, sub in GAUGE:
        if t0 <= tt < t1:
            sc = pop(tt, t0, 0.16, 0.35); fb = font(int(200 * sc)); fu = font(int(64 * sc))
            tw = dl.textlength(v, font=fb); uw = dl.textlength(unit, font=fu)
            x = W / 2 - (tw + 18 + uw) / 2; y = OY + 60
            stroke(dl, (x, y), v, fb, col + (255,), 13)
            stroke(dl, (x + tw + 18, y + fb.size * 0.62), unit, fu, WHITE + (255,), 7)
            if sub and tt >= t0 + 0.35:
                fs = font(int(84 * pop(tt, t0 + 0.35, 0.16, 0.3))); sw_ = dl.textlength(sub, font=fs)
                stroke(dl, (W / 2 - sw_ / 2, y + fb.size * 1.32), sub, fs, RED + (255,), 9)
    if tt >= T_BUST:
        sc = pop(tt, T_BUST, 0.18, 0.6)
        S_ = Image.new("RGBA", (900, 330), (0, 0, 0, 0)); ds = ImageDraw.Draw(S_)
        ds.rounded_rectangle([20, 20, 880, 310], radius=30, outline=RED + (255,), width=22)
        fo = font(210); tw = ds.textlength("BUSTED", font=fo)
        ds.text((450 - tw / 2, 165 - fo.size * 0.62), "BUSTED", font=fo, fill=RED + (255,), stroke_width=6, stroke_fill=(90, 0, 0, 255))
        S_ = S_.resize((int(900 * sc), int(330 * sc))).rotate(-8, resample=Image.BICUBIC, expand=True)
        lay.alpha_composite(S_, (int(W / 2 - S_.size[0] / 2), int(H * 0.45 - S_.size[1] / 2)))
        dl = ImageDraw.Draw(lay)
    for ch in chunks:                                     # altyazı: alt barda, bant kenarına binerek
        if ch[0]["s"] <= tt < ch[-1]["e"] + 0.15:
            fo = font(104); full = " ".join(w["w"] for w in ch)
            while dl.textlength(full, font=fo) > W - 80:
                fo = font(fo.size - 4)
            x = W / 2 - dl.textlength(full, font=fo) / 2; y = OY + BH - fo.size * 0.55
            for w in ch:
                if w["s"] > tt:
                    break
                key = w["w"].lower().strip(".,:")
                col = RED if key in ("190", "çakıldı", "kırmızıya", "kurtaramaz", "ölümcül") else (
                    YELLOW if (key in EMPH or tt < w["e"]) else WHITE)
                stroke(dl, (x, y), w["w"], fo, col + (255,), 11)
                x += dl.textlength(w["w"] + " ", font=fo)
            break
    img.alpha_composite(lay)
    enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
enc.stdin.close(); enc.wait()

# ---- ses ----
SR = sd.SR; N = int(round(DUR * SR))
rd = lambda p, af="anull": np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-af", af, "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"],
                                                        capture_output=True).stdout, np.float32).copy()
vo = rd(f"{S}/w/{VO}.wav", "highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80")
mus = rd(os.environ.get("MUSIC_FILE") or f"{S}/w/music.wav")
voc = np.zeros(N); voc[:min(N, len(vo))] = vo[:N]
m = np.zeros(N); m[:min(N, len(mus))] = mus[:N]
rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 1e-4] ** 2) + 1e-12)
m = m * (rms(voc) / rms(m)) * 10 ** (-13 / 20)            # müzik konuşmanın ~13 dB altında…
env = np.convolve(np.abs(voc), np.ones(int(0.05 * SR)) / int(0.05 * SR), mode="same")
duck = 1 - 0.55 * np.clip(env / (np.percentile(env, 90) + 1e-9), 0, 1)   # …konuşurken ~7 dB daha iner
duck = np.convolve(duck, np.ones(int(0.2 * SR)) / int(0.2 * SR), mode="same")
fr_ = int(FREEZE[0] * SR), int(FREEZE[1] * SR)            # donmada müzik bir an kesilir (düşüş askıda)
gate = np.ones(N); gate[fr_[0]:fr_[1]] = 0.15
gate = np.convolve(gate, np.ones(int(0.03 * SR)) / int(0.03 * SR), mode="same")
MUS_GAIN = float(os.environ.get("MUSIC", "0"))   # sentetik yatak reddedildi; gerçek parça gelince MUSIC_FILE ile
mix = voc + m * duck * gate * MUS_GAIN
fx = np.zeros(N)


def place(sig, t_, g_):
    a = int(t_ * SR); b = min(N, a + len(sig))
    if 0 <= a < N:
        fx[a:b] += sig[:b - a] / (np.max(np.abs(sig)) + 1e-9) * g_


for th in T_HIT:
    place(sd.boom(), th, 0.9)
place(sd.boom(), T_BUST, 0.7)
mix += fx * 0.5
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
