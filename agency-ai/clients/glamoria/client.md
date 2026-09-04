# GLAMORIA

> Bu dosya nadiren değişir. Sık değişen plan ve testler `strategy.md` içindedir.
> Bilinmeyen alan **silinmez**, `BİLİNMİYOR` yazılır.
>
> **Son doğrulama:** 2026-09-04 — işaretli alanlar Meta API'den teyit edildi.
> Ticari alanların çoğu hâlâ boş; bunlar ajans sahibi/müşteriden alınacak.

## Temel bilgiler
- **Marka:** Glamoria (Meta'da "Glamouria Scarf" / `glamouriascarf` olarak geçiyor) ✅
- **Sektör:** Eşarp / şal — kadın tekstil aksesuar, e-ticaret
- **Web sitesi:** BİLİNMİYOR *(pixel aktif ama domain teyit edilmedi)*
- **Instagram:** BİLİNMİYOR *(reklamlar IG yerleşimlerinde dönüyor)*
- **İlgili kişi / karar verici:** BİLİNMİYOR
- **Ajansla çalışmaya başlangıç:** ~2026-08-28 (pixel kurulumu) / 2026-09-01 (ilk reklam) ✅

## Ürün ve ekonomi
- **Ürünler / kategoriler:** Şal ve eşarp. Katalogda desen bazlı ürünler
  (ör. "WATERCOLOR DESEN EŞARP", "ELARA DESEN ŞAL"). ✅
- **Ortalama ürün fiyatı:** BİLİNMİYOR
- **Ortalama sepet tutarı:** BİLİNMİYOR
- **Brüt marj (%):** **BİLİNMİYOR** ← *EN KRİTİK EKSİK. Başabaş ROAS = 1 ÷ marj.
  Bu gelmeden hiçbir ROAS/bütçe/ölçekleme yorumu anlamlı değildir.*
- **Başabaş ROAS:** Hesaplanamıyor (marj yok)
- **Stok / tedarik durumu:** BİLİNMİYOR

## Hesap kimlikleri
- **Meta reklam hesabı ID:** 1397863002539718 ✅ *(ACTIVE, queryable, TRY)*
- **Meta hesap adı:** Glamoria Reklam Hesabı ✅
- **Business ID:** 2250615012176119 (`glamouriascarf`) ✅
- **Meta Pixel / Dataset ID:** 1102430055540483 — "Glamoria" ✅
  *Oluşturulma 2026-08-28. CAPI aktif, first-party cookie açık.*
- **Facebook sayfası:** BİLİNMİYOR
- **Instagram hesabı:** BİLİNMİYOR
- **Google Ads müşteri ID:** BİLİNMİYOR — *hesap tanımlı değil, bu kanal incelenmedi*

## Reklam
- **Aktif kanallar:** Meta (Facebook + Instagram). Google/TikTok yok. ✅
- **Aylık reklam bütçesi:** BİLİNMİYOR
- **Günlük ortalama harcama:** ~₺325/gün (1–4 Eyl 2026 gerçekleşen) ✅
  *Tanımlı günlük bütçe toplamı ₺900 — gerçekleşen bunun çok altında.*
- **Reklam hesabı erişimi:** Var (MCP üzerinden okuma) ✅
- **Ölçüm kurulumu:** Pixel + CAPI kurulu ve veri akıyor ✅ —
  **ama Purchase olayı eksik:** EMQ 6,1; e-posta/telefon/ad-soyad/`fbc` yok.
  Bir önceki adım `AddPaymentInfo` EMQ 9,3 (veri sitede var, Purchase'a geçirilmiyor).
  → **Düzeltilmesi gereken P0 iş.**

## Hedefler ve beklenti
- **Müşterinin sözlü hedefi:** BİLİNMİYOR
- **Ölçülebilir hedef:** BİLİNMİYOR
- **Hedef gerçekçi mi:** Değerlendirilemedi — marj ve hedef yok
- **Müşterinin beklentisi:** BİLİNMİYOR

## Satış süreci
- **Satış kanalı:** Web sitesi (pixel'de tam e-ticaret funnel'ı çalışıyor) ✅
  *Not: pixel'de `SubscribedButtonClick` olayı var — sitede WhatsApp/iletişim butonu
  olabilir. Doğrulanmadı.*
- **Mesajları kim cevaplıyor:** BİLİNMİYOR
- **Cevap saatleri:** BİLİNMİYOR
- **Ortalama ilk cevap süresi:** BİLİNMİYOR
- **Kargo ve iade koşulları:** BİLİNMİYOR
  *Reklamlarda "Tüm Ürünlerde Ücretsiz Kargo" teklifi geçiyor ama koşulu/eşiği bilinmiyor.*
- **Ödeme seçenekleri:** BİLİNMİYOR

## Değerlendirme
- **Güçlü yönleri:**
  - Site zaten satıyor: **~19 sipariş / 7 gün** (~2,7/gün) — pixel, 28 Ağu – 4 Eyl ✅
    *(Olaylar web+CAPI olarak çift gönderiliyor; tekilleştirilmiş rakam budur.)*
  - Ciddi organik trafik: 3 Eylül'de 5.690 PageView ✅
  - Trafiğin ~%85-90'ı mobil ✅
  - Reklam üst funnel'ı sağlıklı: CTR %4,12, link tıklama→LPV %85, LPV→ATC %18,8 ✅
- **Zayıf yönleri:**
  - **Sepet → ödeme adımı çöküyor:** site geneli ATC→InitiateCheckout %13,7 ✅
    (reklamlı trafikte %11,1 — yani trafik kalitesi değil, site problemi)
  - Purchase olayı eksik kurulmuş → reklam atfı çalışmıyor ✅
- **Geçmiş problemler:** İlk hafta; geçmiş yok.
- **Alınmış kararlar:** 2026-09-04 raporundaki 5 karar (bkz. `weekly-reports/2026-09-04.md`)
- **Test edilmiş stratejiler:** Henüz sonuçlanmış test yok.
- **İşe yarayanlar:** En ucuz trafik "Web Site Trafik" ad set'i —
  CPM ₺32,86, link tıklama ₺0,84 ✅
- **İşe yaramayanlar:**
  - Erken retargeting: pixel 2 günlükken açıldı, ₺180,56 harcadı,
    frequency 3,65 / CPC ₺22,57 / CTR %1,51 ✅
  - Satış kampanyasında marka-farkındalık ("yakında geliyor") gönderisi kullanmak ✅
  - Hesabı 3 günde 8 kampanyaya bölmek — hiçbiri öğrenme aşamasını geçemedi ✅

## İlişki notları
- **İletişim tarzı:** BİLİNMİYOR
- **Hassas konular:** BİLİNMİYOR
- **Konulan sınırlar:** BİLİNMİYOR

---
### Bir sonraki güncellemede doldurulacaklar (öncelik sırasıyla)
1. **Brüt marj** — her şeyin önünde
2. Web sitesi adresi ve Instagram hesabı
3. Ortalama sepet tutarı + son 30 gün sipariş sayısı (müşterinin kendi panelinden)
4. Kargo ücreti / ücretsiz kargo eşiği / kargo bedelinin göründüğü adım
5. Karar verici ve aylık bütçe
