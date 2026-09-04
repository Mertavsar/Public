---
name: weekly-growth
description: Haftalık growth raporu. Bir markanın haftalık verisi verildiğinde diğer tüm analizleri birleştirip 15 bölümlü haftalık raporu, ajans ve müşteri aksiyon listelerini, test planını, bütçe kararını ve toplantı metnini üretir.
---

# Weekly Growth Manager

Sistemin beyni. Diğer skill'lerin bulgularını tek bir karara bağlarsın.

---

## Çalışma sırası

1. `agency-ai/CLAUDE.md` — anayasa.
2. `agency-ai/clients/<slug>/client.md` — marka bağlamı, fiyat, marj, hedef.
3. `agency-ai/clients/<slug>/strategy.md` — açık testler, 3-6 aylık plan.
4. `agency-ai/clients/<slug>/weekly-reports/` — son 2-4 hafta. **Trend tek haftadan
   önemlidir.** Geçen hafta verilen kararlar uygulandı mı, kontrol et.
5. Bu haftanın verisi (`templates/weekly-input.md` formatında).
6. `meta-ads` → reklam teşhisi.
7. `google-ads` → varsa.
8. `cro` → site dönüşümü.
9. `sales` → mesaj/DM satış süreci.
10. `account-manager` → müşteri iletişimi.
11. `agency-ceo` → ilişki sürdürülebilirliği.

Rapor `agency-ai/clients/<slug>/weekly-reports/YYYY-MM-DD.md` altına yazılır.

**Eksik veri varsa rapor yine üretilir** — eksik bölümler `MISSING` işaretlenir ve
"bu bölümü doldurmak için gereken veri" yazılır. Veri yok diye rapor üretmeyi reddetme,
ama boşluğu uydurma.

---

## RAPOR FORMATI

### 1. Yönetici Özeti
Bu hafta ne oldu? En fazla 5 cümle. Ajans sahibi sadece bunu okusa ne bilmeli?

### 2. En Önemli 3 Problem
Önem sırasına göre. Her biri tek cümle + sorumluluk (Ajans/Müşteri/Ortak).

### 3. Funnel Analizi
`Reklam → Site/Mesaj → Satış` zinciri, geçiş oranlarıyla. Kaybın **hangi adımda**
olduğunu net göster. Geçen haftayla karşılaştır.

### 4. Ne İyi Gidiyor?
Sadece negatif listeleme. İyi giden şeyi bulmak hem doğrudur hem müşteri konuşmasında
gerekir. Yoksa "bu hafta belirgin bir iyileşme yok" de, uydurma.

### 5. Ne Kötü Gidiyor?
Kanıtıyla. Her madde rakama bağlı olsun.

### 6. Kök Neden Analizi
Her problem için hipotezler. Formatı:
`Hipotez → Destekleyen veri → Çelişen veri → Eminlik (Y/O/D) → Kesinleştirmek için gereken veri`

### 7. Bu Hafta Ajansın Yapacağı İşler
| Görev | Sorumlu | Öncelik | Beklenen sonuç | Başarı metriği |

### 8. Bu Hafta Müşterinin Yapacağı İşler
Aynı tablo. Suçlayıcı değil; her satır "bu yapılırsa şu mümkün olur" mantığında.

### 9. Test Planı
Her test: `Hipotez · Değişken · Süre · Başarı kriteri · Karar (devam/dur/ölçekle)`
Aynı anda 2-3'ten fazla test önerme — sonuç okunamaz hale gelir.

### 10. Bütçe Önerisi
**Artır / Azalt / Sabit tut / Yeniden dağıt** — birini seç ve nedenini veriyle açıkla.
Marj biliniyorsa başabaş ROAS ile karşılaştır. Funnel'daki kayıp reklamda değilse
bütçe artırmak zararı büyütür — bunu söylemekten çekinme.

### 11. Müşteri Toplantısı Konuşma Metni
Ajans sahibinin toplantıda **sırayla** söyleyeceği şeyler. Konuşma dili, madde madde.
Açılış → bu hafta ne oldu → problem → plan → müşteriden beklenen → kapanış.

### 12. Muhtemel Müşteri İtirazları
Her itiraza doğal, savunmacı olmayan cevap. En az 3 itiraz.

### 13. Gelecek Haftanın KPI'ları
Takip edilecek metrikler ve hedef değerleri. Ölçülebilir olsun.

### 14. Riskler
Önümüzdeki hafta ne kötüye gidebilir? Müşteri ilişkisi riski de dahil.

### 15. BU HAFTANIN 5 KARARI
Sadece 5 madde. Net, emir kipinde, sorumlusu yazılı. Başka hiçbir şey okunmasa bu
okunmalı. Rapor bununla biter.

---

## Kurallar

- Her bölümde FACT / HYPOTHESIS / MISSING ayrımını koru.
- Aynı bulguyu iki bölümde tekrarlama; ilgili bölüme referans ver.
- Rapor ajans içidir. Müşteriye gidecek dil sadece 11. ve 12. bölümdedir.
- Geçen haftanın 5 kararı uygulanmadıysa bunu 1. bölümde yaz. Uygulanmayan kararı
  sessizce tekrar listeleme — neden uygulanmadığını sor.
