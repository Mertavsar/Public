# Aşama 9 — İzleyicinin nerede koptuğunu tespit et

**Girdi:** YouTube Studio elde tutma verisi (yayından **48–72 saat** sonra),
`videolar/<no>/metin.txt`, viral-edit `--work` klasöründen `captions.json` ve `edl.tsv`
**Çıktı:** `videolar/<no>/elde-tutma.md` + `kurallar.md` güncellemesi

> Kaynak prompt: *"I am pasting my retention data below with timestamps and the
> percentage of viewers still watching at each point, followed by the full script.
> Act as a retention analyst. First separate the normal early fall off from the real
> problems, since some drop at the start is expected. Then find every sharp drop and
> match it to the exact lines of script running at that moment. For each one, tell me
> which failure caused it: a loop that stayed open too long, a promise the video never
> paid off, a section that repeated something already said, a tone shift, or a slow
> patch where nothing new arrived. Rewrite the 3 worst moments in full, keeping my
> voice. Also flag any place where retention stayed flat but the material was strong,
> because that tells me what to do more of. Finish with 5 rules specific to my channel
> that I can apply to every future script, written plainly enough to sit at the top of
> my script template."*

---

## 1. Veri — kullanıcıdan

YouTube Studio → video → **Analytics → Engagement (Etkileşim)**:

| Veri | Nereden | Neden |
|---|---|---|
| **İzlemeye devam eden %** (Viewed vs swiped away) | Shorts'a özel kart | Açılışın gerçek skoru — Aşama 8 tahminini doğrular |
| Elde tutma eğrisi | Grafiğin üstünde gezinerek saniye → % | Gövdedeki düşüşler |
| Ortalama izleme süresi / % | Aynı sayfa | %100 üstü = döngü çalışıyor |
| İzlenme, abone kazanımı | Overview | Aşama 10'un girdisi |

Eğriyi `videolar/<no>/elde-tutma.csv`'ye yaz (`saniye,yuzde`), **her 1–2 saniyede
bir nokta**. Seyrek nokta düşüşü gizler. Ekran görüntüsü geldiyse noktaları
görüntüden oku ve okuduğunu kullanıcıya teyit ettir.

## 2. Hesap — araçla

```bash
python3 .claude/skills/shorts-kanal/scripts/shorts.py retention videolar/<no>/elde-tutma.csv \
    --captions <work>/captions.json --edl <work>/edl.tsv
```

Araç:
- **Açılış** (0–3 sn) kaybını ayrı raporlar — beklenen kayıp, problem sayılmaz;
  açılışın skoru "izlemeye devam eden %"
- Gövdede normal kayıp hızını (medyan) bulur, bunun **2.5 katını** aşan yerleri
  **sert düşüş** sayar
- Her düşüşü o an konuşulan **cümleye** ve **plana** bağlar — bir önceki cümleyi de
  gösterir (izleyici çoğu zaman bir önceki cümlede karar verir)
- Düz bölgeleri (güçlü malzeme) ve yükselişleri (tekrar izlenen an) ayrı listeler

`captions.json` yoksa düşüşler cümleye bağlanamaz — kelime süresini 2.18 kelime/s
ile kabaca hesapla ve bunu `HYPOTHESIS` olarak işaretle.

## 3. Her sert düşüş için teşhis

Beş başarısızlıktan **birini** seç (kaynak prompt) + Shorts'a özgü iki tane:

| Kod | Başarısızlık | İşaret |
|---|---|---|
| D1 | Döngü çok uzun açık kaldı | Soru soruldu, 10+ sn cevapsız |
| D2 | Ödenmeyen vaat | Başlık/hook'un sözü videoda yok ya da geç |
| D3 | Tekrar | Önceki cümlenin söylediğini başka kelimeyle söylüyor |
| D4 | Ton kayması | Merakla giden metin birden ders anlatır |
| D5 | Yavaş bölge | Yeni bilgi gelmiyor |
| D6 | Görüntü–metin kopukluğu | Cümle bir şey anlatıyor, ekranda o yok (EDL'ye bak) |
| D7 | Görsel durağanlık | Plan > 3 sn ya da kesim ritmi düştü (EDL'ye bak) |

D6–D7 metin değil kurgu sorunudur → çözümü viral-edit'e (EDL) yaz, metne değil.

## 4. En kötü 3 anı yeniden yaz

Tam olarak, **kullanıcının sesini koruyarak**: aynı kelime dağarcığı, aynı cümle
uzunluğu (3–8 kelime), aynı ton. Önce/sonra yan yana.

## 5. Düz ama güçlü bölgeler

Eğrinin düz kaldığı ya da yükseldiği yerlerdeki malzeme **ne yaptı?** (sayı mı
verdi, tehlike mi kurdu, görüntü mü değişti) — "bundan daha fazla" listesi.

## 6. Kanalın 5 kuralı → `kurallar.md`

Bu videodan çıkan dersi kanalın kalıcı kuralına çevir. Kurallar:

- **Sade:** senaryo şablonunun en üstünde durabilecek kadar kısa
- **Kontrol edilebilir:** bir metne bakıp "uyuyor / uymuyor" denebilir
- **Kanala özel:** genel Shorts tavsiyesi değil, bu kanalın verisinden
- **Kaynaklı:** hangi videonun hangi düşüşünden çıktığı yazılı

`kurallar.md`'de en fazla **10 aktif kural** tutulur. Yeni kural eskisiyle
çelişiyorsa ya da daha keskinse eskisini `Emekli` bölümüne taşı (neden ile).
Tek videodan çıkan kural `aday` olarak girer; **ikinci videoda tekrar doğrulanınca**
`aktif` olur. Tek veri noktası kural değil, hipotezdir.

## 7. Havuzu güncelle

`fikir-havuzu.csv`'de bu videonun `durum` → `yayinda`. Kural fikirlerin puanını
değiştiriyorsa (ör. "kitlesi küçük konular düşüyor") etkilenen fikirleri yeniden puanla.
