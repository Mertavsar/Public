#!/usr/bin/env python3
"""Son Yaz – Canan: temiz kesit + sinematik renk + hook + replik altyazısı + özel müzik."""
import json, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.path.dirname(os.path.abspath(__file__))
IN, OUT = f"{S}/w/clean.mp4", f"{S}/out/son_yaz_canan.mp4"
W, H, FPS = 1080, 1920, 30
P = json.load(open(f"{S}/w/plan.json")); cuts = P["cuts"]; DUR = P["dur"]
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
ANTON = "/home/user/Public/.claude/skills/viral-edit/fonts/Anton-Regular.ttf"


def o(shot, src_t, s0, sp):
    return cuts[shot] + (src_t - s0) / sp


SIL0, SIL1 = cuts[5] - 0.9, cuts[5] + 0.45            # ölüm anı: müzik susar, tek nota
SUBS = [  # (t0, t1, [(kelime, giriş zamanı)])
    (cuts[2] + 0.1, cuts[3] - 0.05, [("Tamam aşkım,", cuts[2] + 0.1), ("kontrol ettim.", cuts[2] + 0.7)]),
    (o(3, 9.0, 8.55, 0.8), cuts[4] - 0.05, [("Selim…", o(3, 9.0, 8.55, 0.8))]),
    (o(4, 11.0, 10.90, 0.8), cuts[5] - 0.15, [("Anahtar…", o(4, 11.0, 10.90, 0.8)),
                                              ("saksının", o(4, 12.0, 10.90, 0.8)),
                                              ("altında…", o(4, 14.4, 10.90, 0.8))]),
    (o(5, 16.5, 15.55, 0.9), cuts[6] - 0.1, [("Yağmur…", o(5, 16.5, 15.55, 0.9)), ("ambulans!", o(5, 16.9, 15.55, 0.9)),
                                             ("Yağmur!", o(5, 17.6, 15.55, 0.9))]),
    (o(8, 35.0, 34.85, 0.8), DUR - 0.25, [("Ayrılık vakti…", o(8, 35.0, 34.85, 0.8))])]

# kullanıcı: müziği kendileri koyacak, dizinin kendi sesi kalsın -> kaynak ses kurguya göre
import importlib.util
spec = importlib.util.spec_from_file_location("cutplan", f"{S}/cut.py")
src_txt = open(f"{S}/cut.py").read()
PLAN = eval(src_txt[src_txt.index("PLAN = [") + 7:src_txt.index("]", src_txt.index("PLAN = [")) + 1])
SR = 48000
# kullanıcı: "sadece dizi sesi, arkadaki şarkı kalksın" -> MDX ile vokal (konuşma) ayrıldı;
# şarkının sözlü kısımları da vokal tarafına düştüğü için yalnız replik pencereleri açık.
raw = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f"{S}/w/voc.wav", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                                   capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
DIALOG = [(2.45, 4.10), (8.85, 9.85), (10.85, 15.60), (15.55, 17.65), (34.85, 36.30)]
gate = np.zeros(len(raw))
for a0, a1 in DIALOG:
    gate[int(a0 * SR):int(a1 * SR)] = 1
k_ = int(0.08 * SR); gate = np.convolve(gate, np.ones(k_) / k_, mode="same")
raw *= gate[:, None]
parts, tcur = [], 0.0
for i, (s0, s1, sp, xc) in enumerate(PLAN):
    d = (s1 - s0) / sp; n = int(round((tcur + d) * SR)) - int(round(tcur * SR))
    fi, fo = f"{S}/w/a{i}.f32", f"{S}/w/b{i}.f32"
    raw[int(s0 * SR):int(s1 * SR)].tofile(fi)
    af = f"rubberband=tempo={sp}:pitch=1.0" if abs(sp - 1) > 1e-3 else "anull"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", fi, "-af", af, "-f", "f32le", fo], check=True)
    y = np.fromfile(fo, np.float32).reshape(-1, 2); y = np.pad(y, ((0, max(0, n - len(y))), (0, 0)))[:n].copy()
    r = int(0.04 * SR); y[:r] *= np.linspace(0, 1, r)[:, None]; y[-r:] *= np.linspace(1, 0, r)[:, None]
    parts.append(y); tcur += d
aud = np.concatenate(parts)
aud.astype(np.float32).tofile(f"{S}/w/aud.f32")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", f"{S}/w/aud.f32",
                "-af", "afade=t=out:st=" + f"{DUR - 0.9:.2f}" + ":d=0.9,loudnorm=I=-15:TP=-1.5:LRA=11", f"{S}/w/score.wav"], check=True)

yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.42 * np.clip(np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.46) / (H * 0.55)) ** 2) - 0.45, 0, 1) ** 1.2)[..., None]
rng = np.random.default_rng(1)


def grade(f, cold):
    f = f.astype(np.float32)
    g = f.mean(2, keepdims=True); f = g + (f - g) * (0.72 if cold else 0.88)       # hüzün: soluk renk
    f = 128 + (f - 128) * 1.08
    lum = f.mean(2) / 255
    if cold:
        f[..., 0] += 22 * (1 - lum); f[..., 1] += 6 * (1 - lum); f[..., 2] -= 6
    else:
        f[..., 0] += 14 * (1 - lum) ** 2; f[..., 1] += 6 * (1 - lum) ** 2         # teal gölge
        f[..., 2] += 14 * lum ** 2; f[..., 1] += 6 * lum ** 2                     # sıcak ten
    f = f * VIG + rng.normal(0, 3.2, (H, W, 1))                                  # film greni
    return np.clip(f, 0, 255).astype(np.uint8)


_F = {}


def font(p, s):
    if (p, s) not in _F:
        _F[(p, s)] = ImageFont.truetype(p, s)
    return _F[(p, s)]


def soft_text(img, xy, s, f, col, alpha):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    ds.text((xy[0] + 3, xy[1] + 4), s, font=f, fill=(0, 0, 0, int(220 * alpha)))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(img)
    d.text(xy, s, font=f, fill=col + (int(255 * alpha),), stroke_width=2, stroke_fill=(0, 0, 0, int(180 * alpha)))


dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", IN, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-i", f"{S}/w/score.wav", "-map", "0:v", "-map", "1:a",
                        "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", f"{S}/w/final_hq.mp4"], stdin=subprocess.PIPE)
n = 0
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3:
        break
    tt = n / FPS
    f = grade(np.frombuffer(b, np.uint8).reshape(H, W, 3), cold=tt < cuts[1] or cuts[7] <= tt < cuts[8])
    # kesimlerde 4 karelik siyaha nefes (ölüm sonrası daha uzun)
    for c in cuts[1:-1]:
        d_ = abs(tt - c)
        if d_ < 0.07:
            f = (f * (d_ / 0.07)).astype(np.uint8)
    if tt < 0.35:
        f = (f * (tt / 0.35)).astype(np.uint8)
    if tt > DUR - 0.9:
        f = (f * max(0, (DUR - tt) / 0.9)).astype(np.uint8)
    img = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA")
    if tt < cuts[1] - 0.1:                      # hook: mezar taşının üstünde
        d = ImageDraw.Draw(img)
        for j, (txt, sz, col, y) in enumerate([("CANAN'IN", 120, (255, 255, 255), 300), ("SON SÖZLERİ…", 150, (255, 214, 120), 440)]):
            if tt >= 0.25 + 0.35 * j:
                al = min(1, (tt - 0.25 - 0.35 * j) / 0.35)
                fo = font(ANTON, sz); tw = d.textlength(txt, font=fo)
                soft_text(img, (W / 2 - tw / 2, y - sz * 0.6), txt, fo, col, al)
    for t0, t1, words in SUBS:                  # replik altyazısı: kelime kelime, yumuşak giriş
        if t0 <= tt < t1:
            vis = [(w, ws) for w, ws in words if ws <= tt]
            line = " ".join(w for w, _ in vis)
            fo = font(SERIF, 74)
            full = " ".join(w for w, _ in words)
            while ImageDraw.Draw(img).textlength(full, font=fo) > W - 120:
                fo = font(SERIF, fo.size - 4)
            x = W / 2 - ImageDraw.Draw(img).textlength(full, font=fo) / 2
            al = min(1, (t1 - tt) / 0.25)
            for w, ws in vis:
                a_ = min(1, (tt - ws) / 0.25) * al
                soft_text(img, (x, H * 0.70), w, fo, (255, 248, 236), a_)
                x += ImageDraw.Draw(img).textlength(w + " ", font=fo)
    enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
    n += 1
enc.stdin.close(); enc.wait(); dec.wait()
vk = int(min(14000, 27 * 8 * 1024 / DUR - 200)); pl = f"{S}/w/pass"
common = ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{vk}k", "-maxrate", f"{int(vk * 1.4)}k", "-bufsize", f"{vk * 2}k", "-passlogfile", pl]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/w/final_hq.mp4", *common, "-pass", "1", "-an", "-f", "null", "/dev/null"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/w/final_hq.mp4", "-map", "0:v", "-map", "0:a", *common, "-pass", "2",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], check=True)
print(f"{OUT}: {os.path.getsize(OUT) / 1e6:.1f} MB, {DUR:.2f} sn")
