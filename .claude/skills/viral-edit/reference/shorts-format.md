# Pulse Tales Shorts Formatı — sonuna kadar izletme

Kullanıcı istedi: "etkili hook cümlesi ve cümle içinde dikkat çekici metinlerle
sonuna kadar izletecek bir format". Metin, ekran yazısı ve kurgu tek bir iskelete
bağlanır. Yazım kuralları (`script-writing.md`) ve kanıt kuralı (`SKILL.md` §0)
geçerli: her cümle bir kareye, her bilgi bir kaynağa bağlı.

## İskelet (25–35 sn)

| Zaman | Blok | Seste | Ekranda |
|---|---|---|---|
| 0–2 sn | **HOOK** | Soru veya olay + merak, ≤ 7 kelime. Sonucu söyleme. | Büyük hook yazısı (2 satır, beyaz + sarı). Görüntü: gerilimin başladığı an, **sonuç değil** |
| 2–5 sn | **VAAT** | İzleyiciye bir hedef ver: kaç adım, ne bekleniyor | Sayaç belirir: `1/5` |
| 5–20 sn | **TIRMANMA** | Her 4–6 sn bir vuruş: olay → mini merak → sonuç | Her vuruşta sayaç ilerler, ok + clink |
| her 6–8 sn | **YENİDEN KANCA** | Cümle içi dikkat ifadesi (aşağıdaki banka) | Tek kelimelik pop yazı (`DİKKAT ET`) |
| ~%70 | **BİLGİ BOMBASI** | Kaynaklı tek bilgi, sayıyla | Sayı büyük pop (`4 AYLIK`) |
| son 3–5 sn | **DORUK** | Son adım, "ve…" ile gecikmeli | Sayaç tamamlanır (`5/5 ✓`), vuruş sesi |
| son 1–2 sn | **KAPANIŞ** | İkiye bölen soru **veya** ilk cümleye bağlanan döngü | Yazı yok, görüntü akar |

## Neden çalışıyor

- **Sayaç / hedef** izleyiciye bitiş çizgisi verir: "5'in 3'ü oldu" diyen kişi
  kalan ikiyi görmeden kaydırmaz. Sayılabilir bir şey yoksa hedef cümleyle
  verilir ("son hamleyi kaçırma").
- **Yeniden kanca**: Shorts'ta düşüş 5–8 sn aralığında ve ortada olur. Her
  aralıkta yeni bir açık döngü açılır, öncekinin cevabı verilir.
- **Gecikmeli doruk**: "Ve… kırmızı." Üç nokta yalnız burada.
- **Kapanışta CTA yok.** "Abone ol / beğen" izlenme yüzdesini düşürür. Soru
  yorum getirir, döngü tekrar izletir.

## Yeniden kanca bankası (cümle içi dikkat ifadeleri)

Videoda gerçekten olan bir şeye bağlanmayan ifade kullanılmaz ("bunu kimse
beklemiyordu" ancak kare bunu gösteriyorsa).

| Amaç | İfade |
|---|---|
| Dikkati bir ana çek | `Şimdi şuraya dikkat et.` · `Buraya bak.` |
| Devamı vaat et | `Ama durmuyor.` · `Asıl ilginç kısım şimdi.` · `Bu daha başlangıç.` |
| Sahte son | `Bitti sandın, değil mi?` (kare gerçekten boşalıyorsa) |
| Sona çek | `Ve sıra sonuncusunda.` · `Son hamleyi kaçırma.` |
| Ters köşe | `Ama dikkat et, bu aynı ... değil.` (yalnız kanıtlıysa) |
| Bilgiye geçiş | `Bilim insanlarına göre…` · `Bunun bir açıklaması var.` |

## Ekran yazısı katmanları (giydir.py)

1. **Hook** (`big`, 0–2.5 sn): 2 satır, üst satır beyaz, alt satır sarı, üst
   güvenli bölgede (y 0.13 / 0.21).
2. **Sayaç** (`counters` veya `big`): `1/5` … `5/5`, üst köşe, olay anında değişir.
3. **Pop kelime** (`big`, ≤ 1 sn): yeniden kanca anlarında 1–2 kelime. Video
   başına en fazla 3 — fazlası altyazıyla yarışır.
4. **Altyazı**: kelime söylendikçe belirir (reveal), cap_y 0.80–0.82, anahtar
   kelimeler sarı.
5. **Ok + clink**: yalnız sayılan olaylarda (parça girdi, hamle yapıldı).

## Kapanış kalıpları

| Tür | Örnek |
|---|---|
| İkiye bölen soru | `Sence bunu bir çocuk mu daha hızlı yapar, bu kuzgun mu?` |
| Döngü | son: `Şimdi bir daha izle. Bu sefer gagasına bak.` (tekrar izletir) |

## Kontrol listesi (metni teslim etmeden önce)

- [ ] İlk cümle ≤ 7 kelime, sonucu söylemiyor
- [ ] Hedef / sayaç 5. saniyeden önce verildi
- [ ] Her 6–8 sn'de bir yeniden kanca var
- [ ] Bilgi cümlesi kaynaklı, sayı yazıyla ("dört aylık")
- [ ] Son cümle soru veya döngü; "abone ol" yok
- [ ] Her cümlenin kanıt karesi tabloda

## Viral anlatım dili (kullanıcı: "milyonlarca izlenen kanallardaki metinler gibi")

Format aynı kalır; söyleyiş sertleşir. Kanıt kuralı değişmez — iddia büyümez.

1. **Karşıtlıkla aç**: `Bu oyuncak çocuklar için yapıldı. Şimdi bir kuzgunun önünde.`
2. **Kesik cümle**: 2–5 kelime, yer yer tek kelime (`Üç.` `Dört.`).
3. ⛔ **Hamle hamle anlatma.** `İlki yeşil. Bir delik… bir başkası… ve içeride.`
   kullanıcıya "berbat" geldi: görüntünün zaten gösterdiğini spiker gibi sayıyor.
   Hamleyi ekrandaki sayaç/ok gösterir; ses hikâye ve anlam katar (soru, sahte son,
   ters köşe, bilim cevabı, bekletilen son, "bir daha izle" döngüsü).
4. **Orta köprü**: `Asıl çılgın kısım şu:` — ikinci yarıya taşır.
5. **Bilgi = ters köşe**: `Bilim insanları … test etti. Sonuç: …`
6. **Döngü final**: son cümle ilk cümleyi tekrar eder
   (`Ve unutma… bu oyuncak çocuklar için yapıldı.`).

## Teşhis: "milyonluk Shorts gibi değil" (kedi–fare, kullanıcı: "berbat")

Kaynak olduğu gibi + sabit yazı + renk ayarı yetmedi. Eksikler ve çözüm:

1. **Sesi takip eden altyazı yoksa video ölü görünür.** 21 sn sabit iki satır
   en büyük hataydı. Seslendirme metni yoksa İLK iş metni istemek.
2. **Soğuk açılış**: en gergin an, ağır çekim, sonuçtan hemen önce DONMA +
   hook sorusu + `pop` + 0.4 sn müzik sessizliği → `rewind` ile başa dön.
   (cutter: `slow: 200` donma, `rewind` planı; sounddesign `--pop --mute --rewind`)
3. **Ölü an hızlanır** (1.5x), olay anı ağır çekime alınır (≈1.6x) + ok + clink.
4. Kaynağın kendi yazısı: kutu tüm video boyunca → silinir (alttaki zemini
   kaydırarak kopyala; ProPainter kamerayla birlikte giden kutuda gri yama bıraktı),
   cümle yalnız ilgili 3–4 sn'de altyazı olarak geçer.

## Başkasının dikey editini yeniden kurgulama (LoL, kamera üstte / oyun altta)

Kullanıcı: "profesyonel şekilde değiştir", "globale hitap etsin, TR bir şey yazma".

- Ekran yazıları İngilizce (oyun/esports klipleri global kitleye). Oyunun kendi
  arayüzü (kill feed vb.) kaynak dilinde kalır.
- Panel sınırındaki başlık yazısı silinmez, yerleşim yeniden kurulur: kamera
  paneli yazının üstüne kadar kırpılıp kendi alanını doldurur (≤ %3 ölçek),
  araya kendi ayraç çizgimiz, oyun paneli ölçeksiz. Oyun paneli zoomlanmaz.
- Zamanlar hızlı arama (`-ss` girişte) ile değil, kare kare ölçülür
  (parlaklık/sarı alan eşikleri): hızlı aramada ~0.3 sn kayma oldu.
- Kurgu: son vuruştan hemen önce donan soğuk açılış + soru hook → geri sarma →
  ölü kısım 1.25x → olay (kalkan) anında soru + ok + clink → sahte son → kill
  ağır çekim + boom + sarsıntı → kill feed görünürken donma + sonuç kelimesi.
- "Tekrarlanan içerik olmasın" (v2): yerleşim tersine (oyun üstte, kamera
  altta yuvarlak köşeli küçük kart, kaynak boyutunun altında), ayrı renk
  (gece mavisi oyun, soluk kamera), soğuk açılış başka anda (kalkan), kill sonrası
  nişangahlı `REPLAY` (0.3x), sonda yorum sorusu. Nişangah: can barı
  matchTemplate ile izlenir, yalnız doğrulanmış aralıkta çizilir (barın
  kaybolduğu/kameranın kaydığı yerde kilit kaçtı).
- Görsel değişiklik tek başına YouTube'un "reused content" kuralını aşmaz;
  asıl fark özgün seslendirme/yorum. Seslendirme metnini öner, ses gelince senkronla.
- ⛔ **Yazı oyunu kapatmaz, az olur** (kullanıcı: "çok yazı olmasın, olan yazılar
  da oyunu kapatmasın"). Yerleşim: üstte yorum bandı (0–280), oyun paneli
  (ölçeksiz, alt arayüz şeridi kırpılır), altında çeviri şeridi, en altta kamera
  kartı. Video başına en çok 3 başlık (hook + 1 espri + kapanış) ve 2 çeviri
  etiketi (yalnız ana oyuncunun duyuruları). Ok/nişangah/REPLAY etiketi de oyun
  paneline konmaz.
- Derleme kaynağında (Keria Lux) kullanıcı: "esas sahneler yok, sadece kill anını
  koymuşsun, berbat" → oyunları **baştan sona** koy (yalnız ölü kısım 1.3x),
  sıralama (#4→#1) + anons sesi. "Alt kamerada sadece Keria olsun": kaynağın kamerası
  sahneden sahneye başka oyuncuya geçer — kare kare kimlik sınıflandır (referans
  karelere korelasyon), kullanıcıya yüz tablosuyla teyit ettir, yalnız o aralıklar
  canlı (`cam_keep`), kalanında aynı oyuncunun görüntüsü (`cam_fill`).
- Anons sesi: flite "robotik" bulundu ("daha insansı") → Kokoro `am_michael`.
- ⛔ Oyunun üstünde bant yok (kullanıcı: "yukarıdaki kırmızı alan oyunu bölüyor,
  yarım ekran oluyor"). Varsayılan `"layout": "game_top", "game_scale": 1.2`:
  oyun y=0'dan başlar ve ekranın üst yarısını doldurur, yazı bandı (200 px) oyunla
  kamera kartı arasında.
- LoL formatı sürecek: bazen tek sahne, bazen "en iyi N" geri sayım (kullanıcı).
  Her videoya kapak `esports_cover.py` ile: en parlak an (lazer/patlama) + oyuncu
  yüzü + 2-3 kelimelik provokatif satır ("KERIA'S LUX / IS ILLEGAL") + rozet.
- Pulse Tales, seslendirme gelmediyse (örümcek klibi): İngilizce metni ben yazdım,
  Kokoro `bm_george` (İngiliz belgesel sesi) ile cümle cümle üretip her cümleyi
  olay anına yerleştirdim (`reference/pulse_spider.example.py`). Kaynağın kendi
  müziği/sesi kullanılmadı. İç panel tam 9:16 ise (siyah kenar + üst yazı ekli
  repost) paneli tam ekrana ölçeklemek kırpma DEĞİL: içerik kaybı yok, kaynak
  yazısı da kendiliğinden gider. 4:5 panelde bu yapılmaz (kullanıcı reddetti).
- ⛔ **Altta büyük boşluk bırakma** (kullanıcı, kare kaynakta: "alt taraftaki büyük
  siyahlık ne?"). Yerleşimi kaynağın en-boy oranına göre kur: oyun `game_h` (≈1500)
  ile ekranı yazı bandına kadar doldurur; en alttaki ≈190 px YouTube başlık alanı
  → yalnız ince kanal şeridi (`footer`). Büyütmede yanlar kırpılır → `track`
  (hareket + efekt ağırlık merkezine yumuşak otomatik kadraj) ve `keep`
  (kill duyurusu gibi yazılar o sürede kadrajda kalır). Teslimden önce telefon
  gözüyle bak: boşluk / kesik yazı / kadraj dışı aksiyon var mı?
- Yatay (16:9) yayın + kullanıcı "her açı/sahne görünsün": **bölünmüş ekran**
  (`reference/esports_split.example.py`): üstte TAM yayın karesi 1080x608 (hiçbir
  şey kırpılmaz, yakın plan bölgesi beyaz çerçeveyle işaretli), ortada yazı bandı,
  altta aksiyonu (x+y) takip eden ~1.4x yakın plan. "Gerçek sesi kıs": yayın sesi
  ≈ -12 dB + anonsta ek kısma; üstüne üretilmiş 140 bpm ritim (kick/clap/hat/808),
  donmada susar. Bu kaynakta sahne/turnuva adı emin değilse kapakta yazma
  (MSI mi Worlds mü belli değildi → "2024").
- ⛔ Yüz kamerası yoksa ekranı İKİYE BÖLME (kullanıcı: "neden hep 2'ye bölüyorsun,
  insan yüzü yok ki"; bölünmüş ekranda yazısız anlarda boş kalan bant da kötü).
  Yatay yayında varsayılan **tam ekran** (`reference/esports_fullscreen.example.py`):
  skor şeridi ve alt yayın grafikleri dışında kalan satırlardan 9:16 pencere,
  aksiyonu takip eden yatay kadraj, kill duyurusu o sürede kadrajda, kill anında
  hafif ani yakınlaşma. Yazı yalnız DONMA anlarında (kare hafif kararır): açılış
  hook'u + kapanış sorusu; oyun akarken üstünde yazı yok, ortada boş bant yok.
- ⛔ **Fazla zoom yapma** (kullanıcı: "çok zoom yaptığın için oyun izlenmiyor"):
  16:9 → tam 9:16 (2.2x) savaşın çoğunu dışarıda bırakıyor. Yatay yayında varsayılan
  `reference/esports_wide.example.py`: kaynağın tam yüksekliği, 864 px genişlik →
  1080x1350 (yalnız 1.25x, oyun ekranın %70'i), sakin takip (1 sn yumuşatma),
  ani yakınlaşma yok. Üstte 300 px bant her an dolu ("BLG vs GEN" + değişen
  satır: hook → 5v5 TEAMFIGHT → CHOVY DOWN. → … → kapanış sorusu).
- Kaynağın kapanış geçişi (bulanık wipe) donma karesine girmesin: Laplacian
  varyansıyla netliğin düştüğü anı ölç, donmayı ondan önce al.
- ⛔ Kapak **sade**: tek odak (ulti/patlama), kenarlar güçlü karartılır (blur yok),
  tek büyük cümle (2-3 kelime) + küçük üst satır. Halka/rozet/çok etiket = "karışık".
- **Döngü kapanışı:** son plan, kapanış sorusundan sonra 0.5 sn geri sararak
  videonun İLK karesine döner; son anda üst bant hook'a döner → YouTube başa
  sardığında kesinti yok. **Spiker:** kill/patlama pencerelerinde tam ses
  (çığlık en güçlü hook); ağır çekimde perde korunur
  (rubberband pitch=1.0). Açılış: ilk karede darbe + spiker tam + yükselen gerilim → donma.
- **Kapak (poster):** Anton font (`fonts/`), üstte takım renkli "BLG (VS) GEN",
  ortada tek odak (ulti/patlama) teal-turuncu renk + güçlü kenar karartma,
  altta dev 2 satır ("WHO / SURVIVES?") hafif eğik + parıltı. Kullanıcı önceki
  sade/kalabalık kapakları "berbat" buldu; bu "profesyonel" istendi.
- **LoL'de yapay zekâ seslendirmesi YOK** (kullanıcıyla karar): spiker (kill
  anlarında tam) + ritim + efekt + bant yazıları. Seslendirme gidince donmalar
  kısalır (hook 2.0 sn, kapanış 2.5 sn). Pulse Tales'te anlatım kalır.
- ⛔ **Yayıncı (spiker) sesini kısma/kapatma** (kullanıcı: "çok kötü olmuş"): spiker
  baştan sona tam seviyede; ritim onun ALTINDA, spiker konuştukça kendiliğinden
  çekilir (sidechain). 808 bas distorsiyonsuz ve kısa — kesik, dolu 808 vuruşu
  sahnede "garip bir ses" gibi duyuldu (kullanıcı: "24. saniyede bir ses var").
- **Spiker altyazısı (Descript):** kaynak Descript'e `import_media` (direct upload,
  language "en") → `export_transcript` srt → segment zamanları. Kelimeler segment
  içinde harf sayısıyla dağıtılır, üst bantta kelime kelime belirir (aktif kelime
  sarı). Yanlış duyulan oyuncu adları (ör. "Chillin") gösterilmez ama zamanı korunur.
  Hook spikerin gerçek, yarım kalan cümlesi olabilir ("FAKER IS NOT—"): donmada
  o cümlenin sesi gerçek hızında çalar. Örnek: `reference/esports_captions.example.py`.
- ⛔ (LoL, kullanıcı: "berbat, ilk saniyeler donup kalıyor, geri sarmadan önce
  takılıyor") Soğuk açılış donması + geri sarma + kapanış donması + döngü YOK.
  Üst bantta yalnız iki takımın adı ("T1 vs BLG"), başka yazı/etiket yok. Video
  doğrudan oyunla başlar; yalnız kill anlarında kısa ağır çekim + boom kalır.
