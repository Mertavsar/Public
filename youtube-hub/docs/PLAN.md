# YouTube Hub — Ürün ve Altyapı Planı

> Tarih: 2026-10-05 · Durum: Faz 0 + Faz 1A (çok kanallı analiz) kuruldu, gerçek kanallarda doğrulama bekliyor.
>
> **Öncelik (2026-10-05, kullanıcı kararı):** tüm kanalları tek panelden analiz etmek.
> Kapak/banner işleri ikinci planda.
> Bu belge: neyi inşa ettiğimizi, YouTube'un neye izin verip neye vermediğini, kotanın
> nasıl harcandığını, mimariyi, yol haritasını ve fikir havuzunu tek yerde toplar.

---

## 0. Özet

- **Yapılabilir:** Tüm kanalların verisi tek panelde, her videoya ayrı kapak, kanal başına
  banner, toplu kapak yükleme, kapak yedekleme/geri alma, günlük analitik, kapak gösterim
  sayısı ve tıklama oranı (CTR), zamanlanmış yayın, yorum yönetimi, oynatma listeleri.
- **Yapılamaz (API izin vermiyor):** Profil fotoğrafı değiştirme, Shorts rafındaki dikey
  görseli değiştirme, YouTube'un kendi A/B kapak testi (Test & Compare), topluluk
  gönderileri, gerçek zamanlı analitik, kanal açma.
- **Kota sorun değil:** 10 kanal × 300 video'luk bir portföyün tam günlük senkronizasyonu
  ~150 birim. Günlük limit 10.000. Darboğaz okuma değil, **yazma**: her kapak 50 birim →
  günde en fazla ~190 kapak.
- **Asıl engel Google onayı:** Kendi kanalların için ertesi gün kullanırsın. Başkalarına
  açmak (SaaS) için alan adı, gizlilik politikası, OAuth doğrulaması ve YouTube API denetimi
  gerekir; haftalar sürer, baştan planlanmalı.
- **Kurulan temel:** Kurulum gerektirmeyen Python + SQLite yerel panel. Katmanları SaaS'a
  taşınacak şekilde ayrıldı (servis katmanı arayüzden bağımsız).
- **En büyük kaldıraç:** Bu repo'daki `viral-edit` (video + kapak üretimi) ile birleşince
  döngü kapanır: üret → yayınla → ölç → öğren → daha iyi üret.

---

## 1. Ne inşa ediyoruz

**Çok kanallı YouTube işletim paneli.** Üç kullanıcı tipi, aynı çekirdek:

| Kim | İhtiyaç | Bugün ne kullanıyor | Acısı |
|---|---|---|---|
| **Sen** — çok kanallı içerik üreticisi | Tüm kanallar bir bakışta, hızlı kapak değişimi | YouTube Studio'da kanal kanal geçiş | Studio tek kanal görür; karşılaştırma, toplu işlem yok |
| **Ajans / ekip** | Müşteri kanallarını yönetmek, rapor | Studio + Excel + vidIQ/TubeBuddy | Kanal başına ayrı oturum, rapor elle |
| **SaaS müşterisi** | Aynı şey, hazır ürün olarak | Hootsuite, Metricool, vidIQ | Bu araçlar sosyal medyanın geneline yayılmış; YouTube çok kanal + kapak iş akışında zayıf |

**Farkımız olabilecek şeyler:** (1) Çok kanallı karşılaştırma ve toplu işlem birinci sınıf
özellik, (2) kapak iş akışı (üret → yükle → ölç → geri al), (3) Claude ile teşhis ve
içerik üretimi aynı sistemde.

---

## 2. YouTube API gerçekleri

İki ayrı API kullanıyoruz: **YouTube Data API v3** (kanal/video verisi ve yazma işlemleri) ve
**YouTube Analytics API** (günlük metrikler; kotası ayrıdır).

### 2.1 Yapabildiklerimiz

| Özellik | API çağrısı | Kota (birim) | Not |
|---|---|---|---|
| Kanal bilgisi, abone, toplam izlenme | `channels.list` | 1 | Gizli abone sayısında sayı gelmez |
| Tüm videoları listele | `playlistItems.list` (yüklemeler listesi) | 1 / 50 video | `search.list` 100 birim; **asla kullanmıyoruz** |
| Video istatistikleri | `videos.list` | 1 / 50 video | İzlenme/beğeni sayaçları neredeyse anlık |
| **Video kapağı yükle** | `thumbnails.set` | 50 | JPG/PNG, en fazla 50 MB (2026-09'da 2 MB'tan yükseltildi). **Kanal telefonla doğrulanmış olmalı** |
| **Kanal banner'ı** | `channelBanners.insert` + `channels.update` | 50 + 50 | En az 2048×1152, ≤6 MB |
| Filigran (watermark) | `watermarks.set` | 50 | Videolarda sağ altta çıkan kanal logosu |
| Başlık/açıklama/etiket güncelle | `videos.update` | 50 | Tüm `snippet` gönderilmeli; eksik alan silinir |
| Zamanlanmış yayın | `videos.insert` + `status.publishAt` | ayrı kova | Bkz. 2.3 — denetim olmadan video "özel" kalır |
| Oynatma listeleri | `playlists.*`, `playlistItems.*` | 50 (yazma) | |
| Yorumları oku / cevapla / moderasyon | `commentThreads.list`, `comments.insert` | 1 / 50 | Toplu otomatik cevap spam sayılabilir |
| Altyazı yükle | `captions.insert` | 400 | |
| Çok dilli başlık/açıklama | `videos.update` (`localizations`) | 50 | Türkçe kanalı global açmak için |
| Günlük kanal metrikleri | Analytics `reports` | ayrı kota | İzlenme, izlenme süresi, abone ±, beğeni, paylaşım |
| **Kapak gösterimi + CTR** | Analytics `videoThumbnailImpressions`, `...ClickRate` | ayrı kota | 2026-01-15'te API'ye eklendi — kapak ölçümünü mümkün kılan metrik |
| İzleyici tutma eğrisi | Analytics `audienceWatchRatio` | ayrı kota | Video bazında; `viral-edit` için altın değerinde |
| Gelir | Analytics + `yt-analytics-monetary.readonly` | ayrı kota | Sadece para kazanan kanalın sahibi |
| Rakip kanalların herkese açık sayıları | `channels.list` (API anahtarı) | 1 | Analitikleri değil, sadece herkese açık sayaçlar |
| Yeni video bildirimi | PubSubHubbub (WebSub) | **0** | Kota yemeyen anlık bildirim; herkese açık URL ister (SaaS fazı) |
| Toplu günlük raporlar | YouTube Reporting API | 0 (iş bazlı) | Çok kanal ölçeğinde sorgu yerine günlük CSV |

### 2.2 Yapamadıklarımız — açık konuşalım

| İstek | Neden olmuyor | En yakın alternatif |
|---|---|---|
| **Profil fotoğrafı (avatar) değiştirmek** | API'de böyle bir çağrı yok | Panel, Studio'nun ilgili sayfasına derin bağlantı verir |
| **Shorts rafındaki dikey görseli değiştirmek** | YouTube Shorts için iki görsel tutuyor. `thumbnails.set` normal kapağı değiştirir (arama, kanal sayfası, önerilenler); Shorts rafı/sekmesindeki dikey görsel için belgelenmiş bir API yok. Özel Shorts kapağı 2026-07-24'te YPP kanalları için **sadece Studio masaüstünde** açıldı | Panel Shorts'ta uyarı verir. Gerçek kanalda test edip davranışı belgeleyeceğiz (Faz 1) |
| **YouTube'un "Test & Compare" A/B kapak testi** | API'de yok | Kapak rotasyonu (bkz. Fikir #4) — daha zayıf ama otomatik |
| **Topluluk gönderileri** | API'de yok | — |
| **Gerçek zamanlı analitik** | Analytics verisi ~2-3 gün gecikmeli | Anlık sayaç fotoğrafları (kurulu): "son 24 saat" bunlardan hesaplanır |
| **Kanal açmak** | API'de yok | — |
| **Studio'daki "Yönetici/Editör" izniyle API erişimi** | API, kanalın kendisi adına onay ister; Studio izinleri API'ye taşınmıyor gibi görünüyor (Faz 1'de doğrulanacak) | Kanal sahibi veya marka hesabı yöneticisi onay verir |
| **Kotayı artırmak için çok sayıda Google projesi açmak** | YouTube API politikalarına aykırı; proje askıya alınabilir | Resmi kota artış başvurusu (denetimle) |
| **Başka kanalların analitiği** (izlenme süresi, CTR) | Sadece sahibi görür | Herkese açık sayaçlarla trend takibi |
| **Abone listesinin tamamı** | Sadece aboneliğini herkese açık yapanlar | Analytics'teki toplu abone metrikleri |

### 2.3 Dikkat gerektiren gri alanlar

- **API ile video yükleme kilidi:** 2020-07-28'den sonra açılan ve **denetlenmemiş** Google
  projelerinden yüklenen videolar "özel" moda kilitlenir. Kapak/metadata güncellemesi bundan
  etkilenmez. Zamanlanmış yükleme özelliği → önce YouTube API denetimi.
- **Yükleme kotası değişti:** Üçüncü taraf kaynaklara göre `videos.insert` maliyeti
  2025-12'de ~1.600'den ~100 birime indi ve 2026-06'da ayrı bir kovaya taşındı (proje başına
  günde ~100 yükleme). Google'ın kendi sayfası bu ortamdan erişilemedi; **Cloud Console >
  Quotas ekranı esastır**.
- **`channels.update` ve `videos.update` tuzağı:** Bir parçayı (ör. `brandingSettings`)
  güncellerken o parçanın tamamı yeniden yazılır. Sadece banner gönderirsen kanal açıklaması
  silinir. Sistem önce okuyup sonra birleştirerek yazar (testle korunuyor).
- **Shorts tespiti:** API'de "bu bir Shorts" bayrağı yok. Süre ≤ 180 sn → "muhtemel Shorts"
  sayıyoruz. Kesin değil.
- **Veri saklama politikası:** Kullanıcı erişimi kaldırınca verisi silinmeli (kurulu:
  "Bağlantıyı kes" tüm kanal verisini siler). SaaS aşamasında YouTube API Hizmetleri
  Geliştirici Politikaları'nın veri saklama/yenileme bölümleri hukuki olarak okunmalı.

---

## 3. Kota ekonomisi

Varsayılan: proje başına günde **10.000 birim**, Pasifik saatiyle gece yarısı sıfırlanır.
Analytics API'nin kotası ayrıdır.

**Bir kanalın tam senkronizasyonu** = `channels.list` (1) + `playlistItems.list` (video/50) +
`videos.list` (video/50) + Analytics (ayrı).

| Portföy | Tam senkron (birim) | Günde 4 kez | Kalan (yazma için) |
|---|---|---|---|
| 5 kanal × 100 video | 5 × (1+2+2) = 25 | 100 | 9.900 → ~198 kapak |
| 10 kanal × 300 video | 10 × (1+6+6) = 130 | 520 | 9.480 → ~189 kapak |
| 50 kanal × 500 video | 50 × (1+10+10) = 1.050 | 4.200 | 5.800 → ~116 kapak |

**Verimlilik kuralları (kurulu veya planlı):**
1. `search.list` yasak (100 birim) → yüklemeler listesi (1 birim / 50 video). ✅ kurulu
2. `videos.list`'e 50'şer ID toplu gönderim. ✅ kurulu
3. Yazmadan önce görseli yerelde doğrula — reddedilecek dosyaya 50 birim yakma. ✅ kurulu
4. Kademeli yenileme: son 7 günün videoları saatlik, eskiler günlük/haftalık. (Faz 1)
5. Yeni video tespiti için PubSubHubbub — sıfır kota. (Faz 4, herkese açık URL gerekir)
6. 50+ kanalda Analytics sorguları yerine Reporting API günlük CSV. (Faz 4)
7. Kota defteri: her çağrı kaydedilir, panel tahmini harcamayı gösterir. ✅ kurulu

---

## 4. Kimlik doğrulama ve Google onay yolu

Her kanal ayrı onay verir; token o kanala bağlıdır. Aynı Google hesabındaki 5 marka kanalı =
5 kez "Kanal ekle".

| Seviye | Kimler | Ne gerekir | Süre |
|---|---|---|---|
| **A. Kişisel** | Sadece senin kanalların | Cloud projesi + OAuth istemcisi. Onay ekranını **"In production"** yap (doğrulanmamış). Giriş sırasında "Google bu uygulamayı doğrulamadı" uyarısı çıkar, "Devam"a basılır | 1 saat |
| **B. Ekip** | ≤100 kullanıcı | A ile aynı; doğrulanmamış uygulama ömür boyu 100 kullanıcıyla sınırlı | 1 saat |
| **C. SaaS** | Herkes | Alan adı + ana sayfa + gizlilik politikası + kullanım koşulları, OAuth doğrulaması (hassas kapsamlar: demo videosu, kapsam gerekçesi), YouTube API Hizmetleri denetimi (kota artışı ve yükleme kilidi için) | Haftalar |

> **Önemli tuzak:** Onay ekranı "Testing" modunda kalırsa refresh token'lar **7 günde bir
> ölür** ve her hafta kanalları yeniden bağlamak gerekir. Kişisel kullanımda "In production"a
> al.

İstenen kapsamlar (en az yetki ilkesi):
- `youtube` — okuma, kapak, banner, metadata.
- `yt-analytics.readonly` — günlük metrikler.
- `yt-analytics-monetary.readonly` — sadece gelir istenirse (`YTHUB_MONETARY=1`).
- `youtube.upload` — **eklenmedi**; zamanlanmış yükleme fazında ve denetimden sonra.

---

## 5. Mimari

### 5.1 Faz 0 — kurulan yerel temel

```
                ┌─────────────── arayüzler ───────────────┐
                │  web/index.html   hub.py (CLI)   [MCP]* │   *planlı
                └──────────────────┬──────────────────────┘
                                   │  sadece servis katmanını çağırır
                       ┌───────────▼───────────┐
                       │   core/service.py     │  senkron, kapak/banner, geri al,
                       │   (Hub)               │  özetler, kota defteri
                       └───┬───────┬───────┬───┘
           ┌───────────────┘       │       └──────────────┐
  ┌────────▼────────┐   ┌──────────▼─────────┐   ┌────────▼────────┐
  │ core/api.py     │   │ core/db.py         │   │ core/images.py  │
  │ Data+Analytics  │   │ SQLite, sürümlü    │   │ yerel görsel    │
  │ yeniden deneme, │   │ şema               │   │ doğrulama       │
  │ token yenileme  │   └────────────────────┘   └─────────────────┘
  └────────┬────────┘
  ┌────────▼────────┐
  │ core/oauth.py   │  PKCE + loopback, kanal başına refresh token
  └─────────────────┘
```

Neden bu seçimler:
- **Sıfır kurulum** (sadece Python 3): repo'daki `agency-ai` paneliyle aynı felsefe; bugün
  çalışır, `pip install` yok.
- **Servis katmanı arayüzden bağımsız:** Web, CLI ve ileride MCP sunucusu aynı fonksiyonları
  çağırır. Yeni arayüz = ince bir kabuk.
- **Ağ katmanı enjekte edilebilir:** Testler sahte Google ile çalışır (16 test, <1 sn).
- **Her yazma işlemi denetim kaydında**, önceki görsel yedeklenir → geri alınabilir.
- **Güvenlik:** sadece 127.0.0.1, Host kontrolü (DNS rebinding), yazma isteklerinde oturum
  anahtarı (CSRF), token dosyası 0600, gizli dosyalar git dışı.

### 5.2 Hedef mimari — ekip / SaaS (Faz 4+)

| Katman | Faz 0 | SaaS | Geçiş notu |
|---|---|---|---|
| Arayüz | Tek HTML | Next.js / React | API sözleşmesi aynı kalır |
| API sunucusu | `http.server` | FastAPI | `core/` olduğu gibi taşınır |
| Veritabanı | SQLite | Postgres | Şema birebir; `channel_daily` için zaman serisi bölümleme |
| İş kuyruğu | Thread | Redis + worker (RQ/Celery/Arq) | Senkron ve toplu kapak işleri kuyruğa |
| Zamanlayıcı | cron/launchd | Worker scheduler | Kademeli yenileme |
| Görseller | Yerel klasör | S3 / Cloudflare R2 | |
| Token | SQLite, 0600 | KMS ile şifreli (envelope encryption) | Refresh token = kanalın anahtarı |
| Kimlik | Yok (yerel) | Uygulamaya giriş (Google Sign-In) ayrı, kanal onayı ayrı | Org → üye → kanal, rol bazlı yetki |
| Kota | Defter | Kiracı başına kota bütçesi + öncelik sırası | Bir müşteri tüm kotayı yiyemesin |
| Gözlem | Konsol | Sentry + metrikler | |

---

## 6. Veri modeli (kurulu)

| Tablo | Ne tutar |
|---|---|
| `channels` | Kanal kimliği, başlık, handle, avatar, banner, sayaçlar, son senkron, hata |
| `credentials` | Kanal başına refresh/access token (kanal silinince silinir) |
| `videos` | Video başlığı, süre, muhtemel Shorts, gizlilik, kapak URL, sayaçlar |
| `video_snapshots` / `channel_snapshots` | Her senkronda sayaç fotoğrafı → büyüme hızı, "son 24 saat" |
| `channel_daily` | Analytics günlük metrikleri (izlenme, süre, abone ±, gösterim, CTR) |
| `actions` | Her yazma işlemi: ne, ne zaman, yeni görsel, yedek, sonuç |
| `quota_log` | Tahmini kota harcaması (Pasifik günü) |

Faz 1A'da eklendi: `video_window` (dönemin en iyi videoları), `channel_breakdown`
(kaynak/içerik türü/ülke), `reporting_jobs` + `reporting_files` + `video_daily`
(Reporting API, video × gün).

İleride: `assets` (kapak kütüphanesi), `brand_kits` (kanal başına font/renk/yüz).

---

## 7. Yol haritası

### Faz 0 — Yerel temel ✅ (bu teslim)
Çok kanallı OAuth, senkronizasyon, panel (genel bakış + kanal detayı + 90 günlük grafik),
kapak yükleme (tıkla/sürükle), banner, toplu kapak (CLI), yedek + geri al, kota defteri,
16 otomatik test.

### Faz 1A — Çok kanallı analiz ✅ (kuruldu)
- 7/28/90 gün dönem seçici, her metrikte önceki döneme göre değişim; dönem Analytics'in
  son veri gününe sabitlenir.
- Kanal karşılaştırma tablosu (sıralama, CSV), portföy trendi (toplam / kanallara göre).
- Kırılımlar: izlenme kaynağı, içerik türü (`creatorContentType` ile kesin Shorts/uzun
  ayrımı), ülke — tüm kanallar ve kanal bazında.
- Dönemin en iyi videoları (Analytics `dimensions=video`) — tüm kanallarda.
- **Reporting API:** kanal başına `channel_basic_a3` + `channel_reach_basic_a1` işleri
  otomatik oluşturulur; günlük CSV'ler indirilip `video_daily`'ye işlenir (video × gün:
  izlenme, süre, beğeni, abone ±, kapak gösterimi, CTR). Analytics CTR vermezse kanal
  günlüğü buradan tamamlanır. İş oluşturulmadan önceki 30 gün geriye doldurulur;
  raporlar 30-60 gün sonra silindiği için düzenli senkron şart.

### Faz 1 — Gerçek kanallarda doğrulama (1-2 hafta)
- Google Cloud kurulumu, 2-3 gerçek kanal bağlama.
- **Shorts kapak davranışı testi:** `thumbnails.set` bir Shorts'ta nerede görünüyor, nerede
  görünmüyor — ekran görüntüleriyle belgele.
- Gerçek kota ölçümü (defter vs. Cloud Console).
- Tıklama oranı biriminin (oran / yüzde) gerçek veride doğrulanması.
- Video detay sayfası: yayından sonraki ilk 24/48/72 saat eğrisi, kanal ortalamasıyla kıyas.
- Zamanlanmış senkron (macOS launchd), kademeli yenileme.
- Studio "Yönetici" izni ile API onayı çalışıyor mu — test.
- **Bitti kriteri:** 1 hafta boyunca elle müdahale olmadan günlük veri akıyor; 10 kapak
  panelden değiştirilip geri alındı.

### Faz 2 — Kapak stüdyosu (2-3 hafta)
- Kapak kütüphanesi (kanal/etiket/kullanım geçmişi).
- Kanal başına marka kiti (font, renk, logo, yüz).
- AI kapak üretimi: `viral-edit/scripts/cover.py` + görsel üretim modelleri → panelde
  seç → tek tıkla yükle.
- Kapak rotasyonu (Fikir #4).
- Toplu metadata: açıklama alt bilgisi / link güncelleme tüm kanallarda (önce-sonra
  önizleme + onay).

### Faz 3 — Zeka katmanı (2-3 hafta)
- Anomali uyarıları (Telegram/e-posta): "Bu video ilk 24 saatte kanal medyanının 3 katı".
- Haftalık çok kanallı rapor + Claude teşhisi ("Neden düştü, ne yapmalı").
- **MCP sunucusu:** Claude'dan doğrudan "tüm kanallarımın bu haftası", "şu videonun kapağını
  değiştir" (yazma işlemleri onaylı).
- `viral-edit` ile tutma eğrisi döngüsü (Fikir #12).

### Faz 4 — Ekip / SaaS hazırlığı (4-6 hafta + Google süreçleri)
Postgres, worker, çok kullanıcılı yetki, şifreli token, alan adı, gizlilik politikası,
OAuth doğrulaması, YouTube API denetimi, PubSubHubbub, Reporting API.
> Google süreçleri haftalar sürdüğü için **başvuru Faz 2'de başlatılmalı.**

### Faz 5 — Lansman
Ödeme (Stripe/Iyzico), onboarding, fiyatlama (kanal sayısına göre katman), destek.

---

## 8. Fikir havuzu

Değer: ★ (düşük) – ★★★ (yüksek). Efor: S/M/L.

| # | Fikir | Değer | Efor | Not |
|---|---|---|---|---|
| 1 | Tüm kanallar tek ekranda + son 24 saat büyümesi | ★★★ | ✅ | Kurulu |
| 2 | Kapak yedekleme + tek tıkla geri alma | ★★★ | ✅ | Kurulu — Studio'da yok |
| 3 | Toplu kapak: klasöre `VIDEO_ID.jpg` koy, tek komut | ★★ | ✅ | Kurulu (CLI) |
| 4 | **Kapak rotasyonu testi:** A kapağı N gün → B kapağı N gün → CTR karşılaştır | ★★★ | M | Yeni CTR metrikleri sayesinde mümkün. Dürüst uyarı: rastgele bölünmüş test değildir; videonun yaşı ve algoritmik dağıtım sonucu etkiler. Uzun videolarda YouTube'un kendi testi daha güvenilir |
| 5 | AI kapak üretimi + marka kiti | ★★★ | M | `viral-edit` kapak üreticisi zaten var |
| 6 | Viral sinyal / düşüş uyarıları | ★★★ | S | Sayaç fotoğrafları kurulu; kural + bildirim yeter |
| 7 | Haftalık çok kanallı rapor + Claude teşhisi | ★★★ | S | `agency-ai` rapor kalıbı yeniden kullanılır |
| 8 | **MCP sunucusu** — Claude kanallarını doğrudan yönetir | ★★★ | S | Servis katmanı hazır; ince kabuk |
| 9 | Toplu metadata (açıklama alt bilgisi, link, etiket) | ★★ | M | `videos.update` tam snippet tuzağına dikkat |
| 10 | Zamanlanmış yükleme / yayın takvimi | ★★ | M | API denetimi şart (yoksa video özel kalır) |
| 11 | Birleşik yorum gelen kutusu + Claude cevap taslağı (insan onaylı) | ★★ | M | Otomatik toplu cevap yok — spam riski |
| 12 | **Tutma eğrisi → `viral-edit` geri beslemesi** | ★★★ | M | Her Shorts'un `audienceWatchRatio` eğrisi kurgu stil profiline otomatik akar. Repo zaten bu döngüyü elle kuruyor |
| 13 | Rakip / niş takibi (herkese açık sayaçlar) | ★★ | S | 1 birim/kanal |
| 14 | Çok dilli başlık/açıklama | ★★ | S | Türkçe içeriği global kitleye aç |
| 15 | Kanal sağlık skoru (yayın sıklığı, CTR trendi, tutma trendi) | ★★ | S | Tek sayıda özet |
| 16 | Ekip rolleri + onay akışı (editör önerir, sahip onaylar) | ★★ | L | SaaS için şart |

---

## 9. Riskler ve önlemler

| Risk | Etki | Önlem |
|---|---|---|
| Google proje askıya alınırsa tüm kanallar aynı anda kopar | Yüksek | Politikalara tam uyum, çoklu proje hilesi yok, en az yetki |
| OAuth doğrulaması / denetim gecikir | SaaS takvimi kayar | Başvuru Faz 2'de; o zamana kadar ≤100 kullanıcılı beta |
| YouTube API değişir (metrik, kota, sınır) | Orta | Değerler `config.py`'de tek yerde; metrik yoksa sistem temel metriklerle devam eder (kurulu) |
| Shorts kapak sınırı kullanıcıyı hayal kırıklığına uğratır | Orta | Panelde açık uyarı (kurulu), Faz 1'de belgelenmiş davranış |
| Token sızıntısı | Yüksek | Yerelde 0600 + git dışı; SaaS'ta KMS şifreleme |
| Yanlış toplu işlem (ör. 300 videonun açıklaması bozulur) | Yüksek | Önizleme + onay, denetim kaydı, geri alma |
| Kota tükenmesi | Düşük | Defter, yazma öncesi tahmin, kademeli yenileme |
| Rakipler (vidIQ, TubeBuddy, Metricool) | Orta | Çok kanallı kapak iş akışı + Claude teşhisi + üretim hattı birleşimi |

---

## 10. Başarıyı nasıl ölçeriz

- **Zaman:** Kanal başına haftalık yönetim süresi (Studio'da harcanan) yarıya inmeli.
- **Kapak:** Değiştirilen kapakların önceki/sonraki 7 günlük CTR farkı (Faz 2'den itibaren).
- **Güvenilirlik:** Senkron başarı oranı %99+, elle müdahalesiz 7 gün.
- **Kota:** Günlük kullanım < %20 (yazma işlerine yer kalsın).

---

## 11. Senden gerekenler (Faz 1'i başlatmak için)

1. Google Cloud projesi + iki API'nin açılması + Desktop OAuth istemcisi (adımlar
   `README.md` → "Google Cloud kurulumu").
2. Kanal listesi: kaç kanal, hangileri marka hesabı, hangileri YPP'de, Shorts mı uzun mu ağırlıklı.
   (Kimlik bilgileri paylaşılmaz: bağlantı kullanıcının kendi bilgisayarında kurulur.)
3. Kanallar telefonla doğrulanmış mı? (Değilse özel kapak hiç yüklenemez.)
4. Karar: SaaS hedefi ne zaman? (Google başvurularının ne zaman başlayacağını belirler.)

---

## Kaynaklar

- YouTube Data API — Thumbnails: set (50 MB sınırı) ve Revision History (2026-09-14)
- YouTube Analytics API — Metrics, Revision History (2026-01-15: `videoThumbnailImpressions`, `videoThumbnailImpressionsClickRate`)
- Shorts dikey görsel sınırı: github.com/Oghenefega/ClipFlow/issues/460 (topluluk bulgusu, Faz 1'de doğrulanacak)
- Yükleme kotası değişiklikleri: blotato.com/blog/youtube-api-pricing, outstand.so/blog/youtube-api-pricing-quota (üçüncü taraf; Cloud Console esas)
- YouTube API Services — Developer Policies, Google API Services User Data Policy
