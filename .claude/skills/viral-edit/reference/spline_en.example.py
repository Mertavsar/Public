#!/usr/bin/env python3
"""Spline cutting (EN): fast VO (1.2x), sentence = shot, push-in zooms, schematic
'lock together / rotate as one' animation, 'again and again' rewind, arrows + clinks, word captions."""
import json, os, subprocess, sys, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/user/Public/.claude/skills/viral-edit/scripts")
import sounddesign as sd

S = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = f"{S}/in/src.mp4", f"{S}/out/spline_cutting.mp4"
W, H, FPS, SFPS = 1080, 1920, 30, 25
ANTON = "/home/user/Public/.claude/skills/viral-edit/fonts/Anton-Regular.ttf"
caps = json.load(open(f"{S}/w/cap_fast.json", encoding="utf-8"))
VOD = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{S}/w/vo_fast.wav"],
                           capture_output=True, text=True).stdout)
ws = lambda i: caps[i]["s"] - 0.04
B = [0.0, ws(12), ws(23), ws(32), ws(42), ws(53), ws(69), ws(74), ws(85), ws(96), VOD + 0.6]
# (kind, src a, src b, zoom0, zoom1, cx, cy)
SEG = [("play", 12.6, 14.4, 1.45, 1.25, 540, 560),   # 0 hook: finished grooves
       ("play", 0.5, 3.7, 1.0, 1.08, 540, 700),      # 1 machine starts cutting
       ("play", 5.3, 8.1, 1.15, 1.35, 540, 520),     # 2 every groove perfect (arrow)
       ("play", 8.1, 10.8, 1.0, 1.1, 540, 600),      # 3 connects to another part
       ("play", 10.8, 12.4, 1.0, 1.0, 540, 600),     # 4 SCHEMATIC lock / rotate as one
       ("play", 10.8, 14.6, 1.1, 1.4, 540, 520),     # 5 power through drivetrain
       ("play", 14.6, 15.2, 1.4, 1.6, 540, 520),     # 6 "here's the crazy part" (punch)
       ("play", 15.2, 17.1, 1.6, 1.75, 600, 560),    # 7 small error ruins the fit (red arrow)
       ("rewind", 17.1, 2.6, 1.0, 1.0, 540, 700),    # 8a again and again…
       ("play", 2.6, 6.2, 1.0, 1.15, 540, 600),      # 8b …with extreme precision
       ("play", 11.6, 17.1, 1.5, 1.0, 540, 560)]     # 9 simple lines -> pull out
RW = 0.9                                              # rewind length inside segment 8
spans = [(B[i], B[i + 1]) for i in range(8)] + [(B[8], B[8] + RW), (B[8] + RW, B[9]), (B[9], B[10])]
seq = []
for (kind, a, b, z0, z1, cx, cy), (t0, t1) in zip(SEG, spans):
    n = int(round(t1 * FPS)) - int(round(t0 * FPS))
    for j in range(n):
        u = j / max(1, n - 1)
        s = a + (b - a) * (u if kind == "rewind" else j / n)
        e = 3 * u * u - 2 * u ** 3
        seq.append((s, kind, u, z0 + (z1 - z0) * e, cx, cy, len(seq)))
DUR = len(seq) / FPS
SEGIDX = []
for k, (t0, t1) in enumerate(spans):
    SEGIDX += [k] * (int(round(t1 * FPS)) - int(round(t0 * FPS)))
print(f"dur {DUR:.2f}", "speeds", [round((b - a) / (t1 - t0), 2) for (_, a, b, *_), (t0, t1) in zip(SEG, spans)])


def grade(f):
    f = f.astype(np.float32); g = f.mean(2, keepdims=True); f = g + (f - g) * 1.12
    f = 128 + (f - 128) * 1.12; lum = f.mean(2) / 255
    f[..., 0] += 16 * (1 - lum) ** 2; f[..., 1] += 4 * (1 - lum) ** 2      # steel-blue shadows
    f[..., 2] += 10 * lum ** 2; f[..., 1] += 4 * lum ** 2                  # warm oil highlights
    return np.clip(f, 0, 255).astype(np.uint8)


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


_F = {}
font = lambda s: _F.setdefault(s, ImageFont.truetype(ANTON, s))
WHITE, YELLOW, RED, CYAN = (255, 255, 255), (255, 214, 0), (255, 60, 60), (90, 220, 255)
EMPH = {"torque", "spline", "perfect", "lock", "one", "power", "slipping", "crazy", "error", "ruin", "precision", "again", "drivetrain"}


def stroke(dl, xy, s, f, col, st):
    dl.text((xy[0] + 5, xy[1] + 8), s, font=f, fill=(0, 0, 0, 170), stroke_width=st, stroke_fill=(0, 0, 0, 170))
    dl.text(xy, s, font=f, fill=col, stroke_width=st, stroke_fill=(0, 0, 0, 255))


def arrow(dl, tip, frm, prog, col):
    tip, frm = np.array(tip, float), np.array(frm, float)
    v = tip - frm; L = np.linalg.norm(v); v /= L; nrm = np.array([-v[1], v[0]])
    end = frm + v * L * prog; base = end - v * 80
    poly = [frm + nrm * 20, base + nrm * 20, base + nrm * 52, end, base - nrm * 52, base - nrm * 20, frm - nrm * 20]
    dl.polygon([tuple(p) for p in poly], fill=col + (255,), outline=(0, 0, 0, 255), width=8)


def spline_poly(cx, cy, r_root, r_tip, n, ang, inner=False):
    pts = []
    for i in range(n):
        a0 = ang + 2 * math.pi * i / n
        for frac, r in ((0.0, r_root), (0.12, r_tip), (0.38, r_tip), (0.5, r_root)) if not inner else \
                ((0.0, r_tip), (0.12, r_root), (0.38, r_root), (0.5, r_tip)):
            a = a0 + 2 * math.pi * frac / n
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        a = a0 + 2 * math.pi * 1.0 / n
    return pts


T_LOCK = caps[42]["s"]; T_ONE = next(w["s"] for w in caps[42:] if w["w"].startswith("rotate"))


def schematic(img, tt):
    """cross-section: toothed shaft + hub with internal teeth; hub slides in, locks, both rotate"""
    t0, t1 = spans[4]
    al = min(1, (tt - t0) / 0.25, (t1 - tt) / 0.2)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rectangle([0, 0, W, H], fill=(8, 10, 16, int(200 * al)))
    cx, cy, n = 540, 760, 18
    slide = 1 - min(1, max(0, (tt - (T_LOCK - 0.45)) / 0.45)) ** 2
    hx = cx + 520 * slide
    rot = 0.0 if tt < T_LOCK + 0.3 else (tt - T_LOCK - 0.3) * 2.2
    # hub (outer ring with internal teeth)
    ring = spline_poly(hx, cy, 175, 152, n, rot, inner=True)
    dl.ellipse([hx - 330, cy - 330, hx + 330, cy + 330], fill=(200, 150, 60, int(255 * al)), outline=(0, 0, 0, int(255 * al)), width=8)
    dl.polygon(ring, fill=(8, 10, 16, int(255 * al)), outline=(0, 0, 0, int(255 * al)))
    # shaft (external teeth)
    dl.polygon(spline_poly(cx, cy, 150, 172, n, rot + math.pi / n * 0.0), fill=(205, 215, 230, int(255 * al)),
               outline=(0, 0, 0, int(255 * al)))
    dl.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(120, 130, 145, int(255 * al)))
    # rotation marker so the shared spin is obvious
    for rr, col in ((100, (255, 60, 60)), (300, (255, 60, 60))):
        mx, my = (cx if rr == 100 else hx) + rr * math.cos(rot - math.pi / 2), cy + rr * math.sin(rot - math.pi / 2)
        dl.ellipse([mx - 16, my - 16, mx + 16, my + 16], fill=col + (int(255 * al),), outline=(0, 0, 0, int(255 * al)), width=4)
    f = font(64)
    stroke(dl, (cx - dl.textlength("SHAFT", font=f) / 2, cy + 360), "SHAFT + GEAR HUB", f, WHITE + (int(255 * al),), 6) if False else None
    lab = "LOCKED" if tt >= T_LOCK else "SHAFT  →  HUB"
    if tt >= T_ONE:
        lab = "ROTATE AS ONE"
    fo = font(96); tw = dl.textlength(lab, font=fo)
    stroke(dl, (W / 2 - tw / 2, 300), lab, fo, (YELLOW if tt >= T_LOCK else WHITE) + (int(255 * al),), 9)
    img.alpha_composite(lay)


chunks, cur = [], []
for w in caps:
    cur.append(w)
    if len(cur) >= 3 or w["w"].endswith((".", ",", "…")):
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)
HOOK = [("THESE TINY GROOVES…", WHITE, 112), ("CARRY INSANE TORQUE", YELLOW, 120)]
ARROWS = [(spans[2][0] + 0.9, spans[2][1], (640, 560), (960, 280), YELLOW),
          (spans[7][0] + 0.1, spans[7][1], (620, 600), (950, 330), RED)]
T_CRAZY = spans[6][0]

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", f"{S}/w/video.mp4"],
                       stdin=subprocess.PIPE)
for n, (s, kind, u, z, cx, cy, _) in enumerate(seq):
    tt = n / FPS; si = SEGIDX[min(n, len(SEGIDX) - 1)]
    f = get(s)
    if abs(z - 1) > 1e-3:
        f = cv2.warpAffine(f, np.float32([[z, 0, cx * (1 - z)], [0, z, cy * (1 - z)]]), (W, H), flags=cv2.INTER_CUBIC,
                           borderMode=cv2.BORDER_REFLECT)
    if kind == "rewind":
        sh = int(10 + 16 * np.sin(np.pi * u)); r = f.copy()
        r[..., 2] = np.roll(f[..., 2], sh, 1); r[..., 0] = np.roll(f[..., 0], -sh, 1)
        r[::4] = (r[::4] * 0.72).astype(np.uint8); f = r
    if abs(tt - T_CRAZY) < 0.06 or abs(tt - T_LOCK) < 0.06:
        f = cv2.addWeighted(f, 0.62, np.full_like(f, 255), 0.38, 0)
    img = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA")
    if si == 4:
        schematic(img, tt)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    if tt < spans[0][1]:
        for j, (txt, col, sz) in enumerate(HOOK):
            if tt >= 0.12 * j:
                uu = min(1, (tt - 0.12 * j) / 0.14); sc = 1.25 - 0.25 * (1 - (1 - uu) ** 3) if uu < 1 else 1
                fo = font(int(sz * sc))
                while dl.textlength(txt, font=fo) > W - 80:
                    fo = font(fo.size - 4)
                tw = dl.textlength(txt, font=fo)
                stroke(dl, (W / 2 - tw / 2, [200, 345][j] - fo.size * 0.6), txt, fo, col + (255,), max(7, fo.size // 11))
    if kind == "rewind":
        for x0_ in (60, 110):
            dl.polygon([(x0_ + 50, 120), (x0_ + 50, 190), (x0_, 155)], fill=WHITE + (255,), outline=(0, 0, 0, 255), width=5)
        stroke(dl, (190, 112), "AGAIN", font(70), WHITE + (255,), 6)
    for t0, t1, tip, frm, col in ARROWS:
        if t0 <= tt < t1:
            arrow(dl, tip, frm, min(1, (tt - t0) / 0.18), col)
    for ch in chunks:
        if ch[0]["s"] <= tt < ch[-1]["e"] + 0.12:
            fo = font(92); full = " ".join(w["w"] for w in ch)
            while dl.textlength(full, font=fo) > W - 90:
                fo = font(fo.size - 4)
            x = W / 2 - dl.textlength(full, font=fo) / 2; y = H * 0.775
            for w in ch:
                if w["s"] > tt:
                    break
                key = w["w"].lower().strip(".,…'s")
                col = YELLOW if (key in EMPH or w["w"].lower().strip(".,…") in EMPH or tt < w["e"]) else WHITE
                stroke(dl, (x, y), w["w"], fo, col + (255,), 9)
                x += dl.textlength(w["w"] + " ", font=fo)
            break
    img.alpha_composite(lay)
    enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
enc.stdin.close(); enc.wait()

# ---- audio: VO + machine sound (low, ducked) + clinks / boom / rewind ----
SR = sd.SR; N = int(DUR * SR)
vo = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f"{S}/w/vo_fast.wav", "-af",
                                   "highpass=f=60,acompressor=threshold=-18dB:ratio=3:attack=5:release=80",
                                   "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
src = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                   capture_output=True).stdout, np.float32)
amb = np.zeros(N)
for n_, (s, kind, *_r) in enumerate(seq):
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
    n_ = int(0.9 * SR); t_ = np.arange(n_) / SR; f0 = 1760 * pitch
    s_ = sum(a * np.sin(2 * np.pi * f0 * r * t_) * np.exp(-t_ / dcy) for r, a, dcy in
             [(1.0, 1.0, 0.35), (2.76, 0.45, 0.18), (5.40, 0.25, 0.09), (8.93, 0.12, 0.05)])
    s_ += 0.3 * sd.hp(np.random.default_rng(2).standard_normal(n_), 5000) * np.exp(-t_ / 0.003)
    return s_ * np.clip(t_ / 0.0015, 0, 1)


place(sd.pop(1.0), 0.03, 0.3); place(sd.pop(1.0), 0.15, 0.25)
place(clink2(1.0), ARROWS[0][0], 0.55); place(clink2(0.8), ARROWS[1][0], 0.6)
place(sd.boom(), T_LOCK, 0.9); place(clink2(1.3), T_LOCK + 0.02, 0.45)
place(sd.pop(1.0), T_CRAZY, 0.35)
place(sd.rewind(RW), spans[8][0], 0.5)
mix += fx * 0.55
mix.astype(np.float32).tofile(f"{S}/w/mix.f32")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", f"{S}/w/mix.f32",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "2", f"{S}/w/audio.wav"], check=True)
vk = int(min(14000, 27 * 8 * 1024 / DUR - 200)); pl = f"{S}/w/pass"
c = ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{vk}k", "-maxrate", f"{int(vk * 1.4)}k", "-bufsize", f"{vk * 2}k", "-passlogfile", pl]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/w/video.mp4", *c, "-pass", "1", "-an", "-f", "null", "/dev/null"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/w/video.mp4", "-i", f"{S}/w/audio.wav", "-map", "0:v", "-map", "1:a",
                *c, "-pass", "2", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", OUT], check=True)
print(f"{OUT}: {os.path.getsize(OUT) / 1e6:.1f} MB, {DUR:.2f} s")
