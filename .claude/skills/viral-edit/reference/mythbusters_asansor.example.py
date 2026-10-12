#!/usr/bin/env python3
"""MythBusters – asansör efsanesi (VULRAN tarzı, bizim imza): TR seslendirme (1.15x sıkı), cümle = sahne,
gömülü İngilizce altyazı ProPainter ile silinmiş kaynak, kelime kelime altyazı o bandın üstünde,
hız göstergesi (85 / 82 KM/S), çarpmada flaş + sarsıntı + boom, sonda BUSTED damgası.
Orijinal ses: İngilizce konuşma ayrılmış (MDX), yalnız efekt/ortam kalır; çarpmada açılır."""
import json, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/user/Public/.claude/skills/viral-edit/scripts")
import sounddesign as sd

S = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("SRC") or (f"{S}/w/clean.mp4" if os.path.exists(f"{S}/w/clean.mp4") else f"{S}/in/src.mp4")
OUT = os.environ.get("OUT") or f"{S}/out/asansor_efsanesi.mp4"
W, H, FPS, SFPS = 1080, 1920, 30, 25
ANTON = "/home/user/Public/.claude/skills/viral-edit/fonts/Anton-Regular.ttf"
caps = json.load(open(f"{S}/w/cap_fast.json", encoding="utf-8"))
VOD = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{S}/w/vo_fast.wav"],
                           capture_output=True, text=True).stdout)
ws = lambda i: caps[i]["s"] - 0.05
END = VOD + 1.3                                     # BUSTED damgası için kuyruk
T_HIT = ws(65) + 0.04                               # "çakıldı"
SEG = [(0.0, 0.0, 3.0),           # "Düşen bir asansörde … efsane var." (kabin tepesi, boşluk)
       (ws(14), 3.0, 8.35),       # "Mantık basit görünüyor: … hissetmezsin." (ekip, karanlık boşluk)
       (ws(23), 8.45, 13.85),     # "Efsane Avcıları … boşluğa bıraktı." (işaretlerin önünden düşüş)
       (ws(40), 13.95, 16.0),     # "Kabin dibe … 85 kilometre hızla düşüyordu." (Buster kabinde)
       (ws(49), 16.0, 17.6),      # "Buster son anda zıpladı, … yükseldi." (ağır çekim)
       (ws(58), 17.6, 18.80),     # "Ama yine de yere saatte 82 kilometreyle" (gerilim)
       (T_HIT, 19.0, 20.45),      # "çakıldı." ÇARPMA (18.88–18.96 kaynağın parazit geçişi, dışarıda)
       (ws(66), 22.6, 25.6),      # "Çünkü sen ve asansör birlikte düşüyorsunuz." (ezilen bacaklar)
       (ws(72), 34.95, 38.5)]     # "Kurtulmak için … gerekirdi." (Jamie, Adam) + BUSTED
B = [s[0] for s in SEG] + [END]
seq = []
for k, (t0, a, b) in enumerate(SEG):
    n = int(round(B[k + 1] * FPS)) - int(round(t0 * FPS))
    seq += [(a + (b - a) * j / n, k) for j in range(n)]
DUR = len(seq) / FPS
print(f"süre {DUR:.2f}  hızlar", [round((b - a) / (B[k + 1] - B[k]), 2) for k, (_, a, b) in enumerate(SEG)])


def grade(f):
    f = f.astype(np.float32); g = f.mean(2, keepdims=True); f = g + (f - g) * 1.12
    f = 128 + (f - 128) * 1.08
    return np.clip(f, 0, 255).astype(np.uint8)


need = set()
for s, _ in seq:
    need.add(int(s * SFPS)); need.add(int(s * SFPS) + 1)
store, k = {}, 0
d = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
while True:
    b = d.stdout.read(W * H * 3)
    if len(b) < W * H * 3:
        break
    if k in need:
        store[k] = cv2.imencode(".jpg", grade(np.frombuffer(b, np.uint8).reshape(H, W, 3)), [cv2.IMWRITE_JPEG_QUALITY, 95])[1]
    k += 1
d.wait(); last = max(store)


def get(s):
    i0 = min(int(s * SFPS), last); w_ = s * SFPS - int(s * SFPS)
    a = cv2.imdecode(store[i0], cv2.IMREAD_COLOR)
    if w_ > 0.05 and i0 + 1 in store and abs(w_ - 0.5) < 0.45:
        a = cv2.addWeighted(a, 1 - w_, cv2.imdecode(store[i0 + 1], cv2.IMREAD_COLOR), w_, 0)
    return a


def zoom(f, z, cx=W / 2, cy=H / 2):
    return cv2.warpAffine(f, np.float32([[z, 0, cx * (1 - z)], [0, z, cy * (1 - z)]]), (W, H), borderMode=cv2.BORDER_REFLECT)


_F = {}
font = lambda s: _F.setdefault(s, ImageFont.truetype(ANTON, s))
WHITE, YELLOW, RED = (255, 255, 255), (255, 214, 0), (255, 50, 50)
EMPH = {"asansörde", "zıplarsan", "efsane", "havada", "darbeyi", "buster", "85", "zıpladı", "tavana", "82", "çakıldı",
        "birlikte", "yukarı"}


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
HOOK = [("DÜŞEN ASANSÖRDE", WHITE, 118), ("ZIPLAMAK KURTARIR MI?", YELLOW, 118)]
SPEED = [(ws(45), B[4], "85", YELLOW), (ws(63), B[7], "82", RED)]
T_BUST = ws(80) + 0.55

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", f"{S}/w/video.mp4"],
                       stdin=subprocess.PIPE)
for n, (s, si) in enumerate(seq):
    tt = n / FPS
    f = get(s)
    for c in B[1:-1]:                                     # geçiş: giren plan büyükten oturur (bulanıklık yok)
        if 0 <= tt - c < 0.2 and c != T_HIT:
            f = zoom(f, 1 + 0.1 * (1 - (tt - c) / 0.2) ** 2)
    if 0 <= tt - T_HIT < 0.6:                              # çarpma: flaş + sarsıntı + yakınlaşma
        e = 1 - (tt - T_HIT) / 0.6
        f = zoom(f, 1 + 0.08 * e)
        a = 26 * e * (1 if n % 2 else -1)
        f = cv2.warpAffine(f, np.float32([[1, 0, a], [0, 1, -a * 0.7]]), (W, H), borderMode=cv2.BORDER_REFLECT)
        if tt - T_HIT < 0.1:
            f = cv2.addWeighted(f, 0.45, np.full_like(f, 255), 0.55, 0)
    if tt >= T_BUST:                                       # sonuç: hafif kırmızı ton
        e = min(1, (tt - T_BUST) / 0.25); r = f.copy(); r[..., 2] = np.clip(r[..., 2].astype(int) + 60, 0, 255)
        f = cv2.addWeighted(f, 1 - 0.35 * e, r, 0.35 * e, 0)
    img = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA")
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    if tt < B[1] - 0.05:                                   # hook
        for j, (txt, col, sz) in enumerate(HOOK):
            if tt >= 0.12 * j:
                fo = font(int(sz * pop(tt, 0.12 * j, a=0.25)))
                while dl.textlength(txt, font=fo) > W - 80:
                    fo = font(fo.size - 4)
                tw = dl.textlength(txt, font=fo)
                stroke(dl, (W / 2 - tw / 2, [250, 390][j] - fo.size * 0.6), txt, fo, col + (255,), max(8, fo.size // 11))
    for t0, t1, v, col in SPEED:                           # hız göstergesi
        if t0 <= tt < t1:
            sc = pop(tt, t0, 0.16, 0.35); fb = font(int(230 * sc)); fu = font(int(70 * sc))
            tw = dl.textlength(v, font=fb); uw = dl.textlength("KM/S", font=fu)
            x = W / 2 - (tw + 20 + uw) / 2; y = 330 - fb.size * 0.6
            stroke(dl, (x, y), v, fb, col + (255,), 14)
            stroke(dl, (x + tw + 20, y + fb.size * 0.62), "KM/S", fu, WHITE + (255,), 8)
    if tt >= T_BUST:                                       # BUSTED damgası
        sc = pop(tt, T_BUST, 0.18, 0.6)
        S_ = Image.new("RGBA", (900, 330), (0, 0, 0, 0)); ds = ImageDraw.Draw(S_)
        ds.rounded_rectangle([20, 20, 880, 310], radius=30, outline=RED + (255,), width=22)
        fo = font(210); tw = ds.textlength("BUSTED", font=fo)
        ds.text((450 - tw / 2, 165 - fo.size * 0.62), "BUSTED", font=fo, fill=RED + (255,), stroke_width=6, stroke_fill=(90, 0, 0, 255))
        S_ = S_.resize((int(900 * sc), int(330 * sc))).rotate(-8, resample=Image.BICUBIC, expand=True)
        lay.alpha_composite(S_, (int(W / 2 - S_.size[0] / 2), int(760 - S_.size[1] / 2)))
        dl = ImageDraw.Draw(lay)
    for ch in chunks:                                      # altyazı: gömülü İngilizce bandın üstünde
        if ch[0]["s"] <= tt < ch[-1]["e"] + 0.15:
            fo = font(96); full = " ".join(w["w"] for w in ch)
            while dl.textlength(full, font=fo) > W - 90:
                fo = font(fo.size - 4)
            x = W / 2 - dl.textlength(full, font=fo) / 2; y = 1372 - fo.size * 0.62
            for w in ch:
                if w["s"] > tt:
                    break
                key = w["w"].lower().strip(".,:")
                col = RED if key in ("82", "çakıldı") else (YELLOW if (key in EMPH or tt < w["e"]) else WHITE)
                stroke(dl, (x, y), w["w"], fo, col + (255,), 10)
                x += dl.textlength(w["w"] + " ", font=fo)
            break
    img.alpha_composite(lay)
    enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
enc.stdin.close(); enc.wait()

# ---- ses ----
SR = sd.SR; N = int(round(DUR * SR))
rd = lambda p, af="anull": np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-af", af, "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"],
                                                        capture_output=True).stdout, np.float32).copy()
vo = rd(f"{S}/w/vo_fast.wav", "highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80")
inst = rd(f"{S}/w/src_inst.wav")
parts = []
for k, (t0, a, b) in enumerate(SEG):
    n_ = int(round(B[k + 1] * SR)) - int(round(t0 * SR)); sp = (b - a) / (B[k + 1] - t0)
    fi, fo_ = f"{S}/w/i{k}.f32", f"{S}/w/o{k}.f32"
    inst[int(a * SR):int(b * SR)].tofile(fi)
    af = f"atempo={sp:.4f}" if sp >= 1 else f"rubberband=tempo={sp:.4f}:pitch=1.0"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", fi, "-af", af, "-f", "f32le", fo_], check=True)
    y = np.fromfile(fo_, np.float32); y = np.pad(y, (0, max(0, n_ - len(y))))[:n_].copy()
    r = int(0.015 * SR); y[:r] *= np.linspace(0, 1, r); y[-r:] *= np.linspace(1, 0, r); parts.append(y)
    os.remove(fi); os.remove(fo_)
amb = np.concatenate(parts)[:N]; amb = np.pad(amb, (0, N - len(amb)))
voc = np.zeros(N); voc[:min(N, len(vo))] = vo[:N]
rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 1e-4] ** 2) + 1e-12)
amb = amb * (rms(voc) / rms(amb)) * 10 ** (-12 / 20)
env = np.convolve(np.abs(voc), np.ones(int(0.05 * SR)) / int(0.05 * SR), mode="same")
duck = 1 - 0.5 * np.clip(env / (np.percentile(env, 90) + 1e-9), 0, 1)
duck = np.convolve(duck, np.ones(int(0.15 * SR)) / int(0.15 * SR), mode="same")
gain = np.ones(N); a_, b_ = int((T_HIT - 0.05) * SR), int((T_HIT + 1.2) * SR); gain[a_:b_] = 3.0      # çarpma sesi öne
gain = np.convolve(gain, np.ones(int(0.05 * SR)) / int(0.05 * SR), mode="same")
mix = voc + amb * duck * gain
fx = np.zeros(N)


def place(sig, t_, g_):
    a = int(t_ * SR); b = min(N, a + len(sig))
    if 0 <= a < N:
        fx[a:b] += sig[:b - a] / (np.max(np.abs(sig)) + 1e-9) * g_


place(sd.pop(1.0), 0.03, 0.3); place(sd.pop(1.0), 0.15, 0.25)
for t0, _, _, _ in SPEED:
    place(sd.pop(1.2), t0, 0.35)
place(sd.boom(), T_HIT, 1.0)
place(sd.boom(), T_BUST, 0.8); place(sd.pop(0.8), T_BUST, 0.4)
mix += fx * 0.55
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
