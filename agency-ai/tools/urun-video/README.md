# Ürün videosu üretici

Tek bir statik ürün görselinden reklam videosu üretir. Harici servis, API
anahtarı veya telifli varlık kullanmaz — her şey yerelde üretilir.

Çıktı: 15 sn, 30 fps, H.264 + AAC, 9:16 / 4:5 / 1:1.

## Ne yapar, ne yapmaz

**Yapar**
- Görseli derinlik katmanlarına ayırır ve 2.5B parallaks uygular. Kamera
  hareket ettiğinde ürün arka plandan bağımsız kayar; kadraj değil sahne
  hacim kazanır.
- Posterin üzerindeki grafik katmanını (başlık, alt metin, ikonlar) silip
  "temiz plaka" üretir. Yakın planlarda kırpılmış yazı görünmez; kamera geri
  çekilirken bu öğeler tek tek belirir.
- Metale oturan ışık süzülmesi, şimşek parlamaları, kamera sarsıntısı,
  derinliğe oturan toz, grain, vignette.
- Ses tasarımını sıfırdan sentezler: gök gürültüsü, darbe, drone, whoosh,
  riser, final vuruş. Telifsizdir.

**Yapmaz**
- Üründe olmayan bir hareketi uydurmaz. Ürünün kendisi dönmez, açı
  değişmez — elde tek bir kare vardır. Gerçek çekim hareketi isteniyorsa
  video üreten bir model gerekir; bu pipeline onun yerine geçmez.
- Reklam hesabına dokunmaz.

## Kullanım

```bash
pip install numpy pillow opencv-python-headless imageio-ffmpeg

# 1) poster grafiklerini sil  (kutular: boxes.py)
python3 clean_plate.py urun.jpg clean.png

# 2) derinlik katmanlarina ayir -> depth.png, masks.npz, mask_debug.png
python3 segment.py clean.png

# 3) ses
python3 make_audio.py soundtrack.wav

# 4) video
python3 make_video.py urun.jpg cikis.mp4 \
    --clean clean.png --depth depth.png --plate bgplate.png \
    --ar 9:16 --audio soundtrack.wav --cta "HEMEN SİPARİŞ VER"
```

`pipeline.py` bu dört adımı tek komutta çalıştırır.

## Her yeni ürün için ayarlanması gerekenler

Bu pipeline görsele özel iki yerde elle ayar ister:

| Dosya | Ne |
|---|---|
| `boxes.py` | Posterdeki yazı/ikon kutularının koordinatları |
| `segment.py` | Maske eşikleri ve `head` GrabCut çekirdek poligonu |

`segment.py` çalıştıktan sonra **`mask_debug.png` dosyasına mutlaka bakın.**
Maske yanlışsa parallaks yanlış yerden kırılır ve siluette hayalet oluşur.

`make_video.py` içindeki `build_timeline` (kamera kadrajı), `PARALLAX`
(derinlik hareketi), `REVEALS` (öğelerin belirme anları) ve metin blokları
kurguyu belirler; ses `make_audio.py` içindeki zaman çizelgesiyle hizalıdır.
Birini değiştirirseniz diğerini de kaydırın.

## Doğrulama

Parallaksın gerçekten çalıştığı, bölgelerin farklı hızda kayması ile
ölçülür. Mjölnir örneğinde, kamera uçtan uca gittiğinde:

| Bölge | Yatay kayma |
|---|---|
| Çekiç kafası | 24.5 px |
| Sap | 13.1 px |
| Kaya | 7.4 px |
| Arka plan | 0.3 px |

Bu sıralama bozuksa derinlik haritası yanlıştır.
