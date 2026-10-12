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
