# Kuzu Lahmacun: lezzet şovu

Site lahmacunun hikâyesini anlatır (sitede her yerde "Lahmacun" yazılır). Kaydırma sahnesi altı perde: hamur, açılış, iç, et,
fırın, servis. Havada dökülen her malzemenin adı, düştüğü yerden çıkan ince bir çizgiyle
yazılır. Ardından kısa lahm-ı acîn yazısı, göç hikâyesi, dört kalem (hamur, et, iç, fırın),
ustanın sözlüğü, menü ve paket sipariş butonları, galeri (işletmenin fotoğraflarıyla slider), Google yorumları,
merak edilenler (SSS) ve final gelir. Kısa yazının hemen altında YouTube Shorts videoları (çerçeveli, 9:16).

- `index.html`: sitenin tamamı (tek dosya).
- `kaynak/sahne1-3.mp4`: Google Flow sahneleri (beze ve açılış, malzeme yağmuru, fırın).
- `hazirla.sh`: sahneleri birleştirip `frames/` ve `frames-mobil/` setlerini üretir.
- `frames/`: bilgisayar sahnesi: 330 kare, 2x2'lik 83 pakette (`paket-N.jpg`), önizleme paketleri ve `manifest.json`.
- `frames-mobil/`: telefon sahnesi: yalnızca telefonun gösterdiği orta bölge, kaynağın kendi çözünürlüğünde (870 px); aynı düzen.
- `foto/`: işletmenin kendi fotoğrafları (lahmacun, lahmacun-firin, kilis-tava, sofra), her biri üç boyutta:
  2000 px, `-m` 1200 px, `-k` 720 px. Tarayıcı ekranına uyanı indirir. Galeride (slider) kullanılır; finalde lahmacun.
- `logo.svg`: markanın logosu, orijinalinden (`kaynak/logo-orijinal.webp`) vektöre çevrildi; her boyutta
  keskin. Sitede yeşil kutusuz, şeffaf hâli (`logo-beyaz.svg`) kullanılır: üst çubukta, girişte ve sayfa sonunda. `favicon.svg`: logodaki fırın, tarayıcı sekmesi için.

## WordPress teması

```bash
python3 wp-tema/olustur.py 1.0.0     # sürüm numarası: her güncellemede bir artırın
```

`index.html` tek kaynaktır; betik onu WordPress temasına çevirir ve `wp-tema/dagitim/` altına üç zip yazar:

- `kuzu-lahmacun-<sürüm>.zip` (~35 MB): Görünüm → Temalar → Yeni ekle → Tema yükle → Etkinleştir.
  Güncellemede aynı yoldan yüklenir; WordPress "Yüklenen ile değiştir" der. Paneldeki ayarlar korunur.
- Sunucu büyük zip'i kabul etmezse: `kuzu-lahmacun-<sürüm>-hafif.zip` (~2 MB) tema olarak,
  `kuzu-sahne-kareler.zip` hosting dosya yöneticisiyle `wp-content/uploads/` içine açılır
  (`wp-content/uploads/kuzu-sahne/frames/...`). Tema kareleri kendisi bulur.

Panel (sol menüde **Kuzu Lahmacun**): iletişim ve saatler, menü (`Kategori | Ürün | Fiyat`), videolar
(`YouTube linki | başlık`; oynatıcı yalnızca tıklanınca yüklenir), eve sipariş butonları (satır satır: ikon
Medya'dan, ad, link, renk; sürükleyerek sıralanır; "+ Yemeksepeti" gibi hızlı ekle düğmeleri), merak edilenler,
kayan bant, galeri (Medya'dan seçilir, sürükleyerek sıralanır), Google API anahtarı ve "Yorumları şimdi yenile".
Yorumlar günde bir kez kendiliğinden yenilenir, sitede yalnızca 5 yıldızlılar görünür. Kaydırma sahnesi, perde
yazıları ve tasarım koddadır: değişiklik `index.html`'de yapılır, yeni sürüm zip'i üretilir.

Videolar ayrıca **Görünüm → Özelleştir → Kuzu Lahmacun** içinde: link yapıştırılınca
sağdaki önizleme o bölüme iner ve videoyu yerinde gösterir; **Yayımla** ile sitede. İki ekran aynı ayarı düzenler.
Görünüm menüsünde ayarlar sayfasına kısayol var.

`index.html` içindeki `<!--wp:...-->` işaretleri panelden gelen bölümlerin yeridir; silinmemeli.
Üç zip de bir WordPress 6.8 kurulumunda yüklenip denendi (ilk kurulum, güncelleme, panelden kayıt,
galeri seçimi, yorum çekme, hafif zip).

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
- `onizleme-*.jpg`: bütün karelerin küçük hâli 7 dosyada. Sayfa önce bunları
  indirir; kaydırma ilk saniyeden her karede doğru görüntüyü gösterir. Keskin kareler aynı anda
  4–6 tane, kullanıcının bulunduğu yere en yakın olandan başlayarak gelir ve ancak açıldıktan
  sonra kullanılır.
- Canvas hiçbir zaman videonun dolduramayacağı kadar piksel çizmez (bilgisayarda ~1x, telefonda
  en fazla 1,5x); cihaz zorlanırsa kendiliğinden bir kademe düşer.
- Telefondaki bulanık arka plan ayrı, küçük bir katmandır (`#softbg`); ekran kartı büyütür,
  sadece kare değişince güncellenir.

Telefonda ilk girişin keskin olması için:
- Telefon ayrı bir set yükler (`frames-mobil/`): ekranda görünen orta bölge, ekranın ihtiyacı
  kaynağın tam çözünürlüğünde (16 MB'a karşı 22 MB).
- Kareler 4'erli paketlerde gelir: istek sayısı 4'e bölünür (yavaş sunucuda ilk giriş hızlanır).
- Keskin paketler kabadan inceye iner: önce bütün sahneye yayılmış her 4. paket, sonra aralar.
  Tam karenin keskini yoksa en fazla 4 kare ötedeki keskin kare gösterilir; bulanık önizleme
  yalnızca en baştaki bir iki saniye için yedektir.


## Google: yorumlar, puan, adres ve saatler

```bash
GOOGLE_API_KEY=... python3 google-cek.py
```

`google/yer.json` dosyasını yazar; site bu dosyayı okur. Google Cloud'da "Places API (New)" açık bir
anahtar gerekir. Yorumlar Google'ın seçtiği en fazla 5 yorumdur.

- Doğru işletme: "Kuzu Lahmacun" adında rakip bir işletme daha var. Betik yalnızca müşterinin
  linkindeki kaydı (CID 13202010269743240704) kabul eder; arama başka yer döndürürse durur.
- Dosya yoksa Yorumlar bölümünde yalnızca başlık görünür; hiçbir şey uydurulmaz.
- Site ziyaretçiyi Google'a göndermez; yalnızca "Yol tarifi" butonları işletmenin kendi Google
  Haritalar kaydını açar.

## Ayarlar (`index.html` içinde)

- `KEYS`: kaydırma ile video zamanını perdelere eşler.
- `MARKS`: etiketler. Her biri hangi saniyede çıkıp kaybolacağını, videodaki yerini (u, v),
  yazının hangi tarafta duracağını ve metnini tutar. Yeni video gelirse bunlar ayarlanır.
- `FOCUS`: telefonda tam ekran kadrajın hangi saniyede videonun neresine bakacağı
  (hamur, dökülen malzeme, fırında lahmacun boyunca yavaş pan).
- Adres sonuna `#dene` yazılırsa yeni bir Flow videosunu tarayıcıda deneme kutusu açılır.

## Doldurulacaklar

- Menünün kesik kalan kısmı: çorba adı ve içecekler.
- SSS'ye işletmenin cevaplaması gereken sorular: paket servis / yemek uygulamaları, rezervasyon,
  çalışma saatleri, otopark.
- Adres, telefon, çalışma saatleri: `google-cek.py` çalışınca Google kaydından gelir.
- Sahne 3'te lahmacun alevle pişiyor; işletmenin metni "harlı ateşte değil, taşta" diyor.
