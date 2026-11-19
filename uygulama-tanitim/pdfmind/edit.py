# PDF Mind tanıtım videosu kurgusu (çalışma klasörü: argv[1], içinde ham.mp4, stab.mp4, ses.srt)
import subprocess, math, json, sys, os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
os.chdir(sys.argv[1])
W, H, FPS = 1080, 1920, 30
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FS = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"
F = lambda p, s: ImageFont.truetype(p, s)
ACC = (255, 213, 74)
# ---------- kesimler: (ses başı, ses sonu, görüntü başı) ----------
# "Arkadaşlar merhaba" ve son cümle ("İncelemek isteyenleri…") çıkarıldı; 8.35'teki görüntü PC'deki Claude Code ekranı
SEG = [(2.55, 6.35, 2.55), (6.95, 9.25, 8.35), (12.15, 24.95, 12.15), (26.95, 29.65, 26.95), (31.2, 37.1, 31.2), (38.75, 40.75, 38.75), (41.5, 44.4, 41.5)]
OUT0 = []; acc = 0
for a, b, v in SEG: OUT0.append(acc); acc += b - a
DUR = acc
def s2o(t):
    for (a, b, v), o in zip(SEG, OUT0):
        if a - .3 <= t <= b + .3: return o + min(max(t, a), b) - a
    return None
# ---------- altyazı ----------
words = []
for blk in open("ses.srt").read().strip().split("\n\n"):
    L = blk.split("\n"); t0, t1 = [sum(float(x) * m for x, m in zip(p.replace(",", ".").split(":"), (3600, 60, 1))) for p in L[1].split(" --> ")]
    txt = " ".join(L[2:]).replace("Cloud Code", "Claude Code").replace("PDFMind", "PDF Mind").replace("için-", "için")
    ws = txt.split(); v = lambda w: max(1, sum(c in "aeıioöuüAEIİOÖUÜ" for c in w)); tot = sum(v(w) for w in ws); c = 0
    for w in ws: s = t0 + (t1 - t0) * c / tot; c += v(w); e = t0 + (t1 - t0) * c / tot; words.append([w, s, e])
CAP = []
for w, s, e in words:
    if w.lower().startswith(("arkadaş", "merhaba")): continue
    o = s2o(s)
    if o is not None and s < SEG[-1][1]: CAP.append([w, o, o + (e - s)])
def ow(pre, nth=0):
    c = [x for x in CAP if x[0].lower().startswith(pre)]; return c[nth][1] if len(c) > nth else 0
def eo(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def tracked(d, xy, txt, font, fill, track=0):
    if not track: d.text(xy, txt, font=font, fill=fill, anchor="mm"); return
    w = sum(font.getlength(c) for c in txt) + track * (len(txt) - 1); x = xy[0] - w / 2
    for c in txt: d.text((x, xy[1]), c, font=font, fill=fill, anchor="lm"); x += font.getlength(c) + track
def tw(txt, font, track=0): return sum(font.getlength(c) for c in txt) + track * (len(txt) - 1) if track else font.getlength(txt)
def glass(base, box, r, tint=(12, 14, 20), a=.58):
    x0, y0, x1, y1 = [int(v) for v in box]; x0 = max(0, x0); y0 = max(0, y0); x1 = min(W, x1); y1 = min(H, y1)
    if x1 - x0 < 4 or y1 - y0 < 4: return
    reg = base.crop((x0, y0, x1, y1)).convert("RGB").filter(ImageFilter.GaussianBlur(22)); reg = Image.blend(reg, Image.new("RGB", reg.size, tint), a)
    m = Image.new("L", reg.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, reg.width - 1, reg.height - 1], r, fill=255); base.paste(reg, (x0, y0), m)
    ImageDraw.Draw(base).rounded_rectangle([x0, y0, x1 - 1, y1 - 1], r, outline=(255, 255, 255, 46), width=2)
def fade_glass(base, box, r, a, tint_a=.58):
    tmp = base.copy(); glass(tmp, box, r, a=tint_a); base.alpha_composite(Image.blend(base, tmp, a))
def soft_text(base, xy, txt, font, fill=(255, 255, 255), track=0, alpha=1.0, shadow=True):
    if shadow:
        sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); tracked(ImageDraw.Draw(sh), (xy[0], xy[1] + 4), txt, font, (0, 0, 0, int(140 * alpha)), track); base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0)); tracked(ImageDraw.Draw(lay), xy, txt, font, fill + (int(255 * alpha),), track); base.alpha_composite(lay)
def anim(t, t0, t1, fade=.25):
    if t < t0 or t >= t1: return 0, 0
    return eo((t - t0) / .35), min(1, (t1 - t) / fade)
def chip(base, t, t0, t1, txt, y=300):
    k, out = anim(t, t0, t1)
    if k <= 0: return
    f = F(FS, 46); w = tw(txt, f, 1) + 104; h = 92; dy = 18 * (1 - k); a = k * out; box = (540 - w / 2, y - h / 2 + dy, 540 + w / 2, y + h / 2 + dy)
    fade_glass(base, box, h // 2, a)
    ImageDraw.Draw(base).ellipse([box[0] + 34, y + dy - 9, box[0] + 52, y + dy + 9], fill=ACC + (int(255 * a),))
    soft_text(base, (554, y + dy + 1), txt, f, track=1, alpha=a, shadow=False)
def hook(base, t):
    t1 = OUT0[1] - .05
    if t >= t1: return
    out = min(1, (t1 - t) / .25); k1 = eo(.5 + t / .35)
    soft_text(base, (540, 330 - 14 * (1 - k1)), "YAPAY ZEKÂ", F(FS, 44), ACC, track=10, alpha=k1 * out)
    for i, line in enumerate(("Uygulamamı", "test ediyor")):
        kk = eo((t - .12 - i * .1) / .4); soft_text(base, (540, 430 + i * 118 + 20 * (1 - kk)), line, F(FB, 112), alpha=kk * out)
CHECK = ["Ana Sayfa", "Araçlar", "Belgelerim", "Profil"]
def checklist(base, t, t0, t1):
    k, out = anim(t, t0, t1)
    if k <= 0: return
    n = min(len(CHECK), int((t - t0) / .45) + 1); a = k * out; w, h = 520, 120 + 84 * len(CHECK); y0 = 300 + 20 * (1 - k)
    fade_glass(base, (540 - w / 2, y0, 540 + w / 2, y0 + h), 36, a)
    d = ImageDraw.Draw(base); tracked(d, (540, y0 + 62), "SAYFALAR TARANIYOR", F(FS, 34), (255, 255, 255, int(170 * a)), 6)
    for i, nm in enumerate(CHECK):
        y = y0 + 132 + i * 84; done = i < n; x0 = 540 - w / 2 + 70
        if done: d.ellipse([x0 - 20, y - 20, x0 + 20, y + 20], fill=ACC + (int(255 * a),)); d.line([(x0 - 9, y), (x0 - 2, y + 8), (x0 + 10, y - 8)], fill=(20, 20, 24, int(255 * a)), width=5)
        else: d.ellipse([x0 - 20, y - 20, x0 + 20, y + 20], outline=(255, 255, 255, int(90 * a)), width=3)
        d.text((x0 + 44, y + 1), nm, font=F(FS, 44), fill=(255, 255, 255, int((255 if done else 120) * a)), anchor="lm")
def title(base, t, t0, t1, sub):
    k, out = anim(t, t0, t1)
    if k <= 0: return
    a = k * out; hh = 300 if sub == "CTA" else 250; y0 = 250 + 20 * (1 - k)
    fade_glass(base, (130, y0, 950, y0 + hh), 44, a, .66); soft_text(base, (540, y0 + 105), "PDF Mind", F(FB, 140), alpha=a)
    if sub and sub != "CTA":
        k2 = eo((t - t0 - .35) / .35)
        if k2 > 0: soft_text(base, (540, y0 + 200 + 10 * (1 - k2)), sub, F(FS, 42), ACC, track=8, alpha=k2 * out, shadow=False)
def stores(base, t, t0, ta, t1):
    for i, (nm, ts) in enumerate((("Google Play", t0), ("App Store", ta))):
        k, out = anim(t, ts, t1)
        if k <= 0: continue
        a = k * out; w, h = 420, 170; cx = 540 + (-225 if i == 0 else 225); y0 = 300 + 20 * (1 - k)
        fade_glass(base, (cx - w / 2, y0, cx + w / 2, y0 + h), 34, a)
        d = ImageDraw.Draw(base); tracked(d, (cx, y0 + 52), "YAKINDA", F(FS, 30), ACC + (int(255 * a),), 6); d.text((cx, y0 + 112), nm, font=F(FB, 60), fill=(255, 255, 255, int(255 * a)), anchor="mm")
def cta(base, t, t0):
    if t < t0: return
    k = eo((t - t0) / .35); title(base, t, t0, 99, "CTA")
    f = F(FB, 48); txt = "Hemen incele  ↓"; w = tw(txt, f) + 100; h = 100; y = 250 + 20 * (1 - k) + 225
    d = ImageDraw.Draw(base); d.rounded_rectangle([540 - w / 2, y - h / 2, 540 + w / 2, y + h / 2], h // 2, fill=(255, 255, 255, int(245 * k)))
    d.text((540, y + 2), txt, font=f, fill=(15, 15, 20, int(255 * k)), anchor="mm")
YEL2 = {"claude", "code", "emulatör", "analiz", "tarıyor", "pdf", "mind", "play", "store'da", "app", "yeni", "kullanıcı", "deneyimi"}
CH = []; cur = []; _f = F(FB, 72)
for i, (w, s, e) in enumerate(CAP):
    cur.append([w, s, e]); nxt = CAP[i + 1][1] if i + 1 < len(CAP) else 1e9; nxw = CAP[i + 1][0].strip(".,?!:-") if i + 1 < len(CAP) else ""
    wd = sum(_f.getlength(x[0].strip(".,?!:-")) for x in cur) + _f.getlength(" ") * (len(cur) - 1)
    if len(cur) >= 3 or w[-1] in ".,?!" or nxt - e > .3 or wd + _f.getlength(" " + nxw) > 900: CH.append(cur); cur = []
if cur: CH.append(cur)
def captions(base, t):
    for ci, ch in enumerate(CH):
        s0, e0 = ch[0][1], ch[-1][2]; nx = CH[ci + 1][0][1] if ci + 1 < len(CH) else e0 + .5
        if s0 - .03 <= t < min(nx, e0 + .4):
            f = _f; ws = [w.strip(".,?!:-") for w, _, _ in ch]; sp = f.getlength(" ")
            x = 540 - (sum(f.getlength(w) for w in ws) + sp * (len(ws) - 1)) / 2; y = 1585; k = eo((t - s0 + .03) / .18)
            sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh); xx = x
            for w in ws: ds.text((xx, y + 4), w, font=f, fill=(0, 0, 0, 220), anchor="lm", stroke_width=6, stroke_fill=(0, 0, 0, 220)); xx += f.getlength(w) + sp
            base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12))); d = ImageDraw.Draw(base)
            for (w, s, e), cw in zip(ch, ws):
                on = s - .02 <= t; col = ACC if on and cw.lower() in YEL2 else (255, 255, 255)
                d.text((x, y + 8 * (1 - k)), cw, font=f, fill=col + (int(255 * (1 if on else .55) * k),), anchor="lm", stroke_width=2, stroke_fill=(0, 0, 0, int(60 * k))); x += f.getlength(cw) + sp
            return
T_CC = OUT0[1]; T_EMU = ow("emulatör"); T_TAR = ow("tarıyor"); T_UX = ow("kullanıcı"); T_PDF = ow("pdf"); T_PLAY = ow("play"); T_APP = ow("app"); T_OLD = ow("şu", 1); T_END = s2o(43.15)
def overlay(base, t):
    hook(base, t)
    chip(base, t, T_CC - .05, T_EMU - .2, "Claude Code ile")
    chip(base, t, T_EMU - .05, T_TAR - .1, "Emülatörde canlı test")
    checklist(base, t, T_TAR - .1, T_UX - .1)
    chip(base, t, T_UX - .05, OUT0[3] - .05, "Kullanıcı deneyimi analizi")
    chip(base, t, OUT0[3] - .05, OUT0[4] - .05, "En iyi düzen aranıyor")
    title(base, t, T_PDF - .05, T_PLAY - .15, "YENİ SÜRÜM")
    stores(base, t, T_PLAY - .1, T_APP - .1, OUT0[6] - .05)
    chip(base, t, T_OLD - .05, T_END, "Şu an eski sürümü yayında")
    cta(base, t, T_END)
    captions(base, t)
# ---------- görüntü ----------
VF = "crop=360:640:59:10,scale=1080:1920:flags=lanczos,hqdn3d=1.5:1.5:4:4,unsharp=7:7:1.1:5:5:0.4,eq=contrast=1.12:saturation=1.25:brightness=0.02:gamma=0.97"
enc = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "video_sessiz.mp4"], stdin=subprocess.PIPE)
vg = np.linspace(-1, 1, W)[None, :] ** 2 + np.linspace(-1, 1, H)[:, None] ** 2; VIG = (1 - .32 * np.clip(vg - .3, 0, 1))[..., None]
for (a, b, v), o in zip(SEG, OUT0):
    n = int(round((b - a) * FPS)); raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{v:.3f}", "-i", "stab.mp4", "-frames:v", str(n), "-vf", VF, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    for i in range(n):
        img = fr[min(i, len(fr) - 1)]; lt = i / FPS; t = o + lt
        z = (1.0, 1.12, 1.04, 1.16)[int(lt / 2.4) % 4] + .05 * max(0, 1 - lt / .2)
        if z > 1.001: img = cv2.warpAffine(img, cv2.getRotationMatrix2D((540, 930), 0, z), (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        base = Image.fromarray((img.astype(np.float32) * VIG).clip(0, 255).astype(np.uint8)).convert("RGBA"); overlay(base, t)
        enc.stdin.write(np.array(base.convert("RGB")).tobytes())
enc.stdin.close(); enc.wait()
json.dump({"SEG": SEG, "OUT0": OUT0, "DUR": DUR}, open("plan.json", "w")); print("video ok", round(DUR, 2))
