#!/usr/bin/env python3
"""Seslendirmesiz video için miks: müzik yatağı + bas vurguları, master -16 LUFS.

    python3 build/mix.py   ->  assets/mix.m4a
"""
import os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, '..', '.claude', 'skills', 'viral-edit', 'scripts')
P = lambda *a: os.path.join(ROOT, *a)
with tempfile.TemporaryDirectory() as tmp:
    mix, mst = os.path.join(tmp, 'mix.wav'), os.path.join(tmp, 'master.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', P('assets', 'soundtrack.m4a'), '-i', P('assets', 'hits.wav'),
                    '-filter_complex', '[0]aresample=48000[m];[1]volume=-4dB,aresample=48000,aformat=channel_layouts=stereo[h];'
                    '[m][h]amix=inputs=2:normalize=0:duration=first', mix], check=True)
    subprocess.run([sys.executable, os.path.join(SKILL, 'master.py'), mix, mst, '-16.0', '-3.5'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mst, '-c:a', 'aac', '-b:a', '192k', P('assets', 'mix.m4a')], check=True)
    print('yazıldı:', P('assets', 'mix.m4a'))
