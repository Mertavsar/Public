# Kanalist — tüm YouTube kanalları tek panelde

Kanalı olan herkes **Google ile giriş yapar**; giriş yaptığı hesabın YouTube kanalı
panele kendiliğinden gelir. Diğer kanallarını **Kanal ekle** ile bağlar. Sonra
Studio'da hesap hesap gezmeden hepsini tek ekranda görür.

Ürün adı geçici; `.env` içindeki `APP_NAME` ile tek yerden değişir.

## Ne var

Panel bir yayın kontrol odası gibi tasarlandı: onlarca kanal işleten biri aslında
küçük bir televizyon ağı yönetiyor.

- **Monitör duvarı:** her kanal CH numaralı bir monitör. Büyük izlenme rakamı,
  gidişat çizgisi, toplam izlenmedeki payı gösteren seviye ölçer, yükseliyor /
  düşüyor ışığı. %10'dan sert düşen kanal **DİKKAT** ile işaretlenir. Tablo
  isteyene **Liste** görünümü.
- **Ölçü şeridi:** toplam izlenme, izlenme süresi, net abone, abone. Ölçüye
  tıklayınca grafik o ölçüye geçer, önceki dönemle karşılaştırmalı çizilir; bir
  günün üstüne gelince o günün kanal kırılımı görünür.
- **Hareket bandı:** dönemin en çok yükselen ve düşen kanalları ekranın altında akar.
- **Yayın akışı:** tüm kanallarda dönemin en çok izlenen videoları.
- **Kolay geçiş:** kenar çubuğunda her kanal numarası ve ışığıyla durur. `⌘K` /
  `Ctrl K` ile adını ya da numarasını yaz; kanal sayfasında `←` `→`.
- **Kanal sayfası:** grafik, dönemin en çok izlenenleri, son yüklenenler; YouTube
  ve Studio'ya geçiş.
- **Ayarlar:** paket kullanımı, kanal kaldırma, hesabı silme (onay sayfanın içinde).
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

## GitHub'dan, kurulum yapmadan aç (Codespaces)

1. GitHub'da repoyu aç → yeşil **Code** düğmesi → **Codespaces** → **Create codespace**.
2. Açılan tarayıcı içi editörde, alttaki terminale yaz:
   ```
   python3 youtube-panel/app.py --demo
   ```
3. Sağ altta çıkan **Open in Browser**'a bas (ya da **Ports** sekmesinde 8000'i aç).

Gerçek girişi Codespaces'te denemek için aşağıdaki kurulumu yap. Google Cloud'daki
yönlendirme adresine codespace'in adresini ekle:
`https://<codespace-adı>-8000.app.github.dev/oauth/callback`. Panel bu adresi
kendisi algılar. Başlatırken terminalde `Giriş adresi` olarak yazar.

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

## Tek e-postada onlarca kanal

Bir Gmail adresinin altındaki kanalların her biri ayrı bir Brand Account'tur ve
Google her girişte **yalnızca seçilen tek kanala** erişim verir. "Bu e-postadaki
bütün kanalları ver" diyen bir YouTube API'si yok; tek istisna, YouTube İş Ortağı
(CMS / içerik sahibi) hesaplarıdır.

Panel bunu bir döngüyle çözer:

1. **Google ile giriş yap** → ilk kanal eklenir, ara sayfa açılır (`/ekle`).
2. **Evet, diğer kanallarımı da ekle** → panel seni Google'ın kanal seçicisine
   götürür; Google hesabın önceden seçili gelir (`login_hint`).
3. Kanalı seç, izin ver → eklenir, 3 saniye sonra sıradaki için Google yeniden
   açılır. Zaten ekli kanalı seçersen atlanır.
4. Bitince **Bitti**'ye bas ya da Google ekranında **İptal** de.

Bu her kanal için bir kez yapılır. Sonraki girişlerde, bağlı kanallardan
herhangi birinin hesabıyla girmek bütün kanalları getirir.

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
| `static/landing.html` | Tanıtım ve fiyat sitesi (giriş yapmamış ziyaretçinin gördüğü sayfa) |
| `static/app.html` | Panel |
| `static/ekle.html` | Toplu kanal eklemenin ara sayfası |
| `static/fonts/` | Archivo, Big Shoulders Display, Chivo Mono (SIL Open Font License); Google'a bağlanmadan sunulur |
| `static/img/` | Açılış sayfasındaki panel görüntüleri (örnek veriyle alındı) |

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
