# Dünyanın petrol musluğu kapandı — Hürmüz Boğazı

Dikey (1080×1920), 60 saniye, **seslendirmesiz** izlenecek şekilde tasarlandı. Her ekran
yazısı en az 3–4 saniye kalıyor; görsel ve metin ayrı bölgelerde. Durum 20 Ekim 2026.

| Süre | Sahne | Animasyon |
|---|---|---|
| 0–5,5 | Dünyanın petrol musluğu kapandı | Boğazda kırmızı X, iki yanda bekleyen tankerler |
| 5,5–13 | Savaştan önce: her gün 20 milyon varil | Boğaza yakınlaşma, akan tanker konvoyu, "en dar yeri ≈ 33 km" |
| 13–21 | Günde 85 gemi geçerdi, 18 Ekim'de 4 | Gemiler tek tek kayboluyor, sayaç 85 → 4, boğaz kapanıyor |
| 21–30 | Savaş, abluka, saldırılar | 28 Şubat → Mart → Temmuz → Eylül sonu zaman çizelgesi |
| 30–38 | Boru hatları yetmiyor | Suudi (Yanbu) ve BAE (Fujairah) hatları çiziliyor; 20 / 5,5 çubukları |
| 38–45 | Bir varil petrol: 110 $ | Sayaç; Fransa motorin 2,37 €, ABD benzin 4,29 $ |
| 45–52 | Türkiye'de pompada tablo | Benzin 79,60 TL (bugün −4,30), motorin 96,70 TL |
| 52–56,6 | İran'ın şartı | "Birkaç gün içinde açarız, eğer…" 3 şart |
| 56,6–60 | Sence boğaz bu yıl açılır mı? | A/B, takip et |

## Açıklama önerisi

```
Dünyanın petrol musluğu kapandı 🛢️⛔
Günde 85 gemi geçen Hürmüz Boğazı'ndan artık 4 gemi geçiyor. Benzin neden pahalı, cevap burada.

Sence boğaz bu yıl açılır mı? A mı B mi? 👇

#hürmüz #petrol #benzin #akaryakıt #iran #gündem #ekonomi
```

## Kaynaklar

- 20 milyon varil/gün, deniz yoluyla taşınan petrolün ~%25'i, LNG'nin ~%19'u, boru hattı kapasitesi 3,5–5,5 mb/g: [IEA – Strait of Hormuz](https://www.iea.org/about/oil-security-and-emergency-reserve/strait-of-hormuz)
- 85 → 4 gemi (18 Ekim, IMF PortWatch), Brent 109,86 $ (17 Ekim kapanışı): [Straits.live, 20 Ekim](https://straits.live/briefs/2026-10-20) (yapay zekâ destekli bir bülten; PortWatch verisini aktarıyor)
- Savaşın başlangıcı (28 Şubat), boğazın kapanması, ABD ablukası: [Britannica – 2026 Iran war](https://www.britannica.com/event/2026-Iran-war), [Wikipedia – US naval blockade of Iran](https://en.wikipedia.org/wiki/2026_United_States_naval_blockade_of_Iran)
- Bir haftada 10 tanker (Kpler): [Al Jazeera, 14 Ekim](https://www.aljazeera.com/news/2026/10/14/iran-steps-up-hormuz-surveillance-attacks-soar-oil-flows-crash-again)
- İran'ın şartları: [CBS News canlı yayın](https://www.cbsnews.com/live-updates/iran-war-us-trump-strait-of-hormuz-yemen-houthis-saudi-arabia/)
- ABD benzin 4,29 $: [Everything Briefing, 19 Ekim](https://everythingbriefing.substack.com/p/october-19-2026) (AAA verisi)
- İstanbul akaryakıt, 20 Ekim: [BirGün](https://www.birgun.net/haber/20-ekim-2026-benzin-ve-motorin-fiyatlarinda-indirim-zam-var-mi-guncel-akaryakit-fiyatlari-741363)

Not: PortWatch transponderi kapalı geçen gemileri sayamaz; gerçek geçiş biraz daha
yüksek olabilir. Harita Natural Earth (world-atlas 10m) verisinden çizildi; "≈ 33 km"
ölçüsü temsilîdir.

## Yeniden üretme

```bash
(cd <world-atlas, topojson-client, d3-geo kurulu klasör> && node gulf.mjs ../hurmuz/assets/gulf.js)
python3 build/soundtrack.py && python3 build/mix.py
node build/render.mjs
ffmpeg -i out/video-silent.mp4 -i assets/mix.m4a -map 0:v -map 1:a -c copy -shortest -movflags +faststart hurmuz-bogazi.mp4
```
