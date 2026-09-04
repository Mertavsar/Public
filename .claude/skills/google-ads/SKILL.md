---
name: google-ads
description: Google Ads hesap analizi. Search, PMax, Shopping, Display kampanya verileri; arama terimleri, kalite puanı, dönüşüm ve maliyet metrikleri verildiğinde funnel teşhisi yapar.
---

# Google Ads Director

`meta-ads` ile aynı disiplin: metrik açıklama değil, funnel teşhisi. Önce
`agency-ai/CLAUDE.md` ve markanın `client.md` dosyasını oku.

---

## Adım 0 — Girdi kontrolü

Elde olan ve olmayan veriyi listele. Eksikse `MISSING`.

Beklenen: Harcama · Dönüşüm · Dönüşüm değeri · ROAS · CPA · Impression · Click · CTR ·
CPC · Impression Share · Kayıp IS (bütçe / sıralama) · Kalite Puanı · Arama terimleri ·
kampanya tipi kırılımı.

---

## Kampanya tipine göre teşhis

**Search**
Niyet en yüksek kanal. Satış yoksa önce **arama terimleri raporuna** bak — alakasız
terimlere harcama en sık bulgudur. Sonra: eşleme türleri, negatif kelime eksikliği,
reklam metni–anahtar kelime–landing page uyumu, Kalite Puanı bileşenleri.
Kayıp Impression Share **bütçe** kaynaklıysa ölçeklenecek alan var demektir; **sıralama**
kaynaklıysa teklif veya alaka problemi vardır.

**Performance Max**
Kara kutu. Kırılım sınırlı olduğu için kesin hüküm verirken dikkatli ol. Bakılacaklar:
asset grubu performansı, ürün feed kalitesi, kitle sinyalleri, marka trafiğinin PMax
tarafından yutulup ROAS'ı şişirmesi. **Marka aramaları hariç tutulmadıysa ROAS yanıltıcıdır** —
bunu mutlaka not düş.

**Shopping**
Sorunlar genelde feed'dedir: başlık, görsel, fiyat rekabeti, stok durumu, GTIN eksikliği.
Fiyat rakiplerden yüksekse Shopping'de tıklama alsa da satış gelmez — bu ürün/fiyat
problemidir, reklam problemi değil.

**Display / Demand Gen**
Dönüşüm beklentisi düşük tutulur. Buradaki zayıf CPA'yı Search ile kıyaslama.
Placement raporunda uygulama/oyun trafiği varsa dışla.

---

## Funnel

```
Impression → Click → Landing Page → Dönüşüm
```

Click sonrası kayıp Google'ın değil sitenin problemidir → `cro`.
Telefon/form leadleri satışa dönmüyorsa → `sales`.

---

## Tuzaklar

- **Marka vs marka dışı ayrılmadan ROAS yorumlanmaz.** Marka trafiği zaten gelecek olan
  satışı satın alır; hesabın gerçek performansını gizler.
- **Dönüşüm sayımı.** "Her tıklama" vs "tek dönüşüm" ayarı ve dönüşüm penceresi
  farkı, rakamları ikiye katlayabilir. Ayar bilinmiyorsa `MISSING` yaz.
- **Otomatik teklif** yeterli dönüşüm verisi olmadan çalışmaz. Aylık dönüşüm 30'un
  altındaysa bunu belirt.
- Düşük hacimde CPA farkı yorumlanmaz.

---

## Çıktı formatı

`meta-ads` ile aynı: Bulgu · Olası neden · Kanıt · Eminlik · Aksiyon · Test ·
Başarı kriteri. Sonda IMPACT/EFFORT önceliklendirmesi ve her aksiyonun sorumlusu
(Ajans / Müşteri).
