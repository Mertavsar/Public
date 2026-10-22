#!/usr/bin/env python3
"""PHP saldırısı videosu: müzik + efekt sesleri.

Müzik (assets/soundtrack.m4a): 112 BPM, La minör siber nabız. Telefon hoparlörü
~250 Hz altını vermediği için enerji orta bölgede: 8'lik nabız bas (üst
harmonikli), 16'lık arpej, akor pad'i, yumuşak "tok" kick ve çok hafif hi-hat.
Alkış/snare yok. Pad ve bas her vuruşta hafifçe "pompalanır" (sidechain hissi).
Bölümler sahnelere oturur: hook gerilimli (kick yok), anlatım boyunca tam,
"ne yapmalısın" sahnesinde nefes alır, kapanışta geri gelir.

Efektler (assets/hits.wav, mix.py sidechain'siz ekler): sahne başı bas vuruşu,
vurgulu kelimelerde bas, glitch, klavye tıkı, kilit sesi, alarm, damga vuruşu,
veri blipi, kart "pop"u, zil. Geçişlerde whoosh yok.

    python3 build/soundtrack.py   ->  assets/soundtrack.m4a, assets/hits.wav
"""
import json, os, subprocess, sys, tempfile, wave
import numpy as np
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILL = os.path.join(ROOT, '..', '.claude', 'skills', 'viral-edit', 'scripts')
SR = 44100
TM = json.load(open(os.path.join(ROOT, 'vo', 'timing.json')))
DUR, SC = TM['DUR'], TM['scenes']
BPM = 112.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
N = int(SR * DUR)
rng = np.random.default_rng(2026)

# Am – F – G – Em: (bas kökü, pad akoru, arpej notaları)
CHORDS = [
    (110.00, [220.00, 261.63, 329.63], [440.00, 523.25, 659.25, 880.00]),
    (87.31,  [174.61, 220.00, 261.63], [349.23, 440.00, 523.25, 698.46]),
    (98.00,  [196.00, 246.94, 293.66], [392.00, 493.88, 587.33, 783.99]),
    (82.41,  [164.81, 196.00, 246.94], [329.63, 392.00, 493.88, 659.25]),
]


def lp(x, fc): return sosfilt(butter(2, fc, btype='low', fs=SR, output='sos'), x)
def hp(x, fc): return sosfilt(butter(2, fc, btype='high', fs=SR, output='sos'), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype='band', fs=SR, output='sos'), x)
def T(d): return np.arange(int(SR * d)) / SR


def saw(f, n, harm=12):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, harm + 1):
        if f * k > 9000: break
        out += np.sin(2 * np.pi * f * k * t + k) / k
    return out


def env(n, a, r):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def place(bus, sig, t, gain=1.0):
    i = int(max(0, t) * SR)
    if i >= len(bus): return
    j = min(len(bus), i + len(sig))
    bus[i:j] += sig[:j - i] * gain


# ---------------------------------------------------------------- müzik
def section(t):
    """(pad, bas, arp, arp16, kick, hat) yoğunlukları."""
    if t < SC[1]: return (.9, .7, .45, 0, 0, 0)          # hook: gerilim, vuruş yok
    if t < SC[3]: return (.8, .9, .5, 1, .9, .5)         # anlatım
    if t < SC[6]: return (.8, 1, .55, 1, 1, .6)          # saldırı / arka kapı: tam
    if t < SC[7]: return (.9, .6, .4, 0, 0, .3)          # ne yapmalısın: nefes
    return (.9, .9, .5, 1, .9, .5)                        # kapanış


def pad_chord(notes, d):
    n = int(SR * d); s = np.zeros(n)
    for f in notes: s += saw(f * 1.003, n, 8) + saw(f * .997, n, 8)
    return lp(s, 1700) * env(n, .25, .4) / (len(notes) * 2.5)


def pluck(f, d=.22):
    t = T(d)
    s = np.sin(2 * np.pi * f * t) + .5 * np.sign(np.sin(2 * np.pi * f * t)) * .35 + .2 * np.sin(6 * np.pi * f * t)
    return lp(s, 4200) * np.exp(-t / .07) * np.minimum(1, t / .002)


def bass8(f, d):
    n = int(SR * d)
    body = lp(saw(f * 2, n, 14), 1100) + .6 * np.sin(2 * np.pi * f * np.arange(n) / SR)   # 220 Hz bölgesi telefonda duyulur
    return body * env(n, .004, d * .55)


def kick():
    t = T(.35)
    f = 52 + 90 * np.exp(-t / .035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .12)
    knock = np.sin(2 * np.pi * 160 * t) * np.exp(-t / .025) * .45
    return body + knock


def hat():
    t = T(.04)
    return hp(rng.standard_normal(len(t)), 8000) * np.exp(-t / .008)


L, R = np.zeros(N), np.zeros(N)
pump = np.ones(N)
KICK = kick()
bar_i, t0 = 0, 0.0
while t0 < DUR:
    root, chord, arp = CHORDS[bar_i % 4]
    pad_g, bass_g, arp_g, a16, kick_g, hat_g = section(t0 + .01)
    pc = pad_chord(chord, BAR + .2)
    place(L, pc, t0, .5 * pad_g); place(R, pc, t0, .5 * pad_g)
    for s8 in range(8):
        ts = t0 + s8 * BEAT / 2
        g = section(ts + .01)
        b = bass8(root, BEAT / 2 * .9)
        place(L, b, ts, .42 * g[1]); place(R, b, ts, .42 * g[1])
        if g[5] and s8 % 2:
            h = hat(); place(L, h, ts, .10 * g[5]); place(R, h, ts, .14 * g[5])
    steps = 16 if a16 else 8
    order = [0, 2, 1, 3, 2, 0, 3, 1, 0, 2, 1, 3, 2, 3, 1, 2]
    for k in range(steps):
        ts = t0 + k * BAR / steps
        g = section(ts + .01)
        p = pluck(arp[order[k % 16]])
        acc = 1 if k % (steps // 4) == 0 else .7
        place(L if k % 2 else R, p, ts, .28 * g[2] * acc)
        place(R if k % 2 else L, p, ts + BEAT * .75, .09 * g[2])               # yankı
    for bt in range(4):
        tb = t0 + bt * BEAT
        g = section(tb + .01)
        if g[4]:
            place(L, KICK, tb, .8 * g[4]); place(R, KICK, tb, .8 * g[4])
            i = int(tb * SR); j = min(N, i + int(.22 * SR))                    # pompalama
            pump[i:j] = np.minimum(pump[i:j], 1 - .45 * np.exp(-np.arange(j - i) / (.07 * SR)))
    bar_i += 1; t0 += BAR

L *= pump; R *= pump
tt = np.arange(N) / SR
fade = np.clip(tt / .4, 0, 1) * np.clip((DUR - tt) / 1.4, 0, 1)
L *= fade; R *= fade

# ---------------------------------------------------------------- efektler
def boom(amp=1.0):
    t = T(1.1)
    f = 45 + 75 * np.exp(-t / .05)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .32)
    knock = np.sin(2 * np.pi * 150 * t) * np.exp(-t / .06) * .55
    return (body + knock) * amp


def glitch():
    out = np.zeros(int(SR * .26)); k = 0
    while k * .028 < .24:
        f = 300 + rng.random() * 2200; t = T(.024)
        sq = np.sign(np.sin(2 * np.pi * f * t)) * .5
        crush = np.round(rng.standard_normal(len(t)) * 3) / 3 * .35
        place(out, (sq + crush) * np.exp(-t / .02), k * .028, .8 if rng.random() > .3 else .4)
        k += 1
    return bp(out, 250, 6000) * .6


def key():
    t = T(.03)
    return (bp(rng.standard_normal(len(t)), 2000, 6500) * np.exp(-t / .004) + .4 * np.sin(2 * np.pi * 1500 * t) * np.exp(-t / .006)) * .5


def clunk():
    t = T(.5)
    metal = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(523, 1), (1187, .7), (2093, .5), (3170, .3)]) * np.exp(-t / .09)
    click = bp(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t / .006)
    thud = np.sin(2 * np.pi * 90 * t) * np.exp(-t / .07)
    return (metal * .35 + click * .6 + thud * .8) * .8


def alarm(d=1.0):
    out = np.zeros(int(SR * d))
    for k in range(int(d / .25)):
        f = 880 if k % 2 == 0 else 660; t = T(.22)
        s = (np.sin(2 * np.pi * f * t) + .3 * np.sin(6 * np.pi * f * t)) * env(len(t), .01, .03)
        place(out, s, k * .25, 1 - k / (d / .25) * .6)
    return lp(out, 3500) * .35


def stamp():
    t = T(.6)
    crack = bp(rng.standard_normal(len(t)), 900, 4500) * np.exp(-t / .03)
    return boom(.9)[:len(t)] + crack * .7


def blip():
    t = T(.07); f = 700 + 900 * t / .07
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), .003, .03) * .35


def pop():
    t = T(.1); f = 480 + 520 * np.minimum(1, t / .04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .035) * .55


def zip_():
    t = T(.16); f = 3200 - 2400 * t / .16
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * .3 + bp(rng.standard_normal(len(t)), 900, 5000) * .5
    return s * env(len(t), .005, .05) * .55


def sweep():
    t = T(.9); f = 260 + 700 * (t / .9) ** 1.5
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (.6 + .4 * np.sin(2 * np.pi * 14 * t)) * env(len(t), .05, .15) * .22


def ding():
    t = T(1.4)
    return sum(a * np.sin(2 * np.pi * f * t) for f, a in [(1318.5, 1), (2637, .45), (3955, .2)]) * np.exp(-t / .35) * .4


SFX = dict(glitch=glitch, key=key, clunk=clunk, alarm=alarm, stamp=stamp, blip=blip, pop=pop, zip=zip_, sweep=sweep, ding=ding)
fx = np.zeros(N)
for t, k in TM.get('sfx', []):
    place(fx, SFX[k](), t - .005)
# bas vuruşları: sahne başları güçlü, vurgulu kelimeler biraz daha hafif
for k, t in enumerate(TM.get('hits', [])):
    place(fx, boom(1.0 if k == 0 or t in SC else .75), t - .01, .9)
fx /= np.max(np.abs(fx)) + 1e-9
w = wave.open(os.path.join(ROOT, 'assets', 'hits.wav'), 'w')
w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((fx * .9 * 32767).astype('<i2').tobytes()); w.close()

st = np.stack([L, R], 1)
st /= np.max(np.abs(st)) / .9
with tempfile.TemporaryDirectory() as tmp:
    raw, mst = os.path.join(tmp, 'mix.wav'), os.path.join(tmp, 'master.wav')
    w = wave.open(raw, 'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes()); w.close()
    subprocess.run([sys.executable, os.path.join(SKILL, 'master.py'), raw, mst, '-18.0', '-3.5'], check=True)
    out = os.path.join(ROOT, 'assets', 'soundtrack.m4a')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mst, '-c:a', 'aac', '-b:a', '192k', out], check=True)
    print('yazıldı:', out, '+ assets/hits.wav')
