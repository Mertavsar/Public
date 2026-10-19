#!/usr/bin/env python3
"""Ham seslendirmeyi temizler: nefes, burun çekme, hırıltı ve boşluklar.

Nasıl ayırıyor
--------------
Konuşmanın omurgası sesli harflerdir: perdelidir (otokorelasyonda 70–400 Hz
arası belirgin tepe). Nefes, burun çekme ve hırıltı perdesizdir ve tınısı
alçaktır (spektral merkez ~1–2 kHz). "s/ş" de perdesizdir ama tınısı yüksektir
(> 3.2 kHz) ve hep bir sesli harfe yapışıktır.

1. 10 ms çerçevelerde perde (seslilik), seviye ve spektral merkez ölçülür.
2. Sesli çerçeveler 0.25 s'den kısa aralarla kümelenir: kelime ve cümle parçaları.
3. Her küme korunur; başına 60 ms, sonuna 100 ms pay eklenir. Pay, yüksek
   tınılı (s/ş/z) ve yeterince güçlü çerçeveler sürdükçe başta 220 ms'ye,
   sonda 260 ms'ye kadar uzar. Alçak tınılı perdesiz ses (nefes) payı durdurur.
4. Aradaki perdesiz parça kısa (< 0.18 s) ve güçlüyse (> -32 dB) ya da yüksek
   tınılıysa (s/ş) kelimeye aittir, korunur. Geri kalanı (nefes, burun çekme,
   hırıltı) 12 ms rampalarla tamamen susturulur.
5. Bölgeler arası sessizlik sıkıştırılır: cümle içi kısa ara olduğu gibi,
   uzun ara 0.38 s. Kelimelerin içinden asla kesilmez.
6. Ses zinciri: 75 Hz altı kesim, sıcaklık (+2 dB @120 Hz), telefon kutusu
   kesimi (−3 dB @350 Hz), netlik (+2.5 dB @3 kHz), hava (+2 dB @10 kHz),
   de-esser, iki kademeli yumuşak kompresör.

    python3 build/vo_clean.py vo/ham.wav   ->  vo/temiz.wav, vo/kurgu.json, vo/atilan.json
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
HOP = .01
LEAD_SIL, SHORT_GAP, LONG_GAP, TAIL = .12, .42, .38, .6
PRE, PRE_MAX, POST, POST_MAX = .06, .22, .10, .26
SIB_HZ, SIB_DB = 3200, -42
MERGE, MIN_CLUSTER = .25, .06
RAMP = .012
TAIL_HOLD, TAIL_MIN = .18, .45


def load(path):
    w = wave.open(path)
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(float) / 32768
    if w.getnchannels() == 2:
        x = x.reshape(-1, 2).mean(1)
    return x, sr


def features(x, sr):
    hop, win = int(sr * HOP), int(sr * .03)
    n = (len(x) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    F = x[idx]
    db = 20 * np.log10(np.sqrt(np.mean(F ** 2, axis=1)) + 1e-9)
    Fw = (F - F.mean(1, keepdims=True)) * np.hanning(win)
    S = np.abs(np.fft.rfft(Fw, axis=1)) + 1e-9
    fr = np.fft.rfftfreq(win, 1 / sr)
    cent = (S * fr).sum(1) / S.sum(1)
    A = np.fft.irfft(np.abs(np.fft.rfft(Fw, 2 * win, axis=1)) ** 2, axis=1)[:, :win]
    lo, hi = int(sr / 400), int(sr / 70)
    voiced = (A[:, lo:hi].max(1) / np.maximum(A[:, 0], 1e-12) > .5) & (db > -45)
    return db, cent, voiced


def keep_regions(db, cent, voiced):
    """Korunacak bölgeler.

    Temel birim enerji bölgesidir (-45 dB üstü, 0.15 s'den kısa sessizlikler
    birleşik): cümle ya da cümle parçası, kısık son hecesiyle birlikte.
    - İçinde sesli harf (perdeli küme) olmayan bölge: nefes/burun çekme -> atılır.
    - Bölgenin SONU asla kırpılmaz: cümle sonu kısılıp fısıltıya döner,
      orayı kesmek cümleyi yarım bırakır. Sona 60 ms pay eklenir.
    - Bölgenin BAŞINDA ilk sesli harften önce 0.25 s'den uzun, alçak tınılı
      perdesiz ses varsa bu nefes almadır: ilk sesli harften PRE önceye kadar
      kırpılır (s/ş gibi yüksek tınılı ünsüz sürdükçe PRE_MAX'a kadar korunur).
    """
    n = len(db)
    on = db > -45
    regs, i = [], 0
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
            if (k - j) * HOP >= .15 or k >= n:
                break
            j = k
        regs.append([i, j]); i = j
    sib = (cent > SIB_HZ) & (db > SIB_DB)
    out, inhales = [], []
    for a, b in regs:
        vi = np.flatnonzero(voiced[a:b])
        if len(vi) * HOP < MIN_CLUSTER:
            continue                                         # sesli harf yok: nefes / burun
        first = a + vi[0]
        s = a
        if (first - a) * HOP > .25 and np.median(cent[a:first]) < SIB_HZ:
            s = first - int(PRE / HOP)
            while s > a and first - s < PRE_MAX / HOP and sib[s - 1]:
                s -= 1
            inhales.append(((a) * HOP, s * HOP))
        e = min(n, b + int(.06 / HOP))
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    keep_regions.inhales = inhales
    return [(a * HOP, b * HOP) for a, b in out]


def main(src):
    x, sr = load(src)
    db, cent, voiced = features(x, sr)
    keep = keep_regions(db, cent, voiced)


    # atılan (perdesiz, sesli) parçaların raporu
    dropped, prev = [], 0.0
    for a, b in keep + [(len(x) / sr, len(x) / sr)]:
        seg = db[int(prev / HOP):int(a / HOP)]
        if len(seg) and seg.max() > -50:
            dropped.append(dict(t=[round(prev, 2), round(a, 2)], peak_db=round(float(seg.max()), 1),
                                hz=int(np.median(cent[int(prev / HOP):int(a / HOP)][seg > -55])) if (seg > -55).any() else 0))
        prev = b

    # kurgu: korunan bölgeler + sıkıştırılmış aralar
    rl = int(RAMP * sr)
    ramp = np.linspace(0, 1, rl)
    out, mapping, t_new = [np.zeros(int(LEAD_SIL * sr))], [], LEAD_SIL
    for i, (a, b) in enumerate(keep):
        seg = x[int(a * sr):int(b * sr)].copy()
        # cümle sonu: son sesli harften TAIL_HOLD sonra kesmeden yavaşça kıs (hece
        # duyulur, arkasındaki nefes vermesi öne çıkmaz)
        vi = np.flatnonzero(voiced[int(a / HOP):int(b / HOP)])
        if len(vi):
            t_hold = (vi[-1] * HOP) + TAIL_HOLD
            k0 = int(t_hold * sr)
            if k0 < len(seg):
                g = np.linspace(1, TAIL_MIN, len(seg) - k0)
                seg[k0:] *= g
        if len(seg) > 2 * rl:
            seg[:rl] *= ramp; seg[-rl:] *= ramp[::-1]
        mapping.append(dict(old=[round(a, 3), round(b, 3)], new=[round(t_new, 3), round(t_new + b - a, 3)]))
        out.append(seg); t_new += b - a
        if i + 1 < len(keep):
            g = keep[i + 1][0] - b
            g = g if g < SHORT_GAP else LONG_GAP
            out.append(np.zeros(int(g * sr))); t_new += g
    out.append(np.zeros(int(TAIL * sr))); t_new += TAIL
    y = np.concatenate(out)

    tmp = P('vo', '_kurgu.wav')
    w = wave.open(tmp, 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes()); w.close()
    chain = ','.join([
        'highpass=f=75:poles=2',
        'equalizer=f=120:t=q:w=0.9:g=2',
        'equalizer=f=350:t=q:w=1.1:g=-3',
        'equalizer=f=3000:t=q:w=1.0:g=2.5',
        'treble=g=2:f=10000',
        'deesser=i=0.3:m=0.5:f=0.5:s=o',
        'acompressor=threshold=-26dB:ratio=2.5:attack=12:release=140:makeup=2dB:knee=6',
        'acompressor=threshold=-14dB:ratio=4:attack=3:release=60:makeup=1dB:knee=3',
    ])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', chain, '-ar', '48000', '-ac', '1', P('vo', 'temiz.wav')], check=True)
    os.remove(tmp)
    json.dump(dict(duration=round(t_new, 3), pieces=mapping), open(P('vo', 'kurgu.json'), 'w'), indent=1)
    json.dump(dropped, open(P('vo', 'atilan.json'), 'w'), indent=1)
    print(f'{len(x) / sr:.2f} s -> {t_new:.2f} s · {len(keep)} parça korundu · {len(dropped)} gürültü parçası atıldı')
    for a, b in keep_regions.inhales:
        print(f'  cümle başı nefes alma kırpıldı {a:6.2f}-{b:6.2f}')
    for d in dropped:
        print(f"  atıldı {d['t'][0]:6.2f}-{d['t'][1]:6.2f}  tepe {d['peak_db']:6.1f} dB  ~{d['hz']} Hz")


if __name__ == '__main__':
    main(sys.argv[1])
