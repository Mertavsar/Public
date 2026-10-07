#!/usr/bin/env python3
"""
Esports (LoL) dikey klip -> kanal formatında Shorts. Tek spec, tek komut.

Yerleşim (kullanıcı kuralı: yazı az ve OYUNUN ÜSTÜNE GELMEZ):
  üst yorum bandı (0..band) | oyun paneli (ölçeksiz) | çeviri şeridi | kamera kartı

    python3 esports_short.py spec.json

spec (json):
{
 "src": "src.mp4", "out": "out.mp4", "target_mb": 29,
 "game": [770, 1630],            // kaynakta oyunun temiz satırları (başlık/HUD dışı)
 "cam":  [0, 560, 0, 1080],      // kaynakta kamera: y0, y1, x0, x1
 "band": 280, "card": [90, 1236, 900, 467], "card_label": "CAM",
 "palette": "red" | "purple" | "navy" | "teal",
 "grade": "warm" | "night" | "neon" | "clean",
 "plan": [ {"src": [33.9, 34.45], "speed": 0.5},
           {"freeze": 34.45, "dur": 1.2},
           {"rewind": [34.45, 6.6], "dur": 0.4}, ... ],
 "headlines": [{"at": T, "dur": D, "lines": [["TEXT", "white", 100], ...]}],
 "chips":     [{"at": T, "dur": D, "parts": [["KERIA ", "accent"], ["HAS SLAIN NS VITAL!", "white"]]}],
 "flash": [T...], "shake": [T...],
 "sfx": {"boom": [T], "clink": [T], "pop": [T], "rewind": [[T, D]]},
 "voice": [{"at": T, "text": "Number six.", "voice": "rms"}],
 "cam_keep": [[0, 10.13], [17.63, 21.0]],  // kamerada ana oyuncunun göründüğü aralıklar
 "cam_fill": [[0.5, 9.9]],                 // dışında karta bu aralıklardan oyuncu görüntüsü
 "tts": {"engine": "kokoro", "dir": "/yol/tts", "python": "/yol/tts/venv/bin/python",
         "voice": "am_michael", "speed": 1.05},   // yoksa flite (robotik)
 "duck_db": -9
}
T: çıktı saniyesi (sayı) ya da "S:i:t" = plan[i] içindeki kaynak saniyesi t, ya da
"P:i:x" = plan[i] başlangıcından x sn sonra. Böylece hız değişince yazılar kaymaz.
"""
import json, os, subprocess, sys, tempfile
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sounddesign as sd

W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf"
PAL = {  # bg üst, bg alt (BGR) ; vurgu, ikinci vurgu, kart çerçevesi (RGB)
    "red":    ((22, 10, 48), (8, 6, 12), (255, 60, 70), (255, 210, 60), (255, 60, 70)),
    "purple": ((34, 10, 26), (10, 6, 10), (255, 90, 200), (255, 210, 50), (255, 90, 200)),
    "navy":   ((40, 18, 10), (10, 8, 8), (255, 200, 50), (90, 230, 255), (255, 200, 50)),
    "teal":   ((36, 30, 6), (8, 10, 8), (60, 240, 200), (255, 255, 255), (60, 240, 200)),
}
COL = {"white": (255, 255, 255), "gold": (255, 210, 50), "red": (245, 50, 60), "cyan": (90, 230, 255),
       "pink": (255, 90, 200), "green": (90, 235, 120)}


def sat(f, s):
    g = cv2.cvtColor(np.clip(f, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None]
    return np.clip(g + (f.astype(np.float32) - g) * s, 0, 255)


def grade_game(f, kind):
    sh = cv2.GaussianBlur(f, (0, 0), 1.2)
    f = cv2.addWeighted(f, 1.45, sh, -0.45, 0).astype(np.float32)
    lum = (f.mean(2) / 255)
    if kind == "warm":
        f = sat(f, 1.18); f = 255 * (0.5 + (f / 255 - 0.5) * 1.12)
        f[..., 2] += 12 * lum ** 2; f[..., 1] += 4 * lum ** 2; f[..., 0] += 6 * (1 - lum) ** 2
    elif kind == "night":
        f = sat(f, 1.22); f = 255 * (0.5 + (f / 255 - 0.5) * 1.10)
        f[..., 0] += 16 * (1 - lum) ** 2; f[..., 2] += 7 * (1 - lum) ** 2; f[..., 1] -= 3 * (1 - lum) ** 2
    elif kind == "neon":
        f = sat(f, 1.3); f = 255 * (0.5 + (f / 255 - 0.5) * 1.15)
        f[..., 0] += 10 * (1 - lum) ** 2; f[..., 2] += 10 * lum ** 2
    else:
        f = sat(f, 1.1); f = 255 * (0.5 + (f / 255 - 0.5) * 1.06)
    return np.clip(f, 0, 255).astype(np.uint8)


def grade_cam(f, kind):
    f = f.astype(np.float32)
    if kind == "night":
        f = sat(f, 0.5); f[..., 0] += 10
    elif kind == "warm":
        f = sat(f, 0.9); f[..., 2] += 8; f[..., 0] -= 4
    else:
        f = sat(f, 0.85); f[..., 0] += 5
    return np.clip(255 * (0.5 + (f / 255 - 0.5) * 1.12), 0, 255).astype(np.uint8)


def probe(src):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=r_frame_rate", "-of", "csv=p=0", src], capture_output=True, text=True).stdout
    a, b = o.strip().split("/")
    return float(a) / float(b)


def main():
    sp = json.load(open(sys.argv[1]))
    base = os.path.dirname(os.path.abspath(sys.argv[1]))
    P = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    SRC, OUT = P(sp["src"]), P(sp["out"])
    SFPS = probe(SRC)
    G0, G1 = sp.get("game", [770, 1630]); GH = G1 - G0
    C = sp.get("cam", [0, 560, 0, 1080])
    BAND = sp.get("band", 280)
    cx, cy, cw, ch = sp.get("card", [90, BAND + GH + 96, 900, 467])
    STRIP = BAND + GH + 46
    bgt, bgb, ACC, ACC2, CARD = PAL[sp.get("palette", "red")]
    COL["accent"], COL["accent2"] = ACC, ACC2
    GRADE = sp.get("grade", "warm")

    # ---- zaman çizelgesi ----
    seq, segt, t = [], [], 0.0
    for i, p in enumerate(sp["plan"]):
        if "freeze" in p:
            d = p["dur"]; kind = "freeze"
        elif "rewind" in p:
            d = p["dur"]; kind = "rewind"
        else:
            d = (p["src"][1] - p["src"][0]) / p.get("speed", 1.0); kind = "play"
        n = int(round((t + d) * FPS)) - int(round(t * FPS))
        for k in range(n):
            u = k / max(1, n - 1)
            if kind == "play":
                s = p["src"][0] + (p["src"][1] - p["src"][0]) * k / n
            elif kind == "freeze":
                s = p["freeze"]
            else:
                s = p["rewind"][0] + (p["rewind"][1] - p["rewind"][0]) * u
            seq.append((s, kind, u, i))
        segt.append((t, t + d, p, kind)); t += d
    DUR = len(seq) / FPS

    def T(v):
        if isinstance(v, (int, float)):
            return float(v)
        k, i, x = v.split(":"); i, x = int(i), float(x)
        t0, t1, p, kind = segt[i]
        if k == "P":
            return t0 + x
        if kind == "play":
            return t0 + (x - p["src"][0]) / p.get("speed", 1.0)
        return t0
    print(f"süre {DUR:.2f} sn, {len(segt)} plan")

    # ---- statik katmanlar ----
    yy = np.mgrid[0:H, 0:W][0] / H
    BG = (np.array(bgt)[None, None] * (1 - yy[..., None]) + np.array(bgb)[None, None] * yy[..., None]).astype(np.uint8)
    MASK = np.zeros((ch, cw), np.uint8); r = 30
    cv2.rectangle(MASK, (r, 0), (cw - r - 1, ch - 1), 255, -1); cv2.rectangle(MASK, (0, r), (cw - 1, ch - r - 1), 255, -1)
    for px, py in [(r, r), (cw - r - 1, r), (r, ch - r - 1), (cw - r - 1, ch - r - 1)]:
        cv2.circle(MASK, (px, py), r, 255, -1)
    MASK = MASK[..., None] / 255.0
    a_ = np.linspace(0, 1, W)[None, :, None]
    LINE = (np.array(ACC[::-1]) * (1 - a_) + np.array(ACC2[::-1]) * a_).repeat(5, 0).astype(np.uint8)

    # Kamera kartı: yalnız ana oyuncu. cam_keep: kaynakta kameranın o oyuncu olduğu
    # aralıklar (canlı). Dışındaki anlarda cam_fill aralıklarından görüntü döngüyle
    # akar (aynı oyuncu, zamanı kaymış; etiket canlı demez).
    KEEP = sp.get("cam_keep")
    FILL = sp.get("cam_fill", KEEP or [])
    fill_idx = [k_ for a0_, a1_ in FILL for k_ in range(int(a0_ * SFPS), int(a1_ * SFPS), max(1, int(round(SFPS / FPS))))]

    def live(s):
        return KEEP is None or any(a0_ <= s < a1_ for a0_, a1_ in KEEP)

    cam_src, fp = [], 0
    for s, *_ in seq:
        if live(s):
            cam_src.append(int(round(s * SFPS)))
        else:
            cam_src.append(fill_idx[fp % len(fill_idx)]); fp += 1

    def prep_cam(f):
        cam = f[C[0]:C[1], C[2]:C[3]]
        sc = max(cw / cam.shape[1], ch / cam.shape[0])
        cam = cv2.resize(cam, (int(round(cam.shape[1] * sc)), int(round(cam.shape[0] * sc))), interpolation=cv2.INTER_AREA)
        ox, oy = (cam.shape[1] - cw) // 2, (cam.shape[0] - ch) // 2
        return grade_cam(cam[oy:oy + ch, ox:ox + cw], GRADE)

    def layout(f):
        out = BG.copy()
        out[BAND:BAND + GH] = grade_game(f[G0:G1], GRADE)
        out[BAND - 5:BAND] = LINE; out[BAND + GH:BAND + GH + 4] = LINE[:4]
        return out

    need = {int(round(s * SFPS)) for s, *_ in seq}
    camneed = set(cam_src)
    store, cams, k, last = {}, {}, 0, 0
    SW, SH = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                      "stream=width,height", "-of", "csv=p=0", SRC], capture_output=True,
                                     text=True).stdout.strip().split(","))
    d = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    while True:
        b = d.stdout.read(SW * SH * 3)
        if len(b) < SW * SH * 3:
            break
        if k in need or k in camneed:
            f = np.frombuffer(b, np.uint8).reshape(SH, SW, 3)
            if k in need:
                store[k] = cv2.imencode(".jpg", layout(f), [cv2.IMWRITE_JPEG_QUALITY, 96])[1]; last = k
            if k in camneed:
                cams[k] = cv2.imencode(".jpg", prep_cam(f), [cv2.IMWRITE_JPEG_QUALITY, 95])[1]
        k += 1
    d.wait()

    def card(f, i):
        ki = cam_src[i]
        while ki not in cams:
            ki -= 1
        cam = cv2.imdecode(cams[ki], cv2.IMREAD_COLOR).astype(np.float32)
        reg = f[cy:cy + ch, cx:cx + cw].astype(np.float32)
        f[cy:cy + ch, cx:cx + cw] = (cam * MASK + reg * (1 - MASK)).astype(np.uint8)

    def get(s):
        i = min(int(round(s * SFPS)), last)
        while i not in store:
            i -= 1
        return cv2.imdecode(store[i], cv2.IMREAD_COLOR)

    _F = {}

    def font(sz):
        if sz not in _F:
            _F[sz] = ImageFont.truetype(sp.get("font", FONT), sz)
        return _F[sz]

    def text(img, cxx, cyy, s, sz, col, scale=1.0, alpha=1.0):
        sz = int(sz * scale); f = font(sz); dd = ImageDraw.Draw(img)
        while dd.textlength(s, font=f) > W - 70:
            sz -= 4; f = font(sz)
        tw = dd.textlength(s, font=f); x0, y0 = cxx - tw / 2, cyy - sz * 0.62
        st = max(6, sz // 11); A = int(255 * alpha)
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        dl.text((x0 + 5, y0 + 7), s, font=f, fill=(0, 0, 0, A * 160 // 255), stroke_width=st, stroke_fill=(0, 0, 0, A * 160 // 255))
        dl.text((x0, y0), s, font=f, fill=col + (A,), stroke_width=st, stroke_fill=(0, 0, 0, A))
        img.alpha_composite(lay)

    def chip(img, cyy, parts, alpha):
        dl = ImageDraw.Draw(img); f = font(40)
        tw = sum(dl.textlength(p, font=f) for p, _ in parts); x0 = W / 2 - tw / 2
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(lay); A = int(255 * alpha)
        d2.rounded_rectangle([x0 - 22, cyy - 30, x0 + tw + 22, cyy + 30], radius=14,
                             fill=(10, 8, 16, A * 215 // 255), outline=ACC2 + (A,), width=3)
        x = x0
        for p, c in parts:
            d2.text((x, cyy - 24), p, font=f, fill=COL[c] + (A,)); x += d2.textlength(p, font=f)
        img.alpha_composite(lay)

    def pop(tt, t0):
        u = (tt - t0) / 0.14
        return 1.0 if u >= 1 else 1.3 - 0.3 * (1 - (1 - max(u, 0)) ** 3)

    HL = [(T(h["at"]), T(h["at"]) + h["dur"] if "dur" in h else T(h["until"]), h["lines"]) for h in sp.get("headlines", [])]
    CH = [(T(c["at"]), T(c["at"]) + c["dur"], c["parts"]) for c in sp.get("chips", [])]
    FL = [T(v) for v in sp.get("flash", [])]
    SK = [T(v) for v in sp.get("shake", [])]
    YS = {1: [BAND * 0.6], 2: [BAND * 0.42, BAND * 0.78]}

    tmpv = OUT + ".v.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "13", "-preset", "medium",
                            "-pix_fmt", "yuv420p", tmpv], stdin=subprocess.PIPE)
    for i, (s, kind, u, si) in enumerate(seq):
        tt = i / FPS
        f = get(s).copy()
        card(f, i)
        if kind == "rewind":
            sh_ = int(10 + 14 * np.sin(np.pi * u))
            g_ = f.copy(); g_[..., 2] = np.roll(f[..., 2], sh_, 1); g_[..., 0] = np.roll(f[..., 0], -sh_, 1)
            g_[::4] = (g_[::4] * 0.72).astype(np.uint8); f = g_
        if (kind == "freeze" and u < 0.08) or any(abs(tt - x) < 0.05 for x in FL):
            f = cv2.addWeighted(f, 0.62, np.full_like(f, 255), 0.38, 0)
        for x in SK:
            if 0 <= tt - x < 0.22:
                a = 15 * (1 - (tt - x) / 0.22) * (1 if i % 2 else -1)
                f = cv2.warpAffine(f, np.float32([[1, 0, a], [0, 1, -a * 0.6]]), (W, H), borderMode=cv2.BORDER_REFLECT)
        img = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA")
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        dl.rounded_rectangle([cx - 3, cy - 3, cx + cw + 2, cy + ch + 2], radius=32, outline=CARD + (255,), width=5)
        lab = sp.get("card_label", "")
        if lab:
            lw = dl.textlength(lab, font=font(30))
            dl.rounded_rectangle([cx + 18, cy + 18, cx + 46 + lw, cy + 60], radius=8, fill=(10, 8, 16, 220))
            dl.text((cx + 32, cy + 22), lab, font=font(30), fill=ACC2 + (255,))
        img.alpha_composite(lay)
        for t0, t1, parts in CH:
            if t0 <= tt < t1:
                chip(img, STRIP, parts, min(1, (t1 - tt) / 0.12, (tt - t0) / 0.08))
        for t0, t1, lines in HL:
            if t0 <= tt < t1:
                al = min(1, (t1 - tt) / 0.12)
                for j, ((s_, c_, sz), y) in enumerate(zip(lines, YS[len(lines)])):
                    if tt >= t0 + 0.1 * j:
                        text(img, W / 2, y, s_, sz, COL[c_], pop(tt, t0 + 0.1 * j), al)
        enc.stdin.write(np.asarray(img.convert("RGB")).tobytes())
    enc.stdin.close(); enc.wait()

    # ---- ses ----
    SR = sd.SR
    work = tempfile.mkdtemp(prefix="esp_")
    raw = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                                       capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
    parts = []
    for i, (t0, t1, p, kind) in enumerate(segt):
        n = int(round(t1 * SR)) - int(round(t0 * SR))
        if kind == "play":
            s0, s1 = p["src"]; spd = p.get("speed", 1.0)
            fi, fo = f"{work}/i{i}.f32", f"{work}/o{i}.f32"
            raw[int(s0 * SR):int(s1 * SR)].tofile(fi)
            af = f"atempo={spd}" if spd >= 1 else f"rubberband=tempo={spd}:pitch=0.85"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", fi,
                            "-af", af, "-f", "f32le", fo], check=True)
            y = np.fromfile(fo, np.float32).reshape(-1, 2)
            y = np.pad(y, ((0, max(0, n - len(y))), (0, 0)))[:n]
            rr = int(0.012 * SR); ramp = np.linspace(0, 1, rr)[:, None]
            y[:rr] *= ramp; y[-rr:] *= ramp[::-1]
        else:
            y = np.zeros((n, 2), np.float32)
        parts.append(y)
    game = np.concatenate(parts); N = len(game)
    bus = np.zeros(N); vox = np.zeros(N); duck = np.ones(N)

    def place(buf, sig, t_, g_):
        a = int(t_ * SR); b = min(N, a + len(sig))
        if 0 <= a < N:
            buf[a:b] += sig[:b - a] / (np.max(np.abs(sig)) + 1e-9) * g_

    fx = sp.get("sfx", {})
    for v in fx.get("boom", []): place(bus, sd.boom(), T(v), 1.0)
    for v in fx.get("clink", []): place(bus, sd.clink(), T(v), 0.55)
    for v in fx.get("pop", []): place(bus, sd.pop(1.0), T(v), 0.33)
    for v, dd in fx.get("rewind", []): place(bus, sd.rewind(dd), T(v), 0.5)
    for j, vo in enumerate(sp.get("voice", [])):
        wv = f"{work}/vo{j}.wav"
        tts = sp.get("tts", {})
        if tts.get("engine") == "kokoro":
            raw_v = f"{work}/vo{j}_raw.wav"
            subprocess.run([tts["python"], "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tts_kokoro.py"),
                            tts["dir"], vo.get("voice", tts.get("voice", "am_michael")),
                            str(vo.get("speed", tts.get("speed", 1.05))), raw_v, vo["text"]],
                           check=True, capture_output=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw_v, "-af",
                            "highpass=f=70,equalizer=f=3500:t=q:w=1:g=3,"
                            "acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=1.6",
                            "-ar", str(SR), "-ac", "1", wv], check=True)
        else:
            txt = vo["text"].replace("'", "")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"flite=text='{txt}':voice={vo.get('voice', 'rms')}",
                            "-af", "asetrate=16000*0.92,aresample=44100,atempo=1.0869,highpass=f=120,"
                                   "acompressor=threshold=-20dB:ratio=4:attack=5:release=60,aecho=0.8:0.5:40|75:0.25|0.15,"
                                   "volume=2.0", "-ar", str(SR), "-ac", "1", wv], check=True)
        x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", wv, "-f", "f32le", "-"],
                                         capture_output=True).stdout, np.float32)
        a = int(T(vo["at"]) * SR); place(vox, x, T(vo["at"]), 0.95)
        b = min(N, a + len(x)); g = 10 ** (sp.get("duck_db", -9) / 20)
        duck[max(0, a - 2000):b + 4000] = np.minimum(duck[max(0, a - 2000):b + 4000], g)
    duck = np.convolve(duck, np.ones(1500) / 1500, mode="same")
    mix = game * 0.9 * duck[:, None] + bus[:, None] * 0.7 + vox[:, None] * 0.9
    mix.astype(np.float32).tofile(f"{work}/mix.f32")
    tmpa = OUT + ".a.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", f"{work}/mix.f32",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", tmpa], check=True)

    # ---- 2 geçiş, hedef boyut ----
    mb = sp.get("target_mb", 29)
    vk = int(min(15000, (mb * 8 * 1024 / DUR) - 200))
    pl = f"{work}/pass"
    common = ["-c:v", "libx264", "-preset", "slow", "-b:v", f"{vk}k", "-maxrate", f"{int(vk * 1.4)}k",
              "-bufsize", f"{vk * 2}k", "-passlogfile", pl]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmpv, *common, "-pass", "1", "-an", "-f", "null", "/dev/null"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmpv, "-i", tmpa, "-map", "0:v", "-map", "1:a", *common,
                    "-pass", "2", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", OUT], check=True)
    os.remove(tmpv); os.remove(tmpa)
    print(f"{OUT}: {os.path.getsize(OUT) / 1e6:.1f} MB, {DUR:.2f} sn")


if __name__ == "__main__":
    main()
