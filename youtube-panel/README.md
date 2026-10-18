# Kanalist — tüm YouTube kanalları tek panelde

Kanalı olan herkes **Google ile giriş yapar**; giriş yaptığı hesabın YouTube kanalı
panele kendiliğinden gelir. Diğer kanallarını **Kanal ekle** ile bağlar. Sonra
Studio'da hesap hesap gezmeden hepsini tek ekranda görür.

Ürün adı geçici; `.env` içindeki `APP_NAME` ile tek yerden değişir.

## Ne var

- **Genel bakış:** tüm kanalların toplam izlenme, izlenme süresi, net abone ve
  abonesi; önceki döneme göre değişim. Ana grafik önceki dönemle karşılaştırmalı
  çizilir; bir günün üstüne gelince o gün hangi kanalın ne kadar izlendiği görünür.
  Öne çıkanlar (en hızlı büyüyen, en çok düşen, en çok abone kazanan), izlenme
  payı, sıralanabilir kanal tablosu ve **tüm kanallarda en çok izlenen videolar**.
- **Kolay geçiş:** kenar çubuğunda her kanal değişim okuyla durur, tek tıkla
  açılır. `⌘K` / `Ctrl K` ile kanal ara; kanal sayfasında `←` `→` ile önceki ve
  sonraki kanal.
- **Kanal sayfası:** izlenme / izlenme süresi / net abone grafiği, dönemin en çok
  izlenen videoları (ortalama izlenme yüzdesi, süre, kazandırdığı abone), son
  yüklenenler; YouTube ve Studio'ya tek tıkla geçiş.
- **Ayarlar:** paket ve kanal kullanımı, kanal kaldırma, hesabı silme (Google'ın
  doğrulama için istediği "verimi sil" hakkı).
- 7 / 28 / 90 günlük dönem, açık ve koyu tema, mobil uyumlu.

Panel **sadece okur.** Google'dan istenen izinler `youtube.readonly` ve
`yt-analytics.readonly`'dir; kanallarda hiçbir şey değiştirilemez, yüklenemez,
silinemez.

## Hemen bak (örnek veriyle)

```
pip install -r youtube-panel/requirements.txt
python3 youtube-panel/app.py --demo
```

Tarayıcıda **http://localhost:8000**. 8 uydurma kanalla tüm paneli gezersin;
Google'a bağlanmaz.

## Gerçek girişi açmak (bir kerelik)

### 1. Google Cloud

1. https://console.cloud.google.com → yeni proje.
2. **API'ler ve Hizmetler → Kitaplık**: **YouTube Data API v3** ve
   **YouTube Analytics API**'yi etkinleştir.
3. **Google Auth Platform** → **Başlayın**: uygulama adı (`APP_NAME` ile aynı),
   destek e-postası, kitle **Harici**.
4. **Veri erişimi** → kapsam ekle: `openid`, `email`, `profile`,
   `youtube.readonly`, `yt-analytics.readonly`.
5. **İstemciler → İstemci oluştur → Web uygulaması**.
   **Yetkili yönlendirme URI'leri**: `http://localhost:8000/oauth/callback`
   (sunucuya taşıyınca `https://alanadin.com/oauth/callback` da ekle).
   İstemci kimliğini ve gizli anahtarı kopyala.

### 2. Ayar dosyası

```
cp youtube-panel/.env.example youtube-panel/.env
```

`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` ve `SECRET_KEY`'i doldur (anahtarı
üretme komutu dosyanın içinde). Sonra:

```
python3 youtube-panel/app.py
```

### 3. Test kullanıcıları ve yayın

Google uygulamayı doğrulayana kadar:

- **Kitle** sayfasında uygulama "Test" modundaysa sadece eklediğin **test
  kullanıcıları** girebilir ve bağlantılar **7 günde bir** düşer.
- **Uygulamayı yayınla** dersen herkes girebilir, ama girişte "Google bu uygulamayı
  doğrulamadı" uyarısı çıkar ve en fazla 100 kullanıcı olur.
- Uyarısız ve sınırsız kullanım için Google **uygulama doğrulaması** gerekir: alan
  adı, açılış sayfası, gizlilik politikası ve uygulamanın tanıtım videosu istenir.

## Bir hesapta birden fazla kanal

Google her girişte **tek bir kanala** erişim verir. Bir Google hesabında birden
fazla kanal (Brand Account) varsa, giriş ekranında Google hangi kanalı istediğini
sorar; her kanal için **Kanal ekle**'yi bir kez tekrarlamak gerekir. Panele bağlı
kanallardan herhangi birinin hesabıyla giriş yapmak aynı paneli açar.

Kanalın **sahibi** veya Brand Account **yöneticisi** olan hesapla giriş yapılmalı;
Studio'daki "İzinler" bölümünden davet edilen kullanıcılar genellikle kanalı API'de
göremez.

## Sunucuya kurmak

```
pip install -r requirements.txt
uvicorn app:app --app-dir youtube-panel --host 0.0.0.0 --port 8000
```

- Önüne HTTPS veren bir ters vekil (Caddy, Nginx) veya HTTPS'li bir barındırma
  koy. `BASE_URL`'i `https://...` yap; oturum çerezi o zaman otomatik olarak
  yalnızca HTTPS üzerinden gönderilir.
- `SECRET_KEY`'i ortam değişkeni olarak ver ve yedekle. Kaybolursa kayıtlı kanal
  anahtarları açılamaz, herkes kanallarını yeniden bağlamak zorunda kalır.
- Veritabanı `DATA_DIR/app.db` (SQLite). Kalıcı bir diske koy ve yedekle.

## Yapı

| Dosya | Görevi |
|---|---|
| `app.py` | Sunucu: giriş, oturum, API, paket sınırları (`PLAN_LIMITS`) |
| `youtube.py` | Google/YouTube çağrıları ve hesaplamalar (sadece okuma) |
| `db.py` | Kullanıcılar, oturumlar, şifreli kanal anahtarları |
| `demo.py` | `--demo` için örnek veri |
| `static/landing.html` | Giriş yapmamış ziyaretçinin gördüğü sayfa |
| `static/app.html` | Panel |

## Bilmen gerekenler

- **Veri gecikmesi:** YouTube istatistikleri yaklaşık 2 gün gecikmeli gelir; dönem
  bu yüzden 2 gün önce biter. Abone sayıları anlıktır.
- **Kota:** Her kanalın verisi 10 dakika saklanır, **Yenile** hemen yeniden çeker.
  Varsayılan günlük YouTube kotası ilk yüzlerce kullanıcıya yeter. Daha fazlası
  için YouTube'un ücretsiz uygunluk denetimiyle kota artırılır.
- **Güvenlik:**
  - Kanal anahtarları veritabanında şifreli durur.
  - Oturum çerezleri `HttpOnly`'dir.
  - Her kullanıcı yalnızca kendi kanallarını görür.
  - Kanal kaldırılınca veya hesap silinince Google'daki izin de geri alınır.
