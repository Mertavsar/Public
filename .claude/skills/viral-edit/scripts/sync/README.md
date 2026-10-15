# Altyazılı hazır videoya seslendirme senkronu (EP01, 15 Ekim)

Video (sessiz, gömülü İngilizce altyazılı, 437.9 sn) + ElevenLabs seslendirme (394 sn). İstek: "her sahne ses ve altyazı ile aynı olacak".

1. `cues.py` — altyazı bandını 10 fps tarar. Koyu zeminde beyaz yazı, açık kartlarda koyu yazı. Değişim anlarını bulup her parçayı RapidOCR ile okur (`pip install rapidocr-onnxruntime`). Çıktı `cues.json` (s, e, metin).
2. Seslendirmenin kelime zamanları: Descript SRT, ardından `mapw.py`. ElevenLabs ilk cümleyi iki kez okumuştu, SRT'den elle çıkarıldı.
3. `align2.py`:
   - Cümleleri altyazı parçalarına harf düzeyinde bulanık eşler (cümle başı = çapa).
   - Cümle sınırlarını seste iki cümle arasındaki en uzun sessizliğe oturtur. Arada ≥0.14 sn es yoksa iki cümle birleşik sayılır.
   - Cümle içindeki her altyazı satırını da parça parça oturtur (tempo 0.85–1.35).
   - Son parça penceresine sığmazsa hızlanır. Pencere uzunsa en fazla %10 yavaşlar (0.90), kalan süre es olarak kalır.
   - Sığmayan cümle, önceki boşluktan en fazla 0.4 sn ödünç alır.
   - Sonuç: 199/199 satırda ses altyazıyla başlıyor, medyan kayma 0.06 sn.

## ⛔ align2 sesi bozdu → align3 kullan
Kullanıcı: *"bazı yerlerde ses bozulmuş, hızlanmış, kesilmiş"*. align2, cümleleri tahmini kelime sınırından bölüp parçalara farklı tempolar veriyordu (0.85–1.35). Bu kelime ortasından kesiyor, hız sıçratıyor, yumuşak sonları kırpıyordu.

**align3:**
- Cümle hiç bölünmez, tek parça ve tek tempo (rubberband window=long), aralık 0.92–1.15.
- Sınırlar Descript blok başı/sonundan alınır, pay −0.10/+0.18, 20 ms yumuşak geçiş.
- Sığmayan cümle sonrakini ≤0.45 sn iter.
- Sonuç: cümle başları altyazıyla tam oturuyor (193/199). Satır başı kayması medyan 0.17 sn, %90'ı 0.76 sn içinde. Ani kesik 0.
- Kalan kayma şuradan geliyor: altyazı satırları seslendirmenden yavaş bir okumaya göre zamanlanmış, ama seslendirmen ikinci satıra nefes almadan geçiyor. Kesin çözüm, ElevenLabs'ta daha yavaş (~0.9) seslendirme almak.
- Teslim 30 MB altı: video stream copy + AAC 96k.

## ⛔ Hışırtı (kullanıcı: "neden hışırtılar geliyor")
İki sebep ölçüldü:
1. **Dinamik loudnorm + kompresör sessiz anları yükseltti:** Konuşma arası taban −68 → −49 dB (+19 dB).
2. **rubberband konuşmaya hışırtı ekledi:** 6–8 kHz payı %8.1 → %10.3.

Çözüm:
- **Seviye:** `volume=(−14 − ölçülen I)dB` + `alimiter`, sabit kazanç, sessizliği yükseltmez.
- **Hız:** 0.92–1.15 aralığında `atempo` kullan, rubberband değil.
- **Sonuç:** HF %8.27 (orijinal 8.07), konuşma-taban farkı 44.5 dB.
- **Bundan sonra:** Seslendirmede dinamik loudnorm kullanma, iki geçişli ölçüm + sabit kazanç.
