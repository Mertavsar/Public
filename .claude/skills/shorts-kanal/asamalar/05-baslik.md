# Aşama 5 — Aynı formatta başlıklar üret

**Girdi:** çalışan bir başlık (Aşama 3'teki bir PATLADI video ya da kendi en iyi
Shorts'un), `[niche]`, `kurallar.md`
**Çıktı:** `05-basliklar.md` — yapı çözümlemesi, 25 başlık, ilk 5

> Kaynak prompt: *"Here is a title I want to copy the structure of: [paste title].
> Break down exactly why this structure works, looking at the curiosity gap, word
> order and the promise it makes. Then write me 25 titles for [niche] using that exact
> same structure, not a loose version of it. Keep every title under 60 characters.
> Rank the top 5 and explain what makes them stronger than the rest."*

---

## Shorts'ta başlık iki yerde yaşar

| Yer | Ne zaman görünür | Sınır |
|---|---|---|
| **İlk kare yazısı** (banner) | Akışta, ilk saniyede — kaydırma kararını bu verir | 2–4 kelime, iki satır (`GERGEDAN ONU\|GÖRMÜYOR`) |
| **Video başlığı** | Akışın altında kısaltılmış, kanal sayfasında, aramada | Görünen kısım **≤ 40 karakter**, toplam ≤ 60 |

Bu yüzden her başlık **çift** üretilir: başlık + ilk kare yazısı. İkisi aynı
cümleyi tekrar etmez — iki ayrı kanca olur (viral-edit kapak kuralıyla aynı mantık).

## 1. Yapıyı sök

Verilen başlığı üç eksende çözümle:

- **Merak boşluğu:** neyi bilmiyoruz, boşluk hangi kelimede açılıyor
- **Kelime sırası:** kanca baştaki 3 kelimede mi; özne/fiil/inkâr nerede
- **Vaat:** izleyici sonunda ne öğreneceğini sanıyor

Sonra yapıyı **şablona** indir — doldurulacak yuvalarla:

```
Örnek:  "Gergedan onu görmüyor"
Şablon: [Güçlü özne] + [zayıf hedef] + [beklenmeyen inkâr fiili]
```

## 2. 25 başlık — birebir aynı yapı

**Gevşek versiyon değil.** Her başlık şablonun yuvalarını aynı sırayla doldurur.
Şablonu bozan başlık listeden çıkar. Her satır:

```
| # | Başlık (≤60, görünen ≤40) | Karakter | İlk kare yazısı (2–4 kelime) |
```

Karakter sayısını **say**, tahmin etme (`len()` ile kontrol et). Türkçe karakterler
tek sayılır.

## 3. İlk 5 ve gerekçe

Sırala, ilk 5'in diğerlerinden **neden** güçlü olduğunu yaz: daha büyük fikir mi,
daha keskin inkâr mı, ilk kare yazısı mı daha okunur. Genel övgü yasak.

## Kurallar

- `kurallar.md`'deki başlık kurallarına uy; ihlal eden başlık listeye girmez.
- Hashtag başlığa yazılmaz; açıklamaya en fazla 3 tane.
- Clickbait sınırı: vaat videoda karşılanmalı. Karşılanmayan vaat yorumlarda
  "yalan" olarak döner ve elde tutmayı düşürür (Aşama 9'da "ödenmeyen vaat").
- Fikir havuzundaki fikirlerle eşle: her başlığın yanına `fikir-havuzu.csv` id'si.
