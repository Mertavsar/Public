#!/usr/bin/env python3
"""Seslendirme + müzik miksi ve master.

- Seslendirme -16 LUFS'a, müzik yatağı -30 LUFS'a getirilir (konuşmanın
  ~14 LU altında: duyulur ama öne çıkmaz).
- Müzik konuşmanın altında sidechain ile ~6 dB daha iner, cümle aralarında
  yumuşakça geri açılır (attack 15 ms, release 450 ms; pompalama yapmaz).
- Bas vurguları (assets/hits.wav) sidechain'siz eklenir: tepe konuşma tepesinin
  ~6 dB altında; enerjisi çoğunlukla 45–150 Hz'de olduğu için kelimeyi örtmez.
- Master: viral-edit/master.py ile -14 LUFS, tavan -3.5 dBFS (AAC aşması için pay).

    python3 build/mix.py   ->  assets/mix.m4a  (vo/son.wav yoksa yalnızca müzik + vurgular)
"""
import os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, '..', '.claude', 'skills', 'viral-edit', 'scripts')
P = lambda *a: os.path.join(ROOT, *a)

def lufs(path):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[0-9.]+) LUFS', err)[-1])


def to_level(src, dst, target):
    """Doğrusal kazanç (dinamiği bozmadan) ile hedef loudness'a getir."""
    g = target - lufs(src)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', f'volume={g:.2f}dB,aresample=48000',
                    '-ac', '2', dst], check=True)
    return g


with tempfile.TemporaryDirectory() as tmp:
    vo, mus, mix, mst = (os.path.join(tmp, n) for n in ('vo.wav', 'mus.wav', 'mix.wav', 'master.wav'))
    has_vo = os.path.exists(P('vo', 'son.wav'))
    if has_vo:
        to_level(P('vo', 'son.wav'), vo, -16.0)
    else:   # seslendirme henüz yok: önizleme için sessiz konuşma kanalı, müzik biraz daha önde
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', '1', vo], check=True)
    to_level(P('assets', 'soundtrack.m4a'), mus, -30.0 if has_vo else -20.0)
    hits = P('assets', 'hits.wav')
    ins = ['-i', mus, '-i', vo] + (['-i', hits] if os.path.exists(hits) else [])
    fc = ('[1]asplit=2[v][sc];'
          '[0][sc]sidechaincompress=threshold=0.03:ratio=4:attack=15:release=450:makeup=1[m];')
    if os.path.exists(hits):
        fc += '[2]volume=-9dB,aresample=48000,aformat=channel_layouts=stereo[h];[m][v][h]amix=inputs=3:normalize=0:duration=longest'
    else:
        fc += '[m][v]amix=inputs=2:normalize=0:duration=longest'
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', fc, mix], check=True)
    subprocess.run([sys.executable, os.path.join(SKILL, 'master.py'), mix, mst, '-14.0', '-3.5'], check=True)
    out = P('assets', 'mix.m4a')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mst, '-c:a', 'aac', '-b:a', '192k', out], check=True)
    print('yazıldı:', out)
