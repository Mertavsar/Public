#!/usr/bin/env python3
"""Fransa 2. bölüm: müzik + efekt yatağı.

Müzik burada sentezleniyor (ağ kapalı, hazır kütüphane yok). Telefon hoparlörü
~250 Hz altını neredeyse hiç vermiyor; o yüzden enerji orta bölgede tutuluyor:
akor pad'i, arpej melodisi, tıklı kick, el çırpma ve hi-hat. Bas yalnızca
destek. Sahne geçişlerinde efekt yok; sayaç/satır girişlerinde kısa tık var
(tık sesi viral-edit skill'inin motorundan).

    python3 build/soundtrack.py   ->  assets/soundtrack.m4a
"""
import os, subprocess, sys, tempfile, wave
import numpy as np
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILL = os.path.join(ROOT, '..', '.claude', 'skills', 'viral-edit', 'scripts')
sys.path.insert(0, SKILL)
from audiobed import tick  # noqa: E402

SR = 44100
DUR = 59.6
BPM = 72.0   # sakin: davul/bas yok, yalnızca pad ve seyrek notalar
BEAT = 60.0 / BPM
BAR = 4 * BEAT

MINOR = [2.2, 8.1, 8.9, 13.5, 16.5, 17.3, 18.1, 22.0, 30.5, 32.6, 34.7, 38.8, 41.2, 46.4, 47.9, 49.4, 53.6, 54.2, 57.0]

# i–VI–III–VII (La minör): Am F C G
CHORDS = [
    (110.00, [220.00, 261.63, 329.63], [440.00, 523.25, 659.25, 880.00]),
    (87.31,  [220.00, 261.63, 349.23], [440.00, 523.25, 698.46, 880.00]),
    (130.81, [261.63, 329.63, 392.00], [523.25, 659.25, 783.99, 1046.50]),
    (98.00,  [246.94, 293.66, 392.00], [493.88, 587.33, 783.99, 987.77]),
]

# Bölümlere göre yoğunluk: (başlangıç, pad, arp, arp16, kick, clap, hat, bass)
SECTIONS = [
    # (başlangıç, pad, arp, arp16, kick, clap, hat, bass) — kullanıcı geri bildirimi: müzik
    # dikkat dağıtmasın, seslendirmenin altında fark edilmeden dursun
    (0.0,  .8, .30, 0, 0, 0, 0, 0),
    (20.8, .8, .22, 0, 0, 0, 0, 0),
    (29.6, .8, .30, 0, 0, 0, 0, 0),
    (52.6, .8, .18, 0, 0, 0, 0, 0),
]


def section(t):
    s = SECTIONS[0]
    for row in SECTIONS:
        if t >= row[0]:
            s = row
    return s[1:]


rng = np.random.default_rng(2026)
N = int(SR * DUR)
L = np.zeros(N)
R = np.zeros(N)


def place(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    if i >= N:
        return
    j = min(N, i + len(sig))
    gl, gr = gain * np.sqrt((1 - pan) / 2), gain * np.sqrt((1 + pan) / 2)
    L[i:j] += sig[:j - i] * gl
    R[i:j] += sig[:j - i] * gr


def saw(f, n, harm=12):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, harm + 1):
        if f * k > 9000:
            break
        out += np.sin(2 * np.pi * f * k * t + k) / k
    return out


def lp(x, fc):
    return sosfilt(butter(2, fc, btype='low', fs=SR, output='sos'), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], btype='band', fs=SR, output='sos'), x)


def env(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def pad_chord(notes, d):
    n = int(SR * d)
    s = np.zeros(n)
    for f in notes:
        s += saw(f * 1.0012, n, 8) + saw(f * 0.9988, n, 8)
    return lp(s, 1900) * env(n, 0.35, 0.5) / (len(notes) * 2.5)


def pluck(f, d=0.42):
    n = int(SR * d)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.45 * np.sin(4 * np.pi * f * t) + 0.18 * np.sin(6 * np.pi * f * t)
    return s * np.exp(-t / 0.13) * np.minimum(1, t / 0.003)


def kick():
    n = int(SR * 0.42)
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t / 0.04)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13)
    click = bp(rng.standard_normal(n), 1800, 5200) * np.exp(-t / 0.004) * 0.6
    knock = np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.03) * 0.5   # telefonda "tok" duyulan kısım
    return body + click + knock


def clap():
    n = int(SR * 0.26)
    t = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 900, 5200)
    e = np.exp(-t / 0.09)
    for d in (0.0, 0.011, 0.022):                       # el çırpmanın çoklu vuruşu
        e += (t >= d) * np.exp(-np.maximum(t - d, 0) / 0.006) * 0.8
    return x * e * 0.55 + np.sin(2 * np.pi * 230 * t) * np.exp(-t / 0.04) * 0.25


def hat(d=0.05):
    n = int(SR * d)
    t = np.arange(n) / SR
    x = sosfilt(butter(2, 7000, btype='high', fs=SR, output='sos'), rng.standard_normal(n))
    return x * np.exp(-t / (d / 3.5))


def bass_note(f, d):
    n = int(SR * d)
    return lp(saw(f, n, 10), 900) * env(n, 0.005, min(0.08, d / 3))



KICK, CLAP = kick(), clap()

# ---- müzik ----
bar_i = 0
t0 = 0.0
while t0 < DUR - 0.3:
    root, chord, arp = CHORDS[bar_i % 4]
    pad_g, arp_g, arp16, kick_g, clap_g, hat_g, bass_g = section(t0 + 0.01)
    place(pad_chord(chord, BAR + 0.3), t0, -0.25, 0.55 * pad_g)
    place(pad_chord([c * 2 for c in chord[:2]], BAR + 0.3), t0, 0.3, 0.22 * pad_g)
    steps = 16 if arp16 else 4
    order = [0, 1, 2, 3, 2, 1, 2, 3, 0, 2, 1, 3, 2, 1, 3, 2]
    for s in range(steps):
        ts = t0 + s * BAR / steps
        f = arp[order[s % 16]]
        g = arp_g * (0.95 if s % (steps // 4) == 0 else 0.7)
        pan = -0.35 if s % 2 else 0.35
        place(pluck(f), ts, pan, 0.30 * g)
        place(pluck(f), ts + BEAT * 0.75, -pan, 0.11 * g)       # ping-pong yankı
    for b in range(4):
        tb = t0 + b * BEAT
        tsec = section(tb + 0.01)
        if tsec[3]:
            place(KICK, tb, 0, 0.75 * tsec[3])
        if tsec[4] and b in (1, 3):
            place(CLAP, tb, 0.05, 0.55 * tsec[4])
        if tsec[5]:
            place(hat(), tb + BEAT / 2, 0.25, 0.20 * tsec[5])
            if tsec[2]:
                place(hat(0.03), tb + BEAT / 4, -0.25, 0.10 * tsec[5])
                place(hat(0.03), tb + 3 * BEAT / 4, -0.25, 0.10 * tsec[5])
        if tsec[6]:
            place(bass_note(root, BEAT * 0.45), tb, 0, 0.42 * tsec[6])
            place(bass_note(root * 2, BEAT * 0.3), tb + BEAT / 2, 0, 0.22 * tsec[6])
    bar_i += 1
    t0 += BAR

# Kapanış: son akor çalarak sönsün
place(pad_chord(CHORDS[0][1] + [440.0], 7.0), 52.6, 0, 0.6)

tt = np.arange(N) / SR
fade = np.clip(tt / 0.6, 0, 1) * np.clip((DUR - tt) / 1.5, 0, 1)
L *= fade
R *= fade

# ---- efektler ----
fx = np.zeros(N)


def fx_place(sig, t):
    i = max(0, int(t * SR))
    j = min(N, i + len(sig))
    fx[i:j] += sig[:j - i]


# Sahne geçişlerinde efekt yok (whoosh/darbe/riser kullanıcı isteğiyle kaldırıldı);
# yalnızca sayaç ve satır girişlerinde kısa tık kalıyor.
for t in MINOR:
    fx_place(tick(rng, amp=0.16), t - 0.01)

mus_peak = max(np.max(np.abs(L)), np.max(np.abs(R)))
L, R = L / mus_peak * 0.62, R / mus_peak * 0.62
fx = sosfilt(butter(2, 70, btype='high', fs=SR, output='sos'), fx)
L += fx * 0.85
R += fx * 0.85
st = np.stack([L, R], 1)
st /= np.max(np.abs(st)) / 0.9

with tempfile.TemporaryDirectory() as tmp:
    raw, mst = os.path.join(tmp, 'mix.wav'), os.path.join(tmp, 'master.wav')
    w = wave.open(raw, 'w')
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
    w.close()
    subprocess.run([sys.executable, os.path.join(SKILL, 'master.py'), raw, mst, '-20.0', '-3.5'], check=True)   # tek başına çalan yatak: sakin seviye
    out = os.path.join(ROOT, 'assets', 'soundtrack.m4a')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mst, '-c:a', 'aac', '-b:a', '192k', out], check=True)
    print('yazıldı:', out)
