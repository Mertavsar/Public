# Referans Stil Profili — "Kart + Sayaç" formatı

Ölçüm kaynağı: `Şehrin ANLATILMAYAN Hikayesi` (YouTube Shorts), 720x1280, 58.15s, 30fps.
Aşağıdaki sayılar tahmin değil, kare kare ölçüldü. Yeni bir referans video gelirse
`scripts/analyze.py` ile aynı ölçümleri çıkar ve bu dosyayı güncelle.

---

## Düzen

Kaynak klip **tam ekran değil**. Ortada duran bir kart.

| Öğe | Ölçüm | 1080x1920'ye oran |
|---|---|---|
| Kart genişliği | 580px / 720 | **%80.6** → 870px |
| Kart en-boy oranı | 0.74 (≈3:4 dikey) | aynı |
| Kart üst kenarı | y=175 / 1280 | **%13.7** → y=263 |
| Kart alt kenarı | y=955 / 1280 | **%74.6** → y=1432 |
| Üst boşluk | 175px | %13.7 |
| Alt boşluk | 325px | **%25.4** |
| Kart eğimi | ±1–2°, **her planda değişiyor** | aynı |
| Kenarlık / gölge | yok | yok |

Kart dikeyde ortalanmış değil — **yukarı kaydırılmış**. Alt boşluk üstün iki katı.
Arka plan videosunun görüldüğü asıl alan orası.

## Arka plan

Ana klipten **bağımsız ikinci bir video**. Tüm kareyi doldurur, ağır bulanık,
parlatılmış, doygunluğu düşürülmüş. Baştan sona kesintisiz döner.

Referansta el hareketleri (ASMR tipi) kullanılmış. Amaç: gözün boşluğa takılmaması.
Dolgu videosu yoksa ana klibin bulanıklaştırılmış hali kullanılabilir ama ayrı klip
belirgin şekilde daha iyi durur.

```
gblur=sigma≈34  ·  eq=brightness=+0.10:saturation=0.55
```

## Grafikler

### Kırmızı sayaç — `N/30`

- Kartın **üst kenarına oturur**, kenarı keserek üstüne biner
- Yatayda kart ortası
- Kalın sans-serif, **kırmızı dolgu + siyah kontur**
- Yükseklik ≈ 55px / 1280 (%4.3)
- **Videonun başında yoktur.** Referansta 12. saniyede başlıyor.
- İlerleyiş: `1/30 → 6/30 → 12/30 → 24/30` (düz artmıyor, sıçrıyor)

Açık döngü kurar: "30'unu da göreyim".

### Tek kelimelik altyazı

- Kartın alt kısmında, yatayda ortalı
- Beyaz dolgu, **ağır siyah kontur** (stroke ≈ yazı boyunun %12'si)
- Çok kalın sans-serif
- **Ortalama 0.53s'de bir kelime değişir** (58s'de 52 değişim)
- Kesimlerden bağımsız — kelime kesimin üstünden devam eder

Bu formatın belkemiği. Altyazısız bu stil çalışmaz.

### Kırmızı ok

- Kalın, kaba, **kırmızı dolgu + siyah kontur**
- Konuya doğru açılı gelir
- **58 saniyede sadece 2 kez, toplam 1.8 saniye**

Sürekli kullanılmaz. Tek bir kritik anı işaretler. Her plana ok koymak formatı bozar.

## Ritim

- **37 sert kesim / 58s** → saniyede 0.64
- Ortalama plan **1.55s**, medyan **1.43s**, en kısa 0.03s (tek kare), en uzun 3.77s
- **Hiçbir geçiş efekti yok.** Flash yok, blur yok, whip yok, zoom punch yok, sarsıntı yok.

Tempo efektten değil **kesim sıklığından** gelir. Efekt eklemek bu stili taklit etmez,
bozar.

## Ses

| Ölçüm | Değer |
|---|---|
| Integrated loudness | **-14.6 LUFS** |
| Tepe | 0.0 dB (sonuna kadar limitlenmiş) |
| Medyan RMS | -14.9 dB |
| Sessizlik | **58 saniyede sıfır** |

Altta kesintisiz müzik yatağı var. Seslendirmede dramatik duraklama yok.
Boşluk bırakmak bu formatta ölümcül — izleyici kaydırıyor.

---

## Bu stil ne DEĞİL

Sinematik kurgunun tam tersi. Yavaş zoom, ışık geçişi, dramatik sessizlik, ağır çekim,
sarsıntı — hiçbiri yok. Bu bir **bilgi aktarım formatı**: hızlı, düz, grafik ağırlıklı.

Tutunma şu dört öğeden gelir:

```
1. SAYAÇ            açık döngü
2. TEK KELİME       göz sürekli meşgul
3. ARKA PLAN VİDEO  boşluk yok
4. TEMPO            1.5s'de bir yeni görüntü
```
