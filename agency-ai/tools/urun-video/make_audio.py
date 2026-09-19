#!/usr/bin/env python3
"""Mjolnir reklam filmi - ses tasarimi (sentetik, telifsiz).

Cikti: soundtrack.wav (44.1 kHz, stereo, 15 sn)
Katmanlar: gok gurultusu, cekic darbesi, epik drone, whoosh gecisler,
metalik shimmer, riser ve final vurus.
"""
import numpy as np
import wave
import sys

SR = 44100
DUR = 15.0
N = int(SR * DUR)
T = np.arange(N) / SR

rng = np.random.default_rng(7)


# ---------------------------------------------------------------- filtreler
def _fft_filter(x, H):
    X = np.fft.rfft(x)
    return np.fft.irfft(X * H, n=len(x))


def lowpass(x, fc, order=2):
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return _fft_filter(x, 1.0 / np.sqrt(1.0 + (f / max(fc, 1.0)) ** (2 * order)))


def highpass(x, fc, order=2):
    f = np.fft.rfftfreq(len(x), 1 / SR)
    r = (f / max(fc, 1.0)) ** order
    return _fft_filter(x, r / np.sqrt(1.0 + r ** 2))


def bandpass(x, lo, hi, order=2):
    return lowpass(highpass(x, lo, order), hi, order)


# ---------------------------------------------------------------- yardimcilar
def noise(n):
    return rng.standard_normal(n)


def brown(n):
    w = noise(n)
    b = np.cumsum(w)
    b -= np.linspace(b[0], b[-1], n)
    m = np.max(np.abs(b)) or 1.0
    return b / m


def env(n, attack, decay, curve=2.5):
    """Hizli atak + ustel sonum."""
    a = max(int(SR * attack), 1)
    e = np.empty(n)
    e[:a] = np.linspace(0, 1, a) ** 0.6
    rest = n - a
    if rest > 0:
        e[a:] = np.exp(-np.linspace(0, curve * 3, rest))
    d = max(int(SR * decay), 1)
    if d < n:
        e[d:] *= np.exp(-np.linspace(0, 6, n - d))
    return e


def add(buf, sig, at, gain=1.0, pan=0.0):
    """pan: -1 sol, +1 sag."""
    i = int(at * SR)
    if i >= N:
        return
    s = sig[: N - i]
    l = gain * np.sqrt(0.5 * (1.0 - pan))
    r = gain * np.sqrt(0.5 * (1.0 + pan))
    buf[0, i: i + len(s)] += l * s
    buf[1, i: i + len(s)] += r * s


def sweep(dur, f0, f1, shape=2.0):
    n = int(SR * dur)
    t = np.arange(n) / SR
    k = (t / max(dur, 1e-6)) ** shape
    f = f0 + (f1 - f0) * k
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


mix = np.zeros((2, N))


# ---------------------------------------------------------------- 1. firtina bedi
rumble = lowpass(brown(N), 90, order=3)
bed_env = np.clip(np.interp(T, [0.0, 0.6, 2.4, 2.6, 11.2, 13.6, 15.0],
                            [0.0, 0.55, 0.95, 0.75, 0.70, 0.45, 0.0]), 0, 1)
mix[0] += rumble * bed_env * 0.55
mix[1] += np.roll(rumble, 311) * bed_env * 0.55

rain = highpass(noise(N), 3000, order=2) * 0.012
rain_env = np.clip(np.interp(T, [0, 0.4, 2.6, 6.0, 15.0], [0, 1.0, 0.7, 0.25, 0.0]), 0, 1)
mix[0] += rain * rain_env
mix[1] += np.roll(rain, 173) * rain_env


# ---------------------------------------------------------------- 2. simsek craklari
def thunder(dur=2.0, bright=1.0):
    n = int(SR * dur)
    crack = bandpass(noise(n), 300 * bright, 5200 * bright, order=2) * env(n, 0.002, dur * 0.25, 3.0)
    body = lowpass(brown(n), 160, order=3) * env(n, 0.01, dur * 0.9, 1.2)
    return crack * 0.7 + body * 1.0


add(mix, thunder(1.8, 1.0), 0.30, 0.55, -0.35)
add(mix, thunder(2.4, 0.7), 1.10, 0.70, 0.30)
add(mix, thunder(1.2, 1.2), 1.95, 0.35, 0.10)


# ---------------------------------------------------------------- 3. cekic darbesi
def metal_ring(dur=2.2, gain=1.0):
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f, a, d in [(1180, 1.0, 2.4), (1790, 0.6, 3.1), (2470, 0.4, 4.0),
                    (3310, 0.25, 5.2), (4630, 0.15, 6.8)]:
        out += a * np.sin(2 * np.pi * f * t + rng.random() * 6.28) * np.exp(-d * t)
    return out / 2.4 * gain


def impact(size=1.0):
    dur = 1.6 * size
    n = int(SR * dur)
    sub = sweep(dur, 115 * size, 34, shape=0.45) * env(n, 0.003, dur * 0.7, 1.6)
    punch = lowpass(noise(n), 900, order=2) * env(n, 0.001, 0.22 * size, 3.0)
    return sub * 1.0 + punch * 0.45


add(mix, impact(1.0), 2.60, 0.95, 0.0)
add(mix, metal_ring(2.6, 1.0), 2.60, 0.28, 0.0)

add(mix, impact(0.7), 5.60, 0.55, -0.15)
add(mix, metal_ring(1.6, 0.7), 5.60, 0.14, -0.2)

add(mix, impact(0.8), 8.20, 0.62, 0.15)
add(mix, metal_ring(1.8, 0.8), 8.20, 0.16, 0.2)


# ---------------------------------------------------------------- 4. epik drone
def drone(start, end, freqs, gain):
    n = int((end - start) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f, a in freqs:
        det = 1.0 + 0.0016 * np.sin(2 * np.pi * 0.17 * t + f)
        out += a * np.sin(2 * np.pi * f * det * t)
        out += a * 0.32 * np.sin(2 * np.pi * 2 * f * det * t + 1.1)
        out += a * 0.14 * np.sin(2 * np.pi * 3 * f * det * t + 2.3)
    out /= max(sum(a for _, a in freqs) * 1.5, 1e-6)
    fade = np.clip(np.minimum(t / 0.9, (t[-1] - t) / 1.4), 0, 1)
    trem = 0.86 + 0.14 * np.sin(2 * np.pi * 0.7 * t)
    return out * fade * trem * gain


add(mix, drone(2.5, 11.4, [(73.42, 1.0), (110.0, 0.55), (146.83, 0.35)], 0.30), 2.50, 1.0, -0.12)
add(mix, drone(2.5, 11.4, [(73.42, 1.0), (110.0, 0.50), (220.0, 0.16)], 0.30), 2.52, 1.0, 0.12)

# final akor (D moll genis) 11.2 -> 14.8
add(mix, drone(11.2, 14.8, [(73.42, 1.0), (110.0, 0.6), (174.61, 0.34), (220.0, 0.24)], 0.40),
    11.20, 1.0, -0.1)
add(mix, drone(11.2, 14.8, [(73.42, 1.0), (110.0, 0.6), (293.66, 0.18)], 0.40), 11.22, 1.0, 0.1)


# ---------------------------------------------------------------- 5. nabiz / ritim
BPM = 84.0
beat = 60.0 / BPM
nb = int(SR * 0.26)
tb = np.arange(nb) / SR
pulse = np.sin(2 * np.pi * 52 * tb) * np.exp(-14 * tb)
pulse += lowpass(noise(nb), 240, order=2) * np.exp(-40 * tb) * 0.35
k = 0
while 2.60 + k * beat < 11.0:
    at = 2.60 + k * beat
    g = 0.30 if k % 2 == 0 else 0.17
    if at > 9.8:
        g *= 1.35
    add(mix, pulse, at, g, 0.0)
    k += 1


# ---------------------------------------------------------------- 6. whoosh gecisler
def whoosh(dur=0.55, up=True):
    n = int(SR * dur)
    t = np.arange(n) / SR
    x = noise(n)
    out = np.zeros(n)
    seg = 12
    for i in range(seg):
        a, b = int(n * i / seg), int(n * (i + 1) / seg)
        frac = i / (seg - 1)
        fc = 400 + 5200 * (frac if up else 1 - frac)
        out[a:b] = bandpass(x[a:b], fc * 0.55, fc * 1.9, order=2)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    return out * e / (np.max(np.abs(out)) or 1)


for at, pan in [(5.20, -0.7), (7.80, 0.7), (10.45, -0.5)]:
    w = whoosh(0.6, up=True)
    add(mix, w, at, 0.30, pan)
    add(mix, w, at + 0.06, 0.22, -pan)


# ---------------------------------------------------------------- 7. shimmer / ting
def ting(f0=2093.0, dur=1.8):
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m, a, d in [(1.0, 1.0, 2.2), (2.01, 0.5, 3.4), (3.02, 0.3, 4.6), (4.97, 0.16, 6.2)]:
        out += a * np.sin(2 * np.pi * f0 * m * t) * np.exp(-d * t)
    return out / 2.0


for i, at in enumerate([8.75, 9.25, 9.75, 10.25]):
    add(mix, ting(2093.0 * (1.0 + 0.12 * i)), at, 0.115, -0.5 + i * 0.33)


# ---------------------------------------------------------------- 8. riser + final
rn = int(SR * 1.5)
rt = np.arange(rn) / SR
riser = np.zeros(rn)
seg = 24
rx = noise(rn)
for i in range(seg):
    a, b = int(rn * i / seg), int(rn * (i + 1) / seg)
    fc = 500 + 7000 * (i / (seg - 1)) ** 1.7
    riser[a:b] = highpass(rx[a:b], fc, order=2)
riser *= (rt / rt[-1]) ** 2.2
riser += sweep(1.5, 180, 900, shape=2.4) * (rt / rt[-1]) ** 3 * 0.35
add(mix, riser / (np.max(np.abs(riser)) or 1), 9.70, 0.30, 0.0)

add(mix, impact(1.15), 11.20, 1.0, 0.0)
add(mix, metal_ring(3.4, 1.0), 11.20, 0.32, 0.0)
cn = int(SR * 3.0)
crash = highpass(noise(cn), 2600, order=2) * np.exp(-np.linspace(0, 7, cn))
add(mix, crash, 11.20, 0.22, -0.3)
add(mix, crash, 11.21, 0.22, 0.3)


# ---------------------------------------------------------------- 9. reverb + master
def reverb(x, dur=1.5, wet=0.22):
    ln = int(SR * dur)
    ir = noise(ln) * np.exp(-np.linspace(0, 6.5, ln))
    ir = lowpass(ir, 5200, order=2)
    ir[: int(SR * 0.012)] = 0
    ir /= np.sqrt(np.sum(ir ** 2)) or 1
    nfft = 1 << int(np.ceil(np.log2(len(x) + ln)))
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
    return (1 - wet) * x + wet * y * 2.2


for ch in (0, 1):
    mix[ch] = reverb(mix[ch], 1.6, 0.20)

# genel zarf: bas ve son yumusatma
master_env = np.clip(np.interp(T, [0.0, 0.08, 14.2, 15.0], [0.0, 1.0, 1.0, 0.0]), 0, 1)
mix *= master_env

# soft-clip limiter
peak = np.max(np.abs(mix))
mix = mix / (peak or 1) * 1.25
mix = np.tanh(mix) / np.tanh(1.25) * 0.92

out = np.clip(mix.T, -1, 1)
pcm = (out * 32767).astype("<i2")

path = sys.argv[1] if len(sys.argv) > 1 else "soundtrack.wav"
with wave.open(path, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())

print(f"OK {path}  {DUR:.1f}s  peak={np.max(np.abs(out)):.3f}  rms={np.sqrt(np.mean(out**2)):.3f}")
