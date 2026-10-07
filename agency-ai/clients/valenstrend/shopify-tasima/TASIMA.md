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

BEKLİYOR (kullanıcı):
- Tema zip yükleme (yeni mağazada şu an sadece varsayılan Atelier + Horizon var).
- Ürün CSV içe aktarma (0 ürün).
- Mağaza adı ("Mağazam" → Valenstrend adı), ödeme, plan, alan adı.

SONRA (Claude): tema JSON'larını `veri/tema_json/` ile karşılaştır, ürün sayısı 1038 ve
koleksiyon ürün sayıları `collections.json` ile eşleşiyor mu kontrol et.

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
