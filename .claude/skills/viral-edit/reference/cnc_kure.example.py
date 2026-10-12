#!/usr/bin/env python3
"""CNC torna – küre mafsal: TR seslendirme (sıkı 1.18x), cümle = sahne, kaynak tek yönde akar (geri sarma yok),
'kodladı' anında G-code paneli, 'yanlış değer' alarmı, parlak küre yalnız sonda (clink + ok).
Geçişler: bulanıklıksız zoom-punch + RGB kayması. Makine sesi duyulur ama konuşmanın altında."""
import json, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/user/Public/.claude/skills/viral-edit/scripts")
import sounddesign as sd

S = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = f"{S}/in/src.mp4", f"{S}/out/cnc_kure.mp4"
W, H, FPS, SFPS = 1080, 1920, 30, 30
ANTON = "/home/user/Public/.claude/skills/viral-edit/fonts/Anton-Regular.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
caps = json.load(open(f"{S}/w/cap_fast.json", encoding="utf-8"))
VOD = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{S}/w/vo_fast.wav"],
                           capture_output=True, text=True).stdout)
ws = lambda i: caps[i]["s"] - 0.05
END = VOD + 0.7
SEG = [(0.0, "play", 0.0, 1.4),        # 0 "Bu metalin … tahmin edebilir misin?" (hook)
       (ws(10), "play", 1.4, 3.3),     # 1 "Çünkü makine kesmeye başladığında … anlamsız görünüyor."
       (ws(21), "play", 3.3, 5.6),     # 2 "Ama dikkat et, … milimetre alıyor ve içeride saklı" (ok)
       (ws(34), "play", 5.6, 6.8),     # 3 "olan şekil yavaş yavaş ortaya çıkıyor." (ok + clink)
       (ws(40), "play", 6.8, 7.7),     # 4 "Fakat asıl şaşırtıcı olan kesim değil."
       (ws(46), "play", 7.7, 8.8),     # 5 "Bu makine nerede duracağını kendi kendine bilmiyor." (panel)
       (ws(53), "play", 8.8, 11.0),    # 6 "Her hareketi, … önceden kodladı." (G-code yazılıyor)
       (ws(67), "play", 11.0, 13.0),   # 7 "Tek bir yanlış değer … çöpe çevirebilir." (alarm; parlatma başlıyor)
       (ws(75), "play", 13.0, 18.9)]   # 8 "Ama kod doğru olduğunda … bu hale geliyor." (sonuç yalnız burada)
# kullanıcı: geri sarma yok, sonucu önceden gösterme -> kaynak baştan sona tek yönde akar
B = [s[0] for s in SEG] + [END]
seq = []
for k, (t0, kind, a, b) in enumerate(SEG):
    n = int(round(B[k + 1] * FPS)) - int(round(t0 * FPS))
    for j in range(n):
        u = j / max(1, n - 1)
        if kind == "ffwd":
            u = u ** 1.6                                   # hızlanarak gider
        seq.append((a + (b - a) * (u if kind in ("rewind", "ffwd") else j / n), kind, u, k))
DUR = len(seq) / FPS
print(f"süre {DUR:.2f}  hızlar", [round((b - a) / (B[k + 1] - B[k]), 2) for k, (_, _, a, b) in enumerate(SEG)])

yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.32 * np.clip(np.sqrt(((xx - W * 0.55) / (W / 2)) ** 2 + ((yy - H * 0.3) / (H / 2)) ** 2) - 0.45, 0, 1) ** 1.3)[..., None]


def grade(f):
    f = f.astype(np.float32); g = f.mean(2, keepdims=True); f = g + (f - g) * 1.12
    f = 128 + (f - 128) * 1.12; lum = f.mean(2) / 255
    f[..., 0] += 14 * (1 - lum) ** 2; f[..., 1] += 4 * (1 - lum) ** 2     # çelik mavisi gölge
    f[..., 2] += 8 * lum ** 2; f[..., 1] += 3 * lum ** 2                  # sıcak parlama
    return np.clip(f * VIG, 0, 255).astype(np.uint8)


need = set()
for s, *_ in seq:
    need.add(int(s * SFPS)); need.add(int(s * SFPS) + 1)
store, k = {}, 0
d = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
while True:
    b = d.stdout.read(W * H * 3)
    if len(b) < W * H * 3:
        break
    if k in need:
        f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        sh = cv2.GaussianBlur(f, (0, 0), 1.2); f = cv2.addWeighted(f, 1.35, sh, -0.35, 0)
        store[k] = cv2.imencode(".jpg", grade(f), [cv2.IMWRITE_JPEG_QUALITY, 95])[1]
    k += 1
d.wait(); last = max(store)


def get(s):
    i0 = min(int(s * SFPS), last); w_ = s * SFPS - int(s * SFPS)
    a = cv2.imdecode(store[i0], cv2.IMREAD_COLOR)
    if w_ > 0.05 and i0 + 1 in store:
        a = cv2.addWeighted(a, 1 - w_, cv2.imdecode(store[i0 + 1], cv2.IMREAD_COLOR), w_, 0)
    return a


def zoom(f, z, cx=W / 2, cy=H * 0.3):
    return cv2.warpAffine(f, np.float32([[z, 0, cx * (1 - z)], [0, z, cy * (1 - z)]]), (W, H), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REFLECT)


def rgbsplit(f, sh):
    r = f.copy(); r[..., 2] = np.roll(f[..., 2], sh, 1); r[..., 0] = np.roll(f[..., 0], -sh, 1); return r


_F = {}
font = lambda s, p=ANTON: _F.setdefault((s, p), ImageFont.truetype(p, s))
WHITE, YELLOW, RED, GREEN, CYAN = (255, 255, 255), (255, 214, 0), (255, 60, 60), (90, 255, 120), (120, 220, 255)
EMPH = {"metalin", "anlamsız", "milimetre", "saklı", "şekil", "şaşırtıcı", "kendi", "kodladı", "yanlış", "çöpe", "doğru",
        "dümdüz", "saniyeler"}


def stroke(dl, xy, s, f, col, st):
    dl.text((xy[0] + 5, xy[1] + 8), s, font=f, fill=(0, 0, 0, 170), stroke_width=st, stroke_fill=(0, 0, 0, 170))
    dl.text(xy, s, font=f, fill=col, stroke_width=st, stroke_fill=(0, 0, 0, 255))


def arrow(dl, tip, frm, prog, col):
    tip, frm = np.array(tip, float), np.array(frm, float)
    v = tip - frm; L = np.linalg.norm(v); v /= L; nrm = np.array([-v[1], v[0]])
    end = frm + v * L * prog; base = end - v * 80
    poly = [frm + nrm * 20, base + nrm * 20, base + nrm * 52, end, base - nrm * 52, base - nrm * 20, frm - nrm * 20]
    dl.polygon([tuple(p) for p in poly], fill=col + (255,), outline=(0, 0, 0, 255), width=8)


chunks, cur = [], []
for w in caps:
    cur.append(w)
    if len(cur) >= 3 or w["w"].endswith((".", ",", "?")):
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)
HOOK = [("BU METAL", WHITE, 130), ("NEYE DÖNÜŞECEK?", YELLOW, 140)]
T_MM, T_SEKIL, T_FINAL = ws(29) + 0.05, ws(35) + 0.05, ws(84) + 0.05
ARROWS = [(T_MM, ws(31), (470, 610), (230, 1060), YELLOW),          # takımın ucu: "milimetre"
          (T_SEKIL, B[4], (560, 650), (330, 1090), CYAN),            # basamaklı küre: "şekil"
          (T_FINAL, END, (700, 755), (400, 1170), YELLOW)]           # parlak küre: "bu hale"
T_BAD, T_COPE, T_OK = ws(69) + 0.05, ws(73) + 0.05, ws(76) + 0.05
CUTS = B[1:-1]
# G-code paneli: (satır, görünme anı)
GC = [("O1001  (KURE MAFSAL)", B[5] + 0.2),
      ("G00 X52.0 Z2.0", ws(53) + 0.05),
      ("G01 X30.0 Z-15.0 F0.12", ws(55) + 0.05),
      ("G02 X40.0 Z-35.0 R20.0", ws(57) + 0.05),
      ("G00 X100.0 Z100.0  ; GERI", ws(61) + 0.05),
      ("M30", ws(66) + 0.05)]
PX0, PY0, PX1, PY1 = 60, 960, 1020, 1390

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", f"{S}/w/video.mp4"],
                       stdin=subprocess.PIPE)
for n, (s, kind, u, si) in enumerate(seq):
    tt = n / FPS
    f = get(s)
    if kind == "rewind":
        f = rgbsplit(f, int(10 + 16 * np.sin(np.pi * u))); f[::4] = (f[::4] * 0.72).astype(np.uint8)
    if kind == "ffwd":
        f = rgbsplit(f, int(6 + 18 * np.sin(np.pi * u)))
    for c in CUTS:                                       # geçiş: giren plan büyükten oturur + kısa RGB kayması
        dt = tt - c
        if 0 <= dt < 0.22:
            e = 1 - dt / 0.22; f = zoom(f, 1 + 0.14 * e ** 2)
            if dt < 0.1:
                f = rgbsplit(f, int(22 * e))
    if 0 <= tt - T_FINAL < 1.0:                          # final: nabız gibi yakınlaşma
        f = zoom(f, 1 + 0.06 * np.exp(-(tt - T_FINAL) / 0.35), 760, 560)
    if abs(tt - T_FINAL) < 0.05:
        f = cv2.addWeighted(f, 0.65, np.full_like(f, 255), 0.35, 0)
    if 0 <= tt - T_COPE < 0.5:                           # "çöpe": kırmızı alarm + sarsıntı
        e = 1 - (tt - T_COPE) / 0.5; red = f.copy(); red[..., 2] = 255
        f = cv2.addWeighted(f, 1 - 0.35 * e, red, 0.35 * e, 0)
        a = 18 * e * (1 if n % 2 else -1); f = cv2.warpAffine(f, np.float32([[1, 0, a], [0, 1, -a * 0.5]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    img = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA")
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    if tt < B[1]:
        for j, (txt, col, sz) in enumerate(HOOK):
            if tt >= 0.12 * j:
                uu = min(1, (tt - 0.12 * j) / 0.14); sc = 1.25 - 0.25 * (1 - (1 - uu) ** 3) if uu < 1 else 1
                fo = font(int(sz * sc))
                while dl.textlength(txt, font=fo) > W - 80:
                    fo = font(fo.size - 4)
                tw = dl.textlength(txt, font=fo)
                stroke(dl, (W / 2 - tw / 2, [1060, 1215][j] - fo.size * 0.6), txt, fo, col + (255,), max(7, fo.size // 11))
    if kind == "rewind":
        for x0_ in (60, 110):
            dl.polygon([(x0_ + 50, 120), (x0_ + 50, 190), (x0_, 155)], fill=WHITE + (255,), outline=(0, 0, 0, 255), width=5)
        stroke(dl, (190, 115), "GERİ SAR", font(64), WHITE + (255,), 6)
    if kind == "ffwd":
        for x0_ in (W - 220, W - 170):
            dl.polygon([(x0_, 120), (x0_, 190), (x0_ + 50, 155)], fill=WHITE + (255,), outline=(0, 0, 0, 255), width=5)
        tw = dl.textlength("x15", font=font(64)); stroke(dl, (W - 240 - tw, 115), "x15", font(64), WHITE + (255,), 6)
    if B[5] <= tt < ws(79):                               # G-code paneli
        al = min(1, (tt - B[5]) / 0.2) * min(1, (ws(79) - tt) / 0.15)
        P = Image.new("RGBA", img.size, (0, 0, 0, 0)); dp = ImageDraw.Draw(P)
        bad = T_BAD <= tt < T_OK; ok = tt >= T_OK
        edge = RED if bad else (GREEN if ok else CYAN)
        dp.rounded_rectangle([PX0, PY0, PX1, PY1], radius=22, fill=(8, 12, 18, int(215 * al)), outline=edge + (int(255 * al),), width=6)
        fm = font(46, MONO); y = PY0 + 26
        for j, (ln, t0) in enumerate(GC):
            if tt < t0:
                if j == 1 and int(tt * 3) % 2 == 0:      # henüz kod yok: yanıp sönen imleç
                    dp.text((PX0 + 30, y), "> _", font=fm, fill=CYAN + (int(255 * al),))
                break
            txt = ln[:max(1, int((tt - t0) / 0.018))]   # daktilo
            col = WHITE if j else (150, 160, 175)
            if j == 2 and bad:
                txt, col = "G01 X3.0 Z-15.0 F0.12", RED
            if j == 4 and ws(61) <= tt < ws(66):
                col = YELLOW
            dp.text((PX0 + 30, y), txt, font=fm, fill=col + (int(255 * al),))
            y += 64
        if bad and tt >= T_COPE - 0.1:
            stroke(dp, (PX1 - 300, PY0 + 22), "ALARM!", font(70), RED + (int(255 * al),), 6)
        if ok:
            stroke(dp, (PX1 - 190, PY0 + 22), "OK", font(70), GREEN + (int(255 * al),), 6)
        lay.alpha_composite(P); dl = ImageDraw.Draw(lay)
    for t0, t1, tip, frm, col in ARROWS:
        if t0 <= tt < t1:
            arrow(dl, tip, frm, min(1, (tt - t0) / 0.18), col)
    for ch in chunks:
        if ch[0]["s"] <= tt < ch[-1]["e"] + 0.12:
            fo = font(92); full = " ".join(w["w"] for w in ch)
            while dl.textlength(full, font=fo) > W - 90:
                fo = font(fo.size - 4)
            x = W / 2 - dl.textlength(full, font=fo) / 2; y = 1540
            for w in ch:
                if w["s"] > tt:
                    break
                key = w["w"].lower().strip(".,?")
                col = RED if key in ("yanlış", "çöpe") else (YELLOW if (key in EMPH or tt < w["e"]) else WHITE)
                stroke(dl, (x, y), w["w"], fo, col + (255,), 9)
                x += dl.textlength(w["w"] + " ", font=fo)
            break
    img.alpha_composite(lay)
    enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
enc.stdin.close(); enc.wait()

# ---- ses: seslendirme önde, makine sesi duyulur (konuşmada çekilir) + clink/pop/rewind/boom ----
SR = sd.SR; N = int(round(DUR * SR))
vo = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f"{S}/w/vo_fast.wav", "-af",
                                   "highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80",
                                   "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
src = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                   capture_output=True).stdout, np.float32).copy()
parts = []
for k, (t0, kind, a, b) in enumerate(SEG):
    n_ = int(round(B[k + 1] * SR)) - int(round(t0 * SR)); dur = B[k + 1] - t0
    if kind == "play":
        sp = (b - a) / dur; fi, fo_ = f"{S}/w/i{k}.f32", f"{S}/w/o{k}.f32"
        src[int(a * SR):int(b * SR)].tofile(fi)
        af = f"atempo={sp:.4f}" if sp >= 1 else f"rubberband=tempo={sp:.4f}:pitch=1.0"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", fi, "-af", af, "-f", "f32le", fo_], check=True)
        y = np.fromfile(fo_, np.float32)
    elif kind == "ffwd":
        y = src[int((b - dur) * SR):int(b * SR)].copy()
    else:
        y = np.zeros(n_, np.float32)
    y = np.pad(y, (0, max(0, n_ - len(y))))[:n_].copy(); r = int(0.015 * SR)
    y[:r] *= np.linspace(0, 1, r); y[-r:] *= np.linspace(1, 0, r); parts.append(y)
amb = np.concatenate(parts)[:N]; amb = np.pad(amb, (0, N - len(amb)))
voc = np.zeros(N); voc[:min(N, len(vo))] = vo[:N]
rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 1e-4] ** 2) + 1e-12)
amb = sd.hp(amb, 90) * (rms(voc) / rms(amb)) * 10 ** (-9 / 20)      # makine: konuşmanın 9 dB altı
env = np.convolve(np.abs(voc), np.ones(int(0.05 * SR)) / int(0.05 * SR), mode="same")
duck = 1 - 0.45 * np.clip(env / (np.percentile(env, 90) + 1e-9), 0, 1)   # konuşmada ~-5 dB daha
duck = np.convolve(duck, np.ones(int(0.15 * SR)) / int(0.15 * SR), mode="same")
mix = voc + amb * duck
fx = np.zeros(N)


def place(sig, t_, g_):
    a = int(t_ * SR); b = min(N, a + len(sig))
    if 0 <= a < N:
        fx[a:b] += sig[:b - a] / (np.max(np.abs(sig)) + 1e-9) * g_


def clink2(pitch=1.0):
    """kaliteli metal 'ting': inharmonik kısmîler + kısa parlak tık + uzun sönüm"""
    n_ = int(0.9 * SR); t_ = np.arange(n_) / SR; f0 = 1760 * pitch
    s_ = sum(a * np.sin(2 * np.pi * f0 * r * t_) * np.exp(-t_ / dcy) for r, a, dcy in
             [(1.0, 1.0, 0.35), (2.76, 0.45, 0.18), (5.40, 0.25, 0.09), (8.93, 0.12, 0.05)])
    s_ += 0.3 * sd.hp(np.random.default_rng(2).standard_normal(n_), 5000) * np.exp(-t_ / 0.003)
    return s_ * np.clip(t_ / 0.0015, 0, 1)


place(sd.pop(1.0), 0.03, 0.3); place(sd.pop(1.0), 0.15, 0.25)
for c in CUTS:
    place(sd.pop(0.8), c, 0.22)                  # geçişlerde yumuşak tık (whoosh yok)
place(clink2(1.0), T_MM, 0.5)
place(clink2(1.25), T_SEKIL, 0.55)
for t0 in [t for _, t in GC[1:]]:
    place(sd.pop(0.6), t0, 0.12)                     # kod satırı tıkı
place(sd.boom(), T_COPE, 0.75)
place(clink2(1.5), T_OK, 0.4)
place(clink2(1.0), T_FINAL, 0.75); place(clink2(1.5), T_FINAL + 0.12, 0.45)
mix += fx * 0.55
mix.astype(np.float32).tofile(f"{S}/w/mix.f32")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", f"{S}/w/mix.f32",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "2", f"{S}/w/audio.wav"], check=True)
vk = int(min(14000, 27 * 8 * 1024 / DUR - 200)); pl = f"{S}/w/pass"
c = ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{vk}k", "-maxrate", f"{int(vk * 1.4)}k", "-bufsize", f"{vk * 2}k", "-passlogfile", pl]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/w/video.mp4", *c, "-pass", "1", "-an", "-f", "null", "/dev/null"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/w/video.mp4", "-i", f"{S}/w/audio.wav", "-map", "0:v", "-map", "1:a",
                *c, "-pass", "2", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", OUT], check=True)
print(f"{OUT}: {os.path.getsize(OUT) / 1e6:.1f} MB, {DUR:.2f} sn")
