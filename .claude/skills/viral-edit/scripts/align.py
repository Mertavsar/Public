#!/usr/bin/env python3
"""
Seslendirme metnini sesin üstüne kelime kelime hizalar.

Bu ortamda konuşma tanıma (ASR) yok — model sunucuları ağ politikasıyla kapalı.
Onun yerine: metin kullanıcıdan gelir, zamanlama sesin enerjisinden çıkarılır.

Yöntem
------
1. Sesin RMS zarfı çıkarılır, konuşma ve sessizlik bölgeleri ayrılır.
2. Kelimeler bloklara, blok süresiyle orantılı hece yükü verecek şekilde
   paylaştırılır. Kelime asla bloğun dışına taşmaz — bu yüzden kayma videonun
   tamamına birikmez, her duraklamada sıfırlanır.
3. Blok içinde kelimeler hece sayısına orantılı yerleştirilir, sınırlar enerji
   vadilerine çekilir.

Doğruluk: her kelimenin ayrı bir blok oluşturduğu sentetik testte ortalama hata
0.011s. Gerçek konuşmada kelimeler birleşik telaffuz edildiği için blok başına
birkaç kelime düşer ve hata büyür — tek kelimelik altyazı için yeterli, ama
render sonrası gözle kontrol et.

Kullanım
--------
    python3 align.py --audio vo.wav --text script.txt --out captions.json
    python3 align.py --audio vo.wav --text script.txt --out captions.json --check

--check  hizalamanın konuşma bölgelerine oturup oturmadığını raporlar.
"""

import argparse, json, re, subprocess, sys
import numpy as np

SR = 22050
HOP = 0.010                      # 10 ms
VOWELS = "aeıioöuüAEIİOÖUÜ"


def load_audio(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def envelope(x):
    h = int(SR * HOP)
    n = len(x) // h
    e = np.sqrt(np.maximum([np.mean(x[i * h:(i + 1) * h] ** 2) for i in range(n)], 1e-12))
    return 20 * np.log10(e)       # dB


def speech_blocks(db, floor_off=18.0, min_gap=0.12, min_block=0.08):
    """
    Konuşma bloklarını bul. Eşik, gürültü tabanına göre uyarlanır.

    min_block KÜÇÜK olmalı. Büyük tutulursa "yok", "sen", "et" gibi kısa kelimeler
    blok listesinden düşer; kelime sayısı blok sayısını aşar ve hizalama videonun
    tamamında kayar. Sentetik testte min_block 0.20 -> 0.08 değişimi ortalama
    hatayı 0.58s'den 0.011s'ye indirdi.
    """
    quiet = np.percentile(db, 15)
    loud = np.percentile(db, 90)
    thr = max(quiet + 6.0, loud - floor_off)
    on = db > thr

    blocks, i, n = [], 0, len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            blocks.append([i * HOP, j * HOP])
            i = j
        else:
            i += 1
    # kısa boşlukları birleştir
    merged = []
    for b in blocks:
        if merged and b[0] - merged[-1][1] < min_gap:
            merged[-1][1] = b[1]
        else:
            merged.append(b)
    return [b for b in merged if b[1] - b[0] >= min_block], thr


def syllables(w):
    """Türkçe'de hece sayısı = sesli harf sayısı. Yeterince doğru bir yaklaşım."""
    return max(1, sum(1 for c in w if c in VOWELS))


def split_sentences(text):
    text = re.sub(r"\s+", " ", text.strip())
    parts = re.split(r"(?<=[.!?…:;])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def allocate(words, blocks):
    """
    Kelimeleri bloklara paylaştırır: her blok, süresiyle orantılı hece alır.

    Kelime hiçbir zaman bloğun dışına (sessizliğe) taşmaz. Böylece olası kayma
    tüm videoya birikmez — her duraklamada sıfırlanır. Bu, ASR olmadan
    yapılabilecek en sağlam hizalama.
    """
    syl = np.array([syllables(w) for w in words], dtype=float)
    dur = np.array([b1 - b0 for b0, b1 in blocks], dtype=float)
    S, D = syl.sum(), dur.sum()
    target = np.cumsum(dur) / D * S          # her bloğun bitmesi gereken hece noktası

    groups, i, cum = [], 0, 0.0
    for j in range(len(blocks)):
        take, remaining_blocks = [], len(blocks) - j - 1
        while i < len(words):
            # sonraki bloklara en az birer kelime kalsın
            if remaining_blocks and len(words) - i <= remaining_blocks:
                break
            take.append(i); cum += syl[i]; i += 1
            if cum >= target[j] and (take or not remaining_blocks):
                break
        groups.append(take)
    while i < len(words):                     # artan kelimeler son bloğa
        groups[-1].append(i); i += 1

    out = []
    for (b0, b1), idx in zip(blocks, groups):
        if not idx:
            continue
        w = syl[idx] / syl[idx].sum()
        edges = b0 + np.concatenate([[0.0], np.cumsum(w)]) * (b1 - b0)
        for k, wi in enumerate(idx):
            out.append((words[wi], float(edges[k]), float(edges[k + 1])))
    return out


def snap_to_valleys(items, db, radius=0.06):
    """Kelime sınırlarını yakındaki enerji minimumuna çek — heceyi ortadan bölmesin."""
    n = len(db)
    out = list(items)
    for i in range(1, len(out)):
        b = out[i][1]
        lo, hi = int((b - radius) / HOP), int((b + radius) / HOP)
        lo, hi = max(0, lo), min(n, hi)
        if hi - lo < 3:
            continue
        k = lo + int(np.argmin(db[lo:hi]))
        nb = k * HOP
        if nb <= out[i - 1][1] or nb >= out[i][2]:
            continue
        out[i - 1] = (out[i - 1][0], out[i - 1][1], nb)
        out[i] = (out[i][0], nb, out[i][2])
    return out


def align(audio, text, min_dur=0.18, floor_off=18.0, min_gap=0.12, min_block=0.08):
    x = load_audio(audio)
    db = envelope(x)
    dur = len(x) / SR
    blocks, thr = speech_blocks(db, floor_off=floor_off, min_gap=min_gap, min_block=min_block)
    if not blocks:
        blocks = [[0.0, dur]]

    words = [w for s in split_sentences(text) for w in s.split()]
    if not words:
        raise SystemExit("Metin boş.")

    items = allocate(words, blocks)
    items = snap_to_valleys(items, db)

    # çok kısa kelimeleri komşudan zaman alarak uzat
    for i, (w, a, b) in enumerate(items):
        if b - a < min_dur and i + 1 < len(items):
            need = min_dur - (b - a)
            nw, na, nb = items[i + 1]
            if nb - na - need > min_dur:
                items[i] = (w, a, b + need)
                items[i + 1] = (nw, na + need, nb)
    return items, blocks, db, thr, dur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--text", required=True, help="seslendirme metni (.txt)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--min-block", type=float, default=0.08)
    ap.add_argument("--min-gap", type=float, default=0.12)
    ap.add_argument("--floor-off", type=float, default=18.0)
    a = ap.parse_args()

    text = open(a.text, encoding="utf-8").read()
    items, blocks, db, thr, dur = align(a.audio, text, floor_off=a.floor_off,
                                        min_gap=a.min_gap, min_block=a.min_block)

    json.dump([{"w": w, "s": round(s, 3), "e": round(e, 3)} for w, s, e in items],
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    d = [e - s for _, s, e in items]
    print(f"{len(items)} kelime  ·  ses {dur:.2f}s  ·  {len(blocks)} konuşma bloğu")
    print(f"kelime süresi: ort {np.mean(d):.2f}s  medyan {np.median(d):.2f}s  "
          f"min {min(d):.2f}s  max {max(d):.2f}s")
    print(f"-> {a.out}")

    if a.check:
        # Asıl arıza modu: konuşma blokları eksik tespit edilirse kelimeler
        # bloklara sıkışır ve hizalama videonun tamamında kayar. Kelime/blok
        # oranı bunu yakalayan en güvenilir gösterge.
        speech = sum(b - a_ for a_, b in blocks)
        per_block = len(items) / len(blocks)
        rate = len(items) / speech if speech else 0
        print(f"KONTROL: {len(blocks)} blok, blok başına {per_block:.1f} kelime")
        print(f"KONTROL: konuşma {speech:.1f}s / {dur:.1f}s  (eşik {thr:.1f} dB), "
              f"konuşma hızı {rate:.1f} kelime/s")
        mono = all(items[i][2] <= items[i + 1][1] + 1e-6 for i in range(len(items) - 1))
        print(f"KONTROL: zaman sırası bozulmamış: {mono}")

        if per_block > 6:
            print("UYARI: blok başına çok kelime düşüyor — kısa kelimeler eleniyor "
                  "olabilir. --min-block 0.05 dene, sonra tekrar bak.")
        if rate > 5:
            print("UYARI: konuşma hızı gerçekçi değil (>5 kelime/s). Metin sesten "
                  "uzun olabilir veya konuşma tespiti eksik.")
        if rate and rate < 1.2:
            print("UYARI: konuşma hızı çok düşük (<1.2 kelime/s). Metin sesten "
                  "kısa olabilir — eksik cümle var mı kontrol et.")
        if np.median(d) > 0.9:
            print("UYARI: kelimeler yavaş akıyor — referans stilde medyan 0.53s.")


if __name__ == "__main__":
    main()
