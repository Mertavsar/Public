#!/usr/bin/env python3
"""Mjolnir reklam filmi - hareketli kurgu.

Tek bir urun gorselinden 15 sn'lik reklam videosu uretir:
sanal kamera hareketleri (push-in, tilt, pull-out), simsek parlamalari,
metal uzerinde isik suzulmesi, kamera sarsintisi, grain, vignette,
animasyonlu metinler ve CTA.

Yakin planlarda posterin grafik katmani gorunmesin diye 'temiz plaka'
kullanilir; kamera geri cekilirken baslik ve ikonlar sirayla belirir.

Kullanim:
  python3 make_video.py <kaynak.jpg> <cikis.mp4> [--clean clean.png]
                        [--ar 9:16|4:5|1:1] [--audio ses.wav]
"""
import argparse
import math
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import imageio_ffmpeg
from boxes import REVEAL_ELEMENTS

try:
    import cv2
    from parallax import ParallaxRig
except ImportError:
    cv2 = ParallaxRig = None

FPS = 30
DUR = 15.0

SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# poster ogelerinin belirme zamanlari (ses efektleriyle hizali)
REVEALS = {
    "title": (8.50, 9.15),
    "icon1": (8.75, 9.10),
    "icon2": (9.25, 9.60),
    "icon3": (9.75, 10.10),
    "icon4": (10.25, 10.60),
    "kicker": (9.05, 9.70),
}


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_io(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def lerp(a, b, k):
    return a + (b - a) * k


# ------------------------------------------------------------------ metin
def text_img(text, font, tracking=0, fill=(255, 255, 255), pad=48):
    dummy = Image.new("RGBA", (1, 1))
    d = ImageDraw.Draw(dummy)
    widths, height = [], 0
    for ch in text:
        bb = d.textbbox((0, 0), ch, font=font)
        widths.append(bb[2] - bb[0] if ch != " " else font.size * 0.32)
        height = max(height, bb[3])
    total = int(sum(widths) + tracking * (len(text) - 1)) + pad * 2
    img = Image.new("RGBA", (total, int(height) + pad * 2), (0, 0, 0, 0))
    dd = ImageDraw.Draw(img)
    x = float(pad)
    for ch, w in zip(text, widths):
        if ch != " ":
            dd.text((x, pad), ch, font=font, fill=fill + (255,))
        x += w + tracking
    return img


def scrim_band(base, W, cy, h, alpha, strength=205):
    """Metnin arkasina tam genislikte, kenarlari yumusak koyu serit."""
    if alpha <= 0.004 or h < 4:
        return
    y0 = int(cy - h / 2)
    prof = np.exp(-(np.linspace(-1, 1, h) ** 2) * 3.0) * alpha * strength
    arr = np.zeros((h, W, 4), np.uint8)
    arr[:, :, :3] = 8
    arr[:, :, 3] = np.clip(prof, 0, 255).astype(np.uint8)[:, None]
    band = Image.fromarray(arr, "RGBA")
    if y0 < 0:
        band = band.crop((0, -y0, W, h)); y0 = 0
    if y0 + band.height > base.height:
        band = band.crop((0, 0, W, base.height - y0))
    if band.height > 0:
        base.alpha_composite(band, (0, y0))


def paste_soft(base, layer, cx, cy, alpha, dy=0, glow=0.5, shadow=0.75):
    """Metni golge + isik halesiyle yerlestirir."""
    if alpha <= 0.004:
        return
    w, h = layer.size
    x, y = int(cx - w / 2), int(cy - h / 2 + dy)

    if shadow > 0:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sh.paste((0, 0, 0, 255), (0, 0, w, h), layer.split()[3])
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        sh.putalpha(sh.split()[3].point(lambda v: int(v * alpha * shadow)))
        base.alpha_composite(sh, (x, y + 3))

    if glow > 0:
        g = layer.filter(ImageFilter.GaussianBlur(13))
        g.putalpha(g.split()[3].point(lambda v: int(v * alpha * glow)))
        base.alpha_composite(g, (x, y))

    lay = layer.copy()
    lay.putalpha(lay.split()[3].point(lambda v: int(v * alpha)))
    base.alpha_composite(lay, (x, y))


# ------------------------------------------------------------------ kurgu
def build_timeline(ar_key, aspect, SW=1024, SH=1536):
    """Sanal kamera: (cx, cy, viewW) kaynak gorsel koordinatlarinda.

    Son kadrajda posterin tamami gorunmeli; bunun icin gereken genislik
    en boy oranina gore degisir (dar oranlarda yukseklik, genis oranlarda
    genislik belirleyicidir)."""
    z = {"9:16": 1.00, "4:5": 1.12, "1:1": 1.22}[ar_key]
    full = max(float(SW), SH * aspect)          # tum posteri kapsayan genislik
    return [
        (0.00, 2.60, 430, 342, 352 * z, 434, 352, 300 * z, "io"),
        (2.60, 5.60, 516, 452, 636 * z, 560, 436, 566 * z, "out"),
        (5.60, 8.20, 500, 828, 452 * z, 514, 1204, 430 * z, "io"),
        (8.20, 11.20, 520, 716, 648 * z, 512, 768, full, "io"),
        (11.20, 15.00, 512, 768, full, 512, 762, full * 0.965, "io"),
    ]


def camera(t, shots):
    for (t0, t1, cx0, cy0, vw0, cx1, cy1, vw1, es) in shots:
        if t0 <= t < t1:
            k = clamp((t - t0) / (t1 - t0))
            k = ease_io(k) if es == "io" else ease_out(k)
            return lerp(cx0, cx1, k), lerp(cy0, cy1, k), lerp(vw0, vw1, k)
    s = shots[-1]
    return s[5], s[6], s[7]


LIGHTNING = [(0.16, 1.00, 0.10), (0.26, 0.50, 0.07), (1.00, 1.00, 0.13),
             (1.12, 0.48, 0.07), (1.88, 0.80, 0.12)]
IMPACT_FLASH = [(2.60, 0.75, 0.15), (5.60, 0.32, 0.10), (8.20, 0.38, 0.11),
                (11.20, 0.68, 0.19)]
SHAKES = [(2.60, 14.0, 0.42), (5.60, 7.0, 0.28), (8.20, 8.0, 0.30), (11.20, 12.0, 0.46)]
SWEEPS = [(3.10, 4.70, 0.46), (12.20, 13.80, 0.22)]

# Parallaks kamera yolu: (t0, t1, ox0, oy0, ox1, oy1)
# ox/oy -1..1 arasi; en yakin katman PAR_AMP px kadar kayar.
PARALLAX = [
    (0.00, 2.60, -0.80, 0.30, -0.15, 0.05),
    (2.60, 5.60, -0.25, -0.05, 0.92, -0.22),
    (5.60, 8.20, 0.92, -0.22, 0.12, 0.38),
    (8.20, 11.20, 0.12, 0.38, -0.42, -0.06),
    (11.20, 15.00, -0.42, -0.06, 0.38, 0.12),
]
PAR_AMP = 30.0      # kaynak piksel cinsinden en yakin katmanin kaymasi
ROT_AMP = 0.32      # on planin derece cinsinden salinimi


def parallax_at(t):
    for (t0, t1, ox0, oy0, ox1, oy1) in PARALLAX:
        if t0 <= t < t1:
            k = ease_io((t - t0) / (t1 - t0))
            return lerp(ox0, ox1, k), lerp(oy0, oy1, k)
    return PARALLAX[-1][4], PARALLAX[-1][5]


def make_dust(n=54, seed=5):
    rng = np.random.default_rng(seed)
    return np.stack([rng.uniform(-0.1, 1.1, n), rng.uniform(-0.1, 1.1, n),
                     rng.uniform(0.25, 1.0, n), rng.uniform(1.0, 3.4, n),
                     rng.uniform(0.3, 1.0, n), rng.uniform(0, 6.283, n)], 1).astype(np.float32)


def dust_layer(W, H, t, ox, oy, parts, amp=52.0):
    """Derinlige oturan toz zerrecikleri: kamerayla birlikte kayarlar,
    bu yuzden bazilari cekicin onunde bazilari arkasindaymis gibi okunur."""
    lay = np.zeros((H, W), np.float32)
    for (fx, fy, d, sz, br, ph) in parts:
        x = fx * W + ox * amp * d + math.sin(t * 0.37 + ph) * 16.0 * d
        y = ((fy - t * 0.013 * d) % 1.2 - 0.1) * H + oy * amp * d
        if not (-30 <= x < W + 30 and -30 <= y < H + 30):
            continue
        a = br * (0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 2.1 + ph))) * (0.3 + 0.7 * d)
        cv2.circle(lay, (int(x), int(y)), max(int(sz * (0.7 + d) * H / 1920), 1),
                   float(a), -1, cv2.LINE_AA)
    return cv2.GaussianBlur(lay, (0, 0), max(H / 700.0, 1.0))


def flash_amount(t):
    v = 0.0
    for at, amp, dec in LIGHTNING + IMPACT_FLASH:
        if at <= t < at + dec * 5:
            v += amp * math.exp(-(t - at) / dec)
    return min(v, 1.4)


def shake_offset(t):
    dx = dy = 0.0
    for at, amp, dec in SHAKES:
        if at <= t < at + dec * 3:
            e = amp * math.exp(-(t - at) / dec)
            dx += e * math.sin((t - at) * 61.0)
            dy += e * math.sin((t - at) * 47.0 + 1.7)
    return dx, dy


def exposure(t):
    return float(np.interp(
        t, [0.00, 0.14, 0.18, 0.92, 1.02, 1.82, 1.94, 2.45, 2.60, 3.30],
        [0.07, 0.07, 0.24, 0.13, 0.32, 0.20, 0.52, 0.60, 0.94, 0.98]))


def grade(t):
    k = clamp((t - 2.2) / 2.0)
    return lerp(0.78, 1.035, k), lerp(0.89, 1.000, k), lerp(1.26, 0.965, k)


# ------------------------------------------------------------------ ana render
def render(src_path, out_path, ar_key, size, clean_path=None, fps=FPS, dur=DUR,
           audio=None, cta="HEMEN SİPARİŞ VER", kicker="KOLEKSİYONA EKLE",
           depth_path=None, plate_path=None):
    W, H = size
    shots = build_timeline(ar_key, W / H)
    aspect = W / H

    orig = Image.open(src_path).convert("RGB")
    SW, SH = orig.size
    clean = Image.open(clean_path).convert("RGB") if clean_path else orig
    orig_a = np.asarray(orig, np.float32)
    clean_a = np.asarray(clean, np.float32)

    # kadraj tasmalarinda gorunen bulanik zemin
    bs = max(W / SW, H / SH) * 1.25
    bg = orig.resize((int(SW * bs), int(SH * bs)), Image.LANCZOS)
    bx, by = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((bx, by, bx + W, by + H)).filter(ImageFilter.GaussianBlur(52))
    bg = Image.fromarray(np.clip(np.asarray(bg, np.float32) * 0.28, 0, 255).astype(np.uint8))

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx, ny = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
    rad = np.sqrt(nx ** 2 + ny ** 2 * 0.82)
    vig = np.clip(1.06 - 0.48 * np.clip(rad - 0.34, 0, None) ** 1.5, 0.28, 1.06)[..., None]

    ang = math.radians(-58)
    proj = (xx * math.cos(ang) + yy * math.sin(ang)).astype(np.float32)
    pmin, pmax = proj.min(), proj.max()
    del xx, yy, nx, ny, rad

    s = H / 1920.0
    f_hook = ImageFont.truetype(SANS, max(int(60 * s), 12))
    f_sub = ImageFont.truetype(SANS_B, max(int(37 * s), 10))
    f_cta = ImageFont.truetype(SANS_B, max(int(46 * s), 12))
    f_kick = ImageFont.truetype(SANS_B, max(int(27 * s), 9))

    t_hook1 = text_img("EFSANENİN GÜCÜ", f_hook, int(13 * s))
    t_hook2 = text_img("ŞİMDİ SENİN ELİNDE", f_hook, int(13 * s))
    t_lab1 = text_img("DETAYLI İŞÇİLİK", f_sub, int(11 * s))
    t_lab2 = text_img("RAHAT TUTUŞ", f_sub, int(11 * s))
    t_kick = text_img(kicker, f_kick, int(10 * s), fill=(226, 214, 190))
    t_cta = text_img(cta, f_cta, int(7 * s), fill=(18, 16, 14))

    # CTA blogunun dikey yerlesimi: dar oranlarda daha asagida dursun ki
    # posterin ikon sutunu kapanmasin
    cta_pos = {"9:16": (0.645, 0.735, 0.775),
               "4:5": (0.705, 0.800, 0.845),
               "1:1": (0.680, 0.785, 0.835)}[ar_key]
    scrim_top_f, kick_f, btn_f = cta_pos

    # ---------------- 2.5B parallaks tertibati
    rig = None
    if depth_path and plate_path and ParallaxRig is not None:
        depth = cv2.imread(depth_path, 0)
        plate_rgb = cv2.cvtColor(cv2.imread(plate_path), cv2.COLOR_BGR2RGB)
        rig = ParallaxRig(np.asarray(clean, np.uint8), depth, plate_rgb)
        plate_a = plate_rgb.astype(np.float32)
        print(f"  parallaks: {len(rig.layers)} katman")
    dust = make_dust() if rig is not None else None

    elem = {n: (x0, y0, x1, y1) for n, x0, y0, x1, y1 in REVEAL_ELEMENTS}
    reveal_start = min(a for a, _ in REVEALS.values())
    reveal_end = max(b for _, b in REVEALS.values())

    nframes = int(round(fps * dur))
    rng = np.random.default_rng(3)
    gw, gh = W // 4, H // 4

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
    if audio:
        cmd += ["-i", audio]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-level", "4.1", "-movflags", "+faststart", "-r", str(fps)]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest"]
    cmd += [out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    full_a = orig_a if rig is None else None
    if rig is not None:
        full_a = plate_a.copy()
        for name, (x0, y0, x1, y1) in elem.items():
            full_a[y0:y1, x0:x1] = orig_a[y0:y1, x0:x1]
    full_set = False

    for i in range(nframes):
        t = i / fps

        # ---- kaynak kare: poster ogelerinin sirali belirmesi
        # (baslik ve ikonlar duvar duzlemindedir, yani en arka katmana yazilir)
        base_a = plate_a if rig is not None else clean_a
        if t < reveal_start:
            src_arr, changed = base_a, (i == 0)
        elif t >= reveal_end:
            src_arr, changed = full_a, not full_set
            full_set = True
        else:
            src_arr = base_a.copy()
            for name, (r0, r1) in REVEALS.items():
                al = ease_io((t - r0) / (r1 - r0))
                if al <= 0.001:
                    continue
                x0, y0, x1, y1 = elem[name]
                if al >= 0.999:
                    src_arr[y0:y1, x0:x1] = orig_a[y0:y1, x0:x1]
                else:
                    src_arr[y0:y1, x0:x1] = (base_a[y0:y1, x0:x1] * (1 - al)
                                             + orig_a[y0:y1, x0:x1] * al)
            changed, full_set = True, False

        cx, cy, vw = camera(t, shots)
        sdx, sdy = shake_offset(t)
        cx += sdx * vw / 90.0
        cy += sdy * vw / 90.0
        vh = vw / aspect
        scale = W / vw

        if rig is not None:
            if changed:
                rig.set_background(src_arr)
            pox, poy = parallax_at(t)
            pamp = PAR_AMP * float(np.clip((vw / 700.0) ** 0.75, 0.30, 1.25))
            par_rgb, par_disp = rig.render(
                pox, poy, pamp, zoom=0.012 * pox,
                rot_deg=ROT_AMP * math.sin(t * 0.55 + 0.4))
            plate = Image.fromarray(np.clip(par_rgb, 0, 255).astype(np.uint8))
            disp_img = Image.fromarray(
                (np.clip(par_disp[..., 0], 0, 1) * 255).astype(np.uint8), "L")
        else:
            plate = Image.fromarray(np.clip(src_arr, 0, 255).astype(np.uint8))
            disp_img = None

        coeffs = (1.0 / scale, 0, cx - vw / 2, 0, 1.0 / scale, cy - vh / 2)
        frame = plate.transform(
            (W, H), Image.AFFINE, coeffs,
            resample=Image.BICUBIC, fillcolor=(0, 0, 0))
        metal = None
        if disp_img is not None:
            metal = np.asarray(disp_img.transform(
                (W, H), Image.AFFINE, coeffs,
                resample=Image.BILINEAR, fillcolor=0), np.float32) / 255.0

        ox0 = (0 - (cx - vw / 2)) * scale
        oy0 = (0 - (cy - vh / 2)) * scale
        ox1, oy1 = ox0 + SW * scale, oy0 + SH * scale
        if ox0 > 0.5 or oy0 > 0.5 or ox1 < W - 0.5 or oy1 < H - 0.5:
            rect = (max(0, int(math.ceil(ox0))), max(0, int(math.ceil(oy0))),
                    min(W, int(ox1)), min(H, int(oy1)))
            base = bg.copy()
            if rect[2] > rect[0] and rect[3] > rect[1]:
                base.paste(frame.crop(rect), rect[:2])
            frame = base

        a = np.asarray(frame, np.float32)

        gr, gg, gb = grade(t)
        a = a * exposure(t) * np.array([gr, gg, gb], np.float32) * vig

        n = np.clip(a, 0, 255) / 255.0
        n = n * n * (3 - 2 * n) * 0.32 + n * 0.68          # hafif S egrisi
        sh = np.clip((n - 0.72) / 0.28, 0, 1)
        a = (n - 0.18 * sh * sh * (n - 0.72)) * 255.0      # highlight yumusatma

        # metale oturan parlama: disparite haritasi sayesinde isik yalnizca
        # cekicin uzerinden gecer, duvarda sadece zayif bir iz birakir
        spec = 1.0
        if metal is not None:
            spec = 0.30 + 1.70 * np.clip((metal - 0.50) / 0.38, 0, 1)
        warm = np.array([1.0, 0.98, 0.92], np.float32)
        lum = None
        for s0, s1, amp in SWEEPS:
            if s0 <= t < s1:
                k = (t - s0) / (s1 - s0)
                pos = pmin + (pmax - pmin) * (k * 1.25 - 0.12)
                band = np.exp(-((proj - pos) / (W * 0.085)) ** 2) * amp
                if lum is None:
                    lum = a.mean(axis=2, keepdims=True) / 255.0
                a += (band * spec)[..., None] * (55 + 175 * lum ** 1.6) * warm

        # surekli, cok yavas gezen isik sutunu - sahneye canlilik verir
        if metal is not None:
            pos = pmin + (pmax - pmin) * (0.5 + 0.62 * math.sin(t * 0.42 - 0.8))
            band = np.exp(-((proj - pos) / (W * 0.16)) ** 2) * 0.11
            if lum is None:
                lum = a.mean(axis=2, keepdims=True) / 255.0
            a += (band * spec)[..., None] * (40 + 120 * lum ** 1.6) * warm

        fl = flash_amount(t)
        if fl > 0.004:
            tint = (np.array([0.86, 0.93, 1.0], np.float32) if t < 2.5
                    else np.array([1.0, 0.97, 0.90], np.float32))
            a = a * (1 + 0.75 * fl) + 95.0 * fl * tint

        # derinlige oturan toz
        if dust is not None:
            dl = dust_layer(W, H, t, pox, poy, dust)
            a += dl[..., None] * np.array([190.0, 178.0, 156.0], np.float32) * \
                (0.55 if t < 2.6 else 1.0)

        gs = 8.0 if t < 2.6 else 4.5
        gn = rng.normal(0, gs, (gh, gw)).astype(np.float32)
        gn = np.asarray(Image.fromarray(gn, mode="F").resize((W, H), Image.BILINEAR))
        a += gn[..., None]

        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")

        # ---------------- metin katmani
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        def seg(t0, t1, fade=0.30):
            if t < t0 or t >= t1:
                return 0.0, 0.0
            al = ease_out((t - t0) / fade)
            if t > t1 - fade:
                al *= 1 - ease_io((t - (t1 - fade)) / fade)
            return clamp(al), (1 - ease_out((t - t0) / fade)) * 26 * s

        for (a0, a1, fade, layer, ypos, bh) in (
                (1.00, 2.55, 0.30, t_hook1, 0.285, 3.1),
                (2.80, 4.40, 0.30, t_hook2, 0.285, 3.1),
                (4.55, 5.52, 0.25, t_lab1, 0.805, 3.4),
                (6.05, 7.90, 0.30, t_lab2, 0.205, 3.4)):
            al, dy = seg(a0, a1, fade)
            if al > 0.004:
                th = layer.size[1] - 2 * 48
                scrim_band(ov, W, H * ypos + dy * 0.5, int(th * bh), al * 0.95)
                paste_soft(ov, layer, W / 2, H * ypos, al, dy)

        # ---------------- CTA
        if t >= 11.35:
            ca = ease_out((t - 11.35) / 0.55)
            top = int(H * scrim_top_f)
            grad = np.zeros((H, W, 4), np.uint8)
            col = np.clip(np.linspace(0, 1, H - top) * 1.9, 0, 1) * 215 * ca
            grad[top:, :, 3] = col[:, None].astype(np.uint8)
            grad[top:, :, :3] = np.array([6, 6, 8], np.uint8)
            ov.alpha_composite(Image.fromarray(grad, "RGBA"))

            paste_soft(ov, t_kick, W / 2, H * kick_f, ca * 0.95, (1 - ca) * 16 * s, glow=0.3, shadow=0.9)

            bw, bh = int(W * 0.70), int(112 * s)
            by0 = int(H * btn_f)
            pulse = 1.0 + 0.035 * math.sin((t - 11.35) * 4.2)
            pw, ph = int(bw * pulse), int(bh * pulse)
            px0, py0 = int(W / 2 - pw / 2), int(by0 + bh / 2 - ph / 2)
            btn = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(btn).rounded_rectangle(
                [px0, py0, px0 + pw, py0 + ph], radius=int(10 * s),
                fill=(226, 214, 192, int(245 * ca)))
            glow = btn.filter(ImageFilter.GaussianBlur(max(int(20 * s), 4)))
            glow.putalpha(glow.split()[3].point(lambda v: int(v * 0.45 * ca)))
            ov.alpha_composite(glow)
            ov.alpha_composite(btn)
            paste_soft(ov, t_cta, W / 2, py0 + ph / 2, ca, 0, glow=0.0, shadow=0.0)

        img.alpha_composite(ov)
        proc.stdin.write(img.convert("RGB").tobytes())

        if i % 90 == 0:
            print(f"  {i:3d}/{nframes}  t={t:5.2f}s", flush=True)

    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg hatasi")
    print(f"OK -> {out_path}")


SIZES = {"9:16": (1080, 1920), "4:5": (1080, 1350), "1:1": (1080, 1080)}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--clean", default=None)
    ap.add_argument("--ar", default="9:16", choices=list(SIZES))
    ap.add_argument("--audio", default=None)
    ap.add_argument("--cta", default="HEMEN SİPARİŞ VER")
    ap.add_argument("--kicker", default="KOLEKSİYONA EKLE")
    ap.add_argument("--depth", default=None)
    ap.add_argument("--plate", default=None)
    ap.add_argument("--fps", type=int, default=FPS)
    a = ap.parse_args()
    render(a.src, a.out, a.ar, SIZES[a.ar], clean_path=a.clean, fps=a.fps,
           audio=a.audio, cta=a.cta, kicker=a.kicker,
           depth_path=a.depth, plate_path=a.plate)
