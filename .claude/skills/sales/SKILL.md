---
name: sales
description: Satış süreci analizi. WhatsApp veya Instagram DM üzerinden gelen reklam leadleri satışa dönmüyorsa; konuşma dökümlerini, lead kalitesini, cevap süresini, fiyat sunumunu, itiraz yönetimini ve takibi inceler. Reklam sorumluluğu ile satış ekibi sorumluluğunu ayırır.
---

# Sales Consultant

"20-30 mesaj geliyor ama satış yok" cümlesinin sahibi bu skill'dir.

Bu durumda **reklamı tek başına suçlama.** Mesaj hacmi varsa reklam işinin bir kısmını
yapmıştır. Kayıp konuşmanın içinde olabilir. Önce `agency-ai/CLAUDE.md` ve markanın
`client.md` dosyasını oku (satış süreci ve kim cevaplıyor bilgisi oradadır).

---

## Funnel

```
Reklam → Mesaj → İlk cevap → İhtiyaç tespiti → Ürün sunumu
       → Fiyat → İtiraz → Takip → Satış
```

Her adımda kaç kişi düştüğünü çıkarabiliyorsan çıkar. Çıkaramıyorsan hangi veriye
ihtiyaç olduğunu söyle.

---

## Veri isteme

Konuşma dökümü olmadan bu analiz yapılamaz. Ajans sahibine müşteriden şunları
istemesini öner:

- **Satışa dönüşmeyen 10-20 konuşma** (tam döküm, isim gizlenebilir)
- **Satışa dönüşen 5 konuşma** — karşılaştırma tabanı, en değerli veri budur
- En sık gelen sorular
- Fiyat itirazları
- Kargo itirazları
- Ürün itirazları
- Kim cevaplıyor, hangi saatlerde, kaç kişi

Dökümler `agency-ai/clients/<slug>/conversations/` altına konur.

Veri gelmeden kesin teşhis verme. Bu talebi müşteriye nasıl ileteceğini `account-manager`
formatında yaz — "konuşmalarınızı denetleyeceğim" gibi değil, "nerede kaybettiğimizi
birlikte görelim" dilinde.

---

## İnceleme alanları

**Lead kalitesi** — Gelen kişi gerçekten alıcı mı, yoksa fiyat mı soruyor? Reklam
mesajı yanlış beklenti mi yaratıyor? Kalitesizse sorumluluk reklamda → `meta-ads`.

**Cevap süresi** — İlk cevaba kadar geçen süre. Dakikalar önemlidir; saatler satışı
öldürür. Mesai dışı gelen mesajların akıbeti ayrı incelenir.

**İlk cevap kalitesi** — "Merhaba" ile başlayıp bekleyen mi, yoksa ihtiyacı anlamaya
çalışan mı?

**İhtiyaç tespiti** — Soru soruluyor mu, yoksa direkt fiyat mı veriliyor? Fiyatın erken
verilmesi en yaygın satış hatasıdır.

**Ürün sunumu** — Görsel, video, beden/renk seçeneği paylaşılıyor mu?

**Fiyat sunumu** — Çıplak rakam mı, değerle birlikte mi? Kargo/taksit bilgisi aynı anda
veriliyor mu?

**İtiraz yönetimi** — "Pahalı" itirazına ne cevap veriliyor? İtiraz konuşmayı bitiriyorsa
burada sistematik bir problem vardır.

**Takip (follow-up)** — Cevapsız kalan konuşma takip ediliyor mu? Çoğu markada satışın
kaybedildiği yer burasıdır: kimse geri dönmüyor.

**Kapanış** — Sipariş almaya davet var mı, yoksa konuşma havada mı bitiyor?

---

## Sorumluluk ayrımı — bu skill'in asıl işi

Her bulguyu iki kutudan birine koy ve raporda ayrı başlıkta topla:

| Reklam tarafı (Ajans) | Satış tarafı (Müşteri) |
|---|---|
| Yanlış kitle, niyetsiz lead | Geç cevap |
| Reklamda yanlış fiyat/vaat beklentisi | Zayıf ihtiyaç tespiti |
| Mesaj başı maliyet yüksekliği | İtiraz karşısında pes etme |
| Hacim yetersizliği | Takip yapılmaması |

Bu tablo ajans sahibinin en çok ihtiyaç duyduğu şeydir: "mesaj geliyor, satış sizde
kalıyor" cümlesini **kanıtla** söyleyebilmek.

---

## Çıktı formatı

**1. Funnel tablosu** — Adım adım kayıp (hesaplanabildiği kadar).
**2. Konuşmalardan bulgular** — Her bulgu için kaç konuşmada görüldüğü + kısa alıntı.
**3. Dönüşen vs dönüşmeyen farkı** — Kazanan konuşmalarda ne farklı yapılmış.
**4. Sorumluluk ayrımı** — Yukarıdaki tablo, doldurulmuş.
**5. Aksiyonlar** — Ajans / Müşteri ayrı, sorumlu ve süre ile.
**6. Satış ekibine öneri** — Kullanılabilir cevap şablonları, itiraz cevapları.
**7. Başarı kriteri** — Örn. "ilk cevap süresi ortalama 2 saatten 15 dakikaya inecek".

Eminlik seviyesini her bulguda belirt. 10 konuşma küçük bir örneklemdir — bunu yaz.
