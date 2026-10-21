# MPA Grup İnşaat — WordPress teması

`mpagrup.com` için kurumsal tema. Kimlik, metinler ve referans projeler
**MPA Grup İnşaat Kurumsal Kataloğu (2026)** baz alınarak hazırlandı.

## Kurulum

1. WordPress paneli → **Görünüm › Temalar › Yeni Ekle › Tema Yükle**
2. `mpa-grup.zip` dosyasını seçin → **Şimdi Kur** → **Etkinleştir**

Etkinleştirildiği anda site hazır gelir. Ek eklenti veya ayar gerekmez:

- Ana sayfa: kaydırdıkça temelden bitmiş hale gelen yapı. Anıttepe Olimpik Yüzme Havuzu
  inşaat videosu (Flow) ziyaretçi kaydırdıkça kare kare ileri/geri oynar; hafriyat, temel,
  karkas, cephe ve teslim aşamalarının yazıları videodaki anlarla eşleşir. Ardından
  Kurumsal, Hizmetler ve öne çıkan projelerden kısa tanıtımlar.
- Sayfalar (otomatik oluşturulur): **/kurumsal/** (hakkımızda, ilkeler), **/hizmetler/**
  (hizmet alanları, 7 adımlı çalışma süreci), **/projeler/** (tüm projeler, her birinin
  galerili kendi sayfası), **/iletisim/** (bilgiler, form, harita). Sayfa düzenleyicisine
  yazılan içerik de bu sayfalarda gösterilir.
- Katalogdaki 3 referans proje (İvedik Otel, Ankara Lalahan Araştırma Merkezi,
  Anıttepe Olimpik Yüzme Havuzu) fotoğraflarıyla **Projeler** menüsüne otomatik eklenir.
- İletişim formu eklentisiz çalışır; mesajlar panelde **Gelen Mesajlar** altında saklanır
  ve e-postayla iletilir.

## Yapılması gerekenler (katalogda olmayan bilgiler)

**Görünüm › Özelleştir › MPA Grup › Firma & İletişim Bilgileri**

- Telefon, e-posta, adres, çalışma saatleri, WhatsApp numarası
- Google Haritalar gömme kodu, sosyal medya hesapları
- **Rakamlar** bölümü (deneyim yılı, proje sayısı vb.) katalogda olmadığı için boş bırakıldı;
  yalnızca doğrulanmış rakamları girin. Boş kalırsa bölüm görünmez.

Ayrıca: **Ayarlar › Genel** altında site başlığını ve dilini (Türkçe) kontrol edin;
**Ayarlar › Kalıcı Bağlantılar** "Yazı adı" olmalı (`/projeler/ivedik-otel/` gibi adresler için).

Not: zip yaklaşık 8 MB. Sunucunuz "dosya çok büyük" derse temayı FTP / cPanel Dosya
Yöneticisi ile `wp-content/themes/` altına klasör olarak yükleyip Görünüm › Temalar'dan etkinleştirin.

## Giriş videosu

Temada hazır gelir: `mpa-grup/assets/video/insaat.mp4` (8 sn, 1280×720, sessiz, kaydırmada
akıcı sarma için yeniden kodlanmış) ve ilk karesi `insaat-poster.jpg`.

- Başka bir video için: **Özelleştir › MPA Grup › Giriş: İnşaat Animasyonu › İnşaat videosu**.
- Video dosyası kaldırılırsa giriş fotoğraf efektine döner (çizim → kaba inşaat → bitmiş yapı).
- Kodlama komutları ve aşama zamanlaması: `mpa-grup/assets/video/BENIOKU.txt`.

## Düzenleme

| Ne | Nerede |
|---|---|
| Giriş videosu / bitmiş yapı görseli, başlık, 7 aşamanın metinleri, bitiş metni | Özelleştir › MPA Grup › Giriş: İnşaat Animasyonu |
| Hakkımızda metni ve görseli | Özelleştir › MPA Grup › Kurumsal |
| Hizmetler ve ilkeler | Özelleştir › MPA Grup › Hizmetler & İlkeler |
| Vurgu rengi (logo turuncusu `#eb531e`) | Özelleştir › MPA Grup › Firma & İletişim Bilgileri |
| Logo (varsayılan: katalogdaki logo) | Özelleştir › Site Kimliği |
| Yeni proje | Projeler › Yeni Proje (öne çıkan görsel + Proje Bilgileri kutusu) |
| Menü (boşsa Kurumsal · Hizmetler · Projeler · İletişim kullanılır) | Görünüm › Menüler › "Ana Menü" |

## Dosya yapısı

```
mpa-grup/
├── style.css               tema başlığı + tüm stiller
├── functions.php           kurulum, stil/betik
├── front-page.php          ana sayfa
├── template-parts/build.php  kaydırma animasyonu (video ya da fotoğraf katmanları)
├── assets/js/main.js       animasyon motoru, menü
├── assets/img/             logo ve katalog fotoğrafları
└── inc/                    varsayılan içerik, Özelleştir, projeler, form
```

Aşamaların kaydırmadaki zamanlaması `assets/js/main.js` içindeki `ROUGH`, `DONE`, `VIDEO` aralıklarındadır.
"Hareketi azalt" ayarı açık ziyaretçilere bitmiş bina doğrudan gösterilir.
