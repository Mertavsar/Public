# Kuzu Lahmacun: lezzet şovu

Site lahmacunun hikâyesini anlatır. Kaydırma sahnesi altı perde: hamur, açılış, iç, et,
fırın, servis. Havada dökülen her malzemenin adı, düştüğü yerden çıkan ince bir çizgiyle
yazılır. Ardından lügat, göç hikâyesi, dört kalem (hamur, et, iç, fırın), ustanın sözlüğü,
menü ve final gelir.

- `index.html`: sitenin tamamı (tek dosya).
- `kaynak/sahne1-3.mp4`: Google Flow sahneleri (beze ve açılış, malzeme yağmuru, fırın).
- `hazirla.sh`: sahneleri birleştirip `frames/` klasörüne kare dizisi çıkarır.
- `frames/`: yayındaki sahne (330 kare, 20 MB) ve `manifest.json`.
- `foto/lahmacun.jpg`: işletmenin gerçek lahmacun fotoğrafı (final bölümü).

## Sahneyi yeniden üretmek

```bash
./hazirla.sh kaynak/sahne1.mp4 kaynak/sahne2.mp4 kaynak/sahne3.mp4
python3 -m http.server 8000   # http://localhost:8000
```

Kareler JPG olarak canvas'a çizilir; kaydırmayla ileri geri sarmak her cihazda akıcıdır.

Akıcılık için:
- Kareler ölçülen görüntü değişimine göre seçilir: art arda iki kare arasındaki fark hep
  aynı küçük miktardadır (alev ve hamurun havada dönüşü her karede, duran el seyrek).
- Kaydırma, perde içinde görüntünün değişim hızına göre paylaştırılır (`FLOW`).
- Sahne kaydırmayı kare hızından bağımsız, yumuşak bir gecikmeyle izler; sıradaki kareler
  önceden açılır. Masaüstünde fare tekerleği Lenis ile yumuşatılır, telefonda doğal kaydırma kalır.

İlk giriş için (önbellek boş):
- `frames/onizleme-*.jpg`: bütün karelerin küçük hâli 7 dosyada (2,6 MB). Sayfa önce bunları
  indirir; kaydırma ilk saniyeden her karede doğru görüntüyü gösterir. Keskin kareler aynı anda
  4–6 tane, kullanıcının bulunduğu yere en yakın olandan başlayarak gelir ve ancak açıldıktan
  sonra kullanılır.
- Canvas hiçbir zaman videonun dolduramayacağı kadar piksel çizmez (bilgisayarda ~1x, telefonda
  en fazla 1,5x); cihaz zorlanırsa kendiliğinden bir kademe düşer.
- Telefondaki bulanık arka plan ayrı, küçük bir katmandır (`#softbg`); ekran kartı büyütür,
  sadece kare değişince güncellenir.


## Ayarlar (`index.html` içinde)

- `KEYS`: kaydırma ile video zamanını perdelere eşler.
- `MARKS`: etiketler. Her biri hangi saniyede çıkıp kaybolacağını, videodaki yerini (u, v),
  yazının hangi tarafta duracağını ve metnini tutar. Yeni video gelirse bunlar ayarlanır.
- `FOCUS`: telefonda tam ekran kadrajın hangi saniyede videonun neresine bakacağı
  (hamur, dökülen malzeme, fırında lahmacun boyunca yavaş pan).
- Adres sonuna `#dene` yazılırsa yeni bir Flow videosunu tarayıcıda deneme kutusu açılır.

## Doldurulacaklar

- Menünün kesik kalan kısmı: çorba adı ve içecekler.
- Orijinal logo dosyası (şu an menüden çizilmiş bir benzeri).
- Adres, telefon, çalışma saatleri; yol tarifi şimdilik Google Haritalar araması.
- Sahne 3'te lahmacun alevle pişiyor; işletmenin metni "harlı ateşte değil, taşta" diyor.
