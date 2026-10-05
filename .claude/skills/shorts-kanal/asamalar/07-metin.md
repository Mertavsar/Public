# Aşama 7 — İzleyiciyi sonuna kadar tutacak metin yaz

**Girdi:** seçilmiş fikir + başlık + ilk kare yazısı, kaynak klip, `02-format.md`,
`kurallar.md`
**Çıktı:** `videolar/<no>/metin.md` (metin + plan eşlemesi)

> Kaynak prompt: *"Write a [8] minute narration script for a faceless video titled
> [title] in [niche]. Structure it this way. Open with a hook in the first 15 seconds
> that creates a question the viewer needs answered, then immediately confirm they are
> in the right place. Deliver a small payoff inside the first 90 seconds so they trust
> the video early. Plant a fresh open loop roughly every 90 seconds after that, and
> close every loop you open before the video ends. Escalate through the middle so the
> most interesting material sits around the 70% mark rather than the beginning. Land
> the ending on the answer the hook promised, then point naturally toward a related
> idea. Write it for the ear and not the page. Every sentence must be complete with
> proper verbs, pronouns and adverbs, spell out all numbers so a voice tool reads them
> correctly, and keep the sentences long enough to breathe. Give me clean narration
> only with no headers, no labels, no timestamps and no stage directions anywhere in
> the document."*

---

## Önce oku

1. `kurallar.md` — bağlayıcı
2. `viral-edit/reference/script-writing.md` — metin biçimi, ElevenLabs kuralları,
   hook kalıpları, döngü. **Bu dosyanın kuralları burada tekrar yazılmaz, uygulanır.**
3. Kaynak klip — videoyu görmeden metin yazılmaz (viral-edit `SKILL.md` §1 kontak sayfası)

## Kaynak yapının Shorts ölçeği

Promptun mantığı korunur, saatler Shorts'a ölçeklenir (45 sn için):

| Kaynak (8 dk) | Shorts (45 sn) | Metinde |
|---|---|---|
| İlk 15 sn hook + soru | **0–3 sn** | ≤4 kelimelik ilk cümle; izleyicinin cevabını istediği soru |
| "Doğru yerdesin" onayı | 3–6 sn | Konuyu tek cümlede oturt |
| İlk 90 sn'de küçük ödül | **~10 sn**'de | Küçük ama gerçek bir bilgi — videoya güven |
| Her 90 sn'de yeni açık döngü | **Her 8–10 sn**'de mini soru | "Ama asıl mesele bu değil." / "Bunun bir bedeli var." |
| Açılan her döngü kapanır | Aynı | Kapanmayan döngü = ödenmeyen vaat (Aşama 9'da düşüş) |
| En ilginç malzeme %70'te | **~30–32. saniye** | DÖNÜŞ anı; en güçlü görüntü buraya |
| Sonda hook'un cevabı | Cevabın **yarısı** | Sebebi yarım bırak → ilk cümle tamamlar (sonsuz döngü) |
| İlgili fikre yönlendir | **Yok** | Yerine ikiye bölen soru (yorum) + döngü cümlesi |

### Kaynak prompttan alınan, değiştirilmeyen kurallar

- **Kulak için yaz, sayfa için değil.** Metni sesli oku.
- **Bütün sayıları yazıyla yaz** (`yüzde doksan`, `iki ton`) — ses aracı rakamı bozar.
- **Temiz anlatım:** başlık, etiket, zaman damgası, sahne notu **yok**. Yapıştırılan
  her karakter seslendirilir.

### Kaynak prompttan bilerek ayrılan kural

> *"Keep the sentences long enough to breathe"* — Shorts'ta **tersi**. Tek kelimelik
> altyazıda uzun cümle dağılır; cümle başına **3–8 kelime** (script-writing §4).
> "Nefes" cümle uzunluğundan değil, noktalamadan gelir.

## Teslim

`viral-edit/reference/script-writing.md` §9 biçiminde:

1. Yapıştırılacak metin — tek kod bloğu, başka hiçbir şey yok
   (ElevenLabs modeli bilinmiyorsa etiketli + etiketsiz iki sürüm)
2. Altında: kelime sayısı, tahmini süre (2.18 kelime/s), cümle → görüntü eşlemesi,
   döngü testi (son cümle + ilk cümle arka arkaya)

Hook bu aşamada **taslaktır** — Aşama 8'de test edilip kesinleşir. Kullanıcıya
"ses üretmeden önce hook testini yapalım" de.

## Kalite kapısı

- [ ] Kelime sayısı hedef süreye uyuyor mu (±%10)?
- [ ] Her açılan mini soru kapandı mı?
- [ ] En güçlü bilgi ~%70'te mi, başta harcanmadı mı?
- [ ] Rakam, kısaltma, parantez yok mu?
- [ ] Son + ilk cümle tek cümle gibi akıyor mu?
- [ ] `kurallar.md`'nin her maddesi kontrol edildi mi?
