#!/usr/bin/env python3
"""Pulse Tales: örümceğe elle beslenen sinek. İç 9:16 panel tam ekrana (kırpma yok),
Kokoro anlatım cümleleri olay anlarına yerleşir, kelime kelime altyazı, hook, ok+clink."""
import os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "/home/user/Public/.claude/skills/viral-edit/scripts")
import sounddesign as sd

S = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = f"{S}/in/src.mp4", f"{S}/out/spider_hand_feed.mp4"
W, H, FPS, SFPS = 1080, 1920, 30, 30
PX, PY, PW, PH = 69, 244, 582, 1036            # kaynakta 9:16 iç panel
SC = W / PW

PLAN = [("play", 22.3, 23.1, 0.5),            # 0 soğuk açılış: örümcek sineği kapıyor
        ("freeze", 23.1, 1.6),                 # 1 hook
        ("rewind", 23.1, 2.6, 0.4),            # 2
        ("play", 2.6, 7.6, 1.0),               # 3 at + sinek + yakalama
        ("play", 7.6, 16.0, 1.6),              # 4 yürüyüş
        ("play", 16.0, 21.6, 1.2),             # 5 kova, ağ
        ("play", 21.6, 23.3, 0.6),             # 6 örümcek geliyor
        ("play", 23.3, 30.0, 1.3),             # 7 ipeğe sarma
        ("play", 40.0, 47.8, 1.25)]            # 8 yakın plan
seq, segt, t = [], [], 0.0
for i, p in enumerate(PLAN):
    d = (p[2] - p[1]) / p[3] if p[0] == "play" else (p[2] if p[0] == "freeze" else p[3])
    n = int(round((t + d) * FPS)) - int(round(t * FPS))
    for k in range(n):
        u = k / max(1, n - 1)
        if p[0] == "play":
            s = p[1] + (p[2] - p[1]) * k / n
        elif p[0] == "freeze":
            s = p[1]
        else:
            s = p[1] + (p[2] - p[1]) * u
        seq.append((s, p[0], u, i))
    segt.append((t, t + d, p)); t += d
DUR = len(seq) / FPS


def O(i, s):
    t0, _, p = segt[i]
    return t0 + (s - p[1]) / p[3]


T_SPIDER = O(6, 22.5)
# anlatım: (dosya, metin, başlangıç)
VO = [("h", "This fly was a gift... for something hungry.", 0.12),
      ("1", "This fly picked the wrong horse.", segt[3][0] + 0.1),
      ("3", "So he caught it. With his bare hands.", segt[3][0] + 2.3),
      ("2", "Horse flies bite to drink blood. Horses hate them.", segt[4][0] + 0.15),
      ("4", "But it's not for him.", segt[4][0] + 3.55),
      ("5", "Something on this truck has been waiting.", segt[5][0] + 0.1),
      ("6", "Watch the web.", segt[5][0] + 2.95),
      ("7", "One touch... and it's already there.", T_SPIDER - 1.45),
      ("8", "Garden spiders don't just bite. They wrap their meal in silk.", segt[7][0] + 0.15),
      ("9", "A lunch box made of web.", segt[7][0] + 4.05),
      ("10", "Would you hand-feed a spider?", O(8, 44.0))]
EMPH = {"gift", "hungry", "wrong", "blood.", "bare", "not", "waiting.", "web.", "already", "silk.", "spider?"}
print(f"süre {DUR:.2f}  örümcek {T_SPIDER:.2f}")


def wav_len(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)


# kelime zamanları: satır süresine harf sayısıyla dağıt (baş/son sessizlik payı)
words = []
for k, txt, t0 in VO:
    L = wav_len(f"{S}/vo/{k}.wav")
    ws = txt.split()
    wt = np.array([len(w) + 2.5 + (6 if w.endswith(("...", ".")) else 0) for w in ws], float)
    span = L - 0.25
    acc = t0 + 0.12
    for w, x in zip(ws, wt):
        dd = span * x / wt.sum()
        words.append({"w": w, "s": acc, "e": acc + dd, "line": k}); acc += dd
for a, b in zip(VO, VO[1:]):
    assert a[2] + wav_len(f"{S}/vo/{a[0]}.wav") <= b[2] + 0.05, f"çakışma {a[0]} -> {b[0]}"


# ---- görüntü ----
def grade(f):
    f = f.astype(np.float32)
    g = f.mean(2, keepdims=True); f = g + (f - g) * 1.12
    f = 128 + (f - 128) * 1.08
    lum = f.mean(2) / 255
    f[..., 2] += 10 * lum ** 1.5; f[..., 1] += 4 * lum ** 1.5; f[..., 0] -= 4 * lum
    return np.clip(f, 0, 255)


yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.28 * np.clip(np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) - 0.6, 0, 1) ** 1.3)[..., None]


def build(fr):
    p = fr[PY:PY + PH, PX:PX + PW]
    p = cv2.resize(p, (W, int(round(PH * SC))), interpolation=cv2.INTER_CUBIC)[:H]
    if p.shape[0] < H:
        p = np.vstack([p, np.repeat(p[-1:], H - p.shape[0], 0)])
    return np.clip(grade(p) * VIG, 0, 255).astype(np.uint8)


need = set()
for s, kind, u, i in seq:
    need.add(int(s * SFPS)); need.add(int(s * SFPS) + 1)
store, k = {}, 0
d = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"fps={SFPS}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                     stdout=subprocess.PIPE)
while True:
    b = d.stdout.read(720 * 1280 * 3)
    if len(b) < 720 * 1280 * 3:
        break
    if k in need:
        store[k] = cv2.imencode(".jpg", build(np.frombuffer(b, np.uint8).reshape(1280, 720, 3)),
                                [cv2.IMWRITE_JPEG_QUALITY, 96])[1]
    k += 1
d.wait()
last = max(store)


def get(s):
    i0 = min(int(s * SFPS), last); w_ = s * SFPS - int(s * SFPS)
    a = cv2.imdecode(store[i0], cv2.IMREAD_COLOR)
    i1 = min(i0 + 1, last)
    if w_ > 0.05 and i1 in store:
        a = cv2.addWeighted(a, 1 - w_, cv2.imdecode(store[i1], cv2.IMREAD_COLOR), w_, 0)
    return a


FB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
_F = {}


def font(sz):
    if sz not in _F:
        _F[sz] = ImageFont.truetype(FB, sz)
    return _F[sz]


WHITE, ACC, GOLD = (255, 255, 255), (255, 122, 72), (255, 214, 0)


def stroke_text(d_, xy, s, f, col, st):
    d_.text((xy[0] + 4, xy[1] + 6), s, font=f, fill=(0, 0, 0, 150), stroke_width=st, stroke_fill=(0, 0, 0, 150))
    d_.text(xy, s, font=f, fill=col, stroke_width=st, stroke_fill=(0, 0, 0))


# altyazı parçaları: satır içinde 3 kelimelik gruplar
chunks = []
for k_, txt, t0 in VO:
    if k_ == "h":
        continue
    ws = [w for w in words if w["line"] == k_]
    i = 0
    while i < len(ws):
        g = ws[i:i + 3]
        if len(g) == 3 and g[1]["w"].endswith((".", "...")):
            g = g[:2]
        chunks.append(g); i += len(g)

# ok: örümceğin kaynak konumu (panel px) -> çıktı
ARK = [(22.5, (195, 630)), (22.8, (225, 570)), (23.0, (120, 480)), (23.2, (135, 495)), (23.3, (140, 500))]


def spider_xy(s):
    ts = [a for a, _ in ARK]; s = min(max(s, ts[0]), ts[-1])
    x = np.interp(s, ts, [p[0] for _, p in ARK]); y = np.interp(s, ts, [p[1] for _, p in ARK])
    return x * SC, y * SC


def arrow(d_, tip, prog):
    tip = np.array(tip); frm = tip + np.array([300, -260])
    v = tip - frm; L = np.linalg.norm(v); v /= L; nrm = np.array([-v[1], v[0]])
    end = frm + v * L * prog; base = end - v * 80
    poly = [frm + nrm * 20, base + nrm * 20, base + nrm * 52, end, base - nrm * 52, base - nrm * 20, frm - nrm * 20]
    d_.polygon([tuple(p) for p in poly], fill=GOLD + (255,), outline=(0, 0, 0, 255), width=8)


enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p",
                        f"{S}/w/video.mp4"], stdin=subprocess.PIPE)
for n, (s, kind, u, si) in enumerate(seq):
    tt = n / FPS
    f = get(s)
    if kind == "rewind":
        sh = int(10 + 14 * np.sin(np.pi * u)); g_ = f.copy()
        g_[..., 2] = np.roll(f[..., 2], sh, 1); g_[..., 0] = np.roll(f[..., 0], -sh, 1)
        g_[::4] = (g_[::4] * 0.72).astype(np.uint8); f = g_
    if kind == "freeze" and u < 0.08:
        f = cv2.addWeighted(f, 0.62, np.full_like(f, 255), 0.38, 0)
    img = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA")
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    # hook
    if tt < segt[2][1]:
        for j, (txt, col, sz, y) in enumerate([("THIS FLY WAS A GIFT…", WHITE, 92, 300), ("FOR SOMETHING HUNGRY", GOLD, 100, 410)]):
            if tt >= 0.1 * j:
                uu = min(1, (tt - 0.1 * j) / 0.14); sc_ = 1.25 - 0.25 * (1 - (1 - uu) ** 3) if uu < 1 else 1
                sz_ = int(sz * sc_); fo = font(sz_)
                while dl.textlength(txt, font=fo) > W - 90:
                    sz_ -= 4; fo = font(sz_)
                tw = dl.textlength(txt, font=fo)
                stroke_text(dl, (W / 2 - tw / 2, y - fo.size * 0.6), txt, fo, col + (255,), max(6, fo.size // 11))
    # ok: örümcek anında
    if si == 6 and s >= 22.5:
        arrow(dl, spider_xy(s), min(1, (tt - T_SPIDER) / 0.18))
    if si in (0, 1):
        arrow(dl, spider_xy(min(s, 23.1)), 1.0)
    # altyazı
    for ch in chunks:
        if ch[0]["s"] <= tt < ch[-1]["e"] + 0.15:
            vis = [w for w in ch if w["s"] <= tt]
            fo = font(80); full = " ".join(w["w"] for w in ch)
            tw = dl.textlength(full, font=fo); x = W / 2 - tw / 2; y = int(H * 0.80)
            for w in ch:
                if w not in vis:
                    break
                cur = w is vis[-1] and tt < w["e"]
                col = ACC if (w["w"].lower() in EMPH or cur) else WHITE
                stroke_text(dl, (x, y), w["w"], fo, col + (255,), 8)
                x += dl.textlength(w["w"] + " ", font=fo)
            break
    img.alpha_composite(lay)
    enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
enc.stdin.close(); enc.wait()

# ---- ses: anlatım + efekt (kaynak müzik/ses kullanılmaz) ----
SR = sd.SR
N = int(DUR * SR) + SR
vox = np.zeros(N); bus = np.zeros(N)


def place(buf, sig, t_, g_):
    a = int(t_ * SR); b = min(N, a + len(sig))
    buf[a:b] += sig[:b - a] / (np.max(np.abs(sig)) + 1e-9) * g_


for k_, txt, t0 in VO:
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f"{S}/vo/{k_}.wav", "-af",
                                      "highpass=f=70,equalizer=f=3200:t=q:w=1:g=2.5,acompressor=threshold=-18dB:ratio=3:attack=5:release=80",
                                      "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
    place(vox, x, t0, 0.95)
place(bus, sd.boom(), segt[1][0], 0.55)
place(bus, sd.pop(1.0), 0.03, 0.35); place(bus, sd.pop(1.0), 0.13, 0.3)
place(bus, sd.rewind(0.4), segt[2][0], 0.5)
place(bus, sd.clink(), T_SPIDER, 0.6)
mix = (vox + bus * 0.65)[:int(DUR * SR)]
mix.astype(np.float32).tofile(f"{S}/w/mix.f32")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", f"{S}/w/mix.f32",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "2", f"{S}/w/audio.wav"], check=True)
vk = int(min(14000, 27 * 8 * 1024 / DUR - 200))
pl = f"{S}/w/pass"
common = ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{vk}k", "-maxrate", f"{int(vk * 1.4)}k", "-bufsize", f"{vk * 2}k",
          "-passlogfile", pl]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/w/video.mp4", *common, "-pass", "1", "-an", "-f", "null", "/dev/null"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/w/video.mp4", "-i", f"{S}/w/audio.wav", "-map", "0:v", "-map", "1:a",
                *common, "-pass", "2", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", OUT], check=True)
print(f"{OUT}: {os.path.getsize(OUT) / 1e6:.1f} MB, {DUR:.2f} sn")
