#!/usr/bin/env python3
"""
align.py için sentetik regresyon testi.

Gerçek konuşma yerine, her hecesi 300–900 Hz bandında tek bir enerji tepesi
yapan yapay bir "seslendirme" üretir. Doğru zamanlama bilindiği için hizalama
hatası ölçülebilir. Kelime sınırları bu testte tam olarak bilinir; gerçek
konuşmada daha gevşek olacaktır, ama bir regresyon buradan da görünür.

    python3 test_align.py
"""
import os, subprocess, sys, tempfile, wave
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import align as A

SR = A.SR
TEXT = ("Gergedan onu neden ezmedi? Boynuz burnunun tam dibinde. İki ton. "
        "Karşısında seksen kilo. Tek hamlede biterdi. Ama domuz kıpırdamıyor bile. "
        "Çukurda sıra büyük olanın. Sen olsan kaç saniye dayanırdın?")

SYL = 0.145          # hece süresi (ölçülen gerçek seslendirmeye yakın)
WGAP = 0.05          # kelime arası
SGAP = 0.40          # cümle arası


def synth(text, seed=7):
    rng = np.random.default_rng(seed)
    sents = A.split_sentences(text)
    x = np.zeros(int(SR * 2), dtype=np.float32)
    t, truth, out = 0.30, [], []
    for si, s in enumerate(sents):
        for wi, w in enumerate(s.split()):
            n = A.syllables(w)
            w0 = t
            for k in range(n):
                d = SYL * float(rng.uniform(0.85, 1.15))
                i0 = int(t * SR); ln = int(d * SR)
                tt = np.arange(ln) / SR
                # sesli harf: 300-900 Hz'de iki formant + zarf
                env = np.sin(np.pi * np.arange(ln) / ln) ** 1.5
                sig = (np.sin(2 * np.pi * 420 * tt) + 0.7 * np.sin(2 * np.pi * 760 * tt)
                       + 0.25 * np.sin(2 * np.pi * 1800 * tt))
                if i0 + ln > len(x):
                    x = np.concatenate([x, np.zeros(i0 + ln - len(x) + SR, dtype=np.float32)])
                x[i0:i0 + ln] += (0.5 * env * sig).astype(np.float32)
                t += d
            truth.append((w, w0, t))
            out.append(w)
            t += WGAP if wi < len(s.split()) - 1 else 0.0
        t += SGAP
    return x[:int((t + 0.4) * SR)], truth


def main():
    x, truth = synth(TEXT)
    d = tempfile.mkdtemp()
    wav, txt, js = f"{d}/a.wav", f"{d}/t.txt", f"{d}/c.json"
    w = wave.open(wav, "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()); w.close()
    open(txt, "w", encoding="utf-8").write(TEXT)

    items = A.align(wav, TEXT)[0]
    assert len(items) == len(truth), f"kelime sayısı tutmadı: {len(items)} != {len(truth)}"
    # Altyazı sessizlikleri de doldurduğu için sınırlar gerçek kelimeden geniş.
    # Ölçülen şey: kelime ekranda gerçekten konuşulduğu SÜREYİ kapsıyor mu
    # (örtüşme), ve hiç kaçırılan an var mı.
    err, ov = [], []
    for (w1, a1, b1), (w2, a2, b2) in zip(items, truth):
        assert w1 == w2, f"kelime sırası bozuldu: {w1} != {w2}"
        err.append(max(0.0, a2 - b1) + max(0.0, a1 - b2))
        ov.append(max(0.0, min(b1, b2) - max(a1, a2)) / (b2 - a2))
    print(f"{len(items)} kelime")
    print(f"örtüşme: ort %{100*np.mean(ov):.1f}  min %{100*min(ov):.1f}")
    print(f"kaçırma: ort {np.mean(err):.3f}s  max {max(err):.3f}s")
    ok = np.mean(ov) > 0.85 and min(ov) > 0.40 and max(err) < 0.05
    print("SONUÇ:", "GEÇTİ" if ok else "KALDI")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
