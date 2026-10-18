# İlk savaşı kazanmak — LoL animasyonlu Reels

Dikey (1080×1920), 42 saniyelik, tamamen animasyonla yapılmış bir oyun anlatımı.
Konu tek koridorda **seviye 2 yarışı**: ikinci dalganın ilk yakın dövüş minyonunu kim
önce keserse, ikinci yeteneği o açar ve ilk takası o kazanır.

Stil referans videodan alındı: üstte büyük italik başlık, üstten görünen koridor,
SEN ve RAKİP portreleri, alt tarafta kelime grubu halinde akan altyazı, kırmızı alt
çizgi ve "TEMSİLİ ANLATIM" notu. Harita, portreler ve birimler özgün çizim. Oyunun
kendi görsellerinden hiçbiri kullanılmadı.

| Dosya | Ne |
|---|---|
| `ilk-savasi-kazanmak.mp4` | Yayına hazır video (H.264 + AAC, 30 fps, −14 LUFS) |
| `index.html` | Tarayıcıda oynayan sürüm (boşluk: oynat/durdur, ←/→: 3 sn) |
| `assets/soundtrack.m4a` | Sentezlenmiş müzik ve olay efektleri (whoosh yok) |
| `build/render.mjs` | Sayfayı kare kare yakalayıp MP4'e döker |
| `build/soundtrack.py` | Müziği ve efektleri üretir |

## Akış

| Süre | Altyazı | Görsel |
|---|---|---|
| 0–3 | LoL'de ilk savaşı kazanmak, tek bir minyona bağlı. | İki dalga çarpışıyor |
| 3–9 | İlk dalgada altı minyon var… | Kamera rakip dalgasına yaklaşıyor |
| 9–15 | Hepsi ölünce seviye ikiye çok az kalır. XP barı %97. | Son vuruşlar, +XP yazıları, XP halkası doluyor |
| 15–20 | Eksik olan tek şey: ikinci dalganın ilk yakın dövüşü. | 2. dalga geliyor, kırmızı ok hedefi gösteriyor |
| 20–24 | Onu ilk kim keserse ikinci yeteneğini açar. | SEVİYE 2 patlaması, W yeteneği açılıyor |
| 24–29 | İşte o an saldır. İki yetenek, bire karşı. | Atılma, isabetler, can barları |
| 29–33 | Rakip geri çekilir, dalga senin olur. | Rakip kuleye kaçıyor, KORİDOR SENİN |
| 33–37 | Alt koridorda kural farklı: ilk dalga artı üç yakın dövüş. | Kural kartı |
| 37–41 | Sen o minyonu kovalar mısın, yoksa güvenli mi oynarsın? | A/B seçenek kartı |
| 41–42 | Unutma: | Başa bağlanan sahne. Son kare ilk kareyle aynı, video kesintisiz döner |

## Seslendirme eklemek istersen (ElevenLabs'e yapıştır)

Altyazılar seslendirme hızına göre zamanlandı (~2,2 kelime/sn). Ses gelirse kesimleri
ona göre yeniden hizalarım.

```
LoL'de ilk savaşı kazanmak, tek bir minyona bağlı. İlk dalgada altı minyon var: üç yakın dövüş, üç büyücü. Rakip de aynısını kesiyor. Hepsi ölünce seviye ikiye çok az kalır. XP barı yüzde doksan yedi. Rakibinki de öyle. Eksik olan tek şey: ikinci dalganın ilk yakın dövüşü. Onu ilk kim keserse ikinci yeteneğini açar. Rakibin hâlâ tek yeteneği var. İşte o an saldır. İki yetenek, bire karşı: takası sen kazanırsın. Rakip geri çekilir, dalga senin olur. Alt koridorda kural farklı: ilk dalga artı üç yakın dövüş. Sen o minyonu kovalar mısın, yoksa güvenli mi oynarsın? Unutma:
```

## Açıklama önerisi

```
LoL'de ilk takası kazanmanın sırrı tek bir minyon ⚔️
Sen o minyonu kovalar mısın, yoksa güvenli mi oynarsın? A mı B mi? 👇

#leagueoflegends #lol #loltr #lolturkiye #oyun #gaming
```

## Bilgi notu

- Seviye 2 için 280 XP gerekiyor. Tek koridorda bir yakın dövüş minyonu ~60, bir büyücü
  ~30 XP veriyor; ilk dalga (3+3) ~270 XP eder. Bu yüzden ikinci dalganın ilk yakın
  dövüşü seviyeyi atlatıyor. Değerler: [LoL Wiki – Minion](https://wiki.leagueoflegends.com/en-us/Minion_(League_of_Legends)).
- Alt koridorda XP iki şampiyon arasında paylaşılıyor; seviye 2 için ilk dalga ve
  ardından 3 yakın dövüş gerekiyor: [Mobalytics](https://mobalytics.gg/blog/lol-6-tips-from-your-support-an-adc/).
- XP değerleri yamayla değişebilir. Videodaki süreler ve hasar sayıları temsilîdir.

## Yeniden üretme

```bash
python3 build/soundtrack.py
node build/render.mjs                    # out/video-silent.mp4 (~2,5 dk)
ffmpeg -i out/video-silent.mp4 -i assets/soundtrack.m4a -map 0:v -map 1:a -c copy -shortest -movflags +faststart ilk-savasi-kazanmak.mp4
node build/render.mjs --stills 0,17,20.2 # tek kare kontrolü
```
