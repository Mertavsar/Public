#!/usr/bin/env python3
"""
Seslendirmeyi sıkılaştırır: baştan kes, uzun sessizlikleri kısalt, atempo ile
hızlandır (perde korunur). Altyazı zamanlarını (sentalign çıktısı) aynı
zaman eşlemesiyle yeni sese taşır.

Her klipte elle yapılıyordu (kullanıcı: "sesi hızlandır, aradaki boşluklar çok
uzun"); tek komut oldu.

    python3 votight.py vo.wav vo_hizli.wav --start 14.9 --gap 0.15 --tempo 1.15 \
        --cap cap.json --cap-out cap_hizli.json

--start: sesin bu saniyesinden sonrasını kullan (cap.json zaten bu kesilmiş
sese göreyse --cap-offset 0 ver; varsayılan --start kadar kaydırır)
--target: tempo yerine hedef süre (sn) — tempo buna göre hesaplanır
"""
import argparse, json, subprocess
import numpy as np

SR = 48000


def load(p, start):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", p, "-ac", "1",
                        "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.float32).copy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--gap", type=float, default=0.15, help="sessizlik bu süreye indirilir")
    ap.add_argument("--min-sil", type=float, default=0.22, help="bundan kısa sessizliğe dokunma")
    ap.add_argument("--thr-db", type=float, default=-40)
    ap.add_argument("--tempo", type=float, default=1.0)
    ap.add_argument("--target", type=float)
    ap.add_argument("--cap"); ap.add_argument("--cap-out")
    ap.add_argument("--cap-offset", type=float)
    a = ap.parse_args()

    x = load(a.src, a.start)
    hop = int(SR * 0.01)
    n = len(x) // hop
    rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, 1) + 1e-12)
    db = 20 * np.log10(rms / (rms.max() + 1e-12))
    quiet = db < a.thr_db
    # sessiz koşular -> kısaltılacak parçalar (giriş/çıkışta 'gap/2' bırak)
    keep = np.ones(len(x), bool)
    segs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            dur = (j - i) * 0.01
            lead = i == 0
            if dur >= a.min_sil:
                h = a.gap / 2 if not lead else 0.03
                c0, c1 = int((i * 0.01 + h) * SR), int((j * 0.01 - (a.gap - h if not lead else 0.05)) * SR)
                if j >= n:                       # sondaki sessizlik: 0.25 sn kuyruk kalsın
                    c0, c1 = int((i * 0.01 + 0.25) * SR), len(x)
                if c1 > c0:
                    keep[c0:c1] = False
                    segs.append((c0 / SR, c1 / SR))
            i = j
        else:
            i += 1
    y = x[keep]
    # eski -> sıkılaşmış zaman (tempo öncesi)
    cum = np.cumsum(keep) / SR

    def O(t):
        k = int(np.clip(t * SR, 0, len(cum) - 1))
        return float(cum[k])

    tight = len(y) / SR
    tempo = a.tempo if not a.target else tight / a.target
    tmp = a.out + ".tight.f32"
    y.astype(np.float32).tofile(tmp)
    af = []
    t_ = tempo
    while t_ > 2.0:
        af.append("atempo=2.0"); t_ /= 2.0
    af.append(f"atempo={t_:.6f}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1",
                    "-i", tmp, "-af", ",".join(af), "-ar", str(SR), a.out], check=True)
    import os; os.remove(tmp)
    print(f"kesik {len(x)/SR:.2f}s -> sıkı {tight:.2f}s ({len(segs)} boşluk) -> tempo {tempo:.3f} "
          f"-> {tight/tempo:.2f}s")
    if a.cap:
        off = a.start if a.cap_offset is None else a.cap_offset
        caps = json.load(open(a.cap, encoding="utf-8"))
        for w in caps:
            w["s"] = round(O(w["s"] - off) / tempo, 3)
            w["e"] = round(O(w["e"] - off) / tempo, 3)
        json.dump(caps, open(a.cap_out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print(f"{len(caps)} kelime -> {a.cap_out}")


if __name__ == "__main__":
    main()
