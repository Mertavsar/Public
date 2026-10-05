# Aşama 10 — Para kazanma eşiğine stratejik yol haritası

**Girdi:** `01`–`04` (niş, format, kural, havuz), `kurallar.md`, kanalın Studio
verisi (varsa), `kanal.md` (haftalık üretim kapasitesi)
**Çıktı:** `10-yol-haritasi.md`

> Kaynak prompt: *"Act as a strategist whose only job is getting my faceless channel in
> [niche] to 1,000 subscribers and 4,000 public watch hours in the shortest realistic
> time. Start by telling me which of those 2 targets my niche will hit first, because
> that decides the whole plan. Then build me a 90 day plan working backwards from both
> numbers. Show me the maths: how many videos at what average length and what average
> view duration actually gets me to 4,000 hours, and what subscriber conversion rate I
> need per 1,000 views to reach 1,000 subs in the same window. Split my content into 3
> buckets and tell me exactly how many of each to publish. One bucket for long
> watchable videos that stack hours fast. One for high curiosity videos that pull in
> new viewers who have never seen the channel. One for identity videos that turn a
> casual viewer into a subscriber. Give me 10 specific video ideas per bucket, and mark
> which ones can be filmed with stock footage and voiceover alone. Then give me the
> upload order for the first 30 videos, because the sequence matters more than the
> list. Include 5 mistakes that quietly stall channels at this stage, 3 signals in my
> first 10 videos that tell me the plan is working, and 3 signals that tell me to
> change direction instead of pushing harder. Finish with a simple weekly checklist I
> can follow without thinking."*

---

## Shorts hedefi

Shorts kanalının para kazanma yolu 4.000 saat değil:

| Eşik | Abone | Diğer | Pencere |
|---|---|---|---|
| **Tam YPP (reklam geliri payı)** | 1.000 | **10M geçerli Shorts izlenmesi** | son 90 gün |
| Ara eşik (fan desteği özellikleri) | 500 | 3M Shorts izlenmesi + 3 yükleme | son 90 gün |

> Eşikler YouTube'un kararıdır ve değişebilir. Plana başlamadan önce YouTube İş
> Ortağı Programı sayfasından teyit et; farklıysa araçtaki `--hedef-*` değerlerini değiştir.

**90 gün kayan penceredir:** 100. günde 1. günün izlenmeleri düşer. "Toplamda
10M'e ulaşmak" yetmez; **son 90 günde** 10M gerekir. Plan bu yüzden hızlanan
bir eğri ister, sabit tempo değil.

## 1. Önce hangi hedef gelir — araçla

```bash
python3 .claude/skills/shorts-kanal/scripts/shorts.py roadmap \
    --gunluk <günlük video> --ort-izlenme <video başına ORTALAMA> \
    --abone-orani <1000 izlenmede abone> \
    --mevcut-abone <n> --mevcut-izlenme <son 90 gün> --patlama 1000000
```

- Kanal yeniyse `--ort-izlenme` ve `--abone-orani` yok → **MISSING**. Aşama 3'teki
  rakip medyanlarıyla senaryo kur (kötümser / orta / iyimser), üçünü de göster,
  hangisinin rakip verisinden geldiğini yaz. İlk 10 video yayınlanınca gerçek sayıyla
  yeniden çalıştır.
- Shorts'ta çoğu zaman **abone önce gelir**, darboğaz izlenmedir. Araç hangisinin
  önce geldiğini söyler — plan **darboğaza** göre kurulur.

## 2. Matematiği göster

Araç çıktısını tabloya dök ve şunları açıkça yaz:

- Kaç video × video başına ortalama kaç izlenme = 10M (son 90 günde)
- 1.000 abone için gereken oran (1000 izlenmede kaç abone)
- **Patlama gerçeği:** Shorts izlenmesi eşit dağılmaz. "Video başına 55K" demek
  "her video 55K alır" değil, "birkaç video 1M+ alır, çoğu birkaç bin" demek.
  `--patlama` çıktısı: kaç patlama gerektiği ve videoların yüzde kaçı.
- Ortalama izleme yüzdesi hedefi: döngü kuran Shorts'ta %80–100+ (Aşama 9 verisi)

## 3. Üç kova — Shorts karşılığı

| Kova | Kaynak | Shorts'ta | Ne yapar | Format ipucu |
|---|---|---|---|---|
| **A — Yığan** | Saat yığan uzun video | Kısa (20–35 sn), güçlü döngü, tekrar izlenen | İzlenmeyi yığar (darboğaz izlenmeyse ağırlık burada) | Tek hook, tek ödül, sert döngü |
| **B — Keşif** | Yeni izleyici çeken merak videosu | Nişi bilmeyenin bile durduğu konu (`kitle` ≥ 8) | Algoritmayı yeni kitlelere açar | Herkesin bildiği bir şeyi inkâr eden hook |
| **C — Kimlik** | İzleyiciyi aboneye çeviren video | Numaralı seri, tekrar eden karakter/soru, kanalın imzası | Abone çevirir (darboğaz aboneyse ağırlık burada) | `Bölüm 4`, "her gün bir …", kanala özgü kalıp |

Her kovadan **kaç video** yayınlanacağını darboğaza göre yaz (ör. izlenme darboğazsa
A %50 / B %30 / C %20) ve gerekçelendir.

**Kova başına 10 fikir** — `fikir-havuzu.csv`'den seç ya da yeni üret, her birine
`kova` sütunu. Her fikrin yanında: **sadece klip + seslendirmeyle çekilebilir mi**
(evet/hayır — hayırsa ne eksik).

## 4. İlk 30 videonun sırası

Sıra listeden önemlidir. Kurallar:

- İlk 10: en yüksek puanlı **B** (keşif) ağırlıklı — kanalın ilk kitlesini bulması lazım;
  araya 2–3 A
- Bir video patlarsa: **sonraki 3 video aynı açının devamı** (C kovasına dönüştür:
  "Bölüm 2") — patlayan izleyiciyi kanala bağla
- Aynı formatı art arda 3'ten fazla koyma (format testi bozulur)
- Tablo: `| Sıra | Gün | Kova | Fikir id | Başlık | Neden bu sırada |`

## 5. Bu aşamada kanalı sessizce durduran 5 hata

Nişe ve kanala özgü yaz. Başlangıç listesi (uyan varsa kullan, kanala uyarla):
yayın tutarsızlığı · patlayan videonun devamını getirmemek · ilk 10 videoyu
farklı nişlere dağıtmak · aynı klip kaynağını tükenene kadar kullanmak ·
yeniden kullanılan içerik kuralına takılacak kadar az anlatım katmak.

## 6. Sinyaller — ilk 10 videoda

| Plan çalışıyor (3) | Yön değiştir — daha çok zorlama değil (3) |
|---|---|
| Ölçülebilir eşikle yaz (ör. "izlemeye devam eden ≥ %70") | Ölçülebilir eşikle yaz (ör. "10 videonun hiçbiri kanal medyanının 3 katına çıkmadı") |

Eşikleri Aşama 3'teki rakip verisinden türet; uydurma sayı yazma — rakip verisi
yoksa eşik `MISSING` ve ilk 10 videodan sonra doldurulur.

## 7. Haftalık kontrol listesi

Düşünmeden uygulanacak kadar basit: gün gün ne yapılır (fikir seç → başlık → metin →
hook testi → ses → kurgu → yayın → 72 saat sonra elde tutma). `youtube/sablon/haftalik.md`
şablonunu kanala göre doldur ve `10-yol-haritasi.md`'nin sonuna ekle.

## Yeniden çalıştırma

Yol haritası **canlı**: her 10 videoda bir `roadmap` aracını gerçek ortalamayla
yeniden çalıştır, sapma varsa planı güncelle ve `kanal.md` değişiklik günlüğüne yaz.
