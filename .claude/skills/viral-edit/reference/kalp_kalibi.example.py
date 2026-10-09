#!/usr/bin/env python3
"""Kalp kurabiye kalıbı: TR seslendirme (sıkı 1.15x), cümle = sahne, 'az önce dümdüz' anında
geri sarma, kalp tamamlanınca clink + ok + nabız, kelime kelime altyazı, merak hook'u."""
import json, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, "/home/user/Public/.claude/skills/viral-edit/scripts")
import sounddesign as sd

S = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = f"{S}/in/src.mp4", f"{S}/out/kalp_kalibi.mp4"
W, H, FPS, SFPS, SC = 1080, 1920, 30, 30, 1.5
ANTON = "/home/user/Public/.claude/skills/viral-edit/fonts/Anton-Regular.ttf"
caps = json.load(open(f"{S}/w/cap_fast.json", encoding="utf-8"))
VOD = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{S}/w/vo_fast.wav"],
                           capture_output=True, text=True).stdout)
ws = lambda i: caps[i]["s"]
# (tür, çıktı başlangıcı, kaynak a, kaynak b) — çıktı bitişi bir sonrakinin başı
B = [0.0, ws(10) - 0.05, ws(16) - 0.05, ws(26) - 0.05, ws(31) - 0.05, ws(35) - 0.05, ws(40) - 0.05, ws(48) - 0.05, VOD + 0.5]
SEG = [("play", 0.0, 2.3),       # "Bu düz metal şerit…" (hook)
       ("play", 2.3, 4.6),       # "milim milim büküyor"
       ("play", 4.6, 7.5),       # "tek bir hareket bile rastgele değil"
       ("play", 8.45, 9.40),     # "her kıvrım bir sonrakini hazırlıyor" (ok)
       ("play", 9.40, 10.2),     # "ve birkaç saniye sonra…"
       ("rewind", 10.2, 8.45),   # "az önce dümdüz olan metal," -> geri sar
       ("play", 8.45, 10.30),    # "…kalp kalıbına dönüşüyor." (clink + ok)
       ("play", 11.0, 15.0)]     # "yüzlerce kez…"
seq = []
for k, (kind, a, b) in enumerate(SEG):
    t0, t1 = B[k], B[k + 1]
    n = int(round(t1 * FPS)) - int(round(t0 * FPS))
    for j in range(n):
        u = j / max(1, n - 1)
        seq.append((a + (b - a) * (u if kind == "rewind" else j / n), kind, u, k))
DUR = len(seq) / FPS
T_HEART = B[6] + (10.0 - 8.45) / ((10.30 - 8.45) / (B[7] - B[6]))      # kalp tamamlandı
print(f"süre {DUR:.2f}  kalp {T_HEART:.2f}  hızlar", [round((b - a) / (B[k + 1] - B[k]), 2) for k, (_, a, b) in enumerate(SEG)])

yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.30 * np.clip(np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.5) / (H / 2)) ** 2) - 0.55, 0, 1) ** 1.3)[..., None]


def grade(f):
    f = f.astype(np.float32); g = f.mean(2, keepdims=True); f = g + (f - g) * 1.15
    f = 128 + (f - 128) * 1.1; lum = f.mean(2) / 255
    f[..., 2] += 12 * lum ** 2; f[..., 1] += 3 * lum ** 2; f[..., 0] += 10 * (1 - lum) ** 2     # sıcak ışık, mavi gölge
    return np.clip(f * VIG, 0, 255).astype(np.uint8)


need = set()
for s, *_ in seq:
    need.add(int(s * SFPS)); need.add(int(s * SFPS) + 1)
store, k = {}, 0
d = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
while True:
    b = d.stdout.read(720 * 1280 * 3)
    if len(b) < 720 * 1280 * 3:
        break
    if k in need:
        f = cv2.resize(np.frombuffer(b, np.uint8).reshape(1280, 720, 3), (W, H), interpolation=cv2.INTER_LANCZOS4)
        sh = cv2.GaussianBlur(f, (0, 0), 1.2); f = cv2.addWeighted(f, 1.4, sh, -0.4, 0)
        store[k] = cv2.imencode(".jpg", grade(f), [cv2.IMWRITE_JPEG_QUALITY, 95])[1]
    k += 1
d.wait(); last = max(store)


def get(s):
    i0 = min(int(s * SFPS), last); w_ = s * SFPS - int(s * SFPS)
    a = cv2.imdecode(store[i0], cv2.IMREAD_COLOR)
    if w_ > 0.05 and i0 + 1 in store:
        a = cv2.addWeighted(a, 1 - w_, cv2.imdecode(store[i0 + 1], cv2.IMREAD_COLOR), w_, 0)
    return a


_F = {}
font = lambda s: _F.setdefault(s, ImageFont.truetype(ANTON, s))
WHITE, YELLOW, PINK = (255, 255, 255), (255, 214, 0), (255, 70, 120)
EMPH = {"düz", "farklı", "milim", "rastgele", "kıvrım", "dümdüz", "kalp", "kusursuz", "yüzlerce", "hatasızlıkla", "sevgililer"}


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
    if len(cur) >= 3 or w["w"].endswith((".", ",", "…")):
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)
HOOK = [("BU DÜZ ŞERİT", WHITE, 120), ("NEYE DÖNÜŞECEK?", YELLOW, 132)]
ARROWS = [(B[3], B[4], (645, 900), (930, 600), YELLOW),            # bükme ucu
          (T_HEART - 0.05, B[7], (650, 1040), (950, 760), PINK)]    # kalp
T_100 = ws(53)

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", f"{S}/w/video.mp4"],
                       stdin=subprocess.PIPE)
for n, (s, kind, u, si) in enumerate(seq):
    tt = n / FPS
    f = get(s)
    if kind == "rewind":
        sh = int(10 + 16 * np.sin(np.pi * u)); r = f.copy()
        r[..., 2] = np.roll(f[..., 2], sh, 1); r[..., 0] = np.roll(f[..., 0], -sh, 1)
        r[::4] = (r[::4] * 0.72).astype(np.uint8); f = r
    if abs(tt - T_HEART) < 0.06 or abs(tt - B[5]) < 0.05:
        f = cv2.addWeighted(f, 0.65, np.full_like(f, 255), 0.35, 0)
    if 0 <= tt - T_HEART < 0.9:                    # kalp nabzı: hafif yakınlaşma
        z = 1 + 0.07 * np.exp(-(tt - T_HEART) / 0.3)
        f = cv2.warpAffine(f, np.float32([[z, 0, 650 * (1 - z)], [0, z, 1040 * (1 - z)]]), (W, H), borderMode=cv2.BORDER_REFLECT)
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
                stroke(dl, (W / 2 - tw / 2, [190, 340][j] - fo.size * 0.6), txt, fo, col + (255,), max(7, fo.size // 11))
    if kind == "rewind":
        for x0_ in (60, 110):
            dl.polygon([(x0_ + 50, 120), (x0_ + 50, 190), (x0_, 155)], fill=WHITE + (255,), outline=(0, 0, 0, 255), width=5)
        stroke(dl, (190, 115), "GERİ SAR", font(64), WHITE + (255,), 6)
    for t0, t1, tip, frm, col in ARROWS:
        if t0 <= tt < t1:
            arrow(dl, tip, frm, min(1, (tt - t0) / 0.18), col)
    if T_100 <= tt < DUR:                          # "yüzlerce kez" sayacı
        uu = min(1, (tt - T_100) / 0.14); sc = 1.3 - 0.3 * (1 - (1 - uu) ** 3) if uu < 1 else 1
        txt = "x100+"; fo = font(int(170 * sc)); tw = dl.textlength(txt, font=fo)
        stroke(dl, (W / 2 - tw / 2, 230 - fo.size * 0.6), txt, fo, PINK + (255,), 12)
    for ch in chunks:
        if ch[0]["s"] <= tt < ch[-1]["e"] + 0.12:
            fo = font(92); full = " ".join(w["w"] for w in ch)
            while dl.textlength(full, font=fo) > W - 90:
                fo = font(fo.size - 4)
            x = W / 2 - dl.textlength(full, font=fo) / 2; y = H * 0.775
            for w in ch:
                if w["s"] > tt:
                    break
                key = w["w"].lower().strip(".,…")
                col = PINK if key in ("kalp", "sevgililer") else (YELLOW if (key in EMPH or tt < w["e"]) else WHITE)
                stroke(dl, (x, y), w["w"], fo, col + (255,), 9)
                x += dl.textlength(w["w"] + " ", font=fo)
            break
    img.alpha_composite(lay)
    enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
enc.stdin.close(); enc.wait()

# ---- ses: seslendirme + makine sesi (çok kısık, konuşmada daha da) + clink/pop/rewind ----
SR = sd.SR; N = int(DUR * SR)
vo = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f"{S}/w/vo_fast.wav", "-af",
                                   "highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80",
                                   "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
src = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                   capture_output=True).stdout, np.float32)
amb = np.zeros(N)
for n_, (s, kind, u, si) in enumerate(seq):
    a = int(n_ / FPS * SR); b = int((n_ + 1) / FPS * SR); i0 = int(s * SR)
    if kind != "rewind":
        seg = src[i0:i0 + (b - a)]; amb[a:a + len(seg)] = seg
mix = np.zeros(N); mix[:min(N, len(vo))] += vo[:N]
env = np.convolve(np.abs(mix), np.ones(int(0.05 * SR)) / int(0.05 * SR), mode="same")
duck = 1 - 0.6 * np.clip(env / (np.percentile(env, 90) + 1e-9), 0, 1)
duck = np.convolve(duck, np.ones(int(0.15 * SR)) / int(0.15 * SR), mode="same")
mix += sd.lp(amb, 6000) * 0.07 * duck
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
place(clink2(1.0), B[3] + 0.02, 0.55)                          # ok 1
place(sd.rewind(B[6] - B[5]), B[5], 0.5)                       # geri sarma
place(clink2(1.0), T_HEART, 0.7); place(clink2(1.5), T_HEART + 0.12, 0.45)   # kalp: çift ting
place(clink2(1.25), T_100, 0.55)                               # x100+
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
