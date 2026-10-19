#!/usr/bin/env python3
"""Ham seslendirmeyi temizler ve sıkılaştırır.

1. Kurgu (kelimeye dokunmadan): vo_analyze.py ile konuşma bölgeleri bulunur.
   Yalnızca bölgeler ARASINDAKİ sessizlik kısaltılır; bölgelerin içi asla
   kesilmez (viral-edit skill'i: enerji bloğunun ortasından kesmek kelimeyi
   parçalar). Kısa, perdesiz, düşük enerjili bölgeler (nefes, hırıltı) atılır.
     - baştaki sessizlik  -> 0.12 s
     - cümle içi kısa ara (< 0.45 s) -> olduğu gibi
     - uzun ara           -> 0.40 s (doğal cümle duraksaması)
   Her parçanın kenarına 12 ms yumuşak geçiş; ön 70 ms / arka 140 ms pay
   bırakılır ki ünsüz başı ve kuyruğu kırpılmasın.
2. Ses işleme (ffmpeg): 80 Hz altı uğultu, hafif FFT gürültü azaltma,
   250 Hz çamur kesme, 3.5 kHz netlik, de-esser, yumuşak kompresör.

Çıktı: vo/temiz.wav ve vo/kurgu.json (eski -> yeni zaman eşlemesi).

    python3 build/vo_clean.py vo/ham.wav
"""
import json, os, subprocess, sys, wave
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vo_analyze import load, frames, regions, classify  # noqa: E402

LEAD_SIL, SHORT_GAP, LONG_GAP = .12, .45, .40
PRE, POST, FADE = .07, .14, .012
TAIL = .6

src = sys.argv[1]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
x, sr = load(src)
db, v, h = frames(x, sr)
rs = [r for r in classify(regions(db, v, h)) if r['kind'] == 'konusma']

# Bitişik bölgeleri (kısa aralıklı) aynı "cümle grubu" içinde tut
pieces, gaps = [], []
for i, r in enumerate(rs):
    a, b = max(0.0, r['a'] - PRE), min(len(x) / sr, r['b'] + POST)
    if pieces and a < pieces[-1][1]:                # pay yüzünden çakışma: birleştir
        pieces[-1][1] = b
        continue
    if pieces:
        g = a - pieces[-1][1]
        gaps.append(g if g < SHORT_GAP else LONG_GAP)
    pieces.append([a, b])

out, mapping, t_new = [np.zeros(int(LEAD_SIL * sr))], [], LEAD_SIL
fl = int(FADE * sr)
ramp = np.linspace(0, 1, fl)
for i, (a, b) in enumerate(pieces):
    seg = x[int(a * sr):int(b * sr)].copy()
    seg[:fl] *= ramp; seg[-fl:] *= ramp[::-1]
    mapping.append(dict(old=[round(a, 3), round(b, 3)], new=[round(t_new, 3), round(t_new + (b - a), 3)]))
    out.append(seg); t_new += b - a
    if i < len(gaps):
        out.append(np.zeros(int(gaps[i] * sr))); t_new += gaps[i]
out.append(np.zeros(int(TAIL * sr))); t_new += TAIL
y = np.concatenate(out)

tmp = os.path.join(root, 'vo', 'kurgu_ham.wav')
w = wave.open(tmp, 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes()); w.close()

chain = ','.join([
    'highpass=f=80:poles=2',
    'afftdn=nr=8:nf=-55:tn=1',                       # hafif: konuşmayı boğmadan
    'equalizer=f=250:t=q:w=1.2:g=-2.5',              # çamur
    'equalizer=f=3500:t=q:w=1.0:g=2.5',              # netlik
    'equalizer=f=9000:t=h:w=3000:g=1.5',             # hava
    'deesser=i=0.35:m=0.5:f=0.5:s=o',
    'acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=3dB:knee=4',
])
dst = os.path.join(root, 'vo', 'temiz.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', chain, '-ar', '48000', '-ac', '1', dst], check=True)
os.remove(tmp)

json.dump(dict(duration=round(t_new, 3), pieces=mapping), open(os.path.join(root, 'vo', 'kurgu.json'), 'w'), indent=1)
print(f'{len(x) / sr:.2f} s -> {t_new:.2f} s · {len(pieces)} parça · atılan nefes/hırıltı: '
      f'{sum(1 for r in classify(regions(db, v, h)) if r["kind"] != "konusma")}')
print(dst)
