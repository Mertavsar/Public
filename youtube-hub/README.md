# Kanalist — çok kanallı YouTube analitiği (SaaS)

Tüm YouTube kanalların tek ekranda analiz: 7/28/90 günlük dönem ve önceki döneme göre
değişim, kanal karşılaştırma tablosu, günlük trend, izlenme kaynakları, Shorts/uzun video
ayrımı, ülkeler, tüm kanallarda en çok izlenen videolar ve video bazında günlük veri.

Ürün adı `YTHUB_APP_NAME` ile değiştirilebilir (YouTube marka kuralları gereği adında
"YouTube" geçmemeli). Ürün planı, API sınırları ve yol haritası: **[docs/PLAN.md](docs/PLAN.md)**

## Kullanıcı yolculuğu

| Adres | Ne |
|---|---|
| `/` | Tanıtım sayfası: hero + panel önizlemesi, kimler için, sorun→çözüm, özellikler, nasıl çalışır, güvenlik, fiyatlar, SSS, son çağrı |
| `/giris` | **Google ile devam et** — hesap yoksa ilk girişte açılır |
| → | İlk girişte kanal yoksa doğrudan **kanal seçimine** geçilir; Google hesaptaki kanalları listeler |
| `/panel?connected=…` | "✓ Kanal bağlandı — bu hesapta başka kanalın var mı?" → **+ Bir kanal daha ekle** |
| `/panel` | Analiz paneli; herkes yalnızca kendi kanallarını görür |
| `/gizlilik`, `/kosullar` | Google doğrulaması için zorunlu sayfalar (taslak) |
| `/kurulum` | İlk kurulum: Google OAuth istemcisi (sadece sunucunun kendisinden) |

> **"Maile bağlı tüm kanallar otomatik gelsin" hakkında:** YouTube API tek onayla bir
> hesaptaki tüm kanalları vermez; her kanal için ayrı onay ister. Sistem bunu en kısa hale
> getirir: girişten hemen sonra kanal seçimi açılır, her bağlantıdan sonra "bir kanal daha"
> sorulur. Hesabın tek kanalı varsa tek adımda gelir.

**İzinler:** Giriş sadece kimlik (`openid email profile`). Kanallar **salt okunur**
(`youtube.readonly`, `yt-analytics.readonly`) bağlanır. Kapak/banner değiştirmek isteyene
`youtube` (yazma) izni o an ayrıca sorulur.

## En kısa yol (kendi bilgisayarında)

1. **İlk sefer — kodu indir.** Terminal'e bir kez yapıştır (macOS):
   ```
   cd ~/Desktop && git clone -b claude/youtube-channels-management-8r70gz https://github.com/Mertavsar/Public.git YouTubeHub && open YouTubeHub/youtube-hub/baslat.command
   ```
2. **Sonraki seferler:** `YouTubeHub/youtube-hub/baslat.command` dosyasına çift tıkla
   (Windows: `baslat.bat`). Tarayıcıda tanıtım sayfası açılır; siyah pencere açık kaldığı
   sürece çalışır. Her açılışta son güncellemeleri de çeker.
3. **Giriş yap** → ilk seferde kurulum sayfası açılır: Google Cloud'daki her adım için
   doğrudan bağlantı var; sonunda indirdiğin JSON dosyasını sayfaya sürükleyip bırakırsın.
4. **Google ile devam et** → kanalını seç → izin ver. Diğer kanallar için "bir kanal daha ekle".

Elle çalıştırmak istersen: `python3 youtube-hub/hub.py serve` → http://127.0.0.1:7788

Sadece Python 3.9+ gerekir. `pip install` yok.

## Sunucuda yayınlama (gerçek SaaS)

```
YTHUB_PUBLIC_URL=https://alanadin.com YTHUB_APP_NAME=Kanalist YTHUB_CONTACT_EMAIL=destek@alanadin.com \
  python3 youtube-hub/hub.py serve
```
- Önünde HTTPS sonlandıran bir ters vekil (Caddy/Nginx) olmalı; uygulama `YTHUB_PORT`'ta dinler.
- Google Cloud'da istemci türü **Web application**, yönlendirme adresi
  `https://alanadin.com/oauth/callback`. JSON'u sunucuda `youtube-hub/data/client_secret.json`
  olarak kaydet (güvenlik gereği sunucu modunda web'den yüklenemez).
- Herkese açmadan önce Google OAuth doğrulaması ve YouTube API denetimi gerekir
  (doğrulanmamış uygulama en fazla 100 kullanıcı). Ayrıntı: [docs/PLAN.md §4](docs/PLAN.md).
- Sunucu açıkken kanallar `YTHUB_AUTOSYNC_HOURS` (varsayılan 6) saatte bir kendiliğinden güncellenir.

## Google Cloud kurulumu (bir kez, ~15 dakika)

1. https://console.cloud.google.com → yeni proje aç (ör. "youtube-hub").
2. **APIs & Services → Library** → üçünü de **Enable**:
   - YouTube Data API v3 — kanal/video listesi, sayaçlar
   - YouTube Analytics API — günlük metrikler, kaynaklar, en iyi videolar
   - YouTube Reporting API — video bazında günlük toplu raporlar (ilk raporlar
     kanal bağlandıktan ~24 saat sonra gelir, 30 gün geriye doldurulur)
3. **APIs & Services → OAuth consent screen** (Google Auth Platform):
   - User type: **External**
   - Uygulama adı, destek e-postası → kaydet.
   - **Audience → Publish app → "In production"**.
     *Testing modunda bırakırsan token'lar 7 günde bir ölür ve kanalları her hafta
     yeniden bağlaman gerekir.* Doğrulanmamış uygulama olarak kalması kişisel kullanım
     için sorun değil; girişte "Google bu uygulamayı doğrulamadı" uyarısında
     **Gelişmiş → Devam et**.
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**
   - Application type: **Desktop app**
   - İndirilen JSON'u şuraya kaydet: `youtube-hub/data/client_secret.json`
5. Paneli aç → **+ Kanal ekle** → Google hesabını ve **kanalı** seç → izin ver.
   Birden çok kanal için bu adımı her kanalda tekrarla (Google her seferinde hangi
   kanal olduğunu sorar).

> Özel kapak yüklemek için kanalın telefonla doğrulanmış olması gerekir
> (youtube.com/verify). Bu YouTube'un kuralıdır, panelin değil.

## Komut satırı

```
python3 youtube-hub/hub.py sync                       # tüm kanalları senkronize et
python3 youtube-hub/hub.py status --days 28           # dönem özeti, kanal tablosu, en iyi videolar
python3 youtube-hub/hub.py thumb VIDEO_ID kapak.jpg   # tek kapak
python3 youtube-hub/hub.py bulk-thumbs klasor/        # klasördeki VIDEO_ID.jpg|png dosyaları
python3 youtube-hub/hub.py banner KANAL_ID banner.jpg
python3 youtube-hub/hub.py undo ISLEM_NO              # kapak/banner'ı önceki haline döndür
```

Günlük otomatik senkron (macOS, her gün 08:00 ve 20:00) — `crontab -e`:

```
0 8,20 * * * cd /YOL/Public && /usr/bin/python3 youtube-hub/hub.py sync >> youtube-hub/data/sync.log 2>&1
```

## Neler kurulu

| | |
|---|---|
| Çok kanal | Her kanal ayrı OAuth onayı, token kanala bağlı |
| Dönem | 7 / 28 / 90 gün; her metrik önceki eşit dönemle kıyaslanır. Dönem bugünde değil Analytics verisinin geldiği son günde biter (2-3 gün gecikme yanıltmasın diye) |
| Özet kutuları | İzlenme, izlenme süresi, abone net, ortalama izleme süresi, yüklenen video, kapak gösterimi/tıklama oranı |
| Günlük trend | Toplam (önceki dönem kesikli çizgi) veya kanallara göre; izlenme / süre / abone |
| Kanal karşılaştırma | Sıralanabilir tablo: abone, izlenme ve değişimi, süre, ort. izleme, abone net, yükleme, etkileşim, portföy payı, trend. CSV indirilebilir |
| Kırılımlar | İzlenme kaynakları, içerik türü (Shorts / uzun / canlı — YouTube'un kendi ayrımı), ülkeler |
| En iyi videolar | Tüm kanallarda veya tek kanalda dönemin en çok izlenenleri; Shorts/uzun filtresi |
| Video günlük | Reporting API ile her videonun gün gün izlenme, süre, kapak gösterimi, tıklama oranı |
| Kanal detayı | Aynı analizler tek kanal için + Studio/YouTube bağlantıları |
| Kapak | Görsele tıkla veya dosyayı sürükle. Göndermeden önce yerelde doğrulanır (tür, boyut, çözünürlük) — reddedilecek dosyaya kota harcanmaz |
| Banner | Kanalın diğer marka ayarları korunarak değiştirilir |
| Yedek + geri al | Her değişiklikten önce mevcut görsel indirilir; "Son işlemler"den geri alınır |
| Kota defteri | Her API çağrısının tahmini maliyeti (Pasifik günü) |
| Bağlantıyı kes | Google erişimini iptal eder, kanalın tüm verisini siler |

## Güvenlik

- Panel sadece bu bilgisayardan erişilir (`127.0.0.1`), Host başlığı denetlenir.
- Kanala yazan her istek, sayfa açılırken üretilen gizli anahtarı ister; başka bir site
  tarayıcın üzerinden kanalına işlem yaptıramaz.
- `youtube-hub/data/` (token'lar, veritabanı, istemci bilgisi, görseller) git'e girmez.
  Veritabanı dosyası sadece sahibi tarafından okunabilir (0600).
- Video **yükleme** yetkisi istenmez. Kapsamlar: `youtube`, `yt-analytics.readonly`.
- Panel sadece **senin bilgisayarında** Google'a bağlanır. `client_secret.json` ve
  token'ları kimseyle (Claude dahil) paylaşma.
- Hesaplar: oturum çerezi HttpOnly + SameSite=Lax (HTTPS'te Secure); sunucuda yalnızca
  özeti saklanır. Her yazma isteği oturuma bağlı CSRF anahtarı ister. Google dönüşünde
  `state` çerezle eşleşmeli (giriş CSRF'ine karşı). Her API isteğinde kanal sahipliği
  denetlenir; bir kullanıcı başkasının kanalını göremez.
- Kullanıcı Google'dan erişimi kaldırırsa bir sonraki senkronda kanalın verisi silinir.

## Sınırlar (YouTube API'den)

- Profil fotoğrafı API ile değiştirilemez.
- Shorts: `thumbnails.set` normal kapağı değiştirir; Shorts rafındaki dikey görseli
  değiştiremez. Panel Shorts'ta bunu uyarır.
- Analytics verisi 2-3 gün gecikmeli gelir. "~24 saat" kutusu bu yüzden senkronlar
  arasındaki sayaç farkından hesaplanır (en az iki senkron, ~20 saat arayla).
- Reporting API raporları 30-60 gün sonra silinir; düzenli senkron (günde 1-2) şart,
  yoksa video bazlı geçmişte boşluk kalır.
- Tıklama oranının birimi (oran mı yüzde mi) gerçek veride doğrulanacak; panel >1
  değerleri yüzde kabul ediyor.
- Kapak = 50 birim kota. Günlük 10.000 birimle ~190 kapak.

Ayrıntı: [docs/PLAN.md §2](docs/PLAN.md#2-youtube-api-gerçekleri)

## Testler

```
python3 -m unittest discover -s youtube-hub/tests -v
```

Sahte bir Google ile çalışır, ağa çıkmaz.

## Ayarlar

`youtube-hub/core/config.py`: port, kapsamlar, kota tablosu, görsel kuralları,
analitik metrikleri, Shorts süre eşiği. Ortam değişkenleri: `YTHUB_PORT`,
`YTHUB_DATA_DIR`, `YTHUB_MONETARY=1` (gelir metrikleri).

## Dosyalar

```
youtube-hub/
  hub.py              komut satırı
  core/config.py      ayarlar
  core/oauth.py       Google onayı (PKCE), token yenileme
  core/api.py         Data + Analytics API istemcisi (yeniden deneme, kota)
  core/images.py      görsel doğrulama
  core/db.py          SQLite şeması
  core/service.py     iş mantığı — tüm arayüzler bunu çağırır
  web/server.py       panel sunucusu
  web/index.html      panel arayüzü
  tests/              sahte Google + testler
  docs/PLAN.md        ürün ve altyapı planı
```
