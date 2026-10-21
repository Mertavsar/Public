# MPA Grup İnşaat — WordPress teması

`mpagrup.com` için kurumsal tema. Kimlik, metinler ve referans projeler
**MPA Grup İnşaat Kurumsal Kataloğu (2026)** baz alınarak hazırlandı.

## Kurulum

1. WordPress paneli → **Görünüm › Temalar › Yeni Ekle › Tema Yükle**
2. `mpa-grup.zip` dosyasını seçin → **Şimdi Kur** → **Etkinleştir**

Etkinleştirildiği anda site hazır gelir. Ek eklenti veya ayar gerekmez:

- Ana sayfa: kaydırdıkça teknik çizimden anahtar teslime yükselen bina animasyonu,
  Kurumsal, Hizmetler, Projeler, İletişim.
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

## Düzenleme

| Ne | Nerede |
|---|---|
| Giriş başlığı, 7 inşaat aşamasının metinleri, bitiş metni | Özelleştir › MPA Grup › Giriş: İnşaat Animasyonu |
| Hakkımızda metni ve görseli | Özelleştir › MPA Grup › Kurumsal |
| Hizmetler ve ilkeler | Özelleştir › MPA Grup › Hizmetler & İlkeler |
| Vurgu rengi (logo turuncusu `#eb531e`) | Özelleştir › MPA Grup › Firma & İletişim Bilgileri |
| Logo (varsayılan: katalogdaki logo) | Özelleştir › Site Kimliği |
| Yeni proje | Projeler › Yeni Proje (öne çıkan görsel + Proje Bilgileri kutusu) |
| Menü (boşsa tek sayfa bağlantıları kullanılır) | Görünüm › Menüler › "Ana Menü" |

## Dosya yapısı

```
mpa-grup/
├── style.css               tema başlığı + tüm stiller
├── functions.php           kurulum, stil/betik
├── front-page.php          ana sayfa
├── template-parts/build.php  kaydırma animasyonu (SVG bina)
├── assets/js/main.js       animasyon motoru, menü
├── assets/img/             logo ve katalog fotoğrafları
└── inc/                    varsayılan içerik, Özelleştir, projeler, form
```

Animasyonda her öğe `data-a="başla,bitir"` aralığıyla kaydırma ilerlemesine (0–1) bağlıdır.
"Hareketi azalt" ayarı açık ziyaretçilere bitmiş bina doğrudan gösterilir.
