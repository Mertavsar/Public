#!/usr/bin/env python3
"""
Seslendirmedeki ölü boşluğu kısaltır ve isteğe bağlı olarak tempoyu artırır.

ElevenLabs çıktılarında cümle araları 0.5–0.8 saniyeye çıkabiliyor; bir metnin
üçte biri sessizlik olabiliyor. Referans viral formatta sessizlik izleyiciyi
kaydırtıyor, o yüzden araları sabit ve kısa bir değere çekiyoruz.

Konuşma kesilmez: her bloğun başına ve sonuna pay bırakılır, kenarlara 6 ms
fade uygulanır (tık sesi olmasın).

Kullanım
--------
    python3 retime.py --audio vo.mp3 --out vo_tight.wav
    python3 retime.py --audio vo.mp3 --out vo_tight.wav --gap 0.15 --long-gap 0.26 --tempo 1.06
"""

import argparse, subprocess, sys, wave
import numpy as np

SR = 44100
HOP = 0.010


def load(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def blocks(x, floor_off=18.0, min_gap=0.12, min_block=0.08):
    h = int(SR * HOP)
    n = len(x) // h
    e = np.sqrt(np.maximum([np.mean(x[i * h:(i + 1) * h] ** 2) for i in range(n)], 1e-12))
    db = 20 * np.log10(e)
    thr = max(np.percentile(db, 15) + 6.0, np.percentile(db, 90) - floor_off)
    on = db > thr

    out, i = [], 0
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            out.append([i * HOP, j * HOP])
            i = j
        else:
            i += 1
    merged = []
    for b in out:
        if merged and b[0] - merged[-1][1] < min_gap:
            merged[-1][1] = b[1]
        else:
            merged.append(b)
    return [b for b in merged if b[1] - b[0] >= min_block]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gap", type=float, default=0.15, help="normal cümle arası (s)")
    ap.add_argument("--long-gap", type=float, default=0.26, help="dramatik duraklar (s)")
    ap.add_argument("--long-if", type=float, default=0.55,
                    help="orijinal boşluk bundan uzunsa dramatik sayılır (s)")
    ap.add_argument("--pad", type=float, default=0.045, help="blok başı/sonu payı (s)")
    ap.add_argument("--tempo", type=float, default=1.0, help="atempo çarpanı (1.0 = değiştirme)")
    a = ap.parse_args()

    x = load(a.audio)
    bl = blocks(x)
    if not bl:
        sys.exit("Konuşma bulunamadı.")

    dur = len(x) / SR
    speech = sum(e - s for s, e in bl)
    gaps_in = [bl[i + 1][0] - bl[i][1] for i in range(len(bl) - 1)]

    fade = int(0.006 * SR)
    pieces, gaps_out = [], []
    for i, (s, e) in enumerate(bl):
        s = max(0.0, s - a.pad)
        e = min(dur, e + a.pad)
        seg = x[int(s * SR):int(e * SR)].copy()
        if len(seg) > 2 * fade:
            seg[:fade] *= np.linspace(0, 1, fade)
            seg[-fade:] *= np.linspace(1, 0, fade)
        pieces.append(seg)
        if i < len(bl) - 1:
            g = a.long_gap if gaps_in[i] > a.long_if else a.gap
            gaps_out.append(g)
            pieces.append(np.zeros(int(g * SR), dtype=np.float32))
    y = np.concatenate(pieces)

    tmp = a.out + ".tmp.wav"
    w = wave.open(tmp, "w")
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    w.close()

    if abs(a.tempo - 1.0) > 1e-3:
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", tmp,
                        "-af", f"atempo={a.tempo}", a.out], check=True)
        subprocess.run(["rm", "-f", tmp])
    else:
        subprocess.run(["mv", tmp, a.out])

    new = len(y) / SR / a.tempo
    print(f"{len(bl)} konuşma bloğu")
    print(f"ölü boşluk: {dur - speech:.2f}s  ->  {sum(gaps_out):.2f}s")
    print(f"süre: {dur:.2f}s  ->  {new:.2f}s  (tempo x{a.tempo})")
    print(f"-> {a.out}")


if __name__ == "__main__":
    main()
