#!/usr/bin/env python3
"""Seslendirmeyi bölgelere ayırır: konuşma / nefes / sessizlik.

Her 20 ms'lik çerçeve için enerji ve seslilik (otokorelasyonla perde varlığı)
ölçülür. Sessizlikle ayrılmış her bölge, sesli çerçeve oranına göre sınıflanır:
nefes ve hırıltı perdesizdir; sessiz ünsüzler (s, ş, f) de perdesizdir ama
kısa ve sesli bölgelere yapışıktır.

    python3 build/vo_analyze.py vo/ham.wav
"""
import sys, wave
import numpy as np

def load(path):
    w = wave.open(path)
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(float) / 32768
    return x, sr

def frames(x, sr, hop_s=.02):
    """Çerçeve başına enerji (dB) ve seslilik; otokorelasyon FFT ile, vektörel."""
    hop = int(sr * hop_s)
    n = len(x) // hop - 1
    idx = np.arange(2 * hop)[None, :] + hop * np.arange(n)[:, None]
    F = x[idx]                                            # 40 ms pencereler
    db = 20 * np.log10(np.sqrt(np.mean(F[:, :hop] ** 2, axis=1)) + 1e-9)
    F = (F - F.mean(axis=1, keepdims=True)) * np.hanning(2 * hop)
    S = np.fft.rfft(F, 4 * hop, axis=1)
    ac = np.fft.irfft(np.abs(S) ** 2, axis=1)[:, :2 * hop]
    lo, hi = int(sr / 400), min(int(sr / 70), 2 * hop - 1)
    ratio = ac[:, lo:hi].max(axis=1) / np.maximum(ac[:, 0], 1e-12)
    voiced = (ratio > .45) & (db > -42)
    return db, voiced, hop_s

def regions(db, voiced, hop_s, act=-40.0, gap=.12):
    on = db > act
    out, i, n = [], 0, len(db)
    while i < n:
        if not on[i]:
            i += 1; continue
        j = i
        while j < n:
            if on[j]:
                j += 1; continue
            k = j
            while k < n and not on[k]:
                k += 1
            if (k - j) * hop_s >= gap or k >= n:
                break
            j = k
        seg = slice(i, j)
        out.append(dict(a=i * hop_s, b=j * hop_s, peak=float(db[seg].max()),
                        vr=float(voiced[seg].mean())))
        i = j
    return out

def classify(rs):
    for r in rs:
        d = r['b'] - r['a']
        r['kind'] = 'nefes' if (r['vr'] < .12 and d < 1.0) or (r['peak'] < -30 and r['vr'] < .3) else 'konusma'
    return rs

if __name__ == '__main__':
    x, sr = load(sys.argv[1])
    db, v, h = frames(x, sr)
    for r in classify(regions(db, v, h)):
        print(f"{r['a']:6.2f}-{r['b']:6.2f}  {r['b']-r['a']:5.2f}s  tepe {r['peak']:6.1f}  sesli %{r['vr']*100:4.0f}  {r['kind']}")
