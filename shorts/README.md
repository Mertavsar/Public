# Shorts — özlü söz / sıla hasreti video hattı

`data/quotes.json` içindeki her sözü **1080x1920 dikey mp4**'e çeviren Remotion projesi.
Tek komutla toplu üretim yapar.

## Kullanım

```bash
cd shorts
npm install

npm run studio      # tarayıcıda canlı önizleme + sözü elle düzenleme
npm run batch       # data/quotes.json içindeki tüm sözleri out/ altına render et
npm run batch gurbet-01 ozlem-02   # sadece belirli id'leri render et
npm run typecheck
```

Yeni söz eklemek için `data/quotes.json` dosyasına bir kayıt ekle, `npm run batch` çalıştır.

## Söz nasıl yazılır

```json
{
  "id": "gurbet-01",
  "quote": "Gurbet, memleketin adını duyunca\nsusmayı öğrenmektir.\nSen susarsın, için konuşur.",
  "cta": "Sen kaç yıldır gurbettesin?",
  "accent": "#c9873f"
}
```

- `\n` = ekranda **ayrı açılışta** gelen satır. Şiirsel kırılımlar korunur.
- **İlk satır hook'tur.** 8. karede (0,27 sn) ekrana gelir — Shorts'ta kaydırma kararı
  ilk 1-2 saniyede verildiği için hook kasıtlı olarak geciktirilmez. İlk satırı
  kaydırmayı durduracak şekilde yaz; gerisi ancak o tutarsa izlenir.
- `cta` yorum yemidir, sonda belirir. Yorum oranı Shorts dağıtımını doğrudan besler.
- Video süresi satır sayısından **otomatik** hesaplanır (`quoteDurationInFrames`).
  Sabit süre verilseydi kısa sözlerde ölü bekleme, uzunlarda kesilme olurdu.

## Neler halledilmiş durumda

**Türkçe karakterler.** Fontlar `public/fonts/` altına indirilmiş durumda, render
network'e bağımlı değil. Google Fonts'un `latin` ve `latin-ext` alt kümelerinin ikisi
de yükleniyor — kritik, çünkü `ı` (U+0131) `latin` içinde ama `İ ğ ş` `latin-ext`
içinde. Biri eksik olursa render'da kutu çıkar. Fontlar `FontFace` API + `delayRender`
ile yükleniyor, yani ilk kare fallback font ile render edilmiyor.

Etiketler büyük harfe çevrilirken `lang="tr"` kullanılıyor: Türkçede `i` harfinin
büyüğü `İ`'dir, CSS `uppercase` bunu dil bilgisi olmadan bilemez.

**Shorts güvenli alanı.** `src/theme.ts` içindeki `SAFE`, YouTube arayüzünün kapattığı
bölgeleri tanımlar (altta başlık/kanal adı, sağda beğen-yorum-paylaş sütunu). Studio'da
`showSafeArea` açılırsa kırmızı bölgeler ve yeşil kesikli kutu görünür.

Not: bu kutu `AbsoluteFill` ile **yapılmaz** — o bileşen `width/height: 100%` dayattığı
için `top/left/right/bottom` verince kutu daralmaz, metin sağdaki buton sütununun altına
kayar. Düz `div` + açık `width`/`height` kullanılıyor.

**Taşma koruması.** `fitQuote` metni gerçekten ölçer (`measureText`), kelime bazında
sarar ve sığmazsa puntoyu kademeli düşürür. Sabit punto ile 50 söz basılsa uzun olanlar
ekrandan taşar ve bunu ancak yükledikten sonra fark ederdin. En küçük puntoda bile
sığmayan söz olursa toplu render sonunda `UYARI - metni kısalt: <id>` satırı basılır.

**Loop.** Sonda karartma (fade to black) yok. Shorts videoyu döngüye aldığı için
karartma retention'ı boşa harcar; sert kesişle başa dönmek daha iyi çalışır.

## Arka plan

İki yol var: hazır sahne veya kendi dosyan.

**Hazır sahne** — `scene` alanı:

- `"bozkir"`: kodla çizilmiş Anadolu bozkırı (gün batımı, dört katmanlı tepe
  silueti, yalnız ağaç, süzülen toz). Katmanlar farklı paralaks hızında kaydığı
  için derinlik hissi var. Fotoğraf değil, silüet illüstrasyon -- ama telif riski
  sıfır ve tepe hattı/ışık her videoda değiştirilebilir.
- `"gradient"` (varsayılan): animasyonlu sepya gradyan.

**Kendi dosyan** — `background` alanı. Verilirse `scene` yok sayılır.


Kendi görselini/videonu koymak için dosyayı `public/` altına at ve yolu ver:

```json
"background": "bg/tren-penceresi.mp4"
```

Video veya görsel farkı otomatik anlaşılır, ikisine de yavaş Ken Burns zoom uygulanır
(sabit görüntü Shorts'ta durgun hissettirir ve kaydırılma oranını artırır). B-roll varken
okunabilirlik perdesi otomatik olarak koyulaşır.

## Bu ortama özel not

Remotion kendi Chrome Headless Shell'ini indiremiyor (`remotion.media` ağ
politikasında yok). `scripts/find-chrome.mjs` kurulu Chromium'u bulur;
`headless_shell` önceliklidir çünkü tam Chrome binary'sinde eski headless modu
kaldırılmış ve Remotion onu başlatamıyor. Başka makinede farklı bir yol gerekirse
`REMOTION_BROWSER_EXECUTABLE` ile geçilebilir.

## Henüz yok

- **Seslendirme ve müzik.** Şu an videolar sessiz.
- **Otomatik yükleme.** YouTube Data API bağlanmadı, mp4'ler elle yükleniyor.

## Müzik konusunda uyarı

Bu nişte popüler bir Türkçe şarkı kullanmak Content ID talebi doğurur: video yayında
kalır ve izlenir, ama **gelir şarkının hak sahibine gider**. Telifsiz müzik veya kendi
ürettiğin ses kullanılmalı. Bu kanalın en kritik teknik kararı müzik seçimidir,
animasyon değil.

Ayrıca: YouTube'un "inauthentic content" politikası tam olarak şablona farklı metin
koyup seri üretim yapmayı hedefliyor. Bu hat üretim hızı içindir; her videoya kendi
yorumunu/anlatını katmadan sadece otomasyona yaslanmak monetizasyon riskini büyütür.
