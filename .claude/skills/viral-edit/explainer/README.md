# Yatay animasyonlu anlatım videosu (uzun video)

`viral-edit` dikey klip kurgusu içindir. Kullanıcı **klip olmadan**, sadece
seslendirme + metin verip "animasyon tarzında uzun video" isterse bu klasör
kullanılır. Görüntü sıfırdan çizilir: 1920x1080, 30 fps, canvas + Playwright.

İlk örnek: `altin-neden-dusuyor/` (230 s, 24 sahne).

> **Tıkla Bakalım gündem videoları için** tekrar kullanılabilir sürüm:
> `.claude/skills/tikla-bakalim/` — aynı görünüm, hazır sahne kalıpları,
> `bolum.json` ile her konuya. Bu klasör tek seferlik özel çizim için duruyor. Yeni videoda klasörü
kopyala; `anim.js` içindeki `S[k]` sahne fonksiyonlarını ve `TAGS` listesini
yeniden yaz, gerisi aynen çalışır.

## Akış

```bash
cp <seslendirme>.mp3 vo.mp3
python3 tighten.py            # duraksamaları kısalt  -> vo_tight.wav
# script.txt: seslendirmenin KONUŞULAN biçimi (rakamlar yazıyla), paragraf = sahne
python3 ../../scripts/sentalign.py --audio vo_tight.wav --text script.txt --out cap_sent.json
python3 words.py              # altyazıda rakam biçimi + paragraf no -> words.json
python3 -c "import json;open('words.js','w').write('window.WORDS='+json.dumps(json.load(open('words.json')),ensure_ascii=False)+';')"
export NODE_PATH=/opt/node22/lib/node_modules
node shot.js 5 40 120         # tek tek kareler -> frames/  (BAK)
node collect.js               # sahne geçişleri + pop anları -> events.json (eksik cue da burada çıkar)
python3 audio.py && bash mix.sh   # müzik + efekt (istenirse), master -> mix.wav (-14 LUFS, tavan -4.5)
for i in 0 1 2 3; do node render.js $i 4 30 & done; wait    # chunks/c0..3.mp4
node thumb.js                 # YouTube kapağı
```

Birleştirme ve teslim sıkıştırması: aşağıda "30 MiB".

## Hizalama: align.py değil sentalign.py

230 s'lik seslendirmede `align.py` paragraf başlarını 1.5 s'ye kadar erken
koydu (7–9. sahneler). Ölçü: orijinal sesteki uzun duraklamalar (0.35–0.56 s,
paragraf araları) `sentalign.py` sınırlarıyla 0.1–0.25 s içinde örtüştü,
`align.py` ile örtüşmedi. Uzun seste doğrudan `sentalign.py` kullan.

## Ses

Varsayılan SKILL.md §0: ses = seslendirme. Kullanıcı isterse (altın videosunda
istedi) `audio.py` + `mix.sh`: efekt zamanları `events.json`'dan, yani
görüntüden gelir — whoosh tepesi `wipe()`'ın ekranı kapattığı `SW` anına,
tık öğenin `pop()` anına. Müzik yumuşak kipte (92 BPM, hi-hat yok) ve
seslendirmenin ~18 LU altında; kazanç LUFS ölçülerek hesaplanır.

## Zamanlama: her şey kelimeye bağlı

`cue(p, 'kelime', n)` → p. paragraftaki n. eşleşen kelimenin başladığı an.
Öğeler `A(t0, x, y, çiz, {m, out, sfx})` ile o anda sahneye girer. Sabit saniye
yazma: seslendirme yeniden üretilirse her şey kendiliğinden kayar.
`collect.js` bulunamayan cue'ları `missing` olarak basar — boş olmalı.

## Duraksama kısaltma (`tighten.py`)

Kullanıcı "boşluksuz, tek nefeste" istediğinde. SKILL.md §3'teki yasak
**enerji bloğuna göre** kesmek içindi (kelime ortasındaki 0.09 s'lik ünsüz
kapanışlarından kesiyordu). Burada kural farklı:

- Sadece −35 dB altında **≥0.25 s** süren sessizlikler — ünsüz kapanışları
  (<0.12 s) bu eşiğe hiç girmez.
- Her boşluk 0.13 s'ye iner, birleşimde 12 ms crossfade.
- Ölçüldü: 245.3 s → 230.1 s, 65 boşluk; hizalama tablosu tutarlı kaldı.

## Performans tuzakları

- Canvas çizimleri tembel: `render()` 1 ms sürer ama kare `toDataURL` ile
  boşaltılınca 40–150 ms. Boşaltmadan binlerce kare çizmek (ör. tüm kareleri
  gezen bir tarama) belleği şişirir ve takılır — `collect()` bu yüzden sahne
  başına 8 nokta çizip her birinde `getImageData(0,0,1,1)` ile boşaltıyor.
- `ctx.filter = 'blur()'` yazılımsal çizimde çok pahalı. Gölge için radyal
  gradyan kullan.
- 4 işçi paralelde işçi başına kare ~0.15 s: 230 s'lik video ≈ 5 dk.

## 30 MiB

Teslim yolu 30 MiB üstünü reddediyor. 230 s'de bu toplam ~1.05 Mbit/s demek.
Düz renkli animasyon bunu kaldırıyor: parçaları birleştirip iki geçişli
`-b:v 900k` ile yeniden kodla (aşağıdaki komut), sesi 128k AAC yap.

```bash
printf "file 'chunks/c%d.mp4'\n" 0 1 2 3 > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy video_hq.mp4
ffmpeg -y -i video_hq.mp4 -c:v libx264 -preset slow -b:v 900k -pass 1 -an -f null /dev/null
ffmpeg -y -i video_hq.mp4 -i mix.wav -c:v libx264 -preset slow -b:v 900k -pass 2 \
       -c:a aac -b:a 128k -ar 48000 -movflags +faststart -shortest video.mp4
```

## Doğruluk

Kullanıcının metnindeki sayılar (tarih, oran, fiyat) aynen ekrana gelir;
temsili grafikler "TEMSİLİ" notuyla işaretlenir. Metinde olmayan veri
(ör. gerçek fiyat serisi) çizilmez, uydurulmaz.
