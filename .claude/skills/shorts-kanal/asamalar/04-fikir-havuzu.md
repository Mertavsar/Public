# Aşama 4 — Fikirleri puanla, fikir havuzu oluştur

**Girdi:** `02-format.md`, `03-rakip.md` (kural + 15 fikir), `kurallar.md`
**Çıktı:** `04-fikir-havuzu.md` (cetvel + karar), `fikir-havuzu.csv` (canlı havuz)

> Kaynak prompt: *"Build me a scoring system for video ideas in [niche]. Score every
> idea from 1 to 10 on curiosity, clarity, audience size and how easy it is to produce
> faceless. Show me the rubric first so I can approve it. Then generate 30 video ideas
> and score each one against that rubric in a table. Sort them highest to lowest and
> tell me which 5 I should film first."*

---

## İki tur — cetvel önce onaylanır

**Tur 1: Cetvel.** Puanlamaya başlamadan cetveli göster, **onay bekle**. Onaysız
cetvelle 30 fikir puanlamak, cetvel değişince hepsini çöpe atmak demek.

Varsayılan cetvel — beş kriter, her biri 1–10:

| Kriter | Sütun | 1 | 5 | 10 |
|---|---|---|---|---|
| Merak | `merak` | Cevabı herkes biliyor | Hafif ilginç | İlk kareyle "nasıl yani?" dedirtir |
| Netlik | `netlik` | 2 cümlede anlatılamıyor | Açıklama gerekiyor | 4 kelimelik hook'a sığar |
| Kitle büyüklüğü | `kitle` | Sadece uzmanlar | Niş meraklıları | Nişi bilmeyen de durur |
| Yüzsüz üretim kolaylığı | `uretim` | Özel çekim gerekir | Birkaç kaynaktan derleme | Tek klip + seslendirme yeter |
| Klip bulunabilirliği | `klip` | Klip yok | Düşük kaliteli/filigranlı var | Net, dikey, okunur klip hazır |

`klip` kaynak promptta yok; bu repodaki üretim yolu (hazır klip + seslendirme)
yüzünden eklendi. Kanal stok/AI görsel kullanıyorsa kullanıcıyla birlikte çıkar.

**Veto:** herhangi bir kriter **≤ 3** ise fikir elenir, ortalaması ne olursa olsun.
Klibi olmayan 10/10'luk fikir çekilemez.

Kullanıcı ağırlık isteyebilir (ör. merak ×2). Araç destekler: `--agirlik merak=2`.

**Tur 2: Havuz.** 30 fikir üret (Aşama 3'ün 15 fikri + 15 yeni). Her fikir:
- `kurallar.md`'deki "Rakipten" kuralına uymalı
- Aşama 2'deki formatlardan birine etiketlenmeli (`format` sütunu)

`fikir-havuzu.csv`'ye yaz, sonra:

```bash
python3 .claude/skills/shorts-kanal/scripts/shorts.py pool youtube/kanallar/<slug>/fikir-havuzu.csv --ilk 5
```

Çıkan tabloyu `04-fikir-havuzu.md`'ye yapıştır.

## Kapanış — ilk çekilecek 5

Araç ilk 5'i puana göre seçer. Sen son kararı ver: aynı formattan 5 tane çıktıysa
**en az 2 formatı** karıştır (format testi de yapılmış olur), sırayı gerekçelendir.

## Havuz canlıdır

`fikir-havuzu.csv` her video döngüsünde güncellenir:
- Çekilen fikrin `durum` → `cekildi`, yayınlanan → `yayinda`
- Aşama 9'dan gelen kurallar yeni fikirlerin puanını değiştirir
- Havuzda 10'dan az uygun fikir kaldıysa yeni tur üret

## Kalite kapısı

- [ ] Cetvel onaylandı mı (Tur 1)?
- [ ] 30 fikrin hepsi puanlı, formatı etiketli mi?
- [ ] Sıralama araçtan mı geldi?
- [ ] İlk 5 en az 2 format içeriyor mu?
