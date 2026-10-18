# Fransa'da basitçe ne oluyor? — animasyonlu Reels sunumu

Dikey (1080×1920) ve 86 saniyelik animasyonlu bir açıklayıcı. Durum **18 Ekim 2026**
itibarıyla anlatılıyor. Açılış, referans Reels'teki gibi: siyah zemin, serif başlık,
kendini çizen Fransa sınırı ve Paris'te yanıp sönen kırmızı nokta.

| Dosya | Ne |
|---|---|
| `fransa-ne-oluyor.mp4` | Yayına hazır video (H.264 + AAC, 30 fps) |
| `index.html` | Tarayıcıda oynayan sunum (boşluk: oynat/durdur, ←/→: 3 sn, r: baştan) |
| `assets/geo.js` | Harita geometrisi (Natural Earth / world-atlas'tan üretildi) |
| `assets/soundtrack.m4a` | Sentezlenmiş müzik (sahne geçişlerinde efekt yok) |
| `build/render.mjs` | Sunumu kare kare yakalayıp MP4'e döker |
| `build/soundtrack.py` | Ses yatağını üretir (viral-edit skill'inin sentez motoru) |

## Akış

| Süre | Bölüm | Görsel |
|---|---|---|
| 0–6 sn | Hook: *Fransa'da basitçe ne oluyor?* | Sınır çiziliyor, Paris'te kırmızı nokta |
| 6–14 | Her şey bir lisede başladı | Créteil'e zoom, 35 kişilik sınıf, öğrencinin sözü |
| 14–23 | Ülkeye yayıldı | Paris'ten 18 şehre yayılan çizgiler, 250 bin / 450 bin |
| 23–31 | Bedeli | 6.000+ gözaltı (%87'si reşit değil), 400–500 lise, 24 okul |
| 31–42 | Akaryakıt | Hürmüz → Fransa deniz yolu, 2,37 € motorin, 10 milyon varil |
| 42–51 | 17 Ekim: Sarı Yelekler | Haritaya yağan 320 sarı nokta, 550 bin kişi |
| 51–62 | Bütçe | %119 borç, açık 5,4 → 5,0 (AB sınırı 3), 54 milyar € |
| 62–70 | Siyaset | Lecornu'nun azınlık hükümeti, 2027 anketleri |
| 70–78 | Özet | 4 satırda neden-sonuç |
| 78–86 | Takvim + soru | 20 Ekim / 1 Kasım / 5 Kasım / 17 Kasım, döngüye dönen harita |

Bütün metinler Reels arayüzünün güvenli alanında kalıyor: üstte 230 px, altta
480 px (kullanıcı adı ve açıklama), sağda 130 px (beğeni ve yorum ikonları) boş.

## Yeniden üretme

```bash
python3 build/soundtrack.py                 # assets/soundtrack.m4a
node build/render.mjs                       # out/video-silent.mp4 (~5 dk)
ffmpeg -i out/video-silent.mp4 -i assets/soundtrack.m4a -c:v copy -c:a copy -shortest fransa-ne-oluyor.mp4
node build/render.mjs --stills 3,20,45      # tek kare kontrolü
```

Metni ya da bir rakamı değiştirmek için yalnızca `index.html` dosyasını düzenle. Her
öğenin `data-in` / `data-out` saniyesi ve sayaçların `data-count` değeri orada duruyor.

## Instagram açıklaması

```
Fransa'da basitçe ne oluyor? 🇫🇷

Bir lisenin kapısında başlayan eylem bir ayda bütün ülkeye yayıldı.
Önce öğrenciler, sonra akaryakıt zamları, sonra Sarı Yelekler…
Arkada ise boş bir kasa ve 2027 seçimi var.

Sence kim kazanacak: sokak mı, bütçe mi? 👇

#fransa #paris #sarıyelekler #gündem #dünya #haber #ekonomi
```

## İsteğe bağlı seslendirme metni (~85 sn, ElevenLabs'e yapıştırılabilir)

> Fransa'da basitçe ne oluyor? Her şey Eylül'de, Paris'in banliyösündeki bir lisede
> başladı. Öğretmen yok, sınıflar otuz beş kişi, sandalye bile yetmiyor. Birkaç hafta
> içinde eylem bütün ülkeye yayıldı. Hükümete göre iki yüz elli bin, sendikalara göre
> dört yüz elli bin öğrenci tek günde sokaktaydı. Altı binden fazla gözaltı var,
> çoğu reşit bile değil. Sonra akaryakıt geldi. İran savaşı yüzünden Hürmüz Boğazı
> kapandı, motorin rekora dayandı. On yedi Ekim'de Sarı Yelekler geri döndü; yarım
> milyondan fazla insan sokaktaydı. Üstelik devletin kasası boş. Borç millî gelirin
> yüzde yüz on dokuzu ve hükümet elli dört milyar avro kesinti istiyor. Mecliste
> çoğunluk yok. Anketlerde ise aşırı sağ açık ara önde. Peki sence kim kazanacak:
> sokak mı, bütçe mi?

## Kaynaklar ve doğrulama notları

Rakamlar 1–18 Ekim 2026 tarihli haberlerden alındı. Kaynaklar arasında fark olan
yerlerde ihtiyatlı olan rakam seçildi ve kaynağı ekranda belirtildi.

- Öğrenci eylemleri, gözaltılar, %87 reşit olmayan, 250 bin kişi ve "35 kişiyiz" sözü: [Time, 2 Ekim](https://time.com/article/2026/10/02/france-student-protests-arrests-injuries-school-closures/)
- 400–500 lise ve 24 okul: [Al Jazeera, 4 Ekim](https://www.aljazeera.com/news/2026/10/4/france-to-shutter-up-to-500-schools-as-more-student-protests-called)
- Sendikalara göre 450 bin, başlangıç 17 Eylül: [Wikipedia: 2026 French student protests](https://en.wikipedia.org/wiki/2026_French_lyc%C3%A9e_protests)
- 10 milyon varil motorin ve G7 kararı: [CNBC, 8 Ekim](https://www.cnbc.com/2026/10/08/france-diesel-reserves-protests.html), [Bloomberg, 7 Ekim](https://www.bloomberg.com/news/articles/2026-10-07/french-premier-vows-energy-price-curbs-talks-to-quell-protests)
- Litre fiyatı 2,37 €, rekor 2,38 € ve Hürmüz: [Wikipedia: 2026 French fuel protests](https://en.wikipedia.org/wiki/2026_French_fuel_protests)
- 1 Kasım indirimi: [IBTimes, 13 Ekim](https://www.ibtimes.co.uk/france-diesel-heating-oil-price-cuts-2026-1825277)
- 17 Ekim, 550 bin kişi ve Paris'te 110 bin: [CNN, 17 Ekim](https://www.cnn.com/2026/10/17/europe/half-million-protesters-sweep-france-in-youth-unrest-latam-intl), [Al Jazeera, 17 Ekim](https://www.aljazeera.com/news/2026/10/17/france-wave-of-nationwide-protests)
- 1.300'den fazla planlanan eylem ve 5 Kasım genel eylemi: [Connexion](https://www.connexionfrance.com/news/more-than-1300-protests-planned-across-france-this-saturday/821387), [Connexion takvim](https://www.connexionfrance.com/practical/calendar-dates-of-strikes-and-protests-in-france-this-october/819662)
- Borç %119, açık 5,4 → 5,0 ve 54 milyar €: [Euronews, 6 Ekim](https://www.euronews.com/2026/10/06/frances-sovereign-debt-crisis-explained-how-dangerous-could-it-be), [EU Insider](https://www.euinsider.eu/news/france-2027-budget-deficit-5-percent-watchdog-optimistic-2026)
- Faiz farkının 2012'den beri en yüksek düzeye çıkması ve 20 Ekim oylaması: [Fortune, 17 Ekim](https://fortune.com/2026/10/17/france-debt-crisis-budget-deficit-bond-yields-spread-protests-riots/)
- 17 Kasım bütçe oylaması: [CNBC, 24 Eylül](https://www.cnbc.com/2026/09/24/france-budget-debt-deficit-government.html)
- Anket ortalaması (Le Pen %36, Mélenchon %17, Glucksmann %13): [Vote-Scope, 15 Ekim](https://vote-scope.com/en/france/polls/)
- Le Pen'in adaylık kararı: [ABC News](https://abcnews.com/International/wireStory/marine-le-pens-2027-bid-french-presidency-stake-134538407), [CNN, 7 Temmuz](https://www.cnn.com/2026/07/07/europe/marine-le-pen-france-court-ruling-intl)

**Dikkat:** 17 Ekim'deki gözaltı sayısı kaynaklara göre 160 ile 1.000'in üzeri arasında
değişiyor. Bu yüzden videoda "yüzlerce gözaltı" yazıyor. Akaryakıt fiyatı ve
Hürmüz bilgisinin kaynağı Wikipedia. Bu sayfalar canlı olarak güncelleniyor, paylaşmadan
önce bir kez daha kontrol et.
