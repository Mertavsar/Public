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

# Anahtar kelime vurgusu. Sessiz izleyen kitle altyazıyı tarar, okumaz —
# rengi değişen kelime taramada gözü durduran tek şey. Sayılar ve ölçüler
# kendiliğinden sarıya boyanır; tehlike/şaşırtma kelimelerini --emphasis ile ver.
# "bir" listede yok: Türkçe'de ezici çoğunlukla belirsiz artikel, sayı değil.
# Hepsini sarıya boyamak vurguyu anlamsızlaştırır.
NUMBERS = ("iki üç dört beş altı yedi sekiz dokuz yirmi otuz kırk elli "
           "altmış yetmiş seksen doksan bin milyon ton tonluk kilo kiloluk "
           "metre metrelik santim saniye saniyede dakika kat misli").split()


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


# Noktalama işaretlerinin ürettiği duraklamanın göreli uzunluğu. Paragraf
# sonu en uzun susar, virgül en kısa. Sayılar ölçümle değil sıralamayla
# önemli: eşleştirme bunları ağırlık olarak kullanıyor.
PUNCT_WEIGHT = {"¶": 1.0, "...": 0.9, "…": 0.9, ".": 0.7, "!": 0.7, "?": 0.7,
                ";": 0.45, ":": 0.45, ",": 0.3}
_PUNCT_RE = re.compile(r"(\.\.\.|…|[,;:.!?])\s+")
_DIGIT_SYL = {"0": "sıfır", "1": "bir", "2": "iki", "3": "üç", "4": "dört",
              "5": "beş", "6": "altı", "7": "yedi", "8": "sekiz", "9": "dokuz"}


def syllables_text(t):
    """Bir metin parçasının hece sayısı. Rakamlar okunuşlarına çevrilir —
    "99" yazıda sıfır sesli harf, seslendirmede dört hece ("doksan dokuz")."""
    t = t.replace("İ", "i").replace("I", "ı").lower()
    t = "".join(_DIGIT_SYL.get(c, c) for c in t)
    return sum(1 for c in t if c in "aeıioöuüâî")


def pauses(x, min_dur=0.13, rel_thr=0.08):
    """Seslendirmedeki duraklamalar: (baslangic, bitis, sure)."""
    hop, win = int(SR * HOP), int(SR * 0.025)
    n = (len(x) - win) // hop
    e = np.array([np.sqrt(np.mean(x[i * hop:i * hop + win] ** 2)) for i in range(n)])
    thr = np.percentile(e, 95) * rel_thr
    out, i = [], 0
    while i < n:
        if e[i] < thr:
            j = i
            while j < n and e[j] < thr:
                j += 1
            if (j - i) * HOP >= min_dur:
                out.append((i * HOP, j * HOP, (j - i) * HOP))
            i = j
        else:
            i += 1
    return out


def paragraph_bounds(x, text, skip_expected=2.5, skip_observed=2.0, verbose=False):
    """
    Metnin her paragrafının sesteki başlangıç anını bulur.

    NEDEN AYRI BİR ÖLÇÜM: `align()` kelimeleri hizalar, ama hizalamanın
    TAMAMI aynı anda kayarsa altyazı kendi içinde tutarlı kalır ve hata
    görünmez. Kurgu planları o kayık hizalamaya göre kesilince seslendirme
    ile görüntü birbirini tutmaz — teslim edilen bir videoda kıymık anlatımı
    poşet görüntüsünün üstüne bindi. Buradaki ölçüm metnin NOKTALAMA
    YAPISINI sesin duraklama dizisine oturtur; hece hızına değil sıraya
    dayandığı için global kaymaya karşı bağışık.

    Yöntem: metindeki her noktalama işareti bir duraklama bekler. Beklenen
    kesme dizisi ile gözlenen duraklama dizisi monoton olarak eşleştirilir
    (nefes duraklamaları "fazla", sesletilmeyen işaretler "yok" sayılır).
    Konum tahmini hece sayısı × konuşma hızı ile yapılır, uzun duraklamalar
    güçlü noktalamaya çekilir.

    Döner: paragraf başlangıçları [t0, t1, ... , ses_sonu] (len = paragraf+1).
    """
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    if not paras:
        return []
    marks, cum = [], 0
    for pi, p in enumerate(paras):
        last, segs = 0, []
        for m in _PUNCT_RE.finditer(p):
            segs.append((p[last:m.end(1)], m.group(1)))
            last = m.end()
        segs.append((p[last:], "¶"))
        for txt, mk in segs:
            cum += syllables_text(txt)
            marks.append((cum, mk, pi if mk == "¶" else -1))
    total_syl, marks = cum, marks[:-1]        # son ¶ sesin sonu, kesme değil

    dur = len(x) / SR
    obs = [r for r in pauses(x) if 0.3 < r[0] and r[1] < dur - 0.3]
    E, O = len(marks), len(obs)
    if not E or not O:
        return [0.0] + [dur]
    t0 = obs[0][0] if obs else 0.0
    blocks, _ = speech_blocks(envelope(x))
    t0 = blocks[0][0] if blocks else 0.0
    speech = (dur - t0) - sum(r[2] for r in obs)
    rate = total_syl / max(speech, 1e-6)

    INF = float("inf")
    dp = [[INF] * (O + 1) for _ in range(E + 1)]
    bk, last_t, last_c = {}, [[0.0] * (O + 1) for _ in range(E + 1)], \
                             [[0] * (O + 1) for _ in range(E + 1)]
    dp[0][0] = 0.0
    last_t[0][0] = t0
    for i in range(E + 1):
        for j in range(O + 1):
            if dp[i][j] == INF:
                continue
            base, lt, lc = dp[i][j], last_t[i][j], last_c[i][j]
            if i < E and j < O:
                c, mk, _ = marks[i]
                t = obs[j][0]
                pred = lt + (c - lc) / rate + sum(r[2] for r in obs if lt <= r[0] < t)
                cost = base + abs(t - pred) ** 1.6 * 0.8 - PUNCT_WEIGHT[mk] * obs[j][2] * 2.0
                if cost < dp[i + 1][j + 1]:
                    dp[i + 1][j + 1] = cost
                    bk[(i + 1, j + 1)] = (i, j, "M")
                    last_t[i + 1][j + 1], last_c[i + 1][j + 1] = obs[j][1], c
            if i < E and base + skip_expected < dp[i + 1][j]:
                dp[i + 1][j] = base + skip_expected
                bk[(i + 1, j)] = (i, j, "E")
                last_t[i + 1][j], last_c[i + 1][j] = lt, lc
            if j < O and base + skip_observed < dp[i][j + 1]:
                dp[i][j + 1] = base + skip_observed
                bk[(i, j + 1)] = (i, j, "O")
                last_t[i][j + 1], last_c[i][j + 1] = lt, lc

    path, i, j = [], E, O
    while (i, j) != (0, 0):
        pi_, pj_, op = bk[(i, j)]
        path.append((pi_, pj_, op))
        i, j = pi_, pj_
    path.reverse()

    found, missed, extra, rates = {}, 0, 0, []
    _last_c, _last_t = [0], [t0]
    for pi_, pj_, op in path:
        if op == "M":
            c, mk, par = marks[pi_]
            if par >= 0:
                found[par] = round((obs[pj_][0] + obs[pj_][1]) / 2, 2)
            rates.append((c - _last_c[0], obs[pj_][0] - _last_t[0], mk))
            _last_c[0], _last_t[0] = c, obs[pj_][1]
            if verbose:
                print(f"  {c:5d} {mk:>4s} -> {(obs[pj_][0]+obs[pj_][1])/2:7.2f} "
                      f"({obs[pj_][2]:.2f}s)" + (f"  <== P{par+1}" if par >= 0 else ""))
        elif op == "E":
            missed += 1
            if verbose:
                print(f"  {marks[pi_][0]:5d} {marks[pi_][1]:>4s} -> SESLETILMEDI")
        else:
            extra += 1
            if verbose:
                print(f"  {'':5s} {'':>4s} -> FAZLA {(obs[pj_][0]+obs[pj_][1])/2:7.2f} "
                      f"({obs[pj_][2]:.2f}s)")
    print(f"PARAGRAF HİZASI: {E - missed}/{E} noktalama eşleşti · "
          f"{extra} fazla duraklama · konuşma hızı {rate:.2f} hece/sn")
    if missed > E * 0.15:
        print(f"  UYARI: {missed} noktalama sesle eşleşmedi — metin sesle aynı mı?")

    # KENDİ KENDİNİ DOĞRULAMA. Eşleştirme yanlış noktalamaya oturduğunda
    # aradaki parça fiziksel olarak imkânsız bir hızda "okunmuş" görünür —
    # bir ölçümde 23 hece 1.89 saniyeye sıkışmıştı (12.2 hece/sn). Türkçe
    # seslendirme 2.5–10.5 hece/sn aralığında kalır. Dışına çıkan varsa
    # sonuç güvenilmez; sessizce yanlış sınır döndürmektense None döner.
    bad = [(n, d, mk) for n, d, mk in rates if n >= 6 and d > 0
           and not (2.5 <= n / d <= 10.5)]
    if bad:
        print(f"  UYARI: {len(bad)} parça imkânsız hızda "
              f"({', '.join(f'{n}/{d:.2f}s={n/d:.1f}' for n, d, mk in bad[:3])}) "
              f"— noktalama–duraklama eşleşmesi güvenilmez, sınırlar KULLANILMADI.")
        return None
    # marks[i] içindeki `par`, O PARAGRAFIN SONU — yani bir sonrakinin başı.
    out = [t0]
    for k in range(1, len(paras)):
        out.append(found.get(k - 1, out[-1]))
    return out + [round(dur, 2)]


def colorize(items, emphasis=(), number_color="yellow", emph_color="red"):
    """Kelimelere renk etiketi yazar. Renk `overlay.py`nin PALETTE'inden gelir."""
    emph = {strip_word(w) for w in emphasis}
    out = []
    for w, a, b in items:
        k = strip_word(w)
        if k in emph:
            c = emph_color
        elif k in NUMBERS or any(ch.isdigit() for ch in w):
            c = number_color
        else:
            c = "white"
        out.append((w, a, b, c))
    return out


def strip_word(w):
    """Noktalama at, Türkçe'ye göre küçült.

    Python'un lower()'ı "İ" için birleşik noktalı bir i üretiyor ve kelime
    listeyle eşleşmiyor — "İki" sayı olarak tanınmıyordu."""
    w = w.replace("İ", "i").replace("I", "ı")
    return re.sub(r"[^0-9a-zçğıöşüA-ZÇĞİÖŞÜ]", "", w).lower()


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
    ap.add_argument("--emphasis", nargs="*", default=[],
                    help="kırmızı vurgulanacak kelimeler (tehlike, şaşırtma)")
    a = ap.parse_args()

    text = open(a.text, encoding="utf-8").read()
    (items, blocks, counts, seg, cost, db, thr,
     dur, npk, nsyl) = align(a.audio, text, floor_off=a.floor_off, min_gap=a.min_gap,
                             min_block=a.min_block, lead=a.lead,
                             peak_thr=a.peak_thr, peak_dist=a.peak_dist)

    colored = colorize(items, a.emphasis)
    json.dump([{"w": w, "s": round(s, 3), "e": round(e, 3), "c": c}
               for w, s, e, c in colored],
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nc = sum(1 for *_, c in colored if c != "white")
    print(f"vurgulu kelime: {nc}/{len(colored)}")

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
