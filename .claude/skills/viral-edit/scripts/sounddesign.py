#!/usr/bin/env python3
"""
Belgesel / gizem fonu + yumuşak geçiş sesleri (sentez, ağ gerekmez).

audiobed.py'nin "drive" yatağı ve vuruşları kullanıcıya "gong sesi, berbat"
geldi: tonal çınlayan impact'ler ve öne çıkan ritim. Burada:
  - vuruş yok; geçişte yalnız filtrelenmiş hava sesi (whoosh) ve çok alçak,
    tonsuz bir sub nefesi (50 Hz, 0.25 sn) — çınlamaz
  - müzik bölümlü: gerilim (pad + kalp atışı) → açılış (arpej) → yükseliş
    (parlaklık) → geri çekilme (soru). Bölüm sınırları anlatının döndüğü an.
  - konuşma varken müzik kendiliğinden kısılır (sidechain)

    python3 sounddesign.py --vo vo.wav --dur 36.7 --out mix.wav \
        --whoosh 2.35 4.10 ... --big 13.00 25.00 \
        --reveal 13.00 --lift 25.00 --outro 32.35
"""
import argparse, subprocess, wave
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
rng = np.random.default_rng(7)


def lp(x, f, o=2):
    return sosfilt(butter(o, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, btype="high", fs=SR, output="sos"), x)


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [lo, hi], btype="band", fs=SR, output="sos"), x)


def nf(m):  # MIDI -> Hz
    return 440.0 * 2 ** ((m - 69) / 12)


def place(bus, sig, t):
    i = int(t * SR)
    if i < 0:
        sig, i = sig[-i:], 0
    j = min(len(bus), i + len(sig))
    if j > i:
        bus[i:j] += sig[:j - i]


def env_adsr(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


# ---------------- müzik ----------------
def pad_voice(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for det in (-0.004, 0.0, 0.0045):          # hafif koro
        f = freq * (1 + det)
        for h in range(1, 7):
            s += np.sin(2 * np.pi * f * h * t + rng.uniform(0, 6.28)) / h ** 1.3
    return s


def pluck(freq, dur=0.9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t)
         + 0.12 * np.sin(2 * np.pi * 3 * freq * t))
    return s * np.exp(-t / 0.28) * env_adsr(n, 0.004, 0.05)


def bell(freq, dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t / 0.2)
    return s * np.exp(-t / 0.7) * env_adsr(n, 0.01, 0.1)


def heartbeat(freq=68.0):
    n = int(0.32 * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.6 * np.exp(-t / 0.03))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)


def music(dur, reveal, lift, outro, bpm=90.0, mood="mystery", build=False):
    beat = 60.0 / bpm
    bar = 4 * beat
    if mood == "warm":
        # F – C – Am – G (IV–I–vi–V): umut, kurtarma / bakım hikâyesi
        prog = [(41, [65, 69, 72]), (48, [64, 67, 72]), (45, [64, 69, 72]), (43, [62, 67, 71])]
    else:
        # Dm – Bb – Gm – A  (i–VI–iv–V): gizem, sonda gerilim çözülmeden döner
        prog = [(50, [62, 65, 69]), (46, [62, 65, 70]), (43, [62, 67, 70]), (45, [61, 64, 69])]
    n = int(dur * SR) + SR
    padb, arp, shim, hb, shk = (np.zeros(n) for _ in range(5))
    nb = int(np.ceil(dur / bar)) + 1
    for b in range(nb):
        t0 = b * bar
        root, ch = prog[b % 4]
        # pad: her akor bir ölçü, üst üste binerek
        for m in [root] + ch:
            v = pad_voice(nf(m), bar + 1.2) * env_adsr(int((bar + 1.2) * SR), 0.9, 1.2)
            place(padb, v * (0.55 if m == root else 0.30), t0)
        for k in range(8):                     # 8'lik arpej
            t = t0 + k * beat / 2
            if reveal <= t < outro:
                pat = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 24,
                       ch[2] + 12, ch[0] + 24, ch[1] + 12, ch[2] + 12]
                place(arp, pluck(nf(pat[k])) * (0.9 if k % 2 == 0 else 0.6), t)
            if lift <= t < outro and k % 4 == 0:
                place(shim, bell(nf(ch[k // 4 % 3] + 24)), t)
            if lift <= t < outro:
                nz = hp(rng.standard_normal(int(0.06 * SR)), 6000) * np.exp(
                    -np.arange(int(0.06 * SR)) / SR / 0.015)
                place(shk, nz * (0.5 if k % 2 else 0.25), t)
        for k in (0, 2):                       # kalp atışı: gerilim + soru bölümü
            t = t0 + k * beat
            if t < reveal or t >= outro:
                place(hb, heartbeat(), t)
                place(hb, 0.6 * heartbeat(), t + 0.24)
    padb = lp(padb, 1400)
    arp = lp(arp, 3500)
    # arpeje hafif eko (mekân)
    d = int(beat * 0.75 * SR)
    for g in (0.35, 0.15):
        arp[d:] += g * arp[:-d].copy()
        d *= 2
    tt = np.arange(n) / SR
    # bölüm seviyeleri (yumuşak geçişli)
    def ramp(t_on, t_off=None, fade=0.6):
        g = np.clip((tt - t_on) / fade + 1, 0, 1) if t_on > 0 else np.ones(n)
        if t_off is not None:
            g *= np.clip((t_off - tt) / fade, 0, 1)
        return g
    pad_lvl = 0.55 + 0.25 * ramp(lift) * ramp(0, outro)
    arp_lvl = ramp(reveal, outro + 0.8)
    if build:   # "müzik giderek yükselsin": reveal'dan lift'e doğrusal tırmanış
        arp_lvl = arp_lvl * np.clip(0.35 + 0.65 * (tt - reveal) / max(0.1, lift - reveal), 0.35, 1.0)
    mix = (padb * pad_lvl * 0.9 + arp * 0.55 * arp_lvl
           + shim * 0.22 * ramp(lift, outro + 0.8) + shk * 0.10 * ramp(lift, outro)
           + hb * 0.9)
    # gerilim bölümünde tırmanan hava: reveal'a doğru
    rn = int(1.6 * SR)
    ris = bp(rng.standard_normal(rn), 400, 5000) * np.linspace(0, 1, rn) ** 2
    place(mix, ris * 0.35, reveal - 1.6)
    mix = hp(mix, 45)
    mix *= np.clip((dur + 0.1 - tt) / 1.2, 0, 1)   # sonda sön
    return mix[:int(dur * SR)]


# ---------------- geçiş sesleri ----------------
def whoosh(dur=0.42, peak=0.62, lo=300, hi=6000):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    t = np.linspace(0, 1, n)
    # zamanla değişen band: tepe noktasına doğru açılır, sonra kapanır
    out = np.zeros(n)
    seg = 256
    for i in range(0, n, seg):
        u = t[i]
        f = lo + (hi - lo) * np.exp(-((u - peak) / 0.22) ** 2)
        out[i:i + seg] = x[i:i + seg]
        out[i:i + seg] = lp(x[max(0, i - 2048):i + seg], max(200, f), 1)[-len(out[i:i + seg]):]
    e = np.exp(-((t - peak) / 0.25) ** 2)
    return hp(out, 150) * e


def subbreath(dur=0.45):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 48 * t) * np.exp(-t / 0.14) * env_adsr(n, 0.01, 0.05)


def boom(dur=1.1):
    """Bas vuruşu: perdesi düşen sub + kısa tık. Tiz çınlama YOK (gong değil)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 42 + 90 * np.exp(-t / 0.05)
    body = np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t / 0.32)
    # telefon hoparlörü 100 Hz altını çalmaz: 2. harmonik duyulan kısım
    body += 0.35 * np.sin(4 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2)
    click = lp(rng.standard_normal(n), 2500) * np.exp(-t / 0.006)
    return body + 0.5 * click


def rewind(dur):
    """Kaset geri sarma: hızla titreşen, perdesi yükselen bant gürültüsü."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n)
    seg = 220
    for i in range(0, n, seg):
        u = t[i] / dur
        fc = 700 + 2600 * u + 500 * np.sin(2 * np.pi * 24 * t[i])
        out[i:i + seg] = bp(x[max(0, i - 1024):i + seg], fc * 0.7, fc * 1.3, 1)[-len(out[i:i + seg]):]
    flutter = 0.6 + 0.4 * np.sin(2 * np.pi * 17 * t)
    return out * flutter * env_adsr(n, 0.03, 0.06)


def pop(amp=1.0):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    f = 300 + 700 * np.exp(-t / 0.01)
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.015)


def sfx(dur, whooshes, bigs, booms=(), rewinds=(), pops=()):
    n = int(dur * SR)
    bus = np.zeros(n)
    for t in booms:
        b = boom(); place(bus, b / np.max(np.abs(b)) * 1.0, t)
    for t0, t1 in rewinds:
        r = rewind(t1 - t0); place(bus, r / np.max(np.abs(r)) * 0.55, t0)
    for t in pops:
        place(bus, pop(0.35), t)
    for t in whooshes:
        w = whoosh()
        place(bus, w / np.max(np.abs(w)) * 0.55, t - 0.62 * 0.42)
    for t in bigs:
        w = whoosh(0.7, 0.75, 200, 7000)
        place(bus, w / np.max(np.abs(w)) * 0.7, t - 0.75 * 0.7)
        place(bus, subbreath() * 0.9, t)
    return bus


def read_wav(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f",
                          "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def write_wav(p, x):
    w = wave.open(p, "w")
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
    w.close()


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", required=True); ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--whoosh", nargs="*", type=float, default=[])
    ap.add_argument("--big", nargs="*", type=float, default=[])
    ap.add_argument("--reveal", type=float, required=True)
    ap.add_argument("--lift", type=float, required=True)
    ap.add_argument("--outro", type=float, required=True)
    ap.add_argument("--music-db", type=float, default=-19.0, help="müzik, sese göre (konuşmasız an)")
    ap.add_argument("--duck-db", type=float, default=-7.0, help="konuşma varken ek kısma")
    ap.add_argument("--sfx-db", type=float, default=-9.0)
    ap.add_argument("--mood", choices=["mystery", "warm"], default="mystery")
    ap.add_argument("--build", action="store_true", help="reveal→lift arası müzik giderek yükselir")
    ap.add_argument("--boom", nargs="*", type=float, default=[])
    ap.add_argument("--rewind", nargs="*", default=[], help="t0,t1")
    ap.add_argument("--pop", nargs="*", type=float, default=[])
    ap.add_argument("--mute", nargs="*", default=[], help="t0,t1: müziği kes (dramatik boşluk)")
    a = ap.parse_args()
    n = int(a.dur * SR)
    vo = np.zeros(n); v = read_wav(a.vo); vo[:min(n, len(v))] = v[:n]
    mu = music(a.dur, a.reveal, a.lift, a.outro, mood=a.mood, build=a.build)
    fx = sfx(a.dur, a.whoosh, a.big, a.boom,
             [tuple(float(v) for v in r.split(",")) for r in a.rewind], a.pop)
    vr = rms_db(vo[np.abs(vo) > 0.02]) if np.any(np.abs(vo) > 0.02) else -20
    mu *= 10 ** ((vr + a.music_db - rms_db(mu)) / 20)
    fx *= 10 ** ((vr + a.sfx_db - rms_db(fx[np.abs(fx) > 1e-3])) / 20) if np.any(fx) else 1
    # sidechain: konuşma zarfı -> müzik kısma (atak 30 ms, bırakma 350 ms)
    e = np.abs(vo)
    k = int(0.02 * SR)
    e = np.convolve(e, np.ones(k) / k, mode="same")
    act = (e > 0.02).astype(float)
    a_c, r_c = np.exp(-1 / (0.03 * SR)), np.exp(-1 / (0.35 * SR))
    g = np.zeros(n); s = 0.0
    for i in range(0, n, 64):                     # blok bazlı (hızlı)
        tgt = act[i]
        c = a_c if tgt > s else r_c
        s = tgt + (s - tgt) * c ** 64
        g[i:i + 64] = s
    mu *= 10 ** (a.duck_db * g / 20)
    tt = np.arange(n) / SR
    for m in a.mute:
        t0, t1 = (float(v) for v in m.split(","))
        mu *= np.clip(np.maximum((t0 - tt) / 0.02, (tt - t1) / 0.08), 0, 1)
    mix = vo + mu + fx
    # tepe sınırla, -14 LUFS'a yakın ses ffmpeg loudnorm ile
    write_wav(a.out + ".raw.wav", mix / max(1.0, np.max(np.abs(mix)) / 0.95))
    write_wav(a.out.replace(".wav", "_music.wav"), mu / max(1e-9, np.max(np.abs(mu))) * 0.9)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.out + ".raw.wav", "-af",
                    "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", a.out], check=True)
    print(f"müzik {a.music_db} dB (konuşmada {a.music_db + a.duck_db} dB) · "
          f"{len(a.whoosh)} whoosh · {len(a.big)} büyük geçiş -> {a.out}")


if __name__ == "__main__":
    main()
