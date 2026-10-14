# Lahmacun kaydırma sitesi

Sayfa aşağı kaydırıldıkça hamur bezesi açılır, harç yayılır, taş fırında pişer ve
servis edilir. Yukarı kaydırınca sahne geri sarar.

- `index.html`: sitenin tamamı (tek dosya).
- `hazirla.sh`: Google Flow videosunu `frames/` klasörüne kare dizisi olarak çıkarır.
- `frames/`: Yayındaki sahne. `frames/manifest.json` varsa site bu kareleri oynatır.
  Yoksa koddan çizilen demo çalışır.

## Neden video değil de kare dizisi?

Videoyu kaydırmayla ileri geri sarmak (`video.currentTime`) çoğu tarayıcıda takılır,
özellikle iPhone'da. Kareleri JPG olarak yükleyip canvas'a çizmek her cihazda akıcıdır.
8 saniyelik bir video yaklaşık 190 kare ve 8–12 MB eder.

## Adımlar

1. Google Flow'da ilk kareyi (hamur bezesi) üret.
2. Son kareyi (pişmiş lahmacun) **ilk kareyi düzenleyerek** üret. Böylece kamera, taş ve
   ışık birebir aynı kalır.
3. Flow → Frames to Video ile iki kare arasında 8 saniyelik video üret.
4. Videoyu karelere çevir:
   ```bash
   ./hazirla.sh ~/Downloads/flow-lahmacun.mp4
   ```
5. Yerelde dene. `fetch` yüzünden dosyayı çift tıklayarak açmak yetmez, küçük bir sunucu gerekir:
   ```bash
   python3 -m http.server 8000
   # http://localhost:8000
   ```
6. Klasörü olduğu gibi yayına al (GitHub Pages, Netlify sürükle-bırak, Vercel).

Kare çıkarmadan hızlı deneme için sayfanın altındaki **Flow videosunu dene** kutusuna
videoyu seç. Kareler tarayıcıda çıkarılır, dosya hiçbir yere yüklenmez.
Yayına alırken bu kutuyu gizlemek için `index.html` içinde `showLab: false` yap.

## Çekim kuralları (Flow)

- Kamera tam tepeden ve sabit olmalı. Zoom, pan ve el olmamalı.
- Lahmacun kadrajın ortasında olmalı ve çapı kare yüksekliğinin yaklaşık %55'i kadar olmalı.
  16:9 video telefonda dikey ekrana kırpılınca kenarlar kesilir, orta kısım görünür kalır.

## Doldurulacaklar

Marka adı, menü ve sahne metinlerindeki rakamlar (80 g beze, 300 °C, 3 dk) şimdilik
örnek. Markadan gelen gerçek bilgilerle değiştirilecek. Sipariş bağlantısı ve adres
bilgisi eklenecek.
