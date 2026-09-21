# Performans kaydı

Bu dosya olmadan her karar tahmindir. Referans videodan ölçülen sayılar bir
başlangıç noktası, ama **bu kanalın** izleyicisinin neye tepki verdiğini
sadece burası gösterir.

Her video yayınlandıktan **2–3 gün sonra** kullanıcıdan YouTube Studio
ekran görüntüsü iste ve satırı doldur. Beş video sonra karşılaştır, on video
sonra karar ver.

---

## Kayıt

| # | Tarih | Konu | Sn | Plan | Ort plan | Hook tipi | Kapak | Sayaç | 2.sn tutunma | Ort izlenme % | Beğeni/1000 | Yorum |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-09-20 | Gergedan – görmüyor | 33.0 | 25 | 1.14s | iddia (`GERGEDAN ONU GÖRMÜYOR`) | soru (`KİM KURTARDI?` kalıbı) | yok | | | | |
| 2 | 2026-09-20 | Fil – akıntıda kurtarma | 22.7 | 16 | 1.33s | ünlem (`İNSANLARIN YAPMADIĞINI YAPTI!`) | soru | yok | | | | |
| 3 | 2026-09-21 | Kirpi dikeni – olta şamandırası | 16.1 | 12 | 1.34s | değer (`BU DİKEN BİNLERCE LİRA`) | soru + sarı sayı | yok | | | | |
| 4 | 2026-09-21 | 8 püf noktası – ev | 85.5 | 48 | 1.78s | istatistik (`%99'U BUNU YANLIŞ BİLİYOR`) | başlık + `1/8` | **VAR (N/8)** | | | | |

**Referans (kıyas):** 58.2s · 37 plan · 1.57s · sayaç VAR (`N/30`) · −14.6 LUFS

---

## Ne kaydedilecek

| Alan | Nereden |
|---|---|
| 2.sn tutunma | Studio → Erişim → Kitleyi elde tutma eğrisi, 2. saniyedeki % |
| Ort izlenme % | Studio → "Ortalama görüntülenme yüzdesi" |
| Beğeni/1000 | beğeni ÷ görüntülenme × 1000 |
| Yorum | ilk 10 yorumda tekrar eden şikâyet/övgü varsa tek cümle |

## Nasıl okunacak

Beş satır dolunca **tek değişkenli** karşılaştırma yap:

- Soru ile açılanlar vs iddia ile açılanlar → 2. sn tutunma farkı
- 25 sn altı vs üstü → ortalama izlenme yüzdesi farkı
- Sayaçlı vs sayaçsız → ortalama izlenme yüzdesi farkı
- Kapakta soru vs sayı kontrastı → tıklama (Shorts rafından gelen trafik)

İki şeyi aynı anda değiştirme; hangisinin işe yaradığı anlaşılmaz.

## İlk desen (3 video, henüz veri yok)

**4. videoda sayaç ilk kez kullanıldı.** İlk üçünde yoktu; referansın 58
saniye tutmasını sağlayan açık döngü bizde denenmemişti. Konu sekiz ayrı ipucu
olduğu için vaat gerçek: `1/8 → 8/8`. Kapaktaki `1 / 8` de aynı döngüye
bağlanıyor.

**Bu video aynı zamanda süre testi.** 85.5 saniye — öncekilerin üç katı.
Karşılaştırılacak soru net: *sayaçlı 85 saniye, sayaçsız 16–33 saniyeden daha
mı iyi tutuyor?* Cevabı Studio verisi verecek.

Süre kaynağa bağlı, tercihe değil: 33.0 → 22.7 → 16.1 → 85.5. Kirpi videosunda
26.9s kullanılabilir kaynak vardı ve hiçbir plan tekrar etmedi; püf noktası
videosunda 70s vardı ve ses 85s olduğu için her ipucu 1.2–1.7x ağır çekime
alındı.

## Bilinen açık: A/B testi hiç yapılmadı

Şu ana kadarki her iyileştirme teoriden geldi (YouTube'un genel tavsiyesi,
referans videodan ölçüm). **Aynı videonun iki farklı açılışla yayınlanması
hiç denenmedi.** %48.6 tutunma, yarısının hiçbir şey olmadan kaydırdığı
anlamına geliyor; bunu düzeltecek tek yöntem ölçmek.

Yöntem: aynı kurgu, iki banner metni. Biri Shorts'a, biri Reels'e — ya da
iki gün arayla. 2. saniyedeki eğriyi karşılaştır.
