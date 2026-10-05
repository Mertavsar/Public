# Aşama 1 — Gerçek talebi olan niş bul

**Girdi:** `kanal.md` (geniş ilgi alanı, dil/ülke, üretim yolu)
**Çıktı:** `01-nis.md` — 5 alt niş, sıralama, tek öneri

> Kaynak prompt: *"Act as a faceless YouTube strategist. I want to build a channel
> around [broad interest]. Give me 5 specific sub niches inside it that have a hungry
> audience and weak competition. For each one, show me the core viewer, the 3 things
> they search for most, and 2 channels already winning there. Then rank all 5 by how
> fast a brand new channel could grow using only stock footage, images and voiceover.
> Finish with 1 clear recommendation and the reasoning behind it."*

---

## Shorts için yürütme

Yüzsüz bir **YouTube Shorts** stratejisti gibi çalış. Geniş ilgi alanının içinden
**5 dar alt niş** çıkar: kitlesi aç, rekabeti zayıf.

Her alt niş için:

| Alan | Ne yazılır |
|---|---|
| Çekirdek izleyici | Yaş aralığı, ne zaman izler, neden kaydırmayı bırakır — tek cümle |
| En çok aradığı / merak ettiği 3 şey | Shorts'ta "arama" değil "durdurma": hangi soru kaydırmayı durdurur |
| Kazanan 2 kanal | **Gerçek** kanal + son 90 gündeki en iyi Shorts izlenmesi. Bulamazsan `MISSING` (SKILL §2) |
| Rekabet zayıflığı | Neden zayıf: az kanal mı, kötü üretim mi, Türkçe karşılığı yok mu |
| Klip bulunabilirliği | Bu nişte haftada 7+ kullanılabilir dikey klip bulunur mu (1–10) |
| Döngüye uygunluk | Konu 30–45 sn'de "sebebi yarım bırak" kapanışına izin veriyor mu |
| Risk | Telif yoğunluğu, yeniden kullanılan içerik riski, hassas konu (bir satır) |

### Sıralama

5 nişi **sıfır abonelik yeni bir kanalın ne kadar hızlı büyüyebileceğine** göre sırala.
Üretim yolu `kanal.md`'den gelir (varsayılan: hazır klip + Türkçe seslendirme).
Sıralama ölçütleri, ağırlık sırasıyla:

1. Durdurma gücü — ilk saniyede soru doğuruyor mu
2. Klip bulunabilirliği — haftalık üretimi besleyebilir mi
3. Rekabet boşluğu — özellikle **Türkçe** tarafta
4. Tekrarlanabilirlik — 100 video çıkar mı (Aşama 2'nin habercisi)

### Kapanış

**Tek net öneri** ve gerekçesi (3–5 cümle). "Hepsi olur" deme. İkinci tercihi
yedek olarak bir satırla yaz.

## Kalite kapısı

- [ ] 5 nişin her biri **dar** mı? ("hayvanlar" niş değil; "avcı–av karşılaşmalarındaki hayatta kalma taktikleri" niş)
- [ ] Kanal adlarının her biri FACT mi, değilse `MISSING` mi yazıldı?
- [ ] Önerilen nişte klip bulunabilirliği ≥ 7 mi?
- [ ] Telif/yeniden kullanılan içerik riski bir kez yazıldı mı?

Kullanıcı onaylayınca `kanal.md` → Aşama 1: **onaylandı**, seçilen niş `kanal.md`
"Niş" satırına yazılır. Sonraki aşamalarda `[niche]` = bu satır.
