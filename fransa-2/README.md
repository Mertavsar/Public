# Fransa'da işler büyüdü — 2. bölüm

Dikey (1080×1920), 59,6 saniye. "Fransa'da basitçe ne oluyor?" videosunun devamı.
Durum 19 Ekim 2026 itibarıyla anlatılıyor. Düzen: üstte başlık, ortada görsel, altta
kısa metin. Her sahne 7–9 saniye ekranda kalıyor ve yazılar görsellerin üstüne binmiyor.

| Süre | Sahne | Animasyon |
|---|---|---|
| 0–5 | Fransa'da işler büyüdü | Sınır çiziliyor, Paris'te kırmızı nabız |
| 5–13 | Ülke aynı gün sokağa döküldü | Noktalar Paris'ten dalga gibi yayılıyor; 550.000 ve 800.000 |
| 13–21 | Hafta sonunun bedeli | 120 karelik birim grafiği (her kare 20 gözaltı); ~2.400 / ~1.000 / 1 |
| 21–30 | Limoges: 143 yıllık belediye binası yandı | Haritada Limoges'a yakınlaşma, binanın çizilmesi, alevler, kıvılcım, duman |
| 30–38 | Hükümet sertleşiyor | Sokağa çıkma yasağı, olağanüstü hal, "kontrolü kaybettik" kartları |
| 38–46 | Yarın mecliste kritik bütçe oylaması | 577 sandalyelik meclis dolup ortadan ikiye bölünüyor |
| 46–53 | Sırada ne var? | 20 Ekim, 24 Ekim, 5 Kasım |
| 53–56 | Sence hükümet bu kışı çıkarır mı? | A/B seçenekleri, haritada Paris'e dönüş |
| 56–60 | 3. bölümü kaçırma | Parmak "Takip Et"e basıyor, zil çalıyor; takip et / abone ol |

## Seslendirme ve ses kurgusu

Kayıt `vo/ham.mp3` (2. kayıt, 67,1 sn; ilk kayıt `vo/ham-1.mp3`). İşlem sırası, her adım tek komut:

```bash
python3 build/vo_clean.py vo/ham.wav     # boşluk kısaltma, nefes/hırıltı atma, EQ, de-esser, kompresör -> vo/temiz.wav
python3 ../.claude/skills/viral-edit/scripts/align.py --audio vo/temiz.wav --text seslendirme.txt \
        --out vo/captions.json --check --emphasis kaybetti kundaklandı kontrolü çoğunluğu
python3 build/timing.py                  # sahne eşlemesi + altyazı parçaları -> assets/timing.js, vo/son.wav
python3 build/soundtrack.py              # sakin müzik yatağı, yeni süreye göre
python3 build/mix.py                     # ses -16 / müzik -30 LUFS, sidechain, master -14 LUFS -> assets/mix.m4a
node build/render.mjs
ffmpeg -i out/video-silent.mp4 -i assets/mix.m4a -filter_complex "[1:a]apad[a]" -map 0:v -map "[a]" \
       -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart fransa-bolum-2.mp4
```

- Cümleden ayrı duran nefes ve hırıltılar susturulur (11 parça, liste: `vo/atilan.json`).
- Burun çekme ayrıca spektral imzasıyla bulunur: enerjinin > %50'si 300–3000 Hz'de ve
  spektrum düz (> 0.17). s/ş sesleri bu imzayı taşımaz; "hal" gibi kısa kelimeler
  harmonik olduğu için düzlükleri düşüktür. 2. kayıtta 4 burun çekme bulundu ve çıkarıldı.
- Cümle başındaki uzun nefes alma kırpılır.
- Cümle sonları **asla kırpılmaz** (kısık son hece cümlenin parçasıdır); son sesli
  harften 0,18 sn sonrası kesilmeden yavaşça kısılır, nefes vermesi öne çıkmaz.
- Bölgeler arası uzun sessizlik 0,38 sn'ye iner. Sonuç 58,9 sn.
- Bas vurguları: her sahne açılışında ve dört vurgu kelimesinde (kaybetti, kundaklandı,
  kontrolü, çoğunluğu) derin bir vuruş; ayrı stem (`assets/hits.wav`), whoosh yok.
- Ses zinciri: sıcaklık, telefon kutusu kesimi, netlik, hava, de-esser, iki kademeli
  yumuşak kompresör.
- Altyazı kelime kelime yanar; sayılar sarı, vurgu kelimeleri kırmızı. Ekranda
  "Limoges" yazar, seslendirmede "Limoj" okunur.
- Sahneler cümle başlarına oturur (`timing.js` içindeki WARP).


`seslendirme.txt` okunacak metindir. Yabancı kelimeler okunduğu gibi yazıldı:
**Limoges → "Limoj"**. Altyazıda doğru yazım (Limoges) kullanılacak.

## Açıklama önerisi

```
Fransa'da işler büyüdü 🇫🇷🔥 2. bölüm
1 ölü, ~2.400 gözaltı, 143 yıllık belediye binası yandı. Yarın mecliste kritik oylama var.

Sence hükümet bu kışı çıkarır mı? A mı B mi? 👇

#fransa #paris #gündem #sarıyelekler #haber #dünya
```

## Kaynaklar ve notlar

- 1.800'den fazla gözaltı, 550 bin / 800 bin katılımcı, Limoges belediye binası ve kalp krizinden ölen eylemci: [CBS News](https://www.cbsnews.com/news/protests-france-rising-living-costs-students/), [The National](https://www.thenationalnews.com/news/europe/2026/10/19/france-protests-macron/), [TPR / NPR](https://www.tpr.org/criminal-justice/2026-10-18/french-police-arrest-1-800-after-violent-clashes-and-looting-mar-protests)
- Hafta sonu toplamı ~2.400 gözaltı ve ~1.000 yaralı, sokağa çıkma yasağı, olağanüstü hal, Nuñez'in istifası: [France 24](https://www.france24.com/en/europe/20261019-live-france-macron-slams-unbridled-violence-protests-weekend-unrest), [Al Jazeera](https://www.aljazeera.com/news/liveblog/2026/10/19/france-protests-live-macron-admits-failures-after-days-of-violent-unrest)
- 20 Ekim bütçe oylaması, piyasalardaki düşüş: [Fortune](https://fortune.com/2026/10/17/france-debt-crisis-budget-deficit-bond-yields-spread-protests-riots/), [Traders Agency](https://tradersagency.com/blog/french-bonds-and-paris-stocks-slide-after-worst-unrest-in-years-a-day-before-budget-vote)
- 24 Ekim Sarı Yelek çağrısı: Al Jazeera canlı yayını. 5 Kasım genel eylem: [Connexion](https://www.connexionfrance.com/practical/calendar-dates-of-strikes-and-protests-in-france-this-october/819662)

Gözaltı ve yaralı sayıları gün içinde arttı (1.800 → ~2.400; 500 → ~1.000). Videoda en
güncel hafta sonu toplamı kullanıldı. 20 Ekim oylamasının sonucu paylaşmadan önce
kontrol edilmeli.

## Yeniden üretme

```bash
python3 build/soundtrack.py
node build/render.mjs
ffmpeg -i out/video-silent.mp4 -i assets/soundtrack.m4a -map 0:v -map 1:a -c copy -shortest -movflags +faststart fransa-bolum-2.mp4
```
