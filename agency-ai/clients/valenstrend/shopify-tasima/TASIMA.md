# Valenstrend → yeni Shopify mağazası taşıma planı

Amaç: Valenstrend mağazasının (1t35rr-vh.myshopify.com, valenstrend.myshopify.com) tasarımı ve
içeriği birebir yeni mağazaya kurulsun. Bu dosya bir sonraki oturumun kaldığı yerden devam
etmesi içindir. `veri/` altındaki her şey 7 Ekim 2026'da Valenstrend'den okunmuştur (FACT).

## Durum (7 Ekim 2026, akşam)

Yeni mağaza bağlandı: **"Mağazam" — 9txzze-0r.myshopify.com** (trial plan, TRY, tr).
Yeni mağazadaki ID'ler: `veri/yeni_magaza_ids.json`.

TAMAM (Claude, API ile, doğrulandı):
- 6 tema görseli aynı dosya adlarıyla yüklendi (READY).
- 14 koleksiyon aynı handle/kural/sıralama/SEO ile kuruldu; 13'ü Online Mağaza'da yayında,
  `kampanya-tum-esarp-ve-sallar` gizli (Valenstrend'deki gibi).
- 8 sayfa: contact güncellendi; hakkimizda, sss, gizlilik-politikasi,
  mesafeli-satis-sozlesmesi, cerez-politikasi yayında; kargo-ve-teslimat ve iade-ve-degisim
  gizli (Valenstrend'deki gibi). Boş `ana-sayfa` sayfası taşınmadı.
- Menüler: ana-menu-yeni, footer-kategoriler, footer-yardim, footer-kurumsal oluşturuldu;
  main-menu Valenstrend'deki gibi güncellendi.
- Kargo: Standart Kargo (1000 TL üzeri ücretsiz) 125 TL [0–999,99], Ücretsiz Kargo [≥1000],
  "Hızlı" 299 TL silindi; yurt dışı "Standard" 850 TL (aynı 28 ülke).
- İndirim "5 Eşarp/Şal Alana 1 Koton Eşarp Hediye" aktif.
- 5 yönlendirme oluşturuldu.
- Gizlilik politikası: Shopify'ın otomatik politikası zaten var; kopyalanmadı.

TAMAM (kullanıcı yükledi, Claude doğruladı — 7 Ekim gece):
- Tema zip yüklendi ve yayında; adı "Valenstrend – Güncelleme 3 (Sabit menü)" yapıldı.
  15 tema JSON dosyasının md5'i Valenstrend ile birebir aynı.
- Ürünler: 1038/1038, hepsi aktif ve Online Mağaza'da yayında.
- Koleksiyon ürün sayıları Valenstrend ile birebir aynı (koton-esarp 348, en-cok-satanlar 628,
  kampanya 1035 vb.).

BEKLİYOR (kullanıcı):
- Mağaza adı: kullanıcı "Valenstrend " yaptı (9 Ekim; sonda boşluk var).
- Kapıda ödeme 45 TL ücreti (1000 TL altı): kargo seçeneği + ödeme kuralı uygulaması önerildi, onay bekleniyor.
- Mağaza ve konum adresi boş (hangi adres doğru, kullanıcıya soruldu).
- Plan seçimi (deneme süresi bitiyor) ve şifre kaldırma.
- Ödeme (iyzico uygulaması, kapıda ödeme, havale), vergi ayarı, uygulamalar, alan adı.
- Yurt dışı: yeni mağazada sadece "Türkiye" pazarı var; Valenstrend'deki durum bilinmiyor.

## Ürün açıklaması düzeltmesi (13 Ekim 2026) — TAMAM

Yedek: `veri/urun_aciklamalari_yedek_2026-10-13.json` (28 farklı açıklama + 1038 ürün → açıklama no).
543 üründe yanlış/eski bilgi vardı (fiyat, havale, WhatsApp, "3 adet kargo ücretsiz", 6 taksit,
Rosebella/Amber'de "Flora İpek", "Pakuksu"). Fiyat/ödeme/kargo satırları silindi (tema ürün
sayfasında doğrusu yazıyor), isim ve yazım hataları düzeltildi. Kullanıcı yeni metinleri görüp onayladı.
Uygulanan: Koton Eşarp 345, Jakarlı 77, Çocuk 62, Anne 20, Omuz 7, Triko 7, İncira 25.
Doğrulama: 1038 ürün yeniden okundu; 543'ü yeni metinle birebir, diğer 495 değişmedi; havale,
WhatsApp, ₺, taksit, "Pakuksu", "mavi ve siyah" hiçbir açıklamada kalmadı.

## Tema durumu (14 Ekim 2026)

- CANLI: "Güncelleme 6 (Klasik kategoriler)" 166337773654 (kullanıcı yayınladı). Ödeme yazıları güncel,
  kategori şeridi eski sade görünümde, Koton Eşarp'ta "En Çok Satan" rozeti. Footer "Ödeme ve telif"
  bölümüne kullanıcı ödeme logoları görselini yükledi (`test.png`, 429×32, yükseklik 26 px).
- Güncelleme 5 artık yayında değil (renkli halkalı sürüm).
- YENİ: "Güncelleme 6 (Klasik kategoriler)" 166337773654 = Güncelleme 5 + kategori şeridi eski sade
  görünümde (ince gri çerçeve, 120/78 px), Çok Satanlar ve Tümünü Gör balonları kapalı, sadece Koton
  Eşarp'ta "En Çok Satan" rozeti. Çerçeve stili tema düzenleyicide seçilebilir (klasik / renkli).
  Dosyalar geri okunup doğrulandı. Kullanıcı yayınlayacak. Kopyası: `veri/tema_guncelleme5/`.
- Kategori görselleri: koleksiyonların kendi görseli yok, dairede ilk ürünün fotoğrafı çıkıyor.
  Fotoğrafları seçmek için ortamda cdn.shopify.com erişimi gerekir (şu an kapalı).
- 16 Ekim: Mobilde ürün fotoğrafı kesik görünüyordu. Sebep bizim `sections/vt-stil.liquid` içindeki mobil
  kuralı: `--gallery-aspect-ratio:1 !important` (kare) + `object-position:50% 30%`. Fotoğraflar 4:5
  (1080×1350; ilk 250 üründe 249'u, 1 tanesi 3:4), kare kutuda alt ve üst ~%20 kırpılıyordu.
  Düzeltme: iki satır silindi, mobilde şablonun "Dikey 4:5" ayarı geçerli. Uygulandığı tema:
  "Güncelleme 7 (Mobil görsel kesilmesin)" 166461833302 = Güncelleme 6'nın kopyası + bu düzeltme
  (MD5 geri okunup doğrulandı). Kullanıcı 16 Ekim'de yayınladı → CANLI tema artık Güncelleme 7.
  Yayından sonra 490 tema dosyasının MD5'i Güncelleme 6 ile karşılaştırıldı: tek fark `sections/vt-stil.liquid`.
  Eski dosya: `veri/tema_yedek/vt-stil_2026-10-16_once.liquid`.

## Domain geçişi hazırlığı (15 Ekim 2026)

- Kullanıcı iyzico'yu bağladığını söyledi (doğrulanmadı, API'den görünmüyor).
- WordPress ürün linkleri `valenstrend.com/urun/<slug>/` (Meta kataloğu "Katalog_Ürünler" 3598453573752694'ten okundu).
  Shopify handle'ları çoğunlukla aynı. 1065 yönlendirme CSV ile içe aktarıldı (`veri/yonlendirmeler_wordpress.csv`):
  1038 `/urun/<handle>` → `/products/<handle>`, 6 farklı slug (bone, -2 ekli koza, kibrit-gri, su-yolu-kirmizi),
  12 `/urun-kategori/<handle>` → `/collections/<handle>`, 9 sayfa (/magaza, /sepet, /sss ...). Import id 147161174: 1065 oluşturuldu, 0 hata (toplam 1070 yönlendirme).
- Katalogdaki 1120 üründen Shopify'da olmayan ~82 link için yönlendirme yok; 404 sayfası En Çok Satanlar gösteriyor.
- Facebook & Instagram uygulaması bağlandı (15 Ekim, kullanıcı). Yeni katalog: "Shopify Product Catalog (9txzze-0r.myshopify.com)"
  2558225854645005, aynı işletme (valenstrendonline 631507039023207). 1038 ürün kanalda yayında (otomatik eklenmiş);
  Meta'ya senkron başladı (ilk okumada 931 → 1000+ öğe, görseller henüz işlenmemiş, tanı hatası yok).
  Piksel aynı: Valenstrendonline 1305259216806142, aktif.
- Eski katalog "Katalog_Ürünler" 3598453573752694 silinmeyecek; geçişten birkaç hafta sonra arşivlenebilir.
  Aktif ad set'lerin hiçbirinde ürün seti (product_set) yok — katalog tabanlı kampanya görünmüyor (15 Ekim, Meta API okuması).
  Meta ise eski katalogdaki 5 ürün setinin "aktif reklamları etkileyen" sorunları olduğunu söylüyor; geçiş öncesi reklam/kreatif
  düzeyinde katalog kullanımı ayrıca kontrol edilecek.

## Stok eşitleme — WordPress → Shopify (15 Ekim 2026)

- Kaynak: valenstrend.com bu ortamdan erişilemiyor (proxy 403). WooCommerce'in Meta'ya gönderdiği eski katalog
  (feed "Ürünler", 15 Ekim 15:25 PDT güncellenmiş) kullanıldı: 1120 öğe = 692 stokta + 428 tükendi.
- Eşleştirme **ürün adıyla** yapıldı. Shopify handle'ları WordPress linkinden değil ürün adından türetilmiş
  (ör. WP `organik-soft-esarp-113` = "Organik Soft Eşarp 112", WP `desenli-koton-esarp-474-2` = "...466").
  11 üründe WP linki ile ad farklı.
- Uygulanan: 104 ürün tükendi yapıldı (takip açık + DENY; 15'inde adet 1-3 → 0), 84 ürün satışa açıldı
  (takip kapalı + CONTINUE, mağazadaki diğer stokta ürünlerle aynı ayar). Hatasız.
- Geri okuma sonrası: 608 satışta, 422 tükendi, uyumsuz 0. WordPress'te hiç olmayan 8 ürün
  (desenli-koton-esarp 343/442/443/488/575/577/615/616) tükendi olarak bırakıldı.
- WP'de tükenmiş ama Shopify'da hiç olmayan 6 ürün: Desenli Koton 666/699, Müslin Şal Taş Siyah,
  Organik Soft Eşarp 225, Organik Soft Şal 286/289.
- Not: WP'de 692 stokta öğe var, Shopify'da satışta 608 ürün → WP'de satılan ama Shopify'da olmayan ürünler
  olabilir (ör. Müslin Şal serisi stokta, Shopify'da yok). Liste çıkarılmadı.
- Stok takibi kalıcı değil: WordPress'te sonradan değişen stok Shopify'a kendiliğinden geçmez.
- Yedek ve değişiklik listesi: `veri/stok_esitleme_yedek_2026-10-15.json`.

## Domain geçiş planı (16 Ekim 2026 gecesi, kullanıcı uyguluyor)

Karar: eski WordPress `eski.valenstrend.com` adresinde çalışmaya devam edecek (bekleyen 11 WooCommerce siparişi
ve eski kayıtlar için), `valenstrend.com` Shopify'a geçecek. Shopify planı: Grow.

1. Hazırlık: Cloudflare DNS listesinin ekran görüntüsü (geri dönüş için), Hostinger tam yedek, bekleyen siparişlerin dökümü,
   Shopify şifre koruması kapalı.
2. eski: Cloudflare `A eski → 147.93.73.220` (gri bulut) → Hostinger'da `eski` alt alan adı, klasör public_html → SSL.
3. Geçiş: WP Ayarlar → Genel iki adres `https://eski.valenstrend.com` → hemen ardından Shopify'da alan adı bağla,
   Cloudflare `A @ → 23.227.38.65` (gri), `CNAME www → shops.myshopify.com` (gri), AAAA'lar silinir;
   MX/TXT/CAA ve `eski` kaydına dokunulmaz → Shopify'da doğrula, birincil yap.
4. Sonra: eski sitede arama motoru engeli + Facebook for WooCommerce eklentisi kapatılır, Meta alan adı doğrulaması ve
   Search Console site haritası kontrol edilir.
- Geri dönüş: A kaydı 147.93.73.220'e, AAAA'lar geri, WP adresleri valenstrend.com'a.

**Uygulanan (16 Ekim ~03:15 TR):** kullanıcı eski.valenstrend.com kurmadan doğrudan taşımayı seçti (bekleyen siparişlerin
PDF'ini aldı). Cloudflare'de AAAA yoktu; değişen sadece 2 kayıt:
- `A valenstrend.com`: 147.93.73.220 (Proxied) → 23.227.38.65 (DNS only)
- `CNAME www`: valenstrend.com (Proxied) → shops.myshopify.com (DNS only)
- Dokunulmayan: ftp A (Hostinger), CAA'lar (letsencrypt, pki.goog dahil), autoconfig/autodiscover/hostingermail DKIM CNAME'leri,
  MX mx1/mx2.hostinger.com, NS dns-parking, _dmarc TXT, 2. sayfadaki 1 kayıt.
- Shopify: DNS doğrulandı, tüm bölgelerde yayında, birincil alan adı valenstrend.com (API: sslEnabled true; TLS ekranı ~5 dk diyordu).
- Shopify'da müşteri sayısı 1 (sadece test) → eski WooCommerce müşteri listesi henüz aktarılmadı.

**Geçiş sonrası kontrol (16 Ekim 11:45 TR):**
- Shopify oturumları 00:00'dan beri 166; piksel geçişten sonra hem tarayıcı hem sunucu (CAPI) olayı alıyor;
  #1002/#1003 test siparişlerinin Purchase olayları geldi.
- Sorun: Shopify'da olmayan WP ürünlerinin linkleri 404'e düşüyordu (açılış sayfaları: /urun/organik-soft-esarp-231 19 oturum
  — reklamı yayında olan ürün —, desenli-koton-esarp 663/667/670/674/675/676/682/686/697/698/702, organik-soft-esarp-229,
  /urun-kategori/esarp/koton-esarp). Geçici çözüm: 27 yönlendirme eklendi (13 ürün → ilgili koleksiyon, 14 iç içe kategori yolu).
- Kalıcı çözüm bekliyor: WP'de olup Shopify'da olmayan ürünleri (yaklaşık 80) Shopify'a eklemek. Görseller WP sunucusunda,
  valenstrend.com artık Shopify'ı gösterdiği için görsellere eski.valenstrend.com gibi bir adresle erişim gerekiyor.
- #1002 (COD 1290, iptal) ve #1003 (COD 1250, bekliyor) şehir alanı "3093" → büyük ihtimalle test.

**Reklamlarda "sayfa bulunamadı" (16 Ekim ~12:00 TR):**
- Sebep: katalog reklamları hâlâ eski WooCommerce kataloğunu (3598453573752694) kullanıyor — "1 | Katalog | Koton+Organik"
  (ürün seti 2782131562135032), "2 | Katalog | En Çok Satan Desenli Koton" (843555898610951), LAL kopyaları ve
  "Remarketing/45 - 05.03 - Kopya" (dinamik, 1103182450724892, bugün en çok harcayan). Bu setlerde Shopify'da olmayan ürünler var.
- Eski katalogdaki 1120 linkin tamamı tarandı: 114'ü yönlendirmesizdi → hepsi yönlendirildi (import 147193942: 114 oluşturuldu,
  0 hata; `veri/yonlendirmeler_eksik_urunler_2026-10-16.csv`). Toplam yönlendirme 1211. Sondaki "/" fark etmiyor (Shopify aynı yol sayıyor).
- Shopify'da hiç olmayan seriler: Müslin Şal (11), Fular (13), Organik Pamuk Şal (16), Organik Soft Şal 271-288, Organik Soft Eşarp
  223-232, Premium Eşarp 11-15, Desenli Koton Eşarp 658-702 → şimdilik kategoriye / tüm ürünlere gidiyor.
- Kalıcı çözüm (onay gerekiyor, §0): katalog reklamlarını yeni Shopify kataloğuna (2558225854645005) taşımak; eksik ürünleri Shopify'a eklemek.
  Eski katalog artık güncellenmiyor ve görsel linkleri (valenstrend.com/wp-content/...) Shopify'da 404.

## Test siparişi #1001 (15 Ekim 2026, 23:28 UTC)

- iyzico ile kartla 375 TL (250 ürün + 125 kargo "Standart") — PAID, gerçek çekim (test değil). İade edilecek.
- Kargo adresi telefonu geldi (05062857853). Adreste şehir alanı "3093", il ve posta kodu boş → kargo için il/ilçe eksik kalabilir; ödeme formu kontrol edilecek.
- Meta Purchase olayı: istatistikler saatlik geldiği için henüz görünmüyor; 01:01 UTC'de tekrar bakılacak.

## Yeni Desenli Koton Eşarp ürünleri (22 Ekim 2026)

- Kullanıcı 74 fotoğrafı Shopify → İçerik → Dosyalar'a yükledi (`Desenli_Koton_Esarp_<kod>.jpg`; 42 adet 1080×1350,
  32 adet 1536×2048). Dosya adındaki koddan ürün açıldı, fotoğraf yeniden yüklenmeden mevcut dosya ürüne bağlandı.
- 73 yeni ürün: 156, 192, 223, 231, 658–707 (708 yok), 709–713, 715, 717–722, 724–729, 745. Hepsi ACTIVE;
  Online Mağaza, Point of Sale, Facebook & Instagram kanallarında yayında.
- Ayarlar diğer koton eşarplarla birebir: başlık "Desenli Koton Eşarp <kod>", tip "Koton Eşarp", Valenstrend,
  standart koton açıklaması, 250 TL / üstü çizili 330 TL, stok takibi kapalı + CONTINUE, vergili, kargo gerekli.
- Kategoriler kurala göre doldu: koton-esarp 348 → 421, kampanya-tum-esarp-ve-sallar 1035 → 1108,
  en-cok-satanlar 608 → 681.
- 382 açılmadı: "Desenli Koton Eşarp 382" zaten var (aktif, 2 fotoğraflı). Yüklenen `Desenli_Koton_Esarp_382_v1.jpg`
  Dosyalar'da kullanılmadan duruyor.
- Koton Eşarp sıralaması kullanıcının isteğiyle BEST_SELLING → MANUAL: önce 73 yeni ürün (koda göre büyükten küçüğe),
  sonra satıştaki eskiler (657 → 60), en sonda tükenen 58 ürün. Geri almak için: koleksiyonda "En çok satanlar".
  Manuel sırada yeni eklenen ürün en alta düşer; sonraki yüklemede yenileri en üste taşımak gerekir.
- Açık: 45 eski WordPress linki (`/urun/desenli-koton-esarp-658…702`) hâlâ /collections/koton-esarp'a yönleniyor,
  artık ürün sayfasına yönlendirilebilir.
- Liste (kod, ürün ID, dosya ID): `veri/yeni_koton_urunler_2026-10-22.json`.
- Meta kataloğu (2558225854645005): 73'ü de kendiliğinden geldi; valenstrend.com linki, 330/250 TL, uygun (eligible),
  "All Products" setinde. 13:45 UTC'de 43'ünün görseli çekilmişti, 30'u sıradaydı.

### Organik Soft Eşarp (aynı gün, aynı yöntem)
- 9 yeni ürün: 223, 224, 225, 226, 228, 229, 230, 231, 252 (aynı kodlu Organik Soft **Şal** ürünleri ayrı, dokunulmadı).
- Ayarlar diğer Organik Soft Eşarplarla aynı: tip "Organik Soft Eşarp", standart organik açıklama, 350 TL / üstü çizili
  410 TL, takip kapalı + CONTINUE, 3 kanalda yayında. organik-soft-esarp 149 → 158.
- Koleksiyon zaten MANUAL; sadece 9 yeni ürün en üste alındı (252 → 223), eskilerin sırası değişmedi.
- Ürün ID'leri: 223 10367240077398, 224 10367240175702, 225 10367240437846, 226 10367240601686, 228 10367240699990,
  229 10367240831062, 230 10367241027670, 231 10367241125974, 252 10367241453654.
- `/urun/organik-soft-esarp-231` → `/products/organik-soft-esarp-231` yapıldı (kullanıcı istedi; eski katalogda bu link
  "Organik Soft Eşarp 231" ürününe ait, doğrulandı). 223/224/226/229/230 de eski katalogla doğrulanıp kendi ürünlerine bağlandı (kullanıcı "bağla" dedi).

## Kaynak mağaza özeti

| Öğe | Sayı / not |
|---|---|
| Ürün | 1038 (CSV ile taşınacak) |
| Koleksiyon | 14, hepsi kurallı (smart). Ürün eşlemesi gerekmez |
| Sayfa | 9 (`kargo-ve-teslimat`, `iade-ve-degisim`, `ana-sayfa` yayında DEĞİL) |
| Menü | ana-menu-yeni, footer-kategoriler, footer-yardim, footer-kurumsal (tema bunları kullanır) + main-menu |
| Temadaki görseller | 6 dosya (`veri/theme_images.json`; `Luks-Koton-Esarp-Safir-Mavi...` sorguya takıldı, temada kullanılmıyor) |
| Kargo | Yurt içi: 125 TL (0–999,99), Ücretsiz (≥1000). Yurt dışı: "Standard" 850 TL |
| İndirim | "5 Eşarp/Şal Alana 1 Koton Eşarp Hediye" (otomatik BXGY) |
| Yönlendirme | 5 adet (`veri/ekstra.json`) |
| Politika | Sadece gizlilik politikası dolu (Shopify şablonu) |
| Müşteri / sipariş | 0 / 0, taşınacak bir şey yok |
| Metafield tanımı | Yok |

## Kullanıcının yapacakları (Claude yapamaz)

1. **Tema:** Valenstrend → Online Mağaza → Temalar → canlı tema "•••" → *Tema dosyasını indir*
   (zip maile gelir). Yeni mağaza → Temalar → *Tema ekle* → *Zip dosyası yükle*.
2. **Ürünler:** Valenstrend → Ürünler → *Dışa aktar* → Tüm ürünler, düz CSV.
   Yeni mağaza → Ürünler → *İçe aktar*. Görseller eski mağazanın CDN'inden çekilir;
   taşıma bitene kadar Valenstrend kapatılmamalı.
3. **Bağlantı:** claude.ai/customize/connectors → Shopify → yeni mağaza ile bağla → yeni oturum.
4. Sonra: temayı yayınla, iyzico uygulaması, kapıda ödeme / havale (manuel ödeme yöntemleri),
   alan adı (valenstrend.com şu an Shopify'a bağlı değil), mağaza adı/adres/e-posta,
   Meta/Google satış kanalları, ücretli plan + şifre kaldırma.

## Claude'un yeni mağazada yapacakları (sırayla)

Her GraphQL işleminden önce `validate_graphql_codeblocks` çalıştır.

0. `get-shop-info` + `shopLocales` + `publications`: para birimi TRY, dil `tr` olmalı.
   Online Mağaza publication ID'sini al. Tema yüklendi mi, ürün sayısı 1038 mi kontrol et.
1. **Görseller:** `veri/theme_images.json` içindeki 6 dosyayı `fileCreate` ile
   `originalSource` = eski CDN URL, `filename` = aynı dosya adı olacak şekilde yükle.
   Tema bunlara `shopify://shop_images/<dosya adı>` ile bakıyor; Shopify adı değiştirirse
   (sonek eklerse) tema JSON'undaki referansları güncelle. Logo: `Untitled-image-1_1.png`.
2. **Koleksiyonlar:** `veri/collections.json` → `collectionCreate` (aynı handle, başlık,
   açıklama, sortOrder, ruleSet, SEO). `kampanya-tum-esarp-ve-sallar` HARİÇ hepsini Online
   Mağaza'da yayınla (`publishablePublish`).
3. **Sayfalar:** `veri/pages.json` → `pageCreate` (aynı handle/başlık/gövde/isPublished).
   `contact` için templateSuffix `contact`. Yeni mağazada varsayılan `contact` sayfası varsa
   `pageUpdate` kullan. `ana-sayfa` boş ve yayında değil, atlanabilir.
4. **Menüler:** `veri/menus.json` → aynı handle'larla `menuCreate` / var olanlara `menuUpdate`.
   Kaynak ID'lerini yeni mağazadaki handle'lardan eşle. `ana-men` eski ve kullanılmıyor.
5. **Kargo:** varsayılan teslimat profili → `deliveryProfileUpdate`. Yurt içi bölge: TR (tüm
   iller), iki yöntem ve koşulları `veri/delivery.json`'daki gibi. Yurt dışı bölge: aynı ülke
   listesi, 850 TRY. Yurt dışı için pazar (Markets) ayarı gerekebilir, kontrol et.
6. **İndirim:** `discountAutomaticBxgyCreate`: buys 5 adet `kampanya-tum-esarp-ve-sallar`,
   gets 1 adet %100 `koton-esarp`, usesPerOrderLimit yok, combinesWith order+shipping.
7. **Yönlendirmeler:** `veri/ekstra.json` → 5 × `urlRedirectCreate`.
8. **Gizlilik politikası:** `veri/policies.json` gövdesi (`shopPolicyUpdate`, izin verirse).
9. **Tema doğrulama:** yüklenen temanın JSON dosyalarını `veri/tema_json/` ile karşılaştır.
   Shopify JSON'ları sıkıştırılmış saklar: `json.dumps(d, ensure_ascii=False,
   separators=(',',':'))` md5'i `checksumMd5` ile eşleşir.
10. **Karşılaştırma:** ürün 1038, koleksiyon ürün sayıları `collections.json` ile, sayfa ve
    menüler eşleşmeli. Eksikleri kullanıcıya raporla.

## Kısıtlar (önceki oturumdan)

- Canlı (MAIN) temaya dosya yazılamıyor; tema yayınlanamıyor. Değişiklik → tema kopyası
  (`themeDuplicate`) → kullanıcı yayınlar.
- Mağaza planı Plus değil: ödeme sayfası (checkout) özelleştirilemez.
- Meta / Google reklam hesaplarında onaysız işlem yapılmaz (`agency-ai/CLAUDE.md`).
