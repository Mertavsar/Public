#!/usr/bin/env python3
"""
Seslendirme metnini sesin üstüne kelime kelime hizalar.

Bu ortamda konuşma tanıma (ASR) yok — model sunucuları ağ politikasıyla kapalı.
Onun yerine metin kullanıcıdan gelir, zamanlama sesten çıkarılır.

Yöntem — hece çekirdeği + blok kısıtı
-------------------------------------
Türkçe hece-zamanlı bir dil ve hemen her hecenin çekirdeği bir sesli harf.
Sesli harfler 300–900 Hz bandında belirgin bir enerji tepesi yapar. O tepeleri
saymak, ASR olmadan elde edilebilecek en doğrudan zamanlama sinyali:
seslendirmede 123 tepe sayıldı, metinde 123 hece vardı.

Ama tepeleri sırayla hecelere dağıtmak yetmez — tek bir fazla/eksik tepe
sonrasındaki HER kelimeyi kaydırır. O yüzden tepeler konuşma bloklarına
(sessizlikle ayrılmış bölgelere) hapsedilir:

1. Sessizliğe göre konuşma blokları bulunur.
2. Her bloğun içindeki tepe sayısı sayılır.
3. Dinamik programlama ile kelimeler bloklara bölünür: her bloğun hece yükü
   o bloğun tepe sayısına en yakın olacak şekilde. Kelime bloğun dışına
   taşamaz, yani hata bir bloktan diğerine BİRİKMEZ.
4. Blok içinde hece sayısı tepe sayısına eşitse kelimeler tepelere oturur;
   değilse hece ağırlığına göre orantılı dağıtılır.
5. Sessizlikler altyazıda boşluk bırakmaz — sınır, sonraki kelime en fazla
   `lead` saniye erken görünecek şekilde sessizliğin içine taşınır.

Doğrulama: `--check` blok başına tepe/hece uyumunu ve DP maliyetini basar.
Maliyet toplam hecenin %10'unu aşıyorsa hizalama güvenilmezdir, render'dan
önce gözle kontrol et.

Kullanım
--------
    python3 align.py --audio vo.mp3 --text script.txt --out captions.json --check
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

    min_block KÜÇÜK olmalı. Büyük tutulursa "yok", "sen", "et" gibi kısa
    kelimeler blok listesinden düşer ve hizalama kayar.

    Bloklar cümle sınırı DEĞİLDİR. Bir blok bir kelimenin yarısı da olabilir,
    üç cümle de. Burada tek işlevi hatayı sınırlamak: kelime bloğun dışına
    taşmadığı için bir bloktaki yanlışlık sonrakine geçmez.
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
    merged = []
    for b in blocks:
        if merged and b[0] - merged[-1][1] < min_gap:
            merged[-1][1] = b[1]
        else:
            merged.append(b)
    return [b for b in merged if b[1] - b[0] >= min_block], thr


def syllable_peaks(x, lo=300.0, hi=900.0, thr=0.015, min_dist=0.06):
    """
    Hece çekirdeklerini bul: 300–900 Hz bandındaki enerji tepeleri.

    Bu band sesli harflerin ilk iki formantını kapsar; ünsüzler burada zayıf
    kalır. Eşik ve minimum tepe aralığı ölçümle seçildi — 24s'lik bir
    seslendirmede tepe sayısı metnin hece sayısını tam tutturuyor. Değerleri
    değiştirmeden önce `--check` çıktısındaki tepe/hece toplamına bak.
    """
    x = x.astype(np.float64)
    win, hop = int(0.025 * SR), int(SR * HOP)
    n = (len(x) - win) // hop
    if n < 3:
        return np.array([])
    fr = np.lib.stride_tricks.as_strided(
        x, (n, win), (x.strides[0] * hop, x.strides[0])).copy() * np.hanning(win)
    sp = np.abs(np.fft.rfft(fr, axis=1))
    f = np.fft.rfftfreq(win, 1.0 / SR)
    env = sp[:, (f >= lo) & (f < hi)].sum(axis=1)
    k = np.hanning(9); k /= k.sum()
    env = np.convolve(env, k, mode="same")
    if env.max() <= 0:
        return np.array([])
    env /= env.max()

    raw = [i for i in range(2, len(env) - 2)
           if env[i] >= env[i - 1] and env[i] > env[i + 1] and env[i] > thr]
    out = []
    for p in raw:                         # çok yakın tepeler tek hecedir
        if out and (p - out[-1]) * HOP < min_dist:
            if env[p] > env[out[-1]]:
                out[-1] = p
        else:
            out.append(p)
    return np.array(out) * HOP + 0.5 * HOP


def syllables(w):
    """Türkçe'de hece sayısı = sesli harf sayısı. Yeterince doğru bir yaklaşım."""
    return max(1, sum(1 for c in w if c in VOWELS))


def split_sentences(text):
    text = re.sub(r"\s+", " ", text.strip())
    parts = re.split(r"(?<=[.!?…:;])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def match_blocks(syl, counts, durs, empty_cost=0.5, dur_weight=0.6):
    """
    Kelimeleri bloklara böler: her bloğun hece yükü o bloğun tepe sayısına
    olabildiğince yakın olsun.

    İkinci bir kanıt olarak blok SÜRESİ de kullanılır. Tek başına tepe sayısı
    yanıltabiliyor: 0.14s'lik bir bloğa 3 hece koymak tepe sayısına uysa da
    fiziksel olarak imkânsız. Süre terimi bunu eler — ölçümde videonun son
    dört kelimesini yerine oturtan şey buydu.

    Dönen: her blok için (ilk kelime, son kelime+1). Boş blok (nefes, tıklama)
    mümkün ama küçük bir ceza ile caydırılır.
    """
    cum = np.concatenate([[0], np.cumsum(syl)])
    NW, NB = len(syl), len(counts)
    rate = sum(durs) / max(1.0, float(sum(syl)))      # saniye / hece
    exp = [d / rate for d in durs]                    # süreden beklenen hece
    INF = float("inf")
    dp = np.full((NB + 1, NW + 1), INF)
    dp[0, 0] = 0.0
    back = {}
    for b in range(NB):
        for i in range(NW + 1):
            if dp[b, i] == INF:
                continue
            for j in range(i, NW + 1):
                s = cum[j] - cum[i]
                c = (dp[b, i] + abs(s - counts[b]) + dur_weight * abs(s - exp[b])
                     + (empty_cost if j == i else 0.0))
                if c < dp[b + 1, j]:
                    dp[b + 1, j] = c
                    back[(b + 1, j)] = i
    seg, j = [], NW
    for b in range(NB, 0, -1):
        i = back[(b, j)]
        seg.append((i, j))
        j = i
    seg.reverse()
    return seg, float(dp[NB, NW])


def place(words, syl, span, peaks):
    """
    Bir bloğun kelimelerini zamanla. Hece sayısı tepe sayısına eşitse kelime
    sınırları tepelerin arasına konur (en doğrusu); değilse blok süresi hece
    ağırlığına göre bölünür.
    """
    b0, b1 = span
    if not words:
        return []
    total = sum(syl)
    if len(peaks) == total and total > 0:
        edges = [b0]
        c = 0
        for s in syl[:-1]:
            c += s
            edges.append(float((peaks[c - 1] + peaks[c]) / 2.0))
        edges.append(b1)
        # tepeler bloğun kenarlarını aşarsa sınırları düzelt
        edges = [min(max(e, b0), b1) for e in edges]
        for i in range(1, len(edges)):
            edges[i] = max(edges[i], edges[i - 1])
    else:
        w = np.array(syl, dtype=float); w /= w.sum()
        edges = list(b0 + np.concatenate([[0.0], np.cumsum(w)]) * (b1 - b0))
    return [(wd, float(edges[i]), float(edges[i + 1])) for i, wd in enumerate(words)]


def fill_gaps(items, lead=0.30):
    """
    Altyazıda boşluk bırakma — referans stilde ekran hiç boş kalmıyor.

    Sessizliği bölerken sonraki kelime en fazla `lead` saniye erken görünür;
    kalanı önceki kelime taşır. Erken görünmek geç görünmekten iyidir, ama
    uzun bir duraklamanın tamamını erken vermek de okunuşu bozar.
    """
    out = [list(it) for it in items]
    for i in range(len(out) - 1):
        gap = out[i + 1][1] - out[i][2]
        if gap <= 0:
            continue
        b = out[i + 1][1] - min(lead, gap / 2.0)
        out[i][2] = b
        out[i + 1][1] = b
    return [tuple(o) for o in out]


def align(audio, text, min_dur=0.18, floor_off=18.0, min_gap=0.12, min_block=0.08,
          lead=0.30, peak_thr=0.015, peak_dist=0.06):
    x = load_audio(audio)
    db = envelope(x)
    dur = len(x) / SR
    blocks, thr = speech_blocks(db, floor_off=floor_off, min_gap=min_gap, min_block=min_block)
    if not blocks:
        blocks = [[0.0, dur]]

    words = [w for s in split_sentences(text) for w in s.split()]
    if not words:
        raise SystemExit("Metin boş.")
    syl = [syllables(w) for w in words]

    peaks = syllable_peaks(x, thr=peak_thr, min_dist=peak_dist)
    per_block = [peaks[(peaks >= a - 0.06) & (peaks < b + 0.06)] for a, b in blocks]
    counts = [len(p) for p in per_block]

    if len(blocks) > len(words):            # kelimeden çok blok: birleştir
        while len(blocks) > len(words):
            i = int(np.argmin([counts[k] + counts[k + 1] for k in range(len(blocks) - 1)]))
            blocks[i] = [blocks[i][0], blocks[i + 1][1]]
            per_block[i] = np.concatenate([per_block[i], per_block[i + 1]])
            counts[i] = counts[i] + counts[i + 1]
            del blocks[i + 1], per_block[i + 1], counts[i + 1]

    seg, cost = match_blocks(syl, counts, [b - a for a, b in blocks])

    items = []
    for (i, j), span, pk in zip(seg, blocks, per_block):
        items += place(words[i:j], syl[i:j], span, pk)
    items = fill_gaps(items, lead=lead)

    for i, (w, a, b) in enumerate(items):   # çok kısa kelimeleri uzat
        if b - a < min_dur and i + 1 < len(items):
            need = min_dur - (b - a)
            nw, na, nb = items[i + 1]
            if nb - na - need > min_dur:
                items[i] = (w, a, b + need)
                items[i + 1] = (nw, na + need, nb)
    return items, blocks, counts, seg, cost, db, thr, dur, len(peaks), sum(syl)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--text", required=True, help="seslendirme metni (.txt)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--min-block", type=float, default=0.08)
    ap.add_argument("--min-gap", type=float, default=0.12)
    ap.add_argument("--floor-off", type=float, default=18.0)
    ap.add_argument("--lead", type=float, default=0.30,
                    help="kelime en fazla bu kadar erken görünür (s)")
    ap.add_argument("--peak-thr", type=float, default=0.015)
    ap.add_argument("--peak-dist", type=float, default=0.06)
    a = ap.parse_args()

    text = open(a.text, encoding="utf-8").read()
    (items, blocks, counts, seg, cost, db, thr,
     dur, npk, nsyl) = align(a.audio, text, floor_off=a.floor_off, min_gap=a.min_gap,
                             min_block=a.min_block, lead=a.lead,
                             peak_thr=a.peak_thr, peak_dist=a.peak_dist)

    json.dump([{"w": w, "s": round(s, 3), "e": round(e, 3)} for w, s, e in items],
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    d = [e - s for _, s, e in items]
    print(f"{len(items)} kelime  ·  ses {dur:.2f}s  ·  {len(blocks)} konuşma bloğu")
    print(f"hece: metinde {nsyl}, seste {npk} tepe  ·  DP maliyeti {cost:.1f}")
    print(f"kelime süresi: ort {np.mean(d):.2f}s  medyan {np.median(d):.2f}s  "
          f"min {min(d):.2f}s  max {max(d):.2f}s")
    print(f"-> {a.out}")

    if a.check:
        words = [w for s in split_sentences(text) for w in s.split()]
        print("\nblok  zaman           tepe hece  kelimeler")
        for k, ((i, j), (b0, b1), c) in enumerate(zip(seg, blocks, counts)):
            s = sum(syllables(w) for w in words[i:j])
            flag = "  <-- uyumsuz" if s != c else ""
            print(f"{k:3d}  {b0:6.2f}-{b1:6.2f}  {c:4d} {s:4d}  "
                  f"{' '.join(words[i:j])}{flag}")

        # Asıl gösterge DP maliyeti değil (içinde her zaman sıfırdan büyük bir
        # süre terimi var), blok başına tepe/hece uyumsuzluğu.
        mis = sum(abs(sum(syllables(w) for w in words[i:j]) - c)
                  for (i, j), c in zip(seg, counts))
        mono = all(items[i][2] <= items[i + 1][1] + 1e-6 for i in range(len(items) - 1))
        print(f"\nKONTROL: zaman sırası bozulmamış: {mono}")
        dev = abs(npk - nsyl) / max(1, nsyl)
        print(f"KONTROL: tepe/hece sapması %{dev*100:.1f}  ·  "
              f"blok uyumsuzluğu {mis}/{nsyl} hece")
        if dev > 0.10:
            print("UYARI: tepe sayısı hece sayısını tutturamadı. --peak-thr ile oyna "
                  "(düşür: daha çok tepe). Hizalama bu haliyle güvenilmez.")
        if mis > 0.12 * nsyl:
            print("UYARI: bloklar ile metin örtüşmüyor. Metin sesle birebir aynı mı "
                  "kontrol et (eksik/fazla cümle).")
        if np.median(d) > 0.9:
            print("UYARI: kelimeler yavaş akıyor — referans stilde medyan 0.53s.")


if __name__ == "__main__":
    main()
