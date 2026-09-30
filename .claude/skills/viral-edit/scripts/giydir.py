#!/usr/bin/env python3
"""
Kaynaktaki yazı kutusunu SİLMEDEN üstüne kendi kutumuzu giydirir + kısa
altyazı parçaları + büyük vurgu yazıları. Çıktı saydam katman (mov/png).

Neden: ProPainter ile beyaz kutu silmek CPU'da saatler sürdü (ambergris).
Kullanıcı: "yazıların üzerine giydirebilirsin". Kutu kaynakta konum
değiştiriyor (kaplumbağa klibinde 8 konum) — konum kare kare ölçülür
(boxtrack.json: kaynak karesi başına [y0,y1,x0,x1]) ve kurgudaki her karenin
hangi kaynak karesinden geldiği (srcmap) ile eşlenir.

spec:
{
 "duration": 40.0, "fps": 30,
 "srcmap": "srcmap.json",        // çıktı karesi -> kaynak karesi (-1: kutu yok)
 "boxtrack": "boxtrack.json",
 "cards": [{"t0":0,"t1":2.1,"text":"SADECE BİR TANEYDİ…","color":"yellow"}],
 "big":   [{"t0":5.2,"t1":6.4,"text":"BİTMEMİŞTİ.","y":0.45}],
 "captions": "captions.json",    // kelime zamanları (sentalign çıktısı)
 "cap_y": 0.70, "cap_size": 84, "chunk_words": 4, "chunk_chars": 22,
 "emphasis": ["bitmemişti", "koca"]
}
Altyazı tam cümle değil: 2–4 kelimelik parçalar, konuşulan kelime sarı.
"""
import argparse, json, math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overlay import load_font, stroked_text

WHITE = (255, 255, 255, 255)
YELLOW = (255, 214, 0, 255)
RED = (235, 40, 40, 255)
BLACK = (0, 0, 0, 255)
COL = {"white": WHITE, "yellow": YELLOW, "red": RED}


def chunks(words, max_w, max_c):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        txt = " ".join(words[j]["w"] for j in cur)
        end = re.search(r"[.,…!?]$", w["w"]) is not None
        nxt = words[i + 1]["w"] if i + 1 < len(words) else ""
        if end or len(cur) >= max_w or len(txt) + 1 + len(nxt) > max_c:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def fit_font(d, text, maxw, size):
    while size > 30:
        f = load_font(size)
        if d.textlength(text, font=f) <= maxw:
            return f
        size -= 4
    return load_font(size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--layer", choices=["all", "cards", "text"], default="all",
                    help="cards: yalnız kutu (geçişlerden ÖNCE görüntüye işlenir — zoom "
                         "anında alttaki yazı açılmasın); text: altyazı + büyük yazı")
    a = ap.parse_args()
    sp = json.load(open(a.spec, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(a.spec))
    P = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    W, H, fps = 1080, 1920, sp.get("fps", 30)
    n = int(round(sp["duration"] * fps))
    if sp.get("boxmap"):                      # cutter.py çıktısı: kare başına kutu
        boxmap = json.load(open(P(sp["boxmap"])))
    else:
        srcmap = json.load(open(P(sp["srcmap"])))
        track = json.load(open(P(sp["boxtrack"])))
        boxmap = [track[min(s_, len(track) - 1)] if s_ >= 0 else None for s_ in srcmap]
    cards, bigs = sp.get("cards", []), sp.get("big", [])
    caps = json.load(open(P(sp["captions"]), encoding="utf-8")) if sp.get("captions") else []
    emph = {e.lower() for e in sp.get("emphasis", [])}
    ch = chunks(caps, sp.get("chunk_words", 4), sp.get("chunk_chars", 22))
    spans = []
    for k, c in enumerate(ch):
        s = caps[c[0]]["s"]
        e = caps[ch[k + 1][0]]["s"] if k + 1 < len(ch) else caps[c[-1]]["e"] + 0.4
        spans.append((s, e, c))
    cap_y, cap_size = sp.get("cap_y", 0.70) * H, sp.get("cap_size", 84)

    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
                          "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "png", a.out],
                         stdin=subprocess.PIPE)
    for i in range(n):
        t = i / fps
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # ---- kutu giydirme ----
        bx = boxmap[i] if i < len(boxmap) else None
        if bx and a.layer != "text":
            y0, y1, x0, x1 = bx
            x0, x1 = max(0, x0), min(W, x1)
            d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=(12, 12, 12, 255),
                                outline=YELLOW, width=5)
            act = [c for c in cards if c["t0"] <= t < c["t1"]]
            if act:
                c = act[-1]
                age = t - c["t0"]
                m = 1.0 + 0.10 * math.exp(-age / 0.06)        # beliriş vuruşu
                f = fit_font(d, c["text"], (x1 - x0) - 60, int(round(min(78, (y1 - y0) * 0.62) * m)))
                d.text(((x0 + x1) / 2, (y0 + y1) / 2), c["text"], font=f,
                       fill=COL.get(c.get("color", "white"), WHITE), anchor="mm")
        # ---- büyük vurgu ----
        for b in (bigs if a.layer != "cards" else []):
            if b["t0"] <= t < b["t1"]:
                age = t - b["t0"]
                m = 1.0 + 0.35 * math.exp(-age / 0.07)
                f = fit_font(d, b["text"], W - 90, int(b.get("size", 150) * m))
                jx = 6 * math.exp(-age / 0.08) * math.sin(2 * math.pi * 38 * age)
                stroked_text(d, (W / 2 + jx, b.get("y", 0.45) * H), b["text"], f,
                             COL.get(b.get("color", "yellow"), YELLOW), BLACK, max(6, f.size // 12))
        # ---- altyazı parçası ----
        for s, e, c in (spans if a.layer != "cards" else []):
            if s <= t < e and not any(b["t0"] <= t < b["t1"] for b in bigs):
                words = [caps[j] for j in c]
                txt = " ".join(w["w"] for w in words)
                f = fit_font(d, txt, W - 120, cap_size)
                age = t - s
                m = 1.0 + 0.12 * math.exp(-age / 0.06)
                if m > 1.001:
                    f = fit_font(d, txt, W - 120, int(f.size * m))
                # kelime kelime yerleştir: konuşulan kelime sarı
                widths = [d.textlength(w["w"], font=f) for w in words]
                sp_w = d.textlength(" ", font=f)
                x = W / 2 - (sum(widths) + sp_w * (len(words) - 1)) / 2
                for w, wd in zip(words, widths):
                    on = w["s"] <= t
                    key = re.sub(r"[^\wçğıöşüÇĞİÖŞÜ]", "", w["w"]).lower() in emph
                    col = YELLOW if (on and (key or w["s"] <= t < w["e"] + 0.05)) else WHITE
                    stroked_text(d, (x + wd / 2, cap_y), w["w"], f, col, BLACK, max(5, f.size // 10))
                    x += wd + sp_w
                break
        p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait()
    print(f"{n} kare · {len(cards)} kart · {len(bigs)} büyük yazı · {len(spans)} altyazı parçası -> {a.out}")


if __name__ == "__main__":
    main()
