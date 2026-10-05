---
name: shorts-kanal
description: YouTube Shorts kanal sistemi — niş seçiminden para kazanma yol haritasına 10 aşama. "Yeni kanal açacağım", "hangi nişe girelim", "format belirle", "rakip analizi", "fikir havuzu", "başlık üret", "kapak", "senaryo yaz", "hook test et", "izleyici nerede kopuyor", "elde tutma", "retention", "1000 abone", "para kazanma", "yol haritası" dediğinde ya da bir kanal adı verip "sıradaki aşama" dediğinde kullan. Video kurgusu bu skill'in işi değil — metin onaylanınca viral-edit'e devreder.
---

# Shorts Kanal Sistemi

Bir YouTube Shorts kanalını sıfırdan para kazanma eşiğine götüren **10 aşamalı
hat**. Her aşama bir öncekinin çıktısını girdi olarak alır ve sonucunu kanalın
klasörüne yazar. Sohbette kalan çıktı kaybolur — **dosyaya yazılmayan aşama
yapılmamış sayılır.**

Birden fazla kanal var: her kanal `youtube/kanallar/<slug>/` altında bağımsız
yaşar. Aynı anda iki kanalın verisini karıştırma.

---

## Hat

```
KURULUM (kanal başına bir kez, sırayla)
  1  Niş          gerçek talebi olan, rekabeti zayıf alt niş      -> 01-nis.md
  2  Format       100 kez tekrarlanabilir 3 Shorts formatı        -> 02-format.md
  3  Rakip        patlayan Shorts'ların ortak kuralı              -> 03-rakip.md  (+ rakip-videolar.csv)
  4  Fikir havuzu puan cetveli + 30 puanlı fikir                  -> 04-fikir-havuzu.md (+ fikir-havuzu.csv)
  5  Başlık       çalışan yapıyı birebir kopyala                  -> 05-basliklar.md
  6  Kapak        ilk kare + raf kapağı konseptleri                -> 06-kapaklar.md
  ───────────────────────────────────────────────────────────────
VİDEO DÖNGÜSÜ (her video için)
  7  Metin        izleyiciyi sonuna kadar tutan seslendirme       -> videolar/<no>/metin.md
  8  Hook testi   7 açılış × 5 izleyici, tek final hook           -> videolar/<no>/hook.md
     ── ses üretilir → viral-edit Tur 2 (kurgu) → yayın ──
  9  Elde tutma   48–72 saat sonra: nerede koptu, neden            -> videolar/<no>/elde-tutma.md
                  + kanalın 5 kuralı                               -> kurallar.md
  ───────────────────────────────────────────────────────────────
PLAN
 10  Yol haritası 1.000 abone + 10M Shorts izlenmesi / 90 gün      -> 10-yol-haritasi.md
```

Her aşamanın talimatı `asamalar/` altında. **Aşamaya başlamadan o dosyayı oku.**

| Aşama | Dosya |
|---|---|
| 1 | `asamalar/01-nis.md` |
| 2 | `asamalar/02-format.md` |
| 3 | `asamalar/03-rakip-analizi.md` |
| 4 | `asamalar/04-fikir-havuzu.md` |
| 5 | `asamalar/05-baslik.md` |
| 6 | `asamalar/06-kapak.md` |
| 7 | `asamalar/07-metin.md` |
| 8 | `asamalar/08-hook-testi.md` |
| 9 | `asamalar/09-elde-tutma.md` |
| 10 | `asamalar/10-yol-haritasi.md` |

Sayısal işler `scripts/shorts.py` ile yapılır — elle bölme yapma:

```bash
S=.claude/skills/shorts-kanal/scripts/shorts.py
python3 $S outliers  youtube/kanallar/<slug>/rakip-videolar.csv          # Aşama 3
python3 $S pool      youtube/kanallar/<slug>/fikir-havuzu.csv --ilk 5    # Aşama 4
python3 $S retention videolar/<no>/elde-tutma.csv --captions captions.json --edl edl.tsv  # Aşama 9
python3 $S roadmap   --gunluk 2 --ort-izlenme 15000 --abone-orani 1.2    # Aşama 10
```

Koda dokunduysan: `python3 .claude/skills/shorts-kanal/scripts/test_shorts.py`

---

## 0. Her çağrıda ilk iş

1. **Hangi kanal?** Kullanıcı söylemediyse ve birden fazla kanal varsa sor.
   `youtube/README.md` kanal listesini tutar.
2. Kanalın `kanal.md` dosyasını oku → **Aşama durumu** tablosu nerede kalındığını
   söyler. Kullanıcı "devam et" derse sıradaki `bekliyor` aşamasını yap.
3. Kanalın `kurallar.md` dosyasını oku. Aşama 9'dan gelen kurallar **Aşama 5–8'de
   bağlayıcıdır**; ihlal eden başlık/metin teslim edilmez.
4. Yeni kanalsa → aşağıdaki **Yeni kanal** adımı.

### Sıra kuralı

Aşamalar sırayla yapılır, çünkü her biri bir öncekinin kararına dayanır:
niş seçilmeden format, format seçilmeden fikir puanlanmaz.

- Önceki aşamanın dosyası yoksa ya da `kanal.md`'de **onaylandı** değilse, o aşamaya
  dön. Kullanıcı açıkça atlamak isterse atla ama `kanal.md`'ye **atlandı — neden**
  yaz ve sonraki çıktının başına "Aşama N atlandı, bu çıktı varsayıma dayanıyor" notu düş.
- Kullanıcının mevcut, yayında bir kanalı varsa Aşama 1–2 **mevcut durumu
  belgeleme** olarak yapılır (kanal zaten bir nişte); sıfırdan niş aranmaz.
- Aşama sonunda kullanıcıdan **onay** al, sonra `kanal.md` tablosunu güncelle.
  Onaysız aşama `taslak` kalır.

### Yeni kanal

```bash
cp -r youtube/sablon youtube/kanallar/<slug>
```

Sonra `kanal.md`'yi doldur. Sorulacaklar — **hepsini tek mesajda**, gerekmeyeni sorma:

| Bilgi | Neden |
|---|---|
| Kanal adı / URL (varsa) | Mevcut kanalsa veri oradan gelir |
| Geniş ilgi alanı | Aşama 1'in girdisi |
| Dil ve hedef ülke | Rakip ve kitle oradan seçilir |
| Üretim yolu: hazır klip mi, stok mu, AI görsel mi | Formatı ve nişi sınırlar |
| Günde/haftada kaç video çıkarabilir | Aşama 10'un hesabı |
| Seslendirme: ElevenLabs sesi + model | viral-edit ile aynı standart |

`youtube/README.md` tablosuna kanalı ekle.

---

## 1. Uzun video promptlarından Shorts'a — neyi neden değiştirdik

Kaynak promptlar uzun, yüzsüz YouTube videoları için yazılmıştı. Shorts'ta oyun
farklı; uyarlamalar aşama dosyalarında, özet burada:

| Kaynak | Shorts karşılığı | Sebep |
|---|---|---|
| 8 dakikalık senaryo | 30–45 saniye, ~65–100 kelime | Shorts akışı; viral-edit'in ölçülmüş formülü 2.18 kelime/s |
| Her 90 sn'de açık döngü | Her 8–10 sn'de bir mini soru | Aynı oran, Shorts süresine ölçeklendi |
| İlk 30 sn'lik hook | İlk 1–3 saniye + kare sıfırdaki yazı | Shorts'ta karar ilk 1–2 saniyede: izlemeye devam mı, kaydır mı |
| Thumbnail | İlk kare + raf kapağı (150px) | Akışta video oynuyor, kapak sadece kanal sayfasında/rafta |
| 60 karakter başlık | ≤ 40 karakter görünür kısım | Shorts arayüzü başlığı kısaltıyor |
| 4.000 saat izlenme | 10M Shorts izlenmesi / 90 gün | Shorts yolu bu; saat Shorts'tan sayılmıyor |
| Kanal ortalamasına kıyas | Kanal **medyanına** kıyas | Shorts izlenmesi birkaç patlamaya yığılır, ortalama şişer |
| Sonda ilgili videoya yönlendir | Sonsuz döngü: son cümle ilk cümleye bağlanır | Shorts'ta "sonraki video" yok, tekrar izlenme var |

---

## 2. Kanıt disiplini — rakip ve sayı uydurma

Kaynak promptlar "o nişte kazanan 2 kanalı göster", "en çok aranan 3 şey" gibi
**gerçek dünya verisi** istiyor. Model bunları uydurmaya çok yatkın. Kural:

- **Kanal adı, abone sayısı, izlenme sayısı, arama hacmi uydurulmaz.** Bilmiyorsan
  `MISSING` yaz ve nereden bulunacağını söyle.
- Önce web aramasını dene (WebSearch/WebFetch). YouTube sayfaları bu ortamda
  açılmayabilir. Açılmazsa kullanıcıdan iste: "YouTube'da `<arama>` ara, Shorts
  sekmesinden en çok izlenen 10'unu bana at (kanal, abone, başlık, izlenme, tarih)."
- Her iddiayı etiketle (agency-ai'daki disiplinin aynısı):
  - **FACT** — kaynağı gösterilmiş veri (kullanıcının yapıştırdığı, açılan sayfa)
  - **HYPOTHESIS** — akıl yürütme; eminlik **Yüksek / Orta / Düşük**
  - **MISSING** — veri yok
- Kullanıcının kendi kanal verisi (YouTube Studio) her zaman genel bilgiden üstündür.
  Studio verisi varken "Shorts'ta genelde…" ile karar verme.

Doğrulanmamış bir niş önerisi "bu nişte talep var" diye sunulmaz — "talep var
gibi görünüyor, doğrulamak için şu veri lazım" diye sunulur.

---

## 3. Üretim gerçeği — hazır klip + seslendirme

Bu repodaki üretim hattı: **başkasının dikey klibi + özgün Türkçe seslendirme +
viral-edit kurgusu**. Bu, niş ve format kararlarını doğrudan sınırlar:

- Bir nişte **klip bulunabilirliği** puanlanır (Aşama 1, 4). Klibi olmayan fikir,
  ne kadar iyi olursa olsun çekilemez → puanı ≤3 ise elenir.
- YouTube'un para kazanma incelemesi **"yeniden kullanılan içerik"** kuralına
  bakar: anlamlı yorum/anlatım katmayan klip derlemeleri reddedilir. Seslendirmenin
  bilgi ve bakış açısı katması bu yüzden kalite meselesi olduğu kadar gelir
  meselesidir. Görüntünün telifi yine sahibindedir — bunu Aşama 1'de bir kez
  risk satırı olarak yaz, her aşamada tekrarlama.
- Klip nereden, hangi izinle: `reference/klip-kaynaklari.md`.
- Stok görüntü veya AI görsel kullanan bir kanalsa kısıt farklıdır; `kanal.md`'deki
  üretim yoluna göre davran.

---

## 4. viral-edit ile sınır

| İş | Kimin |
|---|---|
| Hangi video, hangi başlık, hangi açı, hangi metin | **shorts-kanal** (Aşama 4–8) |
| Metnin ElevenLabs'e hazır biçimi | viral-edit `reference/script-writing.md` kuralları — Aşama 7 bunlara uyar |
| Klipten kurgu, altyazı, ses, kapak görseli üretimi | **viral-edit** |
| Yayın sonrası performans → kural | **shorts-kanal** (Aşama 9) |

Aşama 8 bitince final metni `videolar/<no>/metin.txt` olarak yaz; kullanıcı sesi
üretince viral-edit Tur 2 bu dosyayı `--script` ile kullanır. Kapak görselini
`viral-edit/scripts/cover.py` üretir; Aşama 6 yalnızca **konsepti** verir.

---

## 5. Çıktı biçimi

- Türkçe. Tablolar kısa, karar net. Her aşama dosyası **tek bir karar/öneriyle** biter.
- Dosyanın başında: `**Kanal:** <ad> · **Aşama:** N · **Tarih:** YYYY-MM-DD · **Durum:** taslak|onaylandı`
- Kopyalanacak her şey (metin, başlık listesi) kod bloğunda.
- Sohbete tüm dosyayı dökme: kararı ve dosya yolunu söyle, kullanıcı isterse aç.

## 6. Yasaklar

- Aşama atlamak (kullanıcı açıkça istemedikçe) — bkz. §0 Sıra kuralı
- Kanal/izlenme/abone sayısı uydurmak — bkz. §2
- `kurallar.md`'deki bir kuralı ihlal eden metni teslim etmek
- Kapanışta "abone ol / beğen / takip et" — döngüyü kırar (viral-edit ile aynı)
- İki kanalın verisini tek analizde birleştirmek
- Sayaç (`N/30`) vaadi içerikte o kadar madde yokken
