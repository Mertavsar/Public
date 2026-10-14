# MythBusters (Efsane Avcıları) Shorts formatı

Referans: VULRAN – "Korsanlar Neden Göz Bandı Takardı?" (30.3 sn, 1080x1920, 30 fps), ölçüldü 2026-10-12.

## Ölçülen
- **Kesim:** 18 kesim / 30 sn, ortalama plan ~1.6 sn. "Tuzaklarla dolu devasa parkur" cümlesinde 0.2 sn'lik hızlı kesim patlaması (10.0–11.5).
- **Yerleşim:** 16:9 kaynak ortada ~1080x1260 bantta (yaklaşık %48 genişlik kırpılmış). Üst ve alt bantta aynı karenin bulanık büyütülmüş kopyası var. Bizim kural: blur yok, o bantlar başlık / sonuç barıyla dolar.
- **Görseller:** Gerçek bölüm görüntüsü + araya illüstrasyon (çizgi korsan, gemi, göz yakın planı) + bazı planlarda makro yakınlaşma.
- **Altyazı:** Tek kelime, turuncu, siyah kontur, ekranın ~%57 yüksekliğinde, küçük harf.
- **Abone ol:** 9–12 sn arasında "VULRAN ABONE OL" butonu animasyonu.
- **Ses:** Kesintisiz TR seslendirme (~75 kelime / 30 sn, boşluk yok). Altında seslendirmeden ~12 dB kısık müzik ya da orijinal ses yatağı.
- **Yapı (6 adım):**
  1. Efsane (0–3.5): "Efsaneye göre…"
  2. Neden (3.5–9): mantığı
  3. Test kurulumu (9–13): "Efsane Avcıları bunu test etmek için…"
  4. Deney 1 başarısız (13–19.5): "sonuç tam bir felaketti"
  5. Deney 2 / dönüş (19.5–25)
  6. Sonuç (25–30): "Sonuç inanılmazdı…" Video sonuçla biter, soru yok.

## Bizim sürüm (aynısı değil, özgün)
- Blur yok. Kaynak ortada yaklaşık 1.33x kırpılır. Üst bantta efsanenin sorusu, alt bantta efsane metresi (BUSTED / PLAUSIBLE / CONFIRMED) durur.
- Altyazı kelime kelime, kullanıcının metniyle. Önemli kelimeler sarı veya kırmızı.
- Sonuç sadece sonda görünür. Geri sarma yok. Sonuç anında ağır çekim, flaş, boom ve damga.
- Orijinal ses: patlama, çarpışma ve tepki anlarında açılır, geri kalanında seslendirmenin altında kalır.
- Telif: Discovery / Banijay içeriği. Kendi seslendirme, kısa planlar ve kendi grafiklerin olmalı. İlk videolarda Content ID durumu izlenir.

## İlk örnek: asansör (mythbusters_asansor.example.py)
- Kaynak: resmi MythBusters Shorts (9:16, 41 sn, gömülü İngilizce altyazı y≈1290–1450).
- **Altyazı silme:** Telea iz bıraktı; ProPainter (vinpaint.py) temiz. Ayar: `--band 1280,1465 --band-x 40,1040 --white-min 175 --shadow 5,6 --grow 13`. Beyaz şeritli sahnede band kapatılıp `--rect` kullanıldı. Kullanılmayan aralık `--plain`. CPU'da ~50 dk.
- **İngilizce konuşma:** MDX ile ayrıldı, sadece efekt/ortam (inst) kullanıldı. Çarpmada +10 dB.
- **Kaynaktaki parazit geçişi** (18.88–18.96 TV karıncası) atlandı. Sahne sınırlarını kare kare kontrol et, kesim tespiti 1 kare kaçırabiliyor.
- **Metin:** Kaynağın İngilizce transkriptinden (Descript) gerçek rakamlar alındı, km/s'ye çevrildi. Kullanıcı istediğinde 6 adımlı yapıyla taslak metin yazılabilir.
- **Ekrandakiler:** Hız göstergesi (85 / 82 KM/S), BUSTED damgası, ilk cümlede hook başlığı.

## ⛔ Giriş kuralı (kullanıcı, asansörden sonra): "Shorts potansiyelli içerik editi", VULRAN girişi
Asansör hook banner + durağan planla açıldı. Kullanıcı: *"istediğim ilk giriş vibe alamadım… diğer videolarla aynı başladı"*.
VULRAN'ın ilk 4 saniyesi kare kare ölçüldü (korsan göz bandı):
- **0.0'da sunucunun yüzü, tuhaf/komik bir anda** (Adam kostümle, ağzında bıçak, yakın plan). Düzenek ilk karede değil.
- **Hook banner YOK.** Sadece küçük tek kelimelik altyazı.
- **Seslendirme 0.07'de** "Efsaneye göre…" ile başlar. Sessizlik ya da efekt girişi yok.
- **İlk cümlede kesimler 1.4 ve 2.9'da.** İlk plan hafif itme/kamera hareketli.
- **2.9'da imza:** Sunucu kesilip beyaz konturlu çıkartma olarak çizim arka planın önüne konur.
Her MythBusters videosunda: ilk kare sunucu yüzü/tuhaf an → ilk cümle 3 plan → banner yok → ilk 5 sn içinde çıkartma sahnesi.
Bu, genel SKILL.md'deki "kare sıfırda iki satır hook yazısı" kuralının yerine geçer (yalnız bu format için).

## Kaynak seçimi: Shorts potansiyeli
Seç: (1) herkesin kendine sorduğu tek soru ("suya dalarsan mermiden kurtulur musun?"), (2) tek, görsel bir doruk anı (patlama, kırılma, çarpma), (3) şaşırtıcı sonuç, (4) sunucunun yüzünü gösteren tepki planı (giriş için şart).
Bu ortamdan YouTube'a erişim yok (proxy 403). Klibi kullanıcı indirip atar.

## İkinci örnek: şişme top (mythbusters_sismetop.example.py)
- **Kaynak başkasının kurgusuydu** (720x1280, bulanık üst/alt, net bant y 298–918, gömülü turkuaz tek kelime altyazı y≈930–985). Altyazı bandın DIŞINDA kaldığı için silme yok, sadece bant kırpıldı: 2.15x büyütme, ortada 1080x1333, üst/alt koyu bar, kenarlar 70 px yumuşak. Bazı planlarda içerik bandın altında kalıyor (top bırakma 26.77), o planı kullanma.
- **Soğuk açılış (kullanıcı isteği):** Buster helikopterden atılıyor, düşüş YARIDA donuyor (0.25 sn yakınlaşma + kırmızı ton + müzik kesilir), sonra sunucu yüzü. Sonuç saklı kalıyor.
- Kaynaktaki "ESTIMATED VELOCITY 56 MPH" grafiği: metin kutusu sabit kameradan temiz kareyle yamalandı, topa bağlı kesik çizgi ince çizgi tespiti + Telea ile silindi.
- Seslendirme 1.2x hızlandı, kelime zamanları Descript'ten alınıp onaylı metne eşlendi. Müzik `audiobed --mood drive --bpm 118`, konuşmanın ~13 dB altında, konuşurken ~7 dB daha iniyor. İki çarpmada `sd.boom`.

## VULRAN ölçümü 2: "James Bond Tuzağı Gerçek Hayatta İşe Yarar Mı?" (~1 milyon izlenme, 33.7 sn)
`analyze.py` + MDX ayrıştırma, 12 Ekim:
- **Seslendirme hızı: 7.0 hece/sn.** Seslendirmede 0.12 sn'yi aşan boşluk YOK, cümleler birbirine yapışık. Bizim ilk şişme top 5.3 hece/sn'ydi (%19 sessizlik). Kullanıcı: "sesi daha hızlı yap VULRAN gibi".
  → Standart: ElevenLabs çıktısı `votight.py --gap 0.06 --min-sil 0.12 --target <7 hece/sn süresi>`. Şişme top: 43.7 → 25.9 sn (toplam 1.69x), sonuç 6.9 hece/sn.
- **Ses:** −13.3 LUFS. Müzik konuşmanın 15.5 LU altında (VO −13.5, yatak −29.0), baştan sona kesintisiz. Sessizlik %9.
- **Geçiş:** Düz kesim. 20 kesim / 33.7 sn (0.59/sn), medyan plan 1.17 sn. İlk plan 5.9 sn, ilk 10 sn çizim animasyonu (efsanenin düzeneği izometrik çizimle anlatılıyor), sonra gerçek görüntü.
- **Ekranda:** Tek kelimelik turuncu küçük harf altyazı, 10–13 sn'de "VULRAN ABONE OL" butonu, sonda damga yok ("Yani efsanevi Bond tuzağı yalandı.").
- Plan zamanlarını yeni sese taşımak: `tm()` = eski kelime başlangıçlarından yenilere np.interp (örnek dosyada).

## ⛔ Konu ve kapak güvenliği (kullanıcı, şişme top kapağı: "İNTİHARA TEŞVİK GİBİ BU NE")
- Kapakta/başlıkta: düşen insan (manken bile olsa) + "yaşar mısın / hangisi kurtuldu / hayatta kalır mı" YOK. Soru NESNEYE sorulur ("Şişme top düşüşü durdurur mu?"), mankende "TEST MANKENİ" etiketi, üstte "BİLİM DENEYİ".
- Konu seçerken öncelik: nesne/fizik/yemek/ses/araç deneyleri (cam kıran ses, iç içe telefon rehberi, su ısıtıcısı roketi, Mentos-kola, beton mikseri). Yüksekten düşme, silah, çocuk riski içeren efsaneler ikinci planda; seçilirse metin ve kapak bilim çerçevesinde kalır.

## Üçüncü örnek: kızartma yağı (mythbusters_kizartmayagi.example.py)
- Resmi Shorts (1080x1920 25fps), gömülü beyaz cümle altyazısı y≈1391–1447.
- **Disk/süre dersi:** vinpaint tüm kareyi fr.npy'ye yazıyor (68 sn = 10 GB, disk doldu). Çözüm: (1) kullanılacak aralıkları `sel.mp4`'te birleştir, (2) sadece altyazı şeridini kırp (`crop=1080:384:0:1216`), (3) şeridi sil (`--cuts` = birleşim sınırları), (4) kurguda şeridi kareye geri yapıştır. 938 kare.
- Hız: `--scale 0.38 --raft-iter 6 --neighbor 12` → ~3.6 sn/kare (varsayılan 0.5'te ~6 sn). Silme sürerken başka render çalıştırma, işlemciyi paylaşınca 13 sn/kareye çıktı.
- Hızlı yedek: `BAR=1` → Türkçe altyazının arkasında opak bant (1366–1478) İngilizceyi örter, 5 dk'da teslim.
- Seslendirme `votight --gap 0.04 --min-sil 0.08 --target 30` (41 → 30 sn, boşluk yok). Arka ses: kaynağın kendi altyapısı (MDX inst), yeniden sıralanmadan kesintisiz, konuşmanın ~14 dB altında.
- Ok/etiket/grafik seti: arrow(), ring(), tag(), stamp(), gösterge (7,8 LİTRE), verim çubukları, KIVILCIM üstü çizili → SIKIŞTIRMA, kontakta donma + "?". Her biri kelime zamanına (ws(i)) bağlı.
