# YouTube Shorts kanalları

Sistem: `.claude/skills/shorts-kanal/SKILL.md` — 10 aşama, sırayla.

## Kanallar

| Slug | Kanal | Niş | Aşama | Son güncelleme |
|---|---|---|---|---|
| `pulse-files` | Pulse Files (@PulseFiless) | adrenalin / absürt / şaşırtıcı — netleşecek | 1 — veri bekleniyor | 2026-10-05 |

## Yeni kanal

```bash
cp -r youtube/sablon youtube/kanallar/<slug>
```

Sonra `kanallar/<slug>/kanal.md`'yi doldur ve yukarıdaki tabloya ekle.
Claude'a "`<slug>` kanalı için Aşama 1'i başlat" demen yeterli.

## Klasör sözleşmesi

```
kanallar/<slug>/
  kanal.md               profil + aşama durumu + değişiklik günlüğü
  kurallar.md            kanalın bağlayıcı kuralları (Aşama 3 ve 9 doldurur)
  01-nis.md … 06-kapaklar.md, 10-yol-haritasi.md   aşama çıktıları
  rakip-videolar.csv     Aşama 3 verisi
  fikir-havuzu.csv       Aşama 4 — canlı havuz
  haftalik.md            Aşama 10 — haftalık kontrol listesi
  videolar/<no>-<kisa-ad>/
    metin.md  hook.md  metin.txt  kapak.md  elde-tutma.csv  elde-tutma.md
```

Ham klip, ses ve render dosyaları repoya girmez (`.gitignore`); sadece metin,
karar ve veri dosyaları girer.
