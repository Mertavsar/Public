#!/usr/bin/env python3
"""
Efekt ve müzik yatağını üretir. Hazır ses kütüphanesi yok (ağ kapalı), o yüzden
her şey sentezleniyor: vuruş, whoosh, klink, riser, sub-drop ve altta dönen
ritim + pad.

Zamanlar EDL'den gelir — her ses bir KESİMLE aynı karede başlar. Rastgele
serpilen efekt kurguyu desteklemez, dağıtır.

    python3 audiobed.py --dur 24.40 \
        --major 0.00:0.72 4.73:0.48 13.62:0.58 \
        --minor 1.78 3.25 5.33 \
        --riser 13.62 22.19 \
        --out-sfx sfx.wav --out-music music.wav

major   ana vuruş (anlatının döndüğü kesim). t:genlik, genlik 0.4–0.75.
minor   klink (diğer kesimler). Genliği sabit.
riser   o ana doğru tırmanan gerilim + sub-drop.
duck    o andan sonra müzik yatağını kıs (ödül cümlesi nefes alsın).
warm-at anlatı döndüğü an: yatak gerginden (minör, hi-hat'li) sıcağa
        (majör altılı, pad öne çıkmış, vuruş yumuşamış) döner.

Not: 45 Hz altı kesiliyor. Telefon hoparlöründe duyulmuyor ama master
limiterini boşuna çalıştırıp sesi kısıyor.
"""
import argparse, wave
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100


def _norm(s, a):
    m = np.max(np.abs(s))
    return s / m * a if m > 0 else s


class Bus:
    def __init__(self, dur):
        self.n = int(SR * dur)
        self.x = np.zeros(self.n)

    def place(self, sig, t):
        i = int(t * SR)
        if i < 0:
            sig = sig[-i:]
            i = 0
        j = min(self.n, i + len(sig))
        if j > i:
            self.x[i:j] += sig[:j - i]

    def write(self, path, hp, peak=0.80):
        y = sosfilt(butter(2, hp, btype="high", fs=SR, output="sos"), self.x)
        raw = np.max(np.abs(y))
        y = y / raw * peak if raw > 0 else y
        w = wave.open(path, "w")
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
        w.close()
        return raw


def boom(rng, dur=1.1, f0=320, f1=130, amp=0.55):
    """Vuruş. Enerjinin çoğu 300–1000 Hz'de olmalı.

    İlk sürüm 95→42 Hz süpürüyordu ve enerjisinin %95'i 120 Hz altındaydı —
    telefon hoparlöründe hiç duyulmuyordu (ölçüldü). Referans videonun sesinin
    %64'ü 300 Hz–1 kHz bandında. Gövde o banda taşındı; sub sadece dokunuş
    olarak kaldı, kulak onu telefonda hissetmese de iyi hoparlörde duyuyor."""
    t = np.arange(int(SR * dur)) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.10)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.20)
    ring = np.sin(2 * np.pi * 520 * t) * np.exp(-t / 0.09) * 0.55
    crack = sosfilt(butter(2, [400, 2400], btype="band", fs=SR, output="sos"),
                    rng.standard_normal(len(t)) * np.exp(-t / 0.020)) * 0.85
    sub = np.sin(2 * np.pi * 55.0 * t) * np.exp(-t / 0.30) * 0.22
    return _norm(body + ring + crack + sub, amp)


def _sweep(rng, n, f_lo, f_hi, power):
    x = rng.standard_normal(n)
    out = np.zeros(n)
    for k in range(0, n, 256):
        fc = f_lo + (f_hi - f_lo) * (k / n) ** power
        sos = butter(2, [max(80, fc * 0.55), min(SR / 2 - 200, fc * 1.9)],
                     btype="band", fs=SR, output="sos")
        out[k:k + 256] = sosfilt(sos, x[k:k + 256])
    return out


def whoosh(rng, dur=0.40, amp=0.26):
    n = int(SR * dur); t = np.arange(n) / SR
    env = (t / dur) ** 2.2 * np.exp(-((t - dur * 0.88) / (dur * 0.5)) ** 2)
    return _norm(_sweep(rng, n, 350, 3800, 1.5) * env / env.max(), amp)


def tick(rng, amp=0.22):
    """Kesim tıkı — 'klink'. Kısa, parlak, metalik. Zaten duyulur bandda,
    sadece seviyesi düşüktü."""
    n = int(SR * 0.10); t = np.arange(n) / SR
    c = sosfilt(butter(2, [1200, 7000], btype="band", fs=SR, output="sos"),
                rng.standard_normal(n) * np.exp(-t / 0.007))
    tone = (np.sin(2 * np.pi * 1180 * t) + 0.7 * np.sin(2 * np.pi * 1760 * t)) * np.exp(-t / 0.035)
    return _norm(c + tone * 0.8, amp)


def riser(rng, dur=1.35, amp=0.26):
    n = int(SR * dur); t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * np.cumsum(np.linspace(180, 760, n)) / SR) * 0.35
    return _norm((_sweep(rng, n, 260, 2860, 2.0) + tone) * (t / dur) ** 2.6, amp)


def subdrop(dur=1.6, amp=0.38):
    """Düşen ton. Sadece sub olursa telefonda yok; duyulur bandda bir eş
    düşüş ekleniyor."""
    t = np.arange(int(SR * dur)) / SR
    lo = np.sin(2 * np.pi * np.cumsum(58 * np.exp(-t / 0.55) + 26) / SR) * np.exp(-t / 0.5) * 0.35
    mid = np.sin(2 * np.pi * np.cumsum(660 * np.exp(-t / 0.45) + 180) / SR) * np.exp(-t / 0.42)
    return _norm(mid + lo, amp)


def build_sfx(dur, major, minor, risers, out):
    rng = np.random.default_rng(12345)
    bus = Bus(dur)
    for t, a in major:
        bus.place(boom(rng, amp=a), t - 0.02)
        bus.place(whoosh(rng, amp=0.32 if a >= 0.58 else 0.24), t - 0.36)
    for t in minor:
        bus.place(tick(rng), t - 0.01)
    for t in risers:
        bus.place(riser(rng, amp=0.28), t - 1.35)
        bus.place(subdrop(amp=0.36), t)
    raw = bus.write(out, 80)
    print(f"{out}  {dur:.2f}s  ham tepe {raw:.2f}  "
          f"{len(major)} vuruş + {len(minor)} klink + {len(risers)} riser")


def build_music(dur, out, bpm=102.0, peak_at=None, duck=(), warm_at=None):
    """Kesintisiz yatak. Referans stilde 58 saniyede sıfır sessizlik var:
    boşluk bırakmak bu formatta izleyiciyi kaydırtıyor.

    warm_at: anlatı döndüğü an (s). O ana kadar gergin — dar, minör, tok bir
    yatak; sonrasında sıcak — pad öne çıkıyor, majör altılı açılıyor, vuruş
    yumuşuyor. Kullanıcının istediği "gerilimden duygusal sinematiğe geçiş"
    budur; ayrı iki parça yerine tek yatağın rengi değişiyor, böylece geçişte
    dikiş duyulmuyor."""
    rng = np.random.default_rng(5)
    bus = Bus(dur)
    beat = 60.0 / bpm
    peak_at = peak_at if peak_at else dur * 0.9

    def env(n, a, d):
        e = np.ones(n); na, nd = int(a * SR), int(d * SR)
        if na: e[:na] = np.linspace(0, 1, na)
        if nd: e[-nd:] *= np.linspace(1, 0, nd)
        return e

    def kick(amp):
        """Kick'e orta bandda bir 'tok' ekleniyor; sadece 44 Hz telefonda yok."""
        n = int(SR * 0.34); tt = np.arange(n) / SR
        f = 95 + 260 * np.exp(-tt / 0.028)
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.10)
        knock = sosfilt(butter(2, [300, 1600], btype="band", fs=SR, output="sos"),
                        rng.standard_normal(n) * np.exp(-tt / 0.012)) * 0.6
        return _norm(body + knock, amp)

    def pluck(freq, amp, d=0.42):
        """Duyulur banddaki tek kanal. Referansın enerjisinin %64'ü burada."""
        n = int(SR * d); tt = np.arange(n) / SR
        s_ = sum(g * np.sin(2 * np.pi * freq * k * tt)
                 for k, g in ((1, 1.0), (2, 0.5), (3, 0.28), (4, 0.14)))
        return _norm(s_, amp) * np.exp(-tt / (d * 0.32))

    def sub(note, d, amp):
        n = int(SR * d); tt = np.arange(n) / SR
        s = np.sin(2 * np.pi * note * tt) + 0.25 * np.sin(4 * np.pi * note * tt)
        return _norm(s, amp) * env(n, 0.008, min(0.12, d * 0.5))

    def hat(amp, d=0.05):
        n = int(SR * d); x = rng.standard_normal(n)
        y = np.diff(np.concatenate([[0], np.diff(np.concatenate([[0], x]))]))
        return _norm(y, amp) * np.exp(-np.arange(n) / SR / 0.012)

    def pad(freqs, d, amp):
        n = int(SR * d); tt = np.arange(n) / SR; s = np.zeros(n)
        for f in freqs:
            for k, g in ((1, 1.0), (2, 0.35), (3, 0.18)):
                s += g * np.sin(2 * np.pi * f * k * tt + rng.uniform(0, 6.28))
        lfo = 0.55 + 0.45 * np.sin(2 * np.pi * tt / 7.0)
        return _norm(s, 1.0) * amp * lfo * env(n, 1.2, 1.5)

    # A-bölümü: Am (gergin, dar).  B-bölümü: F-majör altılı (sıcak, açık).
    # Pad bir oktav yukari: 110 Hz'lik bir pad telefonda duyulmuyor.
    TENSE = [220.0, 261.63, 329.63]          # A  C  E
    WARM = [349.23, 261.63, 440.0, 523.25]   # F  C  A  C
    if warm_at and 0 < warm_at < dur:
        bus.place(pad(TENSE, warm_at + 0.6, 0.085), 0.1)
        bus.place(pad(WARM, dur - warm_at - 0.1, 0.135), warm_at - 0.5)
    else:
        bus.place(pad(TENSE, dur - 0.2, 0.085), 0.1)

    k, t = 0, 0.0
    while t < dur - 0.5:
        I = 0.52 + 0.48 * min(1.0, (t / peak_at) ** 1.3)
        warm = warm_at is not None and t >= warm_at
        if k % 2 == 0:
            bus.place(kick((0.34 if warm else 0.50) * I), t)
        bus.place(sub(164.81 if (k // 2) % 4 < 2 else 196.0, beat * 0.46,
                      (0.10 if warm else 0.13) * I), t)
        # arpej: duyulur banddaki asil tasiyici
        arp = ([440.0, 523.25, 659.25, 523.25] if warm else
               [440.0, 523.25, 587.33, 523.25])
        bus.place(pluck(arp[k % 4], (0.30 if warm else 0.24) * I), t + beat * 0.25)
        if k % 4 == 2:
            bus.place(pluck(arp[(k + 2) % 4] * 2, 0.16 * I, 0.30), t + beat * 0.75)
        if not warm:                          # hi-hat gerilimi taşıyor,
            bus.place(hat(0.055 * I), t + beat * 0.5)   # sıcak bölümde susuyor
            if k % 8 == 7:
                bus.place(hat(0.075 * I, 0.09), t + beat * 0.75)
        t += beat; k += 1

    tt = np.arange(bus.n) / SR
    g = np.clip(tt / 0.8, 0, 1) * np.clip((dur - tt) / 1.2, 0, 1)
    # Ödül cümlesi ("cevap" satırı) müziğin altında boğulmasın diye o andan
    # itibaren yatağı geri çek; kapanışta geri getir.
    for t, gain in duck:
        g *= np.where(tt > t, gain, 1.0)
    bus.x *= g
    bus.write(out, 125, peak=0.85)
    print(f"{out}  {dur:.2f}s  {bpm:.0f} BPM  {k} vuruş")


# ---------------------------------------------------------------------------
# SİNEMATİK SET (varsayılan). Kullanıcı: "giriş sesi, geçiş efekt sesleri daha
# dikkat çekici olsun". Eski set (boom + whoosh + tık) tek katmanlıydı; Shorts'ta
# dikkat çeken sesler katmanlı: keskin transient + gövde + parlak kuyruk.
# Hepsinin enerjisi 300–4000 Hz'de — telefon hoparlörünün çaldığı band.
# ---------------------------------------------------------------------------
def _sat(x, drive=1.8):
    """Hafif doyum: tepeyi yükseltmeden algılanan sesi büyütür."""
    return np.tanh(x * drive) / np.tanh(drive)


def impact(rng, amp=0.62):
    """Sinematik darbe: tık (2–6 kHz) + yumruk (1200→250 Hz) + gövde gürültüsü
    + metalik parıltı kuyruğu (uyumsuz kısmi tonlar)."""
    n = int(SR * 1.3); t = np.arange(n) / SR
    click = sosfilt(butter(2, [2000, 6000], btype="band", fs=SR, output="sos"),
                    rng.standard_normal(n) * np.exp(-t / 0.004))
    f = 250 + 950 * np.exp(-t / 0.018)
    punch = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    body = sosfilt(butter(2, [400, 1800], btype="band", fs=SR, output="sos"),
                   rng.standard_normal(n) * np.exp(-t / 0.09))
    shimmer = sum(g * np.sin(2 * np.pi * fr * (1 + rng.uniform(-.004, .004)) * t)
                  * np.exp(-t / d) for fr, g, d in
                  ((587, .30, .9), (881, .26, .7), (1319, .22, .55), (1976, .16, .4), (2637, .10, .3)))
    return _norm(_sat(click * 0.9 + punch * 1.0 + body * 0.7 + shimmer * 0.55), amp)


def swoosh(rng, dur=0.36, amp=0.34):
    """Geçiş: bant süpürmesi 500→5000 Hz, sona doğru tepe, altında 'zip' tonu."""
    n = int(SR * dur); t = np.arange(n) / SR
    env = (t / dur) ** 1.8 * np.exp(-((t - dur * 0.9) / (dur * 0.35)) ** 2)
    air = _sweep(rng, n, 500, 5000, 1.3)
    zip_ = np.sin(2 * np.pi * np.cumsum(np.linspace(380, 2100, n)) / SR) * 0.25
    return _norm((air + zip_) * env / env.max(), amp)


def ding(amp=0.40, f0=2093.0):
    """Açılış çanı — 'dikkat!' sesi. Parlak, 0.9s sönümlü."""
    n = int(SR * 1.0); t = np.arange(n) / SR
    s_ = sum(g * np.sin(2 * np.pi * f0 * k * t) * np.exp(-t / d)
             for k, g, d in ((1, 1.0, .45), (2.76, .45, .22), (5.4, .20, .10), (0.5, .25, .6)))
    return _norm(s_ * (1 - np.exp(-t / 0.002)), amp)


def pop(rng, amp=0.30):
    """Ara kesim: yukarı kayan kısa ton + tık — 'klink'ten daha belirgin."""
    n = int(SR * 0.12); t = np.arange(n) / SR
    f = 700 + 1500 * (t / t[-1]) ** 0.6
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.035)
    c = sosfilt(butter(2, [1500, 6000], btype="band", fs=SR, output="sos"),
                rng.standard_normal(n) * np.exp(-t / 0.003)) * 0.6
    return _norm(tone + c, amp)


def build_sfx_cinematic(dur, major, minor, risers, out):
    rng = np.random.default_rng(777)
    bus = Bus(dur)
    for i, (t, a) in enumerate(major):
        bus.place(impact(rng, amp=min(0.75, a + 0.10)), t - 0.01)
        if t > 0.4:                          # açılışta önden gelen ses yok
            bus.place(swoosh(rng, amp=0.36 if a >= 0.58 else 0.30), t - 0.33)
        if t < 0.05:                         # açılış: darbe + çan
            bus.place(ding(), 0.03)
    for t in minor:
        bus.place(pop(rng), t - 0.01)
    for t in risers:
        if t > 1.4:
            bus.place(riser(rng, amp=0.30), t - 1.35)
        bus.place(subdrop(amp=0.22), t)
    raw = bus.write(out, 80)
    print(f"{out}  {dur:.2f}s  ham tepe {raw:.2f}  SİNEMATİK: "
          f"{len(major)} darbe + {len(minor)} pop + {len(risers)} riser")


# Acıklı yatak (mood="sad"). Kurtarma/terk edilme gibi duygusal hikâyelerde
# tempolu yatak yanlış duruyor — kullanıcı "acıklı bir müzik koy" dedi.
# Am–F–C–G: klasik hüzün ilerlemesi. Kick ve hi-hat yok; ritmi bas nabzı
# taşıyor, yoksa drone'a düşer (SKILL.md §6: "drone değil").
# Frekanslar bilerek 170–800 Hz'de: telefon hoparlörü 120 Hz altını çalmıyor.
SAD_PROG = [
    (220.00, [220.00, 261.63, 329.63], [440.00, 523.25, 659.25, 523.25]),  # Am
    (174.61, [174.61, 220.00, 261.63], [349.23, 440.00, 523.25, 440.00]),  # F
    (261.63, [261.63, 329.63, 392.00], [523.25, 659.25, 783.99, 659.25]),  # C
    (196.00, [196.00, 246.94, 293.66], [392.00, 493.88, 587.33, 493.88]),  # G
]


def build_music_sad(dur, out, bpm=64.0, peak_at=None, duck=()):
    rng = np.random.default_rng(11)
    bus = Bus(dur)
    beat = 60.0 / bpm
    bar = beat * 4
    peak_at = peak_at if peak_at else dur * 0.88

    def env(n, a, d):
        e = np.ones(n); na, nd = int(a * SR), int(d * SR)
        if na: e[:na] = np.linspace(0, 1, na)
        if nd: e[-nd:] *= np.linspace(1, 0, nd)
        return e

    def piano(freq, amp, d=1.7):
        """Yüksek harmonikler önce sönüyor — piyanoyu piyano yapan bu."""
        n = int(SR * d); tt = np.arange(n) / SR; s_ = np.zeros(n)
        for k, g in ((1, 1.0), (2, 0.42), (3, 0.20), (4, 0.10), (5, 0.05)):
            s_ += g * np.sin(2 * np.pi * freq * k * tt) * np.exp(-tt / (d * 0.40 / k ** 0.6))
        return _norm(s_, amp)

    def strings(freqs, d, amp):
        n = int(SR * d); tt = np.arange(n) / SR; s_ = np.zeros(n)
        vib = np.cumsum(1.0 + 0.005 * np.sin(2 * np.pi * 5.1 * tt)) / SR
        for f in freqs:
            for k, g in ((1, 1.0), (2, 0.45), (3, 0.22), (4, 0.10)):
                s_ += g * np.sin(2 * np.pi * f * k * vib + rng.uniform(0, 6.28))
        return _norm(s_, 1.0) * amp * env(n, 0.9, 1.0)

    def pulse(note, amp, d=0.55):
        """Kick yerine yumuşak bas nabzı — kalp atışı gibi, vurmuyor."""
        n = int(SR * d); tt = np.arange(n) / SR
        s_ = np.sin(2 * np.pi * note * tt) + 0.30 * np.sin(4 * np.pi * note * tt)
        return _norm(s_, amp) * env(n, 0.02, d * 0.75)

    t, b = 0.0, 0
    while t < dur - 0.3:
        root, chord, arp = SAD_PROG[b % len(SAD_PROG)]
        I = 0.55 + 0.45 * min(1.0, (t / peak_at) ** 1.2)
        bus.place(strings(chord, min(bar + 0.7, dur - t), 0.115 * I), t)
        bus.place(pulse(root, 0.13 * I), t)
        bus.place(pulse(root, 0.085 * I), t + bar * 0.5)
        for j in range(4):                       # arpej: duyulur banddaki taşıyıcı
            bus.place(piano(arp[j], (0.26 if j % 2 == 0 else 0.19) * I), t + j * beat)
        if b % 4 == 3:                           # dönüş öncesi tek yüksek nota
            bus.place(piano(arp[1] * 2, 0.11 * I, 2.2), t + beat * 3.5)
        t += bar; b += 1

    tt = np.arange(bus.n) / SR
    g = np.clip(tt / 1.6, 0, 1) * np.clip((dur - tt) / 1.8, 0, 1)
    for t_, gain in duck:
        g *= np.where(tt > t_, gain, 1.0)
    bus.x *= g
    bus.write(out, 125, peak=0.85)
    print(f"{out}  {dur:.2f}s  {bpm:.0f} BPM  {b} bar  (acikli: Am-F-C-G)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--major", nargs="*", default=[], help="t:genlik")
    ap.add_argument("--minor", nargs="*", type=float, default=[])
    ap.add_argument("--riser", nargs="*", type=float, default=[])
    ap.add_argument("--bpm", type=float, default=102.0)
    ap.add_argument("--peak-at", type=float, default=None,
                    help="müziğin doruğa çıktığı an (s)")
    ap.add_argument("--duck", nargs="*", default=[],
                    help="t:kazanç — o andan sonra müzik yatağını çarp (0.78 iyi)")
    ap.add_argument("--sfx-style", choices=["cinematic", "classic"], default="cinematic",
                    help="cinematic: katmanlı darbe+çan+swoosh+pop · classic: eski boom+tık")
    ap.add_argument("--mood", choices=["drive", "sad"], default="drive",
                    help="drive: tempolu yatak · sad: acıklı piyano+yaylı (Am-F-C-G)")
    ap.add_argument("--warm-at", type=float, default=None,
                    help="bu andan sonra yatak gerginden sıcağa döner (s)")
    ap.add_argument("--out-sfx", default="sfx.wav")
    ap.add_argument("--out-music", default="music.wav")
    a = ap.parse_args()
    major = [(float(s.split(":")[0]), float(s.split(":")[1])) for s in a.major]
    (build_sfx_cinematic if a.sfx_style == "cinematic" else build_sfx)(
        a.dur, major, a.minor, a.riser, a.out_sfx)
    duck = [(float(d.split(":")[0]), float(d.split(":")[1])) for d in a.duck]
    if a.mood == "sad":
        build_music_sad(a.dur, a.out_music, a.bpm if a.bpm != 102.0 else 64.0,
                        a.peak_at, duck)
    else:
        build_music(a.dur, a.out_music, a.bpm, a.peak_at, duck, a.warm_at)


if __name__ == "__main__":
    main()
