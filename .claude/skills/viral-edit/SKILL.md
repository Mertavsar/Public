---
name: viral-edit
description: Dikey kısa video (TikTok / Reels / Shorts) için seslendirme metni yazımı ve kurgu. Kullanıcı ham klip attığında; "bunu editle", "özgün hale getir", "buna metin yaz", "seslendirme metni", "viral video yap", "şu videodaki gibi edit", "altyazı ekle", "geçiş efekti koy", "ok işareti koy", "izlenme almıyor" dediğinde kullan. Videoyu okuyup ona özel metni üretir; ses geldiğinde kesim, altyazı, grafik, ses masteri ve kalite kontrolünü yürütür.
---

# Viral Edit — Metin Yazımı ve Dikey Video Kurgusu

Kullanıcı ham klip atar; sen önce ona özel seslendirme metnini yazarsın, ses gelince
yayına hazır dikey videoyu çıkarırsın.

Varsayılan hedef **referans stil**: `reference/style-profile.md`. O dosya tahmin değil,
milyonlarca izlenen bir videodan kare kare ölçülmüş sayılar içerir. Önce onu oku.

---

## 0. Hangi aşamadayız

İş iki turda yürür. Kullanıcı hangi turu istiyorsa onu yap, ikisini karıştırma.

```
TUR 1   Kullanıcı ham video atar
        -> videoyu oku, ona özel seslendirme metnini yaz
        -> metni kopyalanmaya hazır tek blok halinde ver (reference/script-writing.md)
        -> kullanıcı metni ElevenLabs'e yapıştırıp sesi üretir

TUR 2   Kullanıcı sesi atar
        -> kurgu, altyazı, grafik, master, teslim (§1'den itibaren)
```

Kullanıcı video + ses birlikte attıysa doğrudan Tur 2.
Sadece video attıysa **metni yazmadan kurguya başlama** — ses olmadan kesim ritmi kurulamaz.

### Tur 2 için gerekenler

| Gereken | Neden | Yoksa |
|---|---|---|
| Seslendirme sesi | Kesim ritmi buna oturur | Tur 1'e dön |
| **Seslendirme metni** (.txt) | Tek kelimelik altyazının tek kaynağı | Sen yazdıysan zaten var |
| Müzik yatağı | Referans stilde sessizlik ölümcül | Sentezlenebilir ama zayıf kalır |
| Platform + hedef süre | Kesim yoğunluğunu belirler | 35–45s varsay |

> **ASR yok.** Bu ortamda konuşma tanıma modelleri ağ politikasıyla kapalı
> (huggingface, openaipublic, alphacephei → 403). Metni uydurma. Sen yazdıysan elinde
> zaten var; kullanıcı kendi metnini kullandıysa **iste**. Tek istisna: kaynak videoda
> **gömülü altyazı** varsa kareleri okuyup çıkarabilirsin.

---

## 1. Kaynağı söküp analiz et

Hiçbir şey kesmeden önce ölç. Her adımda `-nostdin` kullan, yoksa ffmpeg döngüdeki
`while read`'in girdisini yer.

```bash
ffprobe -v error -show_entries format=duration -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1 IN.mp4
ffmpeg -nostdin -v error -i IN.mp4 -vf "select='gt(scene,0.2)',metadata=print:file=-" -an -f null - 2>&1 | grep -oP "pts_time:\K[0-9.]+"
ffmpeg -nostdin -y -v error -i IN.mp4 -vf "fps=1/2,scale=150:-1,drawtext=text='%{pts\:hms}':x=3:y=3:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.7,tile=10x3" -frames:v 1 map.jpg
```

Sonra `map.jpg` dosyasını **gözle oku**. Sahne listesi çıkar: hangi saniyede ne var,
hangisi güçlü, hangisi bulanık/boş.

Bu adım Tur 1'de de yapılır: metni yazmadan önce videoyu okuman gerekir.
Metin yazımı: `reference/script-writing.md` (uzunluk formülü: **2.18 kelime/saniye**,
40 saniye ≈ 87 kelime — referans videodan ölçüldü).

### Temizlik kontrolü — atlanırsa videoya gömülür

- **Gömülü altyazı / watermark**: kadrajı kırparak çıkar. Konumu ölç, tahmin etme.
- **Watermark köşe değiştirir.** TikTok logosu genelde ilk ~5 saniye sol üstte,
  sonra sağ altta. Tüm süre boyunca tara, tek kareye bakıp karar verme.
- **Kapanış kartı**: sondaki logo/abone ekranını at. Parlaklık taramasıyla bul.

---

## 2. Planları seç

**Her plan okunabilir bir özne içermeli.** En sık ve en pahalı hata: kadrajda netsiz
bir ön plan ya da boş zemin olan 2 saniye. Kontak sayfasında iyi görünen bir an tam
çözünürlükte boş çıkabilir — seçtiğin her aralığın **orta karesini** tam boyutta aç ve bak.

- Aynı çekimin bitişik iki parçasını arka arkaya koyma. Kesim gibi okunmaz, atlama gibi
  görünür. Arada en az ~2 saniye boşluk olsun ya da araya başka plan gir.
- Uzun bir duyguyu üç sahte kesimle bölme. Tek kesintisiz plan daha güçlüdür.
- Finali hareketin **yükseldiği** yerden seç. Baş düşüyorsa, göz kaçıyorsa o plan kapanış olmaz.

### Her cümle anlattığı şeyi göstermeli

Planları önce görsel güce göre dizip sonra altyazıyı üstüne bindirme. Altyazı
"gagası gözüne birkaç santim kalmış" derken ekranda kuş yoksa video çöker.
Plan listesini **cümle cümle** kur: her bloğun metnini yaz, karşısına o cümleyi
gösteren kaynak aralığını koy.

### Hook: en güçlü an değil, en OKUNABİLİR an

Aksiyonun tepe noktası genelde okunaksızdır — kadrajı dolduran bir kanat, bulanık
bir kütle. İzleyici ilk karede ne gördüğünü anlayamazsa kaydırır.

Kaynağı 0.2 saniye aralıkla tara, kadrajlanmış halleriyle yan yana koy ve
**tek bakışta anlaşılan** kareyi seç. Genelde bu, aksiyonun tepe noktasından
yarım saniye önce ya da sonra olur.

İlk kareye flash koyma — görüntüyü yakar. Açılışta darbe sesi ve sarsıntı yeterli.

---

## 3. Kesim ritmi

Referans stil: **ortalama 1.55s, medyan 1.43s, saniyede 0.64 kesim, sert kesim.**

Seslendirmede duraklama varsa kesimleri **duraklamaların içine** yerleştir — her cümle
yeni görüntüyle açılır. `silencedetect` ile boşlukları çıkar:

```bash
ffmpeg -nostdin -i vo.mp3 -af "silencedetect=noise=-32dB:d=0.25" -f null - 2>&1 | grep silence_
```

### Seslendirme çok boşluklu geliyorsa sıkıştır

ElevenLabs çıktılarında %30'a varan sessizlik olabilir. `scripts/` içindeki yöntem:
cümleleri kes, araları sabit 0.15s'ye (dramatik olanları 0.26s) indir, üstüne
`atempo=1.06` uygula. Kelime başına/sonuna 45ms pay bırak, yoksa hece kırpılır.

---

## 4. Kompozisyon — HER ZAMAN TAM EKRAN

> **Kural, istisnası yok:** görüntü 1080x1920'nin tamamını doldurur.
> Kart yapma. Küçültüp ortaya yerleştirme. Kenarlara bulanık dolgu koyma.
> Bantlama (pillarbox/letterbox) yapma.

Referans videoda kart düzeni vardı çünkü o videonun kaynakları 3:4'tü. Bizde
kullanılmıyor — kullanıcı bunu açıkça reddetti.

**Kaynak 9:16 ise** (çoğu dikey klip öyledir) hiç kırpmadan doldur.

**Kaynak 9:16 değilse** yine tam ekran: kırparak doldur, asla küçültme.
- Daha geniş kaynak (3:4, 1:1): yanlardan kırp, özneyi kadrajda tut
- Yatay kaynak (16:9): özneye göre kırp; plan başına farklı yatay konum
  (pan) seçerek kaybı yönet
- Kayıp çok büyükse süreyi kısaltıp daha az plan kullan — kart kurma

### Watermark

Kırparak kaçamadığın watermark için `delogo` son çare. İzi, arkası düz olmayan
yerde (tüy, saç, desen) **çok belirgin** — kuşun kanadının geçtiği bir kutu
kabul edilemez bir leke bırakır.

Önce şunları dene:
1. Watermark hangi zaman aralığında nerede? Ölç (genelde belli bir saniyede
   köşe değiştirir).
2. Bir dönemdeki watermark kenardaysa, **o dönemin planlarını ayrı kadrajla** —
   `crop` ile tamamen dışarıda bırak. Kadraj planlar arası değişebilir, bu doğal
   bir çeşitlilik olarak okunur.
3. Kalan planları tek bir watermark dönemine kaydır, böylece tek kutu kalır.
4. Ancak düz zemin üzerinde kalan kutuya `delogo` uygula.

Kırparken en-boyu koru: 9:16 için `genişlik / 0.5625 = yükseklik`. Boyu 9:16'ya
oturmayan bir kırpımı doğrudan 1080x1920'ye ölçeklersen görüntü dikey esner
(yüzler uzar) — kırparak düzelt, esneterek değil.

---

## 5. Altyazı ve grafikler

```bash
python3 scripts/align.py --audio vo.wav --text script.txt --out captions.json --check
python3 scripts/overlay.py --spec spec.json --out overlay.mov
```

`align.py` metni sesin enerjisine hizalar (ASR yok, hece ağırlığı + konuşma blokları).
`overlay.py` sayaç + tek kelimelik altyazı + okları saydam bir katman olarak üretir.
Tam ekranda spec'teki `card` alanına tuvalin tamamını ver:
`{"x": 0, "y": 0, "w": 1080, "h": 1920}`, `caption_y` ≈ 0.76 (TikTok arayüzünün üstünde).

**`--check` çıktısını oku.** Blok başına 6'dan fazla kelime düşüyorsa kısa kelimeler
eleniyor demektir; `--min-block 0.05` ile tekrar dene. Bu ayar sentetik testte ortalama
hatayı **0.58s'den 0.011s'ye** indirdi — hizalamanın tek kritik parametresi.

### Ok kullanımı

Referansta **58 saniyede 2 kez, toplam 1.8 saniye**. Sürekli ok koymak stili taklit
etmez, bozar. Tek bir kritik anı işaretle.

Ama koyduğun ok **büyük olmalı**: kadraj genişliğinin ~%45'i (1080'de `len` ≈ 470),
kalın siyah konturlu, `pulse: 0.07` ile nabız atan. Küçük ok fark edilmez —
konmamış sayılır. Okun ucunu ızgara (`drawgrid`) ile doğrula, tahminle yerleştirme.

### Sayaç

`N/30` açık döngü kurar ama **içerikte gerçekten o kadar madde yoksa boş vaattir**;
izleyici fark edince yorumlara yazar. Kullanıcıya kaç madde olduğunu sor.

---

## 6. Ses masteri

| Hedef | Değer |
|---|---|
| Integrated loudness | **-14 LUFS** (referans -14.6) |
| Tepe | -1.0 dB |
| Sessizlik | **sıfır** — altta kesintisiz müzik |

`loudnorm` tek geçişte hedefi tutturamaz (2–3 dB altta kalır). Önce miksle, sonra
**ölç ve sabit kazanç uygula**, ardından limitle.

`amix` varsayılan olarak girdi sayısına böler; `normalize=0` vermezsen miks 6 dB düşer.

### Müzik ve efekt sesi — atlanamaz

Referansta **görsel** geçiş efekti yok; bunu sese uygulama. Referansın altında
baştan sona müzik var ve sessizliği sıfır. Müziksiz ve efektsiz bir kurguda
kesimler çıplak kalır, video "berbat" hissi verir.

- **Müzik gelmediyse sentezle** ama drone değil: tempolu bir yatak kur (kick, sub
  bass, hi-hat, pad). Ham gürültü + sinüs ucuz duruyor ve videoyu aşağı çeker.
  Gerçek parça her zaman daha iyi — kullanıcıdan iste, gelmezse sentezini ver ve
  değiştirilebileceğini söyle.
- **Müziği konuşmanın altına duck et:**
  `sidechaincompress=threshold=0.05:ratio=7:attack=8:release=280`
  Konuşma anında ~9 dB aşağı inmeli. Ölçerek doğrula.
- **Efekt sesleri** `scripts/sfx.py` ile: büyük kesimlerde boom + whoosh, ara
  kesimlerde tik, ödül anından önce riser + sub-drop.
- Her darbeye görsel karşılık ver: flash (0.13s) ve kamera sarsıntısı (6–10px,
  0.28s'de sönen).

---

## 7. Render ve kalite kontrolü

```bash
-c:v libx264 -preset slower -crf 21 -profile:v high -pix_fmt yuv420p
-x264-params "keyint=60:min-keyint=30" -movflags +faststart
-c:a aac -b:a 160k -ar 48000 -ac 2
```

**Teslimden önce her seferinde:**

1. Kare sayısı ve süre beklenen mi
2. Her planın orta karesini tam boyutta aç — boş/netsiz plan var mı
3. İlk kare karanlık değil (fade-in hook'u öldürür)
4. Loudness ölç, -14 LUFS civarında mı
5. Watermark/altyazı artığı kalmış mı
6. **Dosya 30 MiB altında mı** — üstündeyse teslim edilemez, `crf` yükselt

### ffmpeg tuzakları

- `drawbox`'ın `w` ifadesi kare başına hesaplanmaz, `eval` seçeneği de yoktur.
  Dolan ilerleme çubuğu için tam genişlikte bandı `overlay` ile soldan kaydır:
  `overlay=x='-1080+1080*t/SURE':y=0:eval=frame`
- `tile` filtresi zaman damgalarını bozar; kontak sayfasındaki etikete güvenme,
  şüphelendiğin anı `-ss` ile tek tek çıkar.
- `-ss` girdiden **önce** gelmeli, yoksa yavaş.

---

## 8. Neyin ne olduğunu karıştırma

İki ayrı stil var, talep hangisiyse onu uygula:

**Referans stil (bilgi aktarımı)** — tam ekran, sayaç, tek kelimelik altyazı, 1.5s kesim, **hiç görsel geçiş efekti yok** (flash/whip/glitch). Tutunma
grafiklerden gelir. Bu kural SESE UYGULANMAZ: altta kesintisiz müzik ve kesimlerde
darbe sesi vardır.

**Sinematik stil** — yavaş zoom (`zoompan`), ışık geçişi, darbe sesi,
kamera sarsıntısı, ağır çekim final, dramatik sessizlik. Tutunma atmosferden gelir.

İkisini karıştırma. Sinematik videoya sayaç koymak da, referans stile ışık patlaması
eklemek de sonucu bozar.

Kullanıcı "şu videodaki gibi" derse **önce referansı ölç** (§1), stil profilini çıkar,
`reference/` altına yaz. Tahminle taklit etme.
