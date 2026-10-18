# YouTube Paneli — tüm kanallar tek ekranda

Studio'da kanal kanal geçiş yapmak yerine bütün kanallarının gidişatını tek ekranda
görürsün:

- **Genel bakış:** toplam abone, izlenme, izlenme süresi, net abone; her kanal için
  önceki döneme göre değişim (▲ / ▼) ve günlük izlenme gidişat çizgisi.
  Sıralama: en çok izlenen, en hızlı büyüyen, en çok abone, en çok abone kazanan.
- **Kanal detayı:** günlük izlenme ve net abone grafikleri, dönemin en çok izlenen
  videoları (ortalama izlenme yüzdesi, ortalama süre, kazandırdığı abone), son
  yüklenen 20 videonun izlenme / beğeni / yorum sayıları.
- Dönem: 7, 28 veya 90 gün.

Panel **sadece okur.** Kanallarında hiçbir şeyi değiştiremez, video yükleyemez,
silemez; Google'dan istenen izinler yalnızca `youtube.readonly` ve
`yt-analytics.readonly`'dir.

## Hemen bak (örnek veriyle)

```
python3 youtube-panel/server.py --demo
```

Tarayıcıda **http://127.0.0.1:7788**. Uydurma kanallarla panelin nasıl göründüğünü
gösterir; Google'a bağlanmaz.

## Gerçek kanallar — bir kerelik kurulum (~15 dk)

Google, YouTube verisini sadece kendi kayıtlı "uygulamanla" verir. Bu uygulama senin
Google Cloud hesabında durur, ücretsizdir, kimseyle paylaşılmaz.

### 1. Google Cloud projesi

1. https://console.cloud.google.com adresine gir, üstten **Yeni proje** oluştur
   (ad: `YouTube Paneli`).
2. **API'ler ve Hizmetler → Kitaplık**'tan şu ikisini bul ve **Etkinleştir**:
   - **YouTube Data API v3**
   - **YouTube Analytics API**

### 2. Giriş ekranı (OAuth)

1. **Google Auth Platform** (eski adı "OAuth izin ekranı") sayfasına gir,
   **Başlayın**'a bas.
2. Uygulama adı: `YouTube Paneli`, destek e-postası: kendi adresin.
   Kitle: **Harici (External)**.
3. **Kitle (Audience)** sayfasında **Uygulamayı yayınla (Publish app)**'a bas.
   > Bunu atlarsan uygulama "Test" modunda kalır ve Google bağlantıları **7 günde
   > bir siler**; her hafta kanalları yeniden bağlaman gerekir.
4. Google onayı gerekmez. Girişte "Google bu uygulamayı doğrulamadı" uyarısı çıkar:
   **Gelişmiş → YouTube Paneli'ne git (güvenli değil)** de. Uygulama senin olduğu
   için bu normal.

### 3. İstemci dosyası

1. **İstemciler (Clients) → İstemci oluştur**.
2. Uygulama türü: **Masaüstü uygulaması (Desktop app)**. Ad önemli değil.
3. Oluşan istemcinin **JSON'unu indir** ve şu adla kaydet:

```
youtube-panel/data/client_secret.json
```

### 4. Kanalları bağla

```
python3 youtube-panel/server.py
```

http://127.0.0.1:7788 → sağ üstte **+ Kanal bağla**.

- Google hesabını seç. Hesabında birden fazla kanal varsa Google **hangi kanalı**
  istediğini sorar, birini seç → izin ver. Panele dönersin, kanal listededir.
- Her kanal için **+ Kanal bağla**'yı tekrarla. Farklı Google hesaplarındaki kanallar
  da olur: girişte o hesabı seçmen yeterli.
- Kanalın **sahibi** ya da Brand Account **yöneticisi** olan hesapla giriş yapılmalı.
  Studio'daki "İzinler" bölümünden davet edilen kullanıcılar genellikle kanalı
  API'de göremez.

## Bilmen gerekenler

- **Veri gecikmesi:** YouTube istatistikleri yaklaşık 2 gün gecikmeli gelir. Panel bu
  yüzden dönemi 2 gün önce bitirir; böylece son günler grafikte sahte bir düşüş gibi
  görünmez. Abone sayısı ve toplam izlenme anlıktır.
- **Hız:** Veriler 10 dakika saklanır; **Yenile** hemen yeniden çeker.
- **Kota:** Google'ın günlük ücretsiz kotası bu panelin kullanımının çok üstündedir;
  onlarca kanalla gün boyu yenilesen de dolmaz.
- **"Yeniden bağla" uyarısı:** Kanal sahibi erişimi kaldırdıysa veya şifre
  değiştiyse çıkar. Linke tıkla, aynı kanalı tekrar seç.
- **Kanalı kaldırmak:** Kanal detayının en altında. Kanala dokunmaz, sadece panelin
  bağlantısını siler.

## Güvenlik

`youtube-panel/data/` klasöründe istemci dosyan ve kanalların kalıcı bağlantı
anahtarları durur. Bu klasör `.gitignore`'dadır; **kimseyle paylaşma, repoya
ekleme.** Panel sadece senin bilgisayarında (`127.0.0.1`) çalışır, dışarıdan
erişilemez.
