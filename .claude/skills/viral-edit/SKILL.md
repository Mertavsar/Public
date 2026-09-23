---
name: viral-edit
description: Dikey kısa video (TikTok / Reels / Shorts) kurgusu. Kullanıcı ham klip attığında; "bunu editle", "özgün hale getir", "viral video yap", "şu videodaki gibi edit", "altyazı ekle", "geçiş efekti koy", "ok işareti koy", "kapak yap", "izlenme almıyor" dediğinde kullan. Kaynağı ölçer ve raporlar; metin ile ses geldiğinde kesim, altyazı, grafik, ses masteri, kapak ve kalite kontrolünü yürütür. SESLENDİRME METNİNİ YAZMAZ — video izleyemediği için metni kullanıcı verir.
---

# Viral Edit — Dikey Video Kurgusu

Kullanıcı ham klip atar; sen ölçersin. **Seslendirme metnini kullanıcı verir** (§0 —
video izleyemiyorsun). Metin ve ses gelince yayına hazır dikey videoyu çıkarırsın.

Varsayılan hedef **referans stil**: `reference/style-profile.md`. O dosya tahmin değil,
milyonlarca izlenen bir videodan kare kare ölçülmüş sayılar içerir. Önce onu oku.

---

## Dosyalar

| Dosya | İş |
|---|---|
| `scripts/build.py` | **Giriş noktası.** Uçtan uca kurgu + doğrulama + kalite kontrol |
| `scripts/analyze.py` | Referans videoyu ölç (ritim, ses, kadraj) — tahminle taklit etme |
| `scripts/track.py` | Özneyi renkten takip eder, plan başına `cropx` önerir |
| `scripts/align.py` | Metni sese kelime kelime hizalar (ASR yok), renk vurgusu |
| `scripts/overlay.py` | Altyazı, banner, ok — saydam katman |
| `scripts/audiobed.py` | Efekt + müzik yatağı, EDL kesimlerinden türer |
| `scripts/master.py` | Look-ahead limiter (`volume+alimiter` yerine) |
| `scripts/cover.py` | Dikey kapak görseli |
| `scripts/variants.py` | Aynı kurgunun farklı açılış yazısıyla sürümleri — hook A/B testi |
| `scripts/test_align.py` | Hizalama regresyon testi — koda dokunduysan çalıştır |
| `reference/example-gergedan.md` | **Eksiksiz örnek.** Yeni videoda buradan kopyala |
| `reference/script-writing.md` | Metin yapısı, hook kalıpları, döngü kurgusu |
| `reference/voice-settings.md` | Ses seçimi ve ElevenLabs ayar standardı |
| `reference/style-profile.md` | Referans videodan ölçülen sayılar |
| `reference/performance-log.md` | **Yayınlanan videoların gerçek verisi** — her videodan sonra doldur |

---

## 0. ⛔ SESLENDİRME METNİNİ SEN YAZMA

> **Kullanıcının kuralı, istisnası yok.** Ham klip gelince metin önerme,
> taslak verme, "şöyle olabilir" deme. Metni kullanıcı yazar veya verir.

Sebep teknik: **video izleyemiyorsun.** Elinde sadece `ffmpeg` ile çıkardığın
durağan kareler var — hareketi görmüyorsun, kaynaktaki konuşmayı duymuyorsun.
Kareye bakıp hikâye kurmak tahmindir ve iki kez yanlış çıktı:

- Gergedan klibinde kullanıcı "gergedan boynuzuyla odunu kaldırıp domuzu
  kurtardı" metnini getirdi; kareler bunu yalanladı (odun hiç oynamıyor,
  domuz kendi yürüyerek gidiyor). Yalanı yakalamak doğruydu.
- Ayı klibinde **bu kez ben uydurdum**: iki fotoğraftaki boyut farkına bakıp
  "ayı hemen arkasında" dedim. Ölçünce ayı karenin sağ kenarındaydı ve hemen
  sonra kareden çıkıyordu. Kullanıcı haklı olarak "metinler saçma" dedi.

Kareden çıkarılabilen şey **ölçüm**dür, hikâye değil: "ayı 3.4–4.4 arası 8
pikselden 19 piksele büyüyor" doğrulanabilir; "ayı ona saldırmak üzere"
uydurmadır.

### Bunun yerine ne yap

Kullanıcı ham klip atarsa:

1. **Ölç ve raporla** — `scripts/analyze.py`, kontak sayfası, filigran dönemleri,
   kullanılabilir süre, kadraj planı. Bunlar senin işin.
2. **Gördüğün şeyi say, yorumlama.** "0–1.5s adam lens kuruyor", "3.4–4.4s
   kadrajda 8–19 piksellik kahverengi bir cisim" gibi.
3. **Metni iste.** Videoda ne olduğunu ve varsa kaynaktaki konuşmanın ne
   dediğini kullanıcıdan öğren.
4. Kullanıcı isterse getirdiği metni **ElevenLabs biçimine sok**, uzunluğunu
   hece sayısıyla doğrula, cümleleri altyazıya uygun kısalt. Yeni cümle
   uydurma.

`reference/script-writing.md` bu iş için duruyor — kullanıcının metnini
değerlendirmek ve biçimlendirmek için, sıfırdan yazmak için değil.

---

## 0-1. Hangi aşamadayız

```
TUR 1   Kullanıcı ham video atar
        -> ölç, raporla, kullanılabilir süreyi ve kadraj planını çıkar
        -> METNİ İSTE (yukarısı)

TUR 2   Kullanıcı metni + sesi verir
        -> kurgu, altyazı, grafik, master, teslim (§1'den itibaren)
```

Kullanıcı video + ses birlikte attıysa doğrudan Tur 2.
**Ses ve metin olmadan kurguya başlama** — kesim ritmi seslendirmeye oturur.

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

## 0a. Çalıştırma — TEK KOMUT

> Kurguyu elle ffmpeg komutlarıyla kurma. Yirmi adım sürüyor ve her seferinde
> bir adım atlanıyor: ses yatağı eski kesimlere göre kalıyor, kırpılma kontrolü
> unutuluyor, altyazı eski sesle hizalı kalıyor. `build.py` sırayı sabitliyor.

```bash
python3 scripts/build.py \
  --src ham.mp4 --edl edl.tsv --vo ses.mp3 --script metin.txt \
  --spec spec.json --out video.mp4 \
  --usable-end 13.0 --banner-words 3 --emphasis kör hayatta
```

`hizalama → planlar → ses yatağı → mix → master → grafik → birleştirme → kalite kontrol`

| Bayrak | Ne işe yarar |
|---|---|
| `--usable-end` | Kaynakta kullanılabilir son an (end card / logo öncesi) |
| `--banner-words` | Banner'ın kapsadığı kelime sayısı — altyazıdan düşülür |
| `--emphasis` | Kırmızı vurgulanacak kelimeler (3–5 tane, fazlası vurguyu öldürür) |
| `--crop` | Kaynaktan kırpma `GxY`, 9:16 olmalı (varsayılan `416:740`) |
| `--force` | EDL uyarılarına rağmen devam et — **kullanma**, uyarıyı düzelt |

EDL uyarısı varsa **başlamadan duruyor**; çıkışta kırpılma bulursa dosyayı
reddediyor. Uyarıyı susturma, sebebini düzelt.

### EDL biçimi

Sekmeyle ayrılmış, `#` yorum satırı. Her satır bir plan.

```
# out0	out1	src	slow	z0	z1	cx	cy	cropx	beat	not
0.00	1.73	5.55	1.60	1.45	1.58	0.32	0.76	40	R	HOOK
1.73	3.10	5.90	2.00	1.55	1.70	0.34	0.78	40	m	bir karis otesinde
```

| Sütun | Anlam |
|---|---|
| `out0` `out1` | Planın videodaki yeri (s). **Cümle sınırlarına oturur.** |
| `src` | Kaynaktaki başlangıç (s) |
| `slow` | Ağır çekim çarpanı. Kaynaktan çekilen süre `(out1-out0)/slow` |
| `z0` `z1` | Zoom başı/sonu. `1.00` = tam kare. Her planda hafif hareket olsun. |
| `cx` `cy` | Kadraj konumu 0–1 (`0.5` = orta). Özneyi ortala. |
| `cropx` | Kaynaktan kırpmanın sol kenarı — filigran dönemine göre (§4) |
| `beat` | `R` vuruş+riser · `M` ana vuruş · `m` klink · `-` ses yok |
| `not` | plan etiketi. `~` ile başlarsa bölüm başı sayılmaz (teaser/süreklilik) |
| `cropy` | *(isteğe bağlı 12. sütun)* kırpmanın üst kenarı. Boşsa `--crop-y` |

`beat` ses yatağını ve ışık parlamasını belirliyor — elle yazma, buradan türüyor.
`R`'yi anlatının döndüğü 2–3 ana koy (açılış, ödül cümlesi, kapanış sorusu).

### spec.json

```json
{
 "caption_size": 94, "caption_y": 0.80, "caption_pop": 0.16,
 "banners": [{"t": 0.0, "dur": 1.73, "text": "GERGEDAN ONU|GÖRMÜYOR",
              "y": 0.135, "size": 104}],
 "arrows": [{"t": 0.28, "dur": 1.40, "x": 0.295, "y": 0.555, "angle": 135,
             "len": 410, "draw": 0.20, "pulse": 0.07, "pulse_hz": 3.2}]
}
```

`canvas`, `fps`, `duration`, `card`, `captions` alanlarını yazma — `build.py`
dolduruyor.

### Eksiksiz örnek

`reference/example-gergedan.md` — yayınlanmış bir videonun **tamamı**: metin,
EDL'nin 25 satırı, spec, komut, çıkan ölçümler. Yeni videoda oradan kopyala,
sayıları değiştir. Biçim orada donmuş durumda.

---

## 0b. İzleyici elde tutma kontrol listesi

YouTube'un kanala verdiği geri bildirimden çıkarıldı. **Her videoda hepsi
uygulanır**; teslimden önce tek tek doğrula.

| # | Kural | Nerede uygulanır | Nasıl doğrulanır |
|---|---|---|---|
| 1 | İlk karede hareket + ses | EDL plan 0, `audiobed --major 0.00:0.72` | Kare 0'ı çıkar: durağan mı? |
| 2 | İlk saniyede ekranda iddia/soru | `spec.banners[0]`, `t: 0` | Kare 0'da yazı okunuyor mu? |
| 3 | Selamlaşma yok, doğrudan olaydan gir | Metin | İlk cümle olayın içinde mi? |
| 4 | **3 saniye kuralı** — hiçbir plan 3s'yi geçmez | EDL | aşağıdaki awk |
| 5 | Ölü zaman yok | Kesim + müzik yatağı | `silencedetect` |
| 6 | Kelime kelime yanan, renk vurgulu altyazı | `align.py --emphasis`, `caption_pop` | Renk oranı %10–20 |
| 7 | **Sonsuz döngü** — son cümle ilk cümleye bağlanır | Metin | Son + ilk cümleyi arka arkaya oku |
| 8 | İkiye bölen soru (yorum tetikleyici) | Metin, kapanıştan önce | Net bir ikilem var mı? |

### Referansla kıyas — ölçüldü, üç açık bulundu

Çıkardığımız iki video milyonlar izlenen referansla yan yana ölçüldü:

| | Referans | Gergedan | Fil |
|---|---|---|---|
| LUFS · sessizlik | −14.6 · %14 | −14.3 · %14 | −14.3 · %15 |
| Kesim/s | 0.62 | 0.85 | 0.71 |
| Ortalama plan | **1.57s** | 1.14s | 1.33s |
| Süre | 58.2s | 33.0s | 22.7s |
| Sayaç (açık döngü) | **VAR** | yok | yok |

**Teknik eşleşti, hatta geçildi.** Kalan üç açık:

1. **Hızlı kesim tercih değil, mecburiyet.** Plan süresi kısa çünkü kaynak
   kısa (gergedan 13s, ayı 7.7s kullanılabilir). Fil'de 24.6s vardı ve plan
   hemen 1.33'e çıktı. **20–40 saniye gerçek aksiyon içeren kaynak ara** —
   bu, kurguda yapılabilecek her şeyden fazla fark eder.
2. **Açık döngü yok.** Referansta `N/30` sayacı videonun TAMAMINA yayılan bir
   vaat kuruyor; izleyici otuzunu da görmek için kalıyor. Bizde döngü sadece
   son cümlede kapanıyor. `overlay.py`'deki sayaç duruyor, kullanılmıyor —
   içerik sayılabilir bir yapıya uyuyorsa kullan (vaat gerçek olmalı).
3. **Tavan çekingen.** Referansın tepesi +0.3 dBFS, bizimki −3.1. LUFS aynı
   ama referans daha sıkıştırılmış, telefonda daha önde. −2.0 tavanı test
   edilebilir; AAC taşmasını ölçerek doğrula, tahminle yükseltme.

### 3 saniye kuralı

İzleyicinin gözü aynı görüntüde 3 saniyeden fazla kalmamalı. Plan uzunsa
böl: yakınlaş/uzaklaş değişimi, farklı kadraj, başka bir an.

`build.py` bunu zaten doğruluyor ve uyarı varsa başlamıyor. Elle bakmak
istersen (alan numaraları `-v` ile veriliyor — gövdedeki çıplak `$1` skill
argümanlarıyla değiştirilebiliyor):

```bash
awk -F'\t' -v a=1 -v b=2 '!/^#/{d=$(b)-$(a); if(d>3.0) print "UZUN PLAN:",NR,d"s",$NF}' edl.tsv
awk -F'\t' -v a=1 -v b=2 '!/^#/{d=$(b)-$(a);s+=d;n++}END{printf "ort %.2fs · %d plan · %.2f kesim/s\n",s/n,n,n/s}' edl.tsv
```

Ortalama plan **1.2–1.6s** olmalı (referansta 1.55s). 2s'yi geçen ortalama
tempoyu düşürüyor.

### Hook A/B testi — tahmin etme, ölç

Kanalın tutunma oranı **%48.6**: yarısı ilk saniyelerde kaydırıyor. Bugüne
kadarki her hook kararı teoriden geldi; **aynı videonun iki farklı açılışla
yayınlanması hiç denenmedi.**

```bash
python3 scripts/variants.py --work _build --out-dir . --base kirpi \
    --hook "BU DİKEN|BİNLERCE LİRA" \
    --hook "BU DİKENLER|NEDEN TOPLANIYOR?" \
    --hook "ÇÖPE ATTIĞIN ŞEY|BİNLERCE LİRA"
```

Ucuz: görüntü, ses ve altyazı değişmiyor, sadece banner katmanı yeniden
çiziliyor. Tam kurgunun beşte biri kadar iş.

Üç kalıp üç ayrı strateji sınar: **değer iddiası** · **soru** · **ters
beklenti**. Tek değişken değişsin — sadece yazı.

Yöntem: sürümleri aynı anda yayınlama (biri Shorts biri Reels, ya da iki gün
arayla aynı saatte) → 2-3 gün sonra Studio'dan 2. saniye tutunmasını al →
`reference/performance-log.md`ye yaz. Beş testten sonra desen görünür.

### Kaynak nereden bulunur

TikTok'tan klip almak her seferinde şu işi getiriyor: filigran taraması, bant
kırpma, başkasının gömülü yazısı, kısa kullanılabilir süre, telif belirsizliği.
Kirpi videosunda dördü birden vardı.

Bedava ve temiz alternatifler (klipler 10–60 sn ve 4K — plan süresi 1.5 sn'ye
çıkar, tekrar biter):

- [Pexels vahşi yaşam](https://www.pexels.com/search/videos/wildlife/) · [hayvanlar](https://www.pexels.com/search/videos/animals/)
- [Pixabay vahşi yaşam](https://pixabay.com/videos/search/wildlife%20animal/) · [derin deniz](https://pixabay.com/videos/search/deep%20sea/)
- [NOAA Okyanus Keşfi video portalı](https://oceanexplorer.noaa.gov/data/access/) — **tamamı kamu malı**, ROV dalışları, ProRes'e kadar. "NOAA Ocean Exploration" kredisi yeterli. Başka kanalda olmayan görüntü.

### Sonsuz döngü kurgusu

Son cümle, videonun ilk cümlesine **anlamca bağlanacak** şekilde biter —
izleyici bittiğini fark etmeden ikinci tura başlar, izlenme yüzdesi %100'ü
aşar.

En sağlam kalıp: **son cümle sebebi yarım bırakır, ilk cümle sebebi verir.**

```
son:  "... Sebebi tek şey:"
ilk:  "Gergedan onu görmüyor."
```

Kapanışta son kare ile ilk kare arasında sert kesim olmalı; fade **yapma**,
fade döngüyü görünür kılar.

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

### Kaynağı doğrula — kurguya başlamadan önce

Viral hayvan klipleri sık sık **yapay zekâ üretimi** ya da **yanlış
etiketlenmiş** oluyor. Bir tanesini yayınlamak kanalın güvenilirliğini bitirir.

`WebSearch` bu ortamda çalışıyor (sayfa açma ve video indirme kapalı, sadece
arama). Kurguya başlamadan önce klibi ara:

```
<konu> viral video fact check
<konu> AI generated fake
<konu> original source
```

Ölçüldü: "fil sel sularında adamı kurtardı" diye milyonlarca izlenen bir klip
yapay zekâ üretimi çıktı ve Nepal seliyle hiç ilgisi yokmuş — Snopes, Full Fact
ve Lead Stories üçü birden doğruladı. Aynı kategoride çalışıyoruz.

İki ayrı kontrol, ikisi de gerekli:

1. **Klip gerçek mi?** Arama ile fact-check var mı bak.
2. **Metin klibe uyuyor mu?** Kareleri oku (§0). Gergedan klibinde kullanıcının
   getirdiği "fil odunu kaldırdı" anlatısı kareler tarafından yalanlandı.

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

### Kare sıfırda vaat olmalı

YouTube Shorts'un "izlemeye devam edenler / izlemeden geçti" metriği ilk 1-2 saniyede
belirlenir. İzleyici o anda tek bir soruya cevap arar: **bunu neden izleyeyim.**

Tek kelimelik altyazı bu cevabı veremez — "Gözüne" tek başına hiçbir vaat taşımaz.
Bu yüzden **kare sıfırdan itibaren duran, iki satırlık büyük bir hook yazısı** koy
(`overlay.py` → `banners`). Ok da kare sıfırda olmalı, 0.85'te değil; kaydıranların
çoğu o ana kadar gitmiş olur.

Kontrol: ilk kareyi **170 piksel genişliğe** küçültüp bak. Yazı okunmuyorsa ve
görüntüde ne olduğu anlaşılmıyorsa feed'de de anlaşılmaz.

---

## 3. Kesim ritmi

Referans stil: **ortalama 1.55s, medyan 1.43s, saniyede 0.64 kesim, sert kesim.**

Seslendirmede duraklama varsa kesimleri **duraklamaların içine** yerleştir — her cümle
yeni görüntüyle açılır. `silencedetect` ile boşlukları çıkar:

```bash
ffmpeg -nostdin -i vo.mp3 -af "silencedetect=noise=-32dB:d=0.25" -f null - 2>&1 | grep silence_
```

### ⚠ Derleme kaynakta bölüm sınırını GÖZ KARARI okuma

"8 püf noktası", "10 hile" gibi derleme kaynaklarda her bölümün kaynakta
nerede başladığını bilmek zorundasın. Bunu kontakt sayfasından göz kararı
okumak **yetmiyor** — 3 saniyede bir kare alınan bir sayfanın hata payı
±1.5s ve o hata doğrudan görüntüye yansıyor.

Bu bir kez teslim edildi. Kaynakta "kıymık" bölümü 13.40'ta başlıyordu,
kontakt sayfasından 12.40 okunmuştu. Sonuç: kıymık anlatımı başlarken
ekranda hâlâ bir önceki ipucunun poşeti vardı. Kullanıcı *"berbat olmuş
video ile ses eşleşmiyor, kıymık sesi gelirken poşet videosu görünüyor"*
dedi. Aynı hata 3., 4. ve 5. ipucunda da vardı (1.0–2.5s).

**Doğru yöntem:** kaynak zaten kurgulanmış bir derleme — bölüm geçişleri
sahne kesimidir. Sınırı oradan al:

```bash
ffmpeg -v info -i ham.mp4 -vf "crop=316:562:130:222,select='gt(scene,0.22)',metadata=print:file=-" \
    -an -f null - 2>/dev/null | grep -o "pts_time:[0-9.]*"
```

Sonra **kesimin iki yanından 0.1s aralıkla kare çıkar ve BAK** — sahne
kesimi bölüm geçişi mi, yoksa bölüm içi bir kesim mi, ancak bakarak ayırt
edilir.

`build.py` artık render'dan ÖNCE `check_src_on_scene_cuts()` çalıştırıyor:
her bölümün `src` değeri en yakın sahne kesiminden 0.60s'den fazla
sapıyorsa render durur.

```
BOLUM                     kaynak  en yakin sahne    fark
2 kiymik - sicak su        13.40           13.40   +0.00
3 dis fircasi              22.57           22.57   -0.00
```

Bölüm başı = `not` sütunundaki etiketi bir öncekinden farklı olan plan.
Giriş montajı gibi bilerek plan ORTASINDAN alınan teaser kareler bölüm başı
değildir — onların notunu `~` ile başlat (`~GIRIS 1/4`), kontrol atlar.

**Yan gösterge:** `slow` değerleri bölümden bölüme çok oynuyorsa (biri 1.15,
diğeri 1.73) kaynak sınırları yanlıştır — kısa ölçülen bir parça anlatımı
doldurmak için aşırı ağır çekime zorlanıyordur. Doğru sınırlarla hepsi
0.9–1.35 arasına oturdu.

### ⚠ Paragraf–kesim kontrolü (ikincil)

`build.py` ayrıca `align.paragraph_bounds()` ile metnin noktalama yapısını
sesin duraklama dizisine oturtup her paragrafın başlangıcını ölçüyor ve
oraya bir plan kesimi düşüyor mu diye bakıyor.

Bu ölçüm **her seslendirmede çalışmıyor**: noktalama yanlış duraklamaya
oturduğunda aradaki parça imkânsız bir hızda "okunmuş" görünüyor (ölçülen
bir vakada 23 hece 1.89 saniyede, 12.2 hece/sn). Fonksiyon bunu kendi
yakalıyor — 2.5–10.5 hece/sn dışına çıkan parça varsa `None` döner ve
kontrol atlanır. **Sessizce yanlış sınır vermesindense atlaması iyidir;
çıktıda "sınırlar KULLANILMADI" görürsen kaynak sınırı kontrolü tek
güvencendir.**

Asıl sınır ölçüsü `align.py`'nin kelime hizalamasıdır: konuşma bloklarına
hapsedildiği için global kaymaz. Paragrafların başladığı an oradan okunur:

```python
import json
c = json.load(open("_build/captions.json"))
# her paragrafın ilk kelimesinin "s" değeri = o bölümün anlatım başlangıcı
```

### ⛔ Seslendirmeyi KESME

ElevenLabs çıktılarında %30'a varan sessizlik olabilir. Bunu kısaltmak için bir
script yazılmıştı (`retime.py`); **çalışmadığı için silindi, yeniden yazma.**

Sebep ölçüldü: enerji bloklarına göre kesiyordu, ama enerji bloğu cümle
sınırı değil. 24.35s'lik 12 cümlelik bir seslendirmede 20 blok çıktı; 19 aranın
6'sı 0.25s'den kısaydı ve bunlar cümle sonu değil, **kelime ortasındaki ünsüz
kapanışlarıydı** (0.09s, 0.10s'lik parçalar). O noktalardan kesip araya
0.15s sessizlik koyunca kelimeler parçalandı — kullanıcının duyduğu "anlamsız
sesler" buydu.

Bunun yerine: **sesi olduğu gibi kullan**, ritmi kesimden çıkar. Sessizlik
görüntüde boşluk demek değil; duraklamaya bir kesim, bir vuruş ve devam eden
müzik yatağı koy. Referans videoda da 58 saniyede sıfır sessizlik var — ama bu
sesi kesmekle değil, altına kesintisiz müzik sermekle sağlanmış.

Boşluklar gerçekten kabul edilemez uzunluktaysa (>1.5s), çözüm metni kısaltıp
seslendirmeyi **yeniden ürettirmek**; kesmek değil.

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

**Gömülü yazı kaynağın ÜSTÜNDE de olabilir.** Köpek videosunda alt bantta
sürekli bir İngilizce altyazı, 7.5–13.3s arasında ise ÜSTTE ikinci bir yazı
vardı ("She abandoned the puppy."). Alttan kırpmak ilkini çözdü, ikincisini
çözmedi. Çözüm: o dönemin planlarına EDL'nin `cropy` sütunuyla kırpmayı aşağı
kaydırmak — ama o zaman alttaki filigran kadraja girdiğinden `z` ile içeri
kadraj (1.22) ve `cy=0` ile üste yaslama gerekti.

Yani üç şeyi birlikte çöz: `cropx` (yatay filigran), `cropy` (üst yazı),
`z`+`cx`/`cy` (kalan köşe). Her birini ayrı ayrı ölç, tahmin etme:

```bash
# ust yazi kutusu ne zaman gorunuyor (beyaz zemin oranindan)
python3 - <<'EOF'
import subprocess, numpy as np
W,H=576,1024
raw=subprocess.run(["ffmpeg","-v","error","-t","16","-i","ham.mp4",
                    "-vf","fps=10,format=gray","-f","rawvideo","-"],capture_output=True).stdout
n=len(raw)//(W*H); x=np.frombuffer(raw[:n*W*H],dtype=np.uint8).reshape(n,H,W)
box=(x[:,150:215,150:450]>238).mean(axis=(1,2))
on=[i/10 for i in range(n) if box[i]>0.35]
print("ust yazi:", f"{min(on):.1f}-{max(on):.1f}" if on else "yok")
EOF
```

**Her plana tek bir kırpma dayatma.** Gergedan videosunda watermark 5.00'te
soldan sağa geçiyordu; her iki dönemi birden kurtaran `crop=...:160:30` özneyi
(domuzu) kadrajın sol kenarına itiyor, hook okunmuyordu. Plan başına watermark
dönemine göre kırpma orijini seçince (5.20 sonrası `crop x=40`, öncesi `x=160`)
özne kadrajın ortasına geldi. EDL'ye `crop_x` sütunu koy ve şunu doğrula:

```bash
awk -F'\t' -v a=1 -v b=2 -v c=3 -v d=4 -v x=9 '!/^#/{e=$(c)+($(b)-$(a))/$(d);
  if($(x)==40 && $(c)<5.15) print "HATA sol filigran:",NR}' edl.tsv
```

Kırparken en-boyu koru: 9:16 için `genişlik / 0.5625 = yükseklik`. Boyu 9:16'ya
oturmayan bir kırpımı doğrudan 1080x1920'ye ölçeklersen görüntü dikey esner
(yüzler uzar) — kırparak düzelt, esneterek değil.

---

## 5. Altyazı ve grafikler

```bash
python3 scripts/align.py --audio vo.wav --text script.txt --out captions.json --check
python3 scripts/overlay.py --spec spec.json --out overlay.mov
```

`align.py` metni sese hizalar. ASR yok (model sunucuları ağ politikasıyla kapalı),
onun yerine **hece çekirdeği** okunuyor: Türkçe hece-zamanlı bir dil ve hemen her
hecenin çekirdeği bir sesli harf; sesli harfler 300–900 Hz bandında belirgin bir
enerji tepesi yapıyor. Tepeler sayılıp dinamik programlama ile konuşma bloklarına
dağıtılıyor, böylece bir bloktaki hata sonrakine geçmiyor.

`overlay.py` sayaç + tek kelimelik altyazı + okları saydam bir katman olarak üretir.
Tam ekranda spec'teki `card` alanına tuvalin tamamını ver:
`{"x": 0, "y": 0, "w": 1080, "h": 1920}`, `caption_y` ≈ 0.78–0.80 (TikTok arayüzünün üstünde).

### Renk vurgusu ve beliriş (zorunlu)

```bash
python3 scripts/align.py --audio vo.mp3 --text script.txt --out captions.json \
    --emphasis kıpırdamıyor biterdi tehlike --check
```

`--emphasis` verilen kelimeleri **kırmızı**, sayı ve ölçüleri (`iki`, `ton`,
`seksen`, `saniye`, rakamlar) kendiliğinden **sarı** yapar. Gerisi beyaz.
Sessiz izleyen kitle altyazıyı okumaz, tarar; renk değişimi taramada gözü
durduran tek şey.

**Vurgulu kelime oranı %10–20 olmalı.** Hepsini boyamak hiçbirini boyamakla
aynı şey. `--emphasis`'e 3–5 kelimeden fazla verme.

**Banner punto taşmasını `overlay.py` kendisi düzeltiyor** — en uzun satır
tuvale sığana kadar küçültür ve `banner 96 → 78 punto (taşıyordu)` diye basar.
Bu eklenmeden önce teslim edilen bir videoda hook'un ilk satırı sağdan kesikti
("ORKUDAN YAVRUSUN"). Yine de çıktıdaki satırı oku: çok küçülüyorsa metin uzun
demektir, kısalt.

`spec.json`'daki `caption_pop` (varsayılan 0.16) kelimeyi belirirken hafifçe
büyütüp yerine oturtur. Sabit duran altyazı göz için durağan görüntüyle aynı
şey — kapatma.

**`--check` çıktısını oku.** İki sayı önemli:

| Gösterge | İyi | Kötüyse |
|---|---|---|
| tepe/hece sapması | %0–5 | `--peak-thr` düşür (daha çok tepe) |
| blok uyumsuzluğu | < %12 | metin sesle birebir aynı mı? eksik/fazla cümle var mı? |

`--check` blok blok hangi kelimelerin nereye düştüğünü basar. **Bu tabloyu oku.**
Cümleler bloklara mantıklı düşüyorsa hizalama doğrudur; "0.14s'lik bloğa üç kelime"
gibi bir satır görüyorsan yanlıştır.

**Yüzde tek başına karar verdirmez.** 85 saniyelik, 5.0 hece/sn hızındaki bir
seslendirmede sapma %11.6 ve blok uyumsuzluğu %12.2 çıktı — iki uyarı da
ateşledi. Ama tablo baştan sona tutarlıydı ("Anahtarını kirli suya mı" /
"düşürdün? Sakın panik"), çünkü sebep hata değil **elizyon**: hızlı konuşmada
heceler birbirine geçiyor ve tepe sayısı düşüyor. `--peak-thr` düşürmek
çözmedi (en iyi %9.7'de tıkandı).

Uzun ve hızlı seslendirmede yüzde yükselir; karar tabloyla verilir. Tablo
bozuksa dur, tutarlıysa devam et — kelime hatası zaten her blok sınırında
sıfırlanıyor.

Regresyon testi: `python3 scripts/test_align.py` (sentetik seste örtüşme %99.9).

### İlk cümle banner'da ise altyazıdan çıkar

Banner (kare sıfırdan duran hook yazısı) ile tek kelimelik altyazı aynı anda
akarsa ekran kalabalık olur ve hiçbiri okunmaz. Banner'ın kapsadığı cümlenin
kelimelerini `captions.json`'dan çıkar, altyazıyı ikinci cümleden başlat.

### Ok kullanımı

Referansta **58 saniyede 2 kez, toplam 1.8 saniye**. Sürekli ok koymak stili taklit
etmez, bozar. Tek bir kritik anı işaretle.

Ama koyduğun ok **büyük olmalı**: kadraj genişliğinin ~%45'i (1080'de `len` ≈ 470),
kalın siyah konturlu, `pulse: 0.07` ile nabız atan. Küçük ok fark edilmez —
konmamış sayılır. Okun ucunu ızgara (`drawgrid`) ile doğrula, tahminle yerleştirme.

### Kapak görseli

```bash
python3 scripts/cover.py --frame kare.png --spec kapak.json --out kapak.png
```

Shorts akışında video otomatik oynuyor, kapak orada görünmüyor — ama **kanal
sayfasında ve Shorts rafında** görünüyor ve orada genişliği ~150 piksel.
`cover.py` her kapağın 150px sürümünü de yazıyor; **ona bak**, büyük hâline
değil. Okunmuyorsa kapak yok demektir.

Kurallar:
- **Tek fikir.** İki-üç kelimelik başlık. Cümle kurma.
- Videonun ilk karesindeki yazıyı **tekrarlama** — ayrı bir açı ver, iki kanca olsun.
- Sayı kontrastı en hızlı okunan şey: özneleri etiketle (`2 TON` / `80 KİLO`).
- Kırmızı ok kanalın imzası; videodakiyle aynı biçimde kullan.
- Açık gökyüzünde beyaz yazı kayboluyor — `top_shade` ile üstü koyulaştır.

Kare seçimi: en güçlü an değil, **en okunabilir** an. Öznelerin üst üste
binmediği, ikisinin de siluetiyle tanındığı kare.

### Sayaç

`N/30` açık döngü kurar ama **içerikte gerçekten o kadar madde yoksa boş vaattir**;
izleyici fark edince yorumlara yazar. Kullanıcıya kaç madde olduğunu sor.

---

## 6. Ses masteri

> Seslendirme **seçimi** ve ElevenLabs ayarları ayrı dosyada:
> `reference/voice-settings.md`. Kullanıcı "ses kötü" derse önce oradaki
> ölçümü yap — ölçüm temizse ayar kurcalama, sesi değiştir.

| Hedef | Değer |
|---|---|
| Integrated loudness | **-14 LUFS** (referans -14.6) |
| Tepe | -1.0 dB |
| Sessizlik | **sıfır** — altta kesintisiz müzik |

`amix` varsayılan olarak girdi sayısına böler; `normalize=0` vermezsen miks 6 dB düşer.

### Master — `volume + alimiter` KULLANMA

`volume=XdB,alimiter=...` zinciri güvenilir değil: **alimiter keskin transientleri
kaçırıyor**, sinyal tavanı aşıyor ve 16-bit PCM'e yazılırken sert kırpılıyor.
Bir videoda 459 kırpılma platosu oluştu ve baştan sona duyulur distorsiyon verdi.

Bunun yerine `scripts/master.py` kullan:

```bash
python3 scripts/master.py mix_raw.wav mix.wav -14.0 -3.5
```

**Tavan -3.5 dBFS olmalı.** AAC kodlayıcı WAV tepesinin ~3.5 dB üstüne çıkabiliyor.
Ölçüldü: tavan -1.2 → AAC +1.96 dBFS (kırpık), tavan -3.5 → AAC -0.28 dBFS (temiz).

Ayrıca SFX ve müziği `highpass=f=50` ile süz: duyulmayan sub enerji tüm tavanı yiyor.

### Teslimden önce ZORUNLU kırpılma kontrolü

Kodlanmış videonun sesini çözüp ölç. Sıfır tolerans:

```bash
ffmpeg -v error -i OUT.mp4 -ac 1 -ar 48000 -f f32le - | \
python3 -c "import sys,numpy as np; x=np.frombuffer(sys.stdin.buffer.read(),dtype=np.float32); \
print('tepe %.2f dBFS, >0dBFS ornek: %d'%(20*np.log10(abs(x).max()), (abs(x)>1.0).sum()))"
```

`>0dBFS örnek` **0 olmalı**. Değilse tavanı düşür ve yeniden master'la.

### ⚠ Telefon hoparlörü 120 Hz altını çalmaz

Bu en pahalı hataydı ve seviye ölçümü onu göstermiyordu.

Kirpi videosunda müziğin **%89.6'sı**, efektlerin **%95.2'si** 120 Hz altındaydı.
RMS "normal" görünüyordu (−21 dB) ama o enerji telefon hoparlöründen çıkmıyor.
Kullanıcı "müzik duyulmuyor, efekt sesleri yok" dedi ve **haklıydı**.

Referans videonun profili hedeftir:

| Band | Referans | Kötü (eski) | İyi (düzeltilmiş) |
|---|---|---|---|
| 20–120 Hz (telefonda yok) | %1.5 | %89.6 | %4 |
| 120–300 Hz | %23.8 | %9.8 | %40 |
| **300 Hz–1 kHz** | **%64.1** | %0.6 | %46 |
| 1–4 kHz | %9.4 | %0.0 | %10 |

`build.py` artık her kurguda bunu basıyor ve %15'i aşarsa uyarıyor. Sentez
yaparken **gövdeyi 300–1000 Hz'e koy**; sub sadece dokunuş olsun.

### Sidechain müziği öldürmesin

Ölçüldü: `ratio=8, threshold=0.035, release=300` ile müzik konuşma
aralarında **geri gelmiyordu** — sessizlikte −40.9 dB, konuşmada −30.7 dB.
Tam tersi olmalı.

Şimdiki değerler: müzik `ratio=2.5, threshold=0.09, release=160`, seviye 0.78.
Sonuç: aralarda −21.4 dB, konuşmada −23.2 dB. Doğru yön.

**Efekt duck EDİLMİYOR.** Vuruş kısa bir geçici, konuşmayı maskelemiyor;
ducking onu amacından ediyordu.

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
- **Kaynağın kendi sesi** `--src-audio GAIN` ile geri gelir (0.3–0.6 tipik).
  Planlar kaynaktan farklı sıra ve hızda alındığı için kaynak sesi olduğu gibi
  altına sermek olmuyor: `source_audio()` her planın ses parçasını ayrı kesip
  `atempo` ile ağır çekim çarpanını uyguluyor (perde korunur — `asetrate`
  perdeyi kaydırır ve kaynakta konuşma varsa bozar), sonra birleştiriyor.
  Konuşmanın altına duck ediliyor. Ortam sesi, hayvan sesi, kaynağın kendi
  müziği buradan gelir ve çoğu zaman sentetik yataktan iyidir — sahneye ait.
  `--no-music` ile birlikte kullanmak temiz bir kombinasyon.
- **Yatağın rengi** `--music-mood` ile seçilir: `drive` (varsayılan, tempolu
  102 BPM) · `sad` (acıklı — 64 BPM, Am–F–C–G, piyano + yaylı, kick/hi-hat
  yok, ritmi yumuşak bas nabzı taşır). Kurtarma/terk edilme gibi duygusal
  hikâyelerde tempolu yatak yanlış duruyor.
- **`--no-music`** yatağı tamamen susturur, efektler kalır. Referansta
  sessizlik sıfır olduğu için önerilmez — ama kullanıcı isteyebilir, bir
  köpek videosunda istedi. Kapattıktan sonra sessizlik oranını ölç:
  %10'u aşıyorsa kesimler çıplak kalmış demektir.
- **Efekt sesleri** `scripts/audiobed.py` ile: büyük kesimlerde boom + whoosh, ara
  kesimlerde tik, ödül anından önce riser + sub-drop.
- Her darbeye görsel karşılık ver: flash (0.13s) ve kamera sarsıntısı (6–10px,
  0.28s'de sönen).

---

## 7. Render ve kalite kontrolü

`build.py` render'ı da yapıyor; aşağıdakiler onun kullandığı değerler, elle
müdahale gerekmiyor.

```bash
-c:v libx264 -preset slow -crf 18 -profile:v high -level 4.0 -pix_fmt yuv420p
-r 30 -movflags +faststart -c:a aac -b:a 192k -ar 48000 -ac 2
```

**30 MiB sınırı.** Teslim yolu 30 MiB'ı aşan dosyayı reddediyor. 33 saniyelik
bir video crf 18'de 31 MiB çıktı. Aşarsan `content.mp4` + `overlay.mov` +
`mix.wav`'dan yeniden birleştir (ikinci kayıplı kodlama olmasın), `crf 22` ve
`-maxrate 6500k -bufsize 13000k` ekle — 19 MiB'a iniyor, gözle fark yok.
`build.py --work` klasörü bu üç dosyayı bırakıyor, tekrar üretmen gerekmiyor.

**Teslimden önce her seferinde:**

`build.py` artık şunları kendiliğinden basıyor — **üçünü de oku**:

- **PLAN ↔ SÖZ tablosu**: her planın notu ve o an konuşulan kelimeler yan yana.
  Tutmuyorsa EDL yanlış. Bu oturumda iki kez aynı hata yapıldı ("ot yiyor"
  derken ekranda domuz yürüyordu; "akıntıda kapana kısılan bu adam" derken
  ekranda fil vardı) — tablo o hatayı görünür kılıyor.
- **BÖLÜM–SAHNE tablosu**: her bölümün `src` değeri ile kaynağın kendi en
  yakın sahne kesimi. Sapma 0.60s'yi geçerse render durur (§3). Derleme
  kaynakta anlatım–görüntü kaymasını yakalayan ASIL kontrol bu.
- **PARAGRAF–KESİM tablosu**: her paragrafın sesteki başlangıcı ile en yakın
  plan kesimi. "sınırlar KULLANILMADI" yazıyorsa ölçüm bu seslendirmede
  güvenilir değil, atlandı (§3).
- **Kesim–duraklama oranı**: kesimlerin kaçı sessizliğe oturuyor (hedef %40+).
- **`<çıktı>_kontrol.png`**: her planın orta karesi + o anki altyazı. **BAK.**

Sonra:

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
