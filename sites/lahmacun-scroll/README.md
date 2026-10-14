# Lahmacun kaydırma sitesi

Sayfa aşağı kaydırıldıkça hamur bezesi açılır, harç yayılır, taş fırında pişer ve
servis edilir. Yukarı kaydırınca sahne geri sarar.

- `index.html`: sitenin tamamı (tek dosya).
- `hazirla.sh`: Google Flow videosunu `frames/` klasörüne kare dizisi olarak çıkarır.
- `kaynak/flow-lahmacun.mp4`: Google Flow'dan gelen orijinal video (uzun lahmacun, 8 sn, 1280×720).
- `frames/`: Yayındaki sahne. `frames/manifest.json` varsa site bu kareleri oynatır.
  Yoksa koddan çizilen demo çalışır.

## Neden video değil de kare dizisi?

Videoyu kaydırmayla ileri geri sarmak (`video.currentTime`) çoğu tarayıcıda takılır,
özellikle iPhone'da. Kareleri JPG olarak yükleyip canvas'a çizmek her cihazda akıcıdır.

Taş dokusu ve un taneleri sıkıştırmayı zorladığı için 192 karenin hepsi ~50 MB tutuyor.
`hazirla.sh` hareketli anları (açılış, harç, servis) her karede, durağan anları seyrek alır:
89 kare, 15 MB. Kareler önce seyrek sonra sık sırayla yüklenir; sayfa ilk saniyede
kullanılabilir olur, gerisi arkadan dolar. Kareler arası geçiş harmanlanır.

`index.html` içindeki `keys` ayarı, kaydırma ile video zamanını aşamalara göre eşler.
Videoda açılış ve harç birer saniyeden kısa, pişme 4 saniye sürüyor; düz oynatılsa ilk
anlar kaydırmanın küçük bir kısmına sıkışırdı.

Telefonda (dikey ekran) yatay video 90° çevrilir: uzun lahmacun ekranda boydan boya uzanır,
yazılar altındaki taş rengi alana oturur. Yeni bir video gelirse `keys` ve `hazirla.sh` içindeki `PLAN`
yeniden ayarlanır.

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

- Kamera tam tepeden ve sabit olmalı. Zoom, pan, titreşim ve el olmamalı.
- Uzun lahmacun yatay durmalı, kadraj genişliğinin yaklaşık %80'i kadar olmalı.
- Değişim her saniye eşit hızda olmalı; buhar ve ışık değişimi olmamalı.

## Doldurulacaklar

- Menünün kesik kalan kısmı: çorba adı ve içecekler.
- Orijinal logo dosyası (şu an menüden çizilmiş bir taklit).
- Adres, telefon, çalışma saatleri; yol tarifi şimdilik Google Haritalar araması.
- Sarımsaklı/soğanlı, Kilis Tava, katmer ve sütlaç açıklamaları işletmeye teyit ettirilmeli.
