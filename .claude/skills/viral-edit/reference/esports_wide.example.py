#!/usr/bin/env python3
"""Yatay (16:9) yayın -> dikey Shorts, "her açı görünsün": üstte TAM yayın karesi
(hiçbir şey kırpılmaz), ortada yazı bandı, altta aksiyonu takip eden yakın plan.
Gerçek ses kısık; üstüne üretilmiş ritim + Kokoro anons + efekt."""
import os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "/home/user/Public/.claude/skills/viral-edit/scripts")
import sounddesign as sd

S = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = f"{S}/in/src.mp4", f"{S}/out/blg_gen_loop.mp4"
W, H, FPS, SFPS = 1080, 1920, 30, 60
SW, SH = 1920, 1080
TOPB = 300                                     # üst başlık bandı (her an dolu)
GH_ = 1350                                     # oyun yüksekliği (ekranın %70'i)
VY0, VY1 = 0, 1080                             # tam yükseklik: zoom yalnız 1.25x
CW = int(round((VY1 - VY0) * W / GH_))         # kaynakta 864 px genişlik

PLAN = [("play", 3.9, 4.5, 0.5),       # 0 soğuk açılış: J4 ultisi kapanıyor
        ("freeze", 4.5, 3.7),           # 1 hook
        ("rewind", 4.5, 0.0, 0.4),      # 2
        ("play", 0.0, 3.0, 1.15),       # 3 kurulum
        ("play", 3.0, 3.6, 0.5),        # 4 dalış
        ("play", 3.6, 5.3, 1.0),        # 5
        ("play", 5.3, 5.8, 0.5),        # 6 shut down
        ("play", 5.8, 13.8, 1.1),       # 7
        ("play", 13.8, 14.4, 0.45),     # 8 Chovy düşüyor
        ("play", 14.4, 17.3, 1.0),      # 9
        ("play", 17.3, 17.8, 0.45),     # 10 Kiin, Bin'i alıyor
        ("play", 17.8, 19.8, 1.0),      # 11
        ("freeze", 19.8, 2.9),          # 12 kapanış sorusu
        ("rewind", 19.8, 3.9, 0.5)]     # 13 DÖNGÜ: ilk kareye geri sarar
seq, segt, t = [], [], 0.0
for i, p in enumerate(PLAN):
    d = (p[2] - p[1]) / p[3] if p[0] == "play" else (p[2] if p[0] == "freeze" else p[3])
    n = int(round((t + d) * FPS)) - int(round(t * FPS))
    for k in range(n):
        u = k / max(1, n - 1)
        s = (p[1] + (p[2] - p[1]) * k / n) if p[0] == "play" else (p[1] if p[0] == "freeze" else p[1] + (p[2] - p[1]) * u)
        seq.append((s, p[0], u, i))
    segt.append((t, t + d, p)); t += d
DUR = len(seq) / FPS


def O(i, s):
    t0, _, p = segt[i]
    return t0 + (s - p[1]) / p[3]


T_DIVE, T_SHUT, T_CHOVY, T_BIN = O(4, 3.25), O(6, 5.42), O(8, 14.05), O(10, 17.55)
print(f"süre {DUR:.2f}  dalış {T_DIVE:.2f} chovy {T_CHOVY:.2f} bin {T_BIN:.2f}")

# ---- aksiyon takibi (x, y) ----
lw, lh = 240, 135
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"scale={lw}:{lh},format=gray", "-f", "rawvideo", "-"],
                     capture_output=True).stdout
A = np.frombuffer(raw, np.uint8).reshape(-1, lh, lw).astype(np.float32)
mask = np.zeros((lh, lw), np.float32)
mask[int(lh * 0.07):int(lh * 0.80), int(lw * 0.05):int(lw * 0.95)] = 1      # HUD dışarıda
ys, xs = (np.arange(lh) + 0.5) / lh, (np.arange(lw) + 0.5) / lw
cx, cy, px, py = [], [], 0.5, 0.45
for i in range(len(A)):
    m = (np.abs(A[i] - A[max(0, i - 3)]) ** 2 + 500.0 * (A[i] > 225)) * mask
    tot = m.sum()
    if tot > 3e5:
        px = float((m.sum(0) * xs).sum() / tot); py = float((m.sum(1) * ys).sum() / tot)
    cx.append(px); cy.append(py)


def smooth(v, sec):
    sig = sec * SFPS; k = np.arange(-int(3 * sig), int(3 * sig) + 1)
    g = np.exp(-0.5 * (k / sig) ** 2); g /= g.sum()
    return np.convolve(np.pad(np.array(v), len(k) // 2, mode="edge"), g, mode="valid")[:len(v)]


cx = smooth(cx, 1.0)
X0 = np.clip(cx * SW - CW / 2, 0, SW - CW)
lo, hi = np.zeros(len(X0)), np.full(len(X0), SW - CW, float)
for t0_, t1_, a0_, a1_ in [(5.35, 7.7, 860, 1340), (14.0, 16.6, 712, 1190), (17.5, 19.9, 769, 1199)]:
    i0_, i1_ = int(t0_ * SFPS), min(len(X0), int(t1_ * SFPS))
    lo[i0_:i1_] = np.maximum(lo[i0_:i1_], a1_ - CW); hi[i0_:i1_] = np.minimum(hi[i0_:i1_], a0_)
X0 = np.clip(X0, lo, np.maximum(lo, hi))
X0 = np.clip(smooth(X0, 0.6), lo, np.maximum(lo, hi))
print(f"takip x {X0.min():.0f}-{X0.max():.0f}")

# ---- renk ----
def grade(f, punch=1.0):
    f = f.astype(np.float32)
    g = f.mean(2, keepdims=True); f = g + (f - g) * (1.18 * punch)
    f = 128 + (f - 128) * 1.10
    lum = f.mean(2) / 255
    f[..., 0] += 12 * (1 - lum) ** 2; f[..., 2] += 6 * (1 - lum) ** 2      # mor gölge
    f[..., 2] += 10 * lum ** 2; f[..., 1] += 4 * lum ** 2                  # turuncu ışık
    return np.clip(f, 0, 255).astype(np.uint8)


yy = np.mgrid[0:H, 0:W][0] / H
BG = np.stack([30 * (1 - yy) + 10, 10 * (1 - yy) + 6, 24 * (1 - yy) + 12], -1).astype(np.uint8)
a_ = np.linspace(0, 1, W)[None, :, None]
LINE = (np.array((40, 140, 255)) * (1 - a_) + np.array((230, 70, 170)) * a_).repeat(5, 0).astype(np.uint8)


def build(f, k):
    x0 = int(X0[min(k, len(X0) - 1)])
    z = cv2.resize(f[VY0:VY1, x0:x0 + CW], (W, GH_), interpolation=cv2.INTER_LANCZOS4)
    sh = cv2.GaussianBlur(z, (0, 0), 1.2); z = cv2.addWeighted(z, 1.35, sh, -0.35, 0)
    out = BG.copy()
    out[TOPB:TOPB + GH_] = grade(z, 1.0)
    out[TOPB - 5:TOPB] = LINE; out[TOPB + GH_:TOPB + GH_ + 5] = LINE
    return out


need = {int(round(s * SFPS)) for s, *_ in seq}
store, k = {}, 0
d = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
while True:
    b = d.stdout.read(SW * SH * 3)
    if len(b) < SW * SH * 3:
        break
    if k in need:
        store[k] = cv2.imencode(".jpg", build(np.frombuffer(b, np.uint8).reshape(SH, SW, 3), k), [cv2.IMWRITE_JPEG_QUALITY, 95])[1]
    k += 1
d.wait()
last = max(store)


def get(s):
    i = min(int(round(s * SFPS)), last)
    while i not in store:
        i -= 1
    return cv2.imdecode(store[i], cv2.IMREAD_COLOR)


FB = "/home/user/Public/.claude/skills/viral-edit/fonts/Anton-Regular.ttf"
_F = {}


def font(sz):
    if sz not in _F:
        _F[sz] = ImageFont.truetype(FB, sz)
    return _F[sz]


WHITE, ORANGE, VIOLET = (255, 255, 255), (255, 145, 30), (200, 120, 255)


def text(dl, cy_, s, sz, col, scale=1.0, alpha=1.0):
    sz = int(sz * scale); f = font(sz)
    while dl.textlength(s, font=f) > W - 70:
        sz -= 4; f = font(sz)
    tw = dl.textlength(s, font=f); x, y = W / 2 - tw / 2, cy_ - sz * 0.62; A_ = int(255 * alpha)
    st = max(6, sz // 11)
    dl.text((x + 5, y + 7), s, font=f, fill=(0, 0, 0, A_ * 160 // 255), stroke_width=st, stroke_fill=(0, 0, 0, A_ * 160 // 255))
    dl.text((x, y), s, font=f, fill=col + (A_,), stroke_width=st, stroke_fill=(0, 0, 0, A_))


def pop(tt, t0):
    u = (tt - t0) / 0.14
    return 1.0 if u >= 1 else 1.3 - 0.3 * (1 - (1 - max(u, 0)) ** 3)


HL = [(0.0, segt[2][1], [("BLG vs GEN", WHITE, 110), ("WHO WALKS OUT ALIVE?", ORANGE, 100)]),
      (segt[2][1], T_CHOVY, [("BLG vs GEN", WHITE, 104), ("5v5 TEAMFIGHT", ORANGE, 92)]),
      (T_CHOVY, T_BIN, [("BLG vs GEN", WHITE, 104), ("CHOVY DOWN.", ORANGE, 100)]),
      (T_BIN, segt[12][0], [("BLG vs GEN", WHITE, 104), ("KIIN HITS BACK.", ORANGE, 100)]),
      (segt[12][0], segt[13][0], [("WHO PLAYED IT BETTER?", WHITE, 84), ("BLG or GEN?", ORANGE, 112)]),
      (segt[13][0], DUR + 1, [("BLG vs GEN", WHITE, 104), ("WHO WALKS OUT ALIVE?", ORANGE, 92)])]
YS = {2: [TOPB * 0.36, TOPB * 0.72]}
PUNCH = [T_DIVE, T_CHOVY, T_BIN]
FLASH = [T_DIVE, T_SHUT, T_CHOVY, T_BIN]

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-crf", "13", "-preset", "medium", "-pix_fmt", "yuv420p",
                        f"{S}/w/video.mp4"], stdin=subprocess.PIPE)
for n, (s, kind, u, si) in enumerate(seq):
    tt = n / FPS
    f = get(s)
    if kind == "rewind":
        sh_ = int(10 + 14 * np.sin(np.pi * u)); g_ = f.copy()
        g_[..., 2] = np.roll(f[..., 2], sh_, 1); g_[..., 0] = np.roll(f[..., 0], -sh_, 1)
        g_[::4] = (g_[::4] * 0.72).astype(np.uint8); f = g_
    if (kind == "freeze" and u < 0.07) or any(abs(tt - x) < 0.05 for x in FLASH):
        f = cv2.addWeighted(f, 0.64, np.full_like(f, 255), 0.36, 0)
    for x in (T_DIVE, T_CHOVY, T_BIN):
        if 0 <= tt - x < 0.22 and False:
            a = 14 * (1 - (tt - x) / 0.22) * (1 if n % 2 else -1)
            f = cv2.warpAffine(f, np.float32([[1, 0, a], [0, 1, -a * 0.6]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    zm = 1.0                                     # ani yakınlaşma kapalı (kullanıcı: çok zoom)
    for x in []:
        d_ = tt - x
        if 0 <= d_ < 1.3:
            zm = max(zm, 1 + 0.08 * (min(1, d_ / 0.12) if d_ < 0.12 else np.exp(-(d_ - 0.12) / 0.45)))
    if zm > 1.001:
        f = cv2.warpAffine(f, np.float32([[zm, 0, W / 2 * (1 - zm)], [0, zm, H * 0.45 * (1 - zm)]]), (W, H),
                           flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    pass
    img = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA")
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    for t0, t1, lines in HL:
        if t0 <= tt < t1:
            al = min(1, (t1 - tt) / 0.12)
            for j, ((s_, col, sz), y) in enumerate(zip(lines, YS[len(lines)])):
                same = (j == 0 and s_ == "BLG vs GEN" and t0 > 0.01) or t0 < 0.01
                if tt >= t0 + 0.1 * j or same:
                    text(dl, y, s_, sz, col, 1.0 if same else pop(tt, t0 + 0.1 * j), 1.0 if same else al)
    ff = font(34); fw = dl.textlength("TikLOLet", font=ff)
    dl.text((W / 2 - fw / 2, TOPB + GH_ + 40), "TikLOLet", font=ff, fill=(255, 255, 255, 150))
    img.alpha_composite(lay)
    enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
enc.stdin.close(); enc.wait()

# ---- ses ----
SR = sd.SR
src = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                                   capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
work = f"{S}/w/aud"; os.makedirs(work, exist_ok=True)
parts = []
for i, (t0, t1, p) in enumerate(segt):
    n = int(round(t1 * SR)) - int(round(t0 * SR))
    if p[0] == "play":
        _, s0, s1, spd = p
        fi, fo = f"{work}/i{i}.f32", f"{work}/o{i}.f32"
        src[int(s0 * SR):int(s1 * SR)].tofile(fi)
        af = f"atempo={spd}" if spd >= 1 else f"rubberband=tempo={spd}:pitch=1.0"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", fi, "-af", af, "-f", "f32le", fo], check=True)
        y = np.fromfile(fo, np.float32).reshape(-1, 2); y = np.pad(y, ((0, max(0, n - len(y))), (0, 0)))[:n]
        r = int(0.012 * SR); ramp = np.linspace(0, 1, r)[:, None]; y[:r] *= ramp; y[-r:] *= ramp[::-1]
    else:
        y = np.zeros((n, 2), np.float32)
    parts.append(y)
game = np.concatenate(parts); N = len(game)


def place(buf, sig, t_, g_):
    a = int(t_ * SR); b = min(N, a + len(sig))
    if 0 <= a < N:
        buf[a:b] += sig[:b - a] / (np.max(np.abs(sig)) + 1e-9) * g_


# ritim: 140 bpm trap (kick, clap, hat, 808), hook donmasında susar
bpm = 140; beat = 60 / bpm; tt_ = np.arange(N) / SR
beatbus = np.zeros(N)
roots = [38, 38, 34, 36]                         # D D Bb C


def kick():
    n_ = int(0.35 * SR); t_ = np.arange(n_) / SR
    f_ = 45 + 120 * np.exp(-t_ / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f_) / SR) * np.exp(-t_ / 0.16)


def clap():
    n_ = int(0.18 * SR); t_ = np.arange(n_) / SR
    return sd.bp(np.random.default_rng(3).standard_normal(n_), 900, 5000) * np.exp(-t_ / 0.05)


def hat():
    n_ = int(0.05 * SR); t_ = np.arange(n_) / SR
    return sd.hp(np.random.default_rng(5).standard_normal(n_), 7000) * np.exp(-t_ / 0.012)


def b808(m, dur):
    n_ = int(dur * SR); t_ = np.arange(n_) / SR
    return np.tanh(1.8 * np.sin(2 * np.pi * sd.nf(m) * t_)) * np.exp(-t_ / 0.55)


start = segt[3][0]                               # ritim geri sarmadan sonra girer
t_b, bi = start, 0
while t_b < DUR:
    bar = bi // 4; pos = bi % 4
    if pos in (0,) or (pos == 2 and bar % 2 == 1):
        place(beatbus, kick(), t_b, 0.9)
    if pos == 0:
        place(beatbus, b808(roots[bar % 4], beat * 4), t_b, 0.6)
    if pos in (1, 3):
        place(beatbus, clap(), t_b, 0.55)
    for h in range(2 if bar % 4 != 3 else 4):
        place(beatbus, hat(), t_b + h * beat / (2 if bar % 4 != 3 else 4), 0.25)
    t_b += beat; bi += 1
# soğuk açılışta gerilim yatağı (düşük pad)
pad = sd.music(segt[3][0] + 0.5, 99, 99, 99, mood="mystery")
place(beatbus, pad, 0.0, 0.35)
beatbus = sd.lp(beatbus, 9000)

vox = np.zeros(N)
VO = [("h", segt[1][0] + 0.05), ("a", T_CHOVY + 1.25), ("b", T_BIN + 1.05), ("e", segt[12][0] + 0.05)]
for k_, t0 in VO:
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f"{S}/vo/{k_}.wav", "-af",
                                      "highpass=f=70,equalizer=f=3200:t=q:w=1:g=3,acompressor=threshold=-18dB:ratio=3:attack=5:release=80",
                                      "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
    place(vox, x, t0, 1.0)
fx = np.zeros(N)
place(fx, sd.boom(), segt[1][0], 0.9); place(fx, sd.pop(1.0), segt[1][0] + 0.03, 0.35)
place(fx, sd.boom(), 0.0, 0.8)                                   # ilk karede darbe
rn = int(1.1 * SR); ris = sd.bp(np.random.default_rng(9).standard_normal(rn), 500, 6000) * np.linspace(0, 1, rn) ** 2
place(fx, ris, segt[1][0] - 1.1, 0.45)                           # donmaya yükselen gerilim
place(fx, sd.rewind(0.5), segt[13][0], 0.6)                      # döngü geri sarması
place(fx, sd.rewind(0.4), segt[2][0], 0.6)
for x in (T_DIVE, T_CHOVY, T_BIN):
    place(fx, sd.boom(), x, 1.0)
place(fx, sd.clink(), T_SHUT, 0.5)

# seviyeler: gerçek ses kısık (-12 dB), anons varken ek kısma
env = np.convolve(np.abs(vox), np.ones(2000) / 2000, mode="same")
duck = 1 - 0.55 * np.clip(env / (env.max() * 0.15 + 1e-9), 0, 1)
duck = np.convolve(duck, np.ones(3000) / 3000, mode="same")
gg = np.full(N, 0.22)
for a0, a1 in [(0.0, segt[1][0]), (T_DIVE - 0.2, T_DIVE + 1.6), (T_SHUT - 0.2, T_SHUT + 1.4),
               (T_CHOVY - 0.2, T_CHOVY + 1.2), (T_BIN - 0.2, T_BIN + 1.0)]:
    gg[int(a0 * SR):int(a1 * SR)] = 0.95
gg = np.convolve(gg, np.ones(int(0.15 * SR)) / int(0.15 * SR), mode="same")
mix = game * gg[:, None] * duck[:, None] + (beatbus * 0.33 * duck * (1.25 - 0.55 * (gg - 0.22) / 0.73))[:, None] + fx[:, None] * 0.55 + vox[:, None] * 0.95
mix.astype(np.float32).tofile(f"{work}/mix.f32")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", f"{work}/mix.f32",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", f"{S}/w/audio.wav"], check=True)
vk = int(min(14000, 27 * 8 * 1024 / DUR - 200)); pl = f"{work}/pass"
common = ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{vk}k", "-maxrate", f"{int(vk * 1.4)}k", "-bufsize", f"{vk * 2}k", "-passlogfile", pl]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/w/video.mp4", *common, "-pass", "1", "-an", "-f", "null", "/dev/null"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/w/video.mp4", "-i", f"{S}/w/audio.wav", "-map", "0:v", "-map", "1:a",
                *common, "-pass", "2", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", OUT], check=True)
print(f"{OUT}: {os.path.getsize(OUT) / 1e6:.1f} MB, {DUR:.2f} sn")
