# Aşama 3 — Rakiplerin öne çıkan videolarını analiz et

**Girdi:** `rakip-videolar.csv` (15+ Shorts), `01-nis.md`, `02-format.md`
**Çıktı:** `03-rakip.md` — outlier analizi, **paylaşılan kural**, 15 yeni fikir

> Kaynak prompt: *"I am pasting 15 videos from channels in [niche] below, each with its
> view count, the channel subscriber count and the upload date. First, calculate
> roughly how far each video beat or missed its channel average, and mark anything
> that clearly broke out. For every outlier, break down the reason in 4 parts: the
> promise the title makes, the emotion the thumbnail triggers, the size of the idea
> itself, and whether the appeal is curiosity, conflict, aspiration or surprise.
> Ignore production quality entirely in your analysis. Then find what the outliers
> share that the underperformers do not, and write that shared pattern as a rule I
> could hand to someone else. Generate 15 new video ideas built on that rule, and mark
> which of them are safe repeats of a proven angle and which are bigger swings. End
> by telling me the 1 thing every underperformer in the list did wrong."*

---

## 1. Veri

**Veri uydurulmaz.** `rakip-videolar.csv`'yi kullanıcı doldurur (ya da açılabilen
sayfalardan sen doldurursun, kaynağıyla). Şablon `youtube/sablon/rakip-videolar.csv`.

```
kanal,abone,baslik,izlenme,tarih,ilk_kare_yazisi,kanal_ort
```

- En az **3 kanal**, kanal başına **5+ Shorts**. Tek videoyla kanal tabanı çıkmaz.
- Her kanaldan **en çok izlenenleri de** ekle; sadece son videolarla outlier görünmez.
- `ilk_kare_yazisi`: Shorts'ta thumbnail'in yerini ilk karedeki yazı tutar — varsa yaz.
- `kanal_ort` boş kalabilir; doluysa medyan yerine o kullanılır.

## 2. Hesap — araçla

```bash
python3 .claude/skills/shorts-kanal/scripts/shorts.py outliers youtube/kanallar/<slug>/rakip-videolar.csv
```

Araç her videoyu **kendi kanalının medyanına** böler (ortalama değil — bir patlama
ortalamayı şişirir), 7 günden genç videoları "genç" işaretler, ≥3x'i **PATLADI**,
≤0.5x'i **altında** sayar. Tabloyu `03-rakip.md`'ye yapıştır.

## 3. Her PATLADI video için 4 parça

| Parça | Shorts'ta neye bakılır |
|---|---|
| Vaat | Başlık + ilk kare yazısı ne söz veriyor |
| Duygu | İlk karenin tetiklediği duygu (korku, şaşkınlık, tiksinti, hayranlık) |
| Fikrin büyüklüğü | Kaç kişiyi ilgilendirir: herkes mi, meraklılar mı |
| Çekim türü | **merak / çatışma / özlem / sürpriz** — birini seç |

**Üretim kalitesini tamamen yok say.** Kurgu, ses, renk analize girmez.

## 4. Paylaşılan kural

Outlier'ların paylaşıp `altında` kalanların paylaşmadığı şeyi bul ve
**başkasına verilebilecek tek bir kural** olarak yaz:

```
KURAL: <Bir cümle. Ölçülebilir ya da kontrol edilebilir.>
Kontrol: <Bir fikrin bu kurala uyup uymadığı nasıl anlaşılır — evet/hayır sorusu>
```

"İlgi çekici ol" kural değildir. "İlk kare yazısı izleyicinin bildiği bir şeyi
inkâr eder" kuraldır.

Bu kural `kurallar.md`'ye **"Rakipten"** başlığıyla eklenir.

## 5. 15 yeni fikir

Kurala göre üret. Her fikrin yanında:
- **GÜVENLİ** — kanıtlanmış bir açının tekrarı (hangi outlier'ın)
- **BÜYÜK ATIŞ** — kuralı yeni bir alana taşıyor
Oran öneri: 10 güvenli / 5 büyük atış. Fikirler Aşama 4'ün havuzuna girer.

## 6. Kapanış

**Altında kalan her videonun yaptığı tek hata** — tek cümle.

## Kalite kapısı

- [ ] Tablo araçtan mı geldi (elle hesap yok)?
- [ ] "az veri" / "genç" uyarıları raporda belirtildi mi?
- [ ] Kural bir evet/hayır kontrolüne indirgenebiliyor mu?
- [ ] 15 fikrin her biri GÜVENLİ/BÜYÜK ATIŞ etiketli mi?
