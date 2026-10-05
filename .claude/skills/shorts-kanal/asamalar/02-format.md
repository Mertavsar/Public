# Aşama 2 — Tekrarlanabilir Shorts formatı belirle

**Girdi:** `01-nis.md` (onaylı niş), `kanal.md` (üretim yolu)
**Çıktı:** `02-format.md` — 3 format, her biri vuruş vuruş; tek seçim

> Kaynak prompt: *"You are helping me design a faceless channel in [niche]. Give me 3
> repeatable video formats I can run 100 times without the channel feeling stale. For
> each format, break down the structure beat by beat, the average length, the visual
> style, and why that structure holds attention. Show me 5 sample video ideas per
> format. Then tell me which of the 3 formats is easiest to hand over to an editor
> later and why."*

---

## Shorts için yürütme

`[niche]` içinde **100 kez çalıştırılabilecek** ve kanalı bayatlatmayacak 3 Shorts
formatı tasarla. Format = sabit iskelet, değişen malzeme.

Her format için:

### a) Vuruş vuruş yapı

Saniye aralıklarıyla. Başlangıç noktası viral-edit'in ölçülmüş yapısı
(`viral-edit/reference/script-writing.md` §3); format bunu kendi diline çevirir:

```
0–3s    HOOK      ...
3–10s   KURULUM   ...
10–30s  TIRMANMA  ...  (her 8–10 sn'de bir mini soru)
30–38s  DÖNÜŞ     ...
38–42s  SORU      ...  (ikiye bölen ikilem)
42–45s  DÖNGÜ     ...  (sebebi yarım bırak → ilk cümle tamamlar)
```

### b) Ortalama süre ve kelime sayısı

Süre → kelime: **2.18 kelime/saniye** (30s ≈ 65, 40s ≈ 87, 45s ≈ 98).

### c) Görsel stil

viral-edit'in iki stilinden hangisi: **referans stil** (tam ekran, tek kelimelik
altyazı, ~1.5 sn kesim, sayaç olabilir) mı, **sinematik stil** mi. İkisini karıştırma.
Kare sıfırdaki banner yazısının kalıbı (ör. `X ONU | GÖRMÜYOR`).

### d) Neden tutuyor

Hangi psikolojik mekanizma: merak boşluğu, beklenti ihlali, tehlike, sıralama
(sayaç), karşılaştırma. Bir cümle — "ilgi çekici" yazmak yasak.

### e) 5 örnek fikir

Gerçekten bu nişte, bu formatta, **klibi bulunabilecek** fikirler.

---

## Kapanış — iki karar

1. **Bir editöre (veya viral-edit'e) en kolay devredilecek format hangisi, neden.**
   Ölçüt: iskelet ne kadar sabit, klip seçimi ne kadar kural ile yapılabiliyor,
   metin ne kadar şablona oturuyor.
2. **Ana format önerisi** — kanal ilk 30 videoda hangisiyle açılmalı. Devretme
   kolaylığı ile büyüme gücü farklıysa ikisini ayrı söyle.

## Kalite kapısı

- [ ] 3 format birbirinden yapısal olarak farklı mı (sadece konu değil)?
- [ ] Her formatın döngü kapanışı yazıldı mı?
- [ ] 15 örnek fikrin hepsi niş içinde mi?
- [ ] Süre/kelime formülle tutarlı mı?

Onaydan sonra `kanal.md` "Ana format" satırını doldur. Aşama 4'te her fikir bir
formata etiketlenir.
