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
