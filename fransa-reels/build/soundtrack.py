#!/usr/bin/env python3
"""Sunumun müzik + efekt yatağı. Sentez motoru viral-edit skill'inden gelir;
vuruşlar sahne geçişlerine, klinkler sayaç/satır girişlerine oturur.

    python3 build/soundtrack.py   ->  assets/soundtrack.m4a
"""
import os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILL = os.path.join(ROOT, '..', '.claude', 'skills', 'viral-edit', 'scripts')
sys.path.insert(0, SKILL)
from audiobed import build_sfx, build_music  # noqa: E402

DUR = 86.0
# Sahne başları (index.html SCENES ile aynı)
MAJOR = [(0.3, .55), (6, .5), (14.5, .5), (23, .55), (31, .6), (42, .75), (51, .6), (62, .55), (70, .5), (78, .5), (83.5, .65)]
MINOR = [2.6, 7.8, 9.5, 11.6, 15.9, 18.5, 19.3, 23.6, 25.0, 26.6, 28.3, 32.2, 35.0, 36.0, 38.7,
         43.2, 46.7, 47.3, 48.6, 51.6, 53.8, 54.4, 55.0, 57.1, 62.5, 64.6, 65.0, 65.4, 66.8,
         70.7, 72.0, 73.3, 74.6, 78.6, 79.4, 80.2, 81.0, 85.3]
RISER = [42.0, 83.5]

with tempfile.TemporaryDirectory() as tmp:
    sfx, mus, mix, mst = (os.path.join(tmp, n) for n in ('sfx.wav', 'music.wav', 'mix.wav', 'master.wav'))
    build_sfx(DUR, MAJOR, MINOR, RISER, sfx)
    build_music(DUR, mus, bpm=96.0, peak_at=50.0, duck=[(70.0, 0.8)])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mus, '-i', sfx, '-filter_complex',
                    '[0]volume=0.75[m];[1]volume=0.9[s];[m][s]amix=inputs=2:normalize=0', mix], check=True)
    subprocess.run([sys.executable, os.path.join(SKILL, 'master.py'), mix, mst, '-14.0', '-3.5'], check=True)
    out = os.path.join(ROOT, 'assets', 'soundtrack.m4a')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mst, '-c:a', 'aac', '-b:a', '160k', out], check=True)
    print('yazıldı:', out)
