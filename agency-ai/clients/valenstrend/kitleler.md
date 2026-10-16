# Valenstrend — Hedef kitleler (VT | standart seti)

Kuruldu: 16 Ekim 2026, ajans sahibinin açık onayıyla ("KUR"). Hesap: valenstrendonline — 1251147858925019.
Piksel 1305259216806142, Instagram 6416183631737916. Hepsi geçmiş veriyle dolduruldu (prefill); eski WordPress
ziyaretçilerini de içerir (aynı piksel). Eski kitlelere dokunulmadı.

## Site (piksel)
| Ad | ID | Kural |
|---|---|---|
| VT \| Site \| Tüm Ziyaretçiler \| 30G | 120249795809090677 | Tüm ziyaretçiler, 30 gün |
| VT \| Site \| Tüm Ziyaretçiler \| 180G | 120249795811440677 | Tüm ziyaretçiler, 180 gün |
| VT \| Site \| En Çok Vakit Geçiren %25 \| 30G | 120249795811490677 | Zaman yüzdeliği 75-100 |
| VT \| Site \| Ürün Görüntüleyen \| 7G | 120249795811520677 | ViewContent |
| VT \| Site \| Ürün Görüntüleyip Almayan \| 14G | 120249795811620677 | ViewContent − Purchase |
| VT \| Site \| Ürün Görüntüleyen veya Sepete Ekleyen \| 45G | 120249795811700677 | ViewContent ∪ AddToCart (eski katalog kitlesinin yerine) |
| VT \| Site \| Sepete Ekleyip Almayan \| 7G | 120249795814430677 | AddToCart − Purchase |
| VT \| Site \| Sepete Ekleyip Almayan \| 30G | 120249795814740677 | AddToCart − Purchase |
| VT \| Site \| Ödeme Başlatıp Almayan \| 14G | 120249795815330677 | InitiateCheckout − Purchase |
| VT \| Site \| Ödeme Başlatıp Almayan \| 45G | 120249795815420677 | InitiateCheckout − Purchase |
| VT \| Site \| Satın Alanlar \| 30G | 120249795815460677 | Purchase (hariç tutma) |
| VT \| Site \| Satın Alanlar \| 180G | 120249795815650677 | Purchase (benzer kitle kaynağı) |
| VT \| Site \| Koton Eşarp İlgilenen \| 45G | 120249795819110677 | (ViewContent ∪ AddToCart) ∩ url "koton-esarp" |
| VT \| Site \| Organik Soft İlgilenen \| 45G | 120249795819390677 | (ViewContent ∪ AddToCart) ∩ url "organik-soft" |

Not: Meta, ViewContent/AddToCart kurallarına Facebook ve Instagram Mağaza (shopping_page / shopping_ig) ürün
görüntüleme ve sepete ekleme kurallarını otomatik ekledi. Bu eklenen kurallarda URL filtresi yok. Bu yüzden Koton
ve Organik Soft kitlelerine Mağaza'da herhangi bir ürüne bakanlar da giriyor (Mağaza trafiği azsa etkisi küçük).

## Instagram
| Ad | ID | Kural |
|---|---|---|
| VT \| IG \| Profil Etkileşimi \| 30G | 120249795819660677 | ig_business_profile_all |
| VT \| IG \| Profil Etkileşimi \| 90G | 120249795819720677 | ig_business_profile_all |
| VT \| IG \| Mesaj Gönderen \| 90G | 120249795819790677 | ig_business_profile_user_messaged |
| VT \| IG \| Mesaj Gönderen \| 365G | 120249795819830677 | ig_business_profile_user_messaged |
| VT \| IG \| Takipçiler \| Güncel | 120249795819860677 | INSTAGRAM_PROFILE_FOLLOW |

## Benzer kitleler
| Ad | ID | Kaynak |
|---|---|---|
| VT \| Benzer %1 \| Satın Alanlar 180G | 120249795823680677 | VT \| Site \| Satın Alanlar \| 180G |
| VT \| Benzer %3 \| Satın Alanlar 180G | 120249795824060677 | VT \| Site \| Satın Alanlar \| 180G |
| VT \| Benzer %1 \| IG Mesaj Gönderen 365G | 120249795822340677 | İnstagram Mesaj(365) 120214644267550677 |
| VT \| Benzer %1 \| Müşteri Listesi | 120249795822610677 | Müşteri Valens listesi 120221604968110677 |

Kurulmadı: "VT | Benzer %1 | Sepete Ekleyen 180G" — Meta reddetti (aynı kaynak/oran zaten var:
"Benzer Hedef Kitle (1%) - Sepete Ekleme(180)" 120247659428090677, aktif). Satın alanlar %1/%3 ilk denemede aynı
sebeple reddedildi, yeni "VT | Site | Satın Alanlar | 180G" kaynağıyla kuruldu.

## Kurulamayanlar (araçta yok — Reklam Yöneticisi'nden)
- Video izleyen kitleleri
- Yeni katalog (2558225854645005) ürün kitleleri
- Facebook sayfası etkileşim kitleleri
- Yeni müşteri listesi (WordPress müşteri dökümü gerekiyor)

## Hariç tutma kitlesi (16 Ekim 2026, kullanıcının isteğiyle)
| Ad | ID | Kural |
|---|---|---|
| VT \| HARİÇ TUT \| Bizi Tanıyan Herkes (Site 180G + IG 365G + FB 365G + Takipçi) | 120249795901600677 | Site tüm ziyaretçi 180G ∪ IG profil etkileşimi 365G (ig_business_profile_all) ∪ IG takipçi ∪ FB sayfa etkileşimi 365G (page_engaged, sayfa 122097826928016240) ∪ FB/IG Mağaza ziyaretçileri 180G (Meta ekledi) |

Soğuk kampanyalarda hariç tutulur. Ek olarak hariç tutulması önerilen mevcut kitleler (bu kitleye eklenemedi, araç
video kaynağını desteklemiyor): "may-haz-%25 video izlenme" 120246970414880677, "Video İzlenme/Max/%50/(30 ocak)"
120225172603900677, "14 gün video thr" 120249323600800677, "Müşteri Valens - musteri_listesi_ayrik_sutunlar.csv"
120221604968110677. Reklamı sadece "gören" (etkileşimsiz) kişiler için Meta'da kitle türü yok.
