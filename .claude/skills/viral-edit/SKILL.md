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
| Dolgu (arka plan) videosu | Kartın altındaki alanı doldurur | Ana klibin bulanık hali kullanılır |
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

## 4. Kompozisyon — kart düzeni

Ölçüler `reference/style-profile.md`'de. 1080x1920 için:

```bash
ffmpeg -nostdin -y -i SRC.mp4 -i overlay.mov -filter_complex "\
[0:v]crop=W:H:X:Y,split=2[c][b];\
[b]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,\
   gblur=sigma=34,eq=brightness=0.10:saturation=0.55[bg];\
[c]scale=870:1176:flags=lanczos,setsar=1,format=rgba,\
   rotate=1.4*PI/180:c=none:ow=930:oh=1230[card];\
[bg][card]overlay=(W-w)/2:236:format=auto[base];\
[base][1:v]overlay=0:0:format=auto,format=yuv420p[v]" -map "[v]" ...
```

- Kart genişliği **%80.6**, en-boy **0.74**, üst kenar **%13.7**, eğim **±1–2° ve her planda farklı**
- Arka plan ayrı dolgu videosuysa `[b]` yerine o klibi kullan
- `rotate` çıktısı büyür (`ow/oh`), overlay konumunu ona göre kaydır

---

## 5. Altyazı ve grafikler

```bash
python3 scripts/align.py --audio vo.wav --text script.txt --out captions.json --check
python3 scripts/overlay.py --spec spec.json --out overlay.mov
```

`align.py` metni sesin enerjisine hizalar (ASR yok, hece ağırlığı + konuşma blokları).
`overlay.py` sayaç + tek kelimelik altyazı + okları saydam bir katman olarak üretir.

**`--check` çıktısını oku.** Blok başına 6'dan fazla kelime düşüyorsa kısa kelimeler
eleniyor demektir; `--min-block 0.05` ile tekrar dene. Bu ayar sentetik testte ortalama
hatayı **0.58s'den 0.011s'ye** indirdi — hizalamanın tek kritik parametresi.

### Ok kullanımı

Referansta **58 saniyede 2 kez, toplam 1.8 saniye**. Sürekli ok koymak stili taklit
etmez, bozar. Tek bir kritik anı işaretle.

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

**Referans stil (bilgi aktarımı)** — kart düzeni, sayaç, tek kelimelik altyazı, dolgu
arka plan, 1.5s kesim, **hiç geçiş efekti yok**. Tutunma grafiklerden gelir.

**Sinematik stil** — tam ekran, yavaş zoom (`zoompan`), ışık geçişi, darbe sesi,
kamera sarsıntısı, ağır çekim final, dramatik sessizlik. Tutunma atmosferden gelir.

İkisini karıştırma. Sinematik videoya sayaç koymak da, referans stile ışık patlaması
eklemek de sonucu bozar.

Kullanıcı "şu videodaki gibi" derse **önce referansı ölç** (§1), stil profilini çıkar,
`reference/` altına yaz. Tahminle taklit etme.
