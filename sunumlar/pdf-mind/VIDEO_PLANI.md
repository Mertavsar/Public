# PDF Mind — video üretim planı
Bu dosya `PROMPT.md` §4'ün uygulanış planıdır. Görseller: `ekran/` (uygulamanın kendi ekranları, 1179×2556).
Makine okunur sürüm: `video_sahneler.json` · Seslendirme metinleri: `seslendirme_uzun.txt`, `seslendirme_teaser.txt`.

## Genel
- **Araç:** Lemo-Opuscar, stil **living-screencast** (`~/lemo-opuscar/styles/living-screencast/STYLE.md`).
- **Görsel dil:** gerçek ekran görüntüsü telefon çerçevesi (yuvarlak köşe, ince siyah çerçeve, yumuşak gölge) içinde,
  arka planda uygulamanın moru (#5b3fe0) → açık lavanta yumuşak duvar kâğıdı. Vurgular ve imleç tıklama halkası kırmızı #e3141b.
  Arayüzü yeniden çizme; yalnızca kırp, yakınlaştır, vurgula, üstüne maskot ve etiket koy.
- **Maskot:** özgün "Sayfa" karakteri — katlanmış köşeli beyaz PDF sayfası, iki büyük göz, ince kollar; ezilip esneme,
  hazırlanma, taşma; anten yerine kırmızı yer imi şeridi. Problemde ezilir, her araçta küçük bir şaka yapar, sonda yığının tepesinde.
- **Tipografi:** Outfit (başlık) + Inter (metin) — uygulamanın kendi fontları (`PDF-Mind/assets/google_fonts`).
- **Ses:** Türkçe anlatım (kullanıcı kaydı varsa o; yoksa edge-tts `tr-TR-AhmetNeural`, hız +5%), her satır Whisper kontrolü.
  Müzik: hafif, iyimser elektronik/pop ritim (~110 BPM), bölüm başlarında kısa vuruş; efekt: tık, kaydırma, kâğıt hışırtısı, kart çevirme,
  imza kalemi, başarı "ding". Problem → tanışma geçişinden önce 0,5 sn sessizlik. −14 LUFS. Altyazı gömülü + `.srt`.
- **Kurallar:** Uygulamadaki örnek kullanıcı yorumları, "X kişi Pro'ya geçti" sayısı, kelime/sayfa kapasite rakamları ve fiyatlar videoya girmez.
  Sonuç ekranlarındaki içerik örnektir; ilk sahnede küçük not: "Örnek belgelerle gösterilmiştir."

## 1) Uzun sunum videosu — 1920×1080, ~3 dk 25 sn
Her AI aracı sahnesinin kalıbı: araç adı kartı (0,6 sn, kırmızı şerit) → telefon girer → imleç ilgili butona gider ve tıklar →
sonuç kısmına yakınlaşma → maskot şakası → bir sonraki araca kart çevirme geçişi.

| # | Başlangıç | Bölüm | Süre | Ekran(lar) | Kamera / hareket | Seslendirme | Ekran yazısı |
|---|---|---|---|---|---|---|---|
| h1 | 0:00 | Hook | 4 sn | `13-test-soru.jpg` | Telefon ekranı hızla büyüyerek gelir; soruya hızlı yakınlaşma | Yüz sayfalık bir PDF'i iki dakikada öğrenmek ister misin? | **100 SAYFA → 2 DAKİKA** |
| h2 | 0:04 | Hook | 4 sn | `14-test-cevap.jpg` | 'B) Su' şıkkına imleç tıklar, yeşil yanar, hafif sarsıntı | PDF Mind ile özet, test ve bilgi kartı tek dokunuşta. | **PDF MIND** |
| p1 | 0:08 | Problem | 6 sn | — (maskot sahnesi) | Maskot (PDF sayfası karakteri) devasa bir PDF yığınının altında ezilir, terler | Ders notları, raporlar, sözleşmeler… Okumaya vakit yok, önemli bilgi metnin içinde kayboluyor. | **Okumaya vakit yok** |
| p2 | 0:14 | Problem | 5 sn | — (maskot sahnesi) | Maskot ekranda beş ayrı uygulama simgesi arasında koşturur | Özet için bir uygulama, PDF birleştirmek için başka bir uygulama… | **5 uygulama?** |
| t1 | 0:19 | Tanışma | 8 sn | `01-ana-ekran.jpg` | Telefon ortada, yavaş yaklaşma; üstteki Belge Tara / AI Sohbet / Özetle kartları sırayla parlar | Hepsi tek yerde: PDF Mind. Yapay zekâ destekli belge asistanı. | **Yapay Zekâ Destekli Belge Asistanı** |
| t2 | 0:27 | Tanışma | 6 sn | `01-ana-ekran.jpg` | Kamera aşağı kayar: AI Araçları ızgarası; alt menü vurgulanır | Ana ekranda yapay zekâ araçları ve dönüştürücüler; altta Araçlar, Rehber, Geçmiş ve Profil. | **12 AI aracı + 10 belge aracı** |
| o1 | 0:33 | İlk açılış | 6 sn | `02-onboarding-1.jpg` | Tanıtım sayfası, sağdan sola kaydırma geçişiyle | İlk açılışta kısa bir tanıtım seni karşılar. | **Akıllı PDF Analizi** |
| o2 | 0:39 | İlk açılış | 7 sn | `04-onboarding-amac.jpg` | İmleç 'Öğrenci'ye tıklar, kart seçilir | Ne için kullanacağını seçersin: öğrenci, profesyonel, araştırmacı ya da hukuk. Araçlar sana göre önerilir. | **Sana özel öneriler** |
| a1 | 0:46 | AI · Özetle | 10 sn | `10-ozet-sonuc.jpg` | Özet metnine kaydırma; 'Sınavda dikkat' kutusuna yakınlaşma | Özetle: uzun belgeyi en önemli noktalarıyla madde madde verir; sınavda dikkat edilecekleri bile ayırır. | **ÖZETLE** |
| a2 | 0:56 | AI · Sohbet | 8 sn | `11-sohbet-belge-sec.jpg` | 'Dosya Seç' butonuna imleç; maskot butondan zıplar | PDF ile Sohbet: belgeni seç, aklına takılanı sor; cevap belgenin içinden gelir. | **PDF İLE SOHBET** |
| a3 | 1:04 | AI · Derin Analiz | 9 sn | `12-derin-analiz.jpg` | Analiz puanı rozetine yakınlaşma (%86 sayaçla dolar), bulgulara kaydırma | Derin Analiz: anahtar bulguları ve eksikleri çıkarır, belgeye puan verir. | **DERİN ANALİZ** |
| a4 | 1:13 | AI · Test | 9 sn | `13-test-soru.jpg` | Soru kartı, ardından 14-test-cevap'a geçiş: doğru şık yeşil | Test Hazırla: belgeden çoktan seçmeli sorular üretir, cevabını anında görürsün. | **TEST HAZIRLA** |
| a5 | 1:22 | AI · Bilgi Kartları | 8 sn | `15-bilgi-karti.jpg` | Kart 3D döner → 15b-bilgi-karti-arka.jpg | Bilgi Kartları: önemli bilgileri soru-cevap kartlarına çevirir; dokun, çevir, ezberle. | **BİLGİ KARTLARI** |
| a6 | 1:30 | AI · Boşluk Doldurma | 8 sn | `16-bosluk-doldurma.jpg` | Boşluğa harf harf 'kloroplast' yazılır; zorluk rozeti vurgulanır | Boşluk Doldurma: kolay, orta ya da zor; aktif hatırlamayla kalıcı öğrenme. | **BOŞLUK DOLDURMA** |
| a7 | 1:38 | AI · Basitleştir | 8 sn | `17-basitlestir.jpg` | 'En basit haliyle' kutusuna yakınlaşma; maskot gözlüklerini çıkarır | Basitleştir: karmaşık metni herkesin anlayacağı sade bir dile çevirir. | **BASİTLEŞTİR** |
| a8 | 1:46 | AI · Risk Analizi | 10 sn | `18-risk-analizi.jpg` | Puan %58'e kırmızıya döner; 'Madde 7' bulgusuna yakınlaşma | Risk Analizi: sözleşmedeki riskli maddeleri bulur ve puanlar. İmzadan önce neye dikkat edeceğini bilirsin. | **RİSK ANALİZİ** |
| a9 | 1:56 | AI · Karşılaştır | 9 sn | `19-karsilastir.jpg` | 'Belge A → Belge B' satırlarında ok animasyonu | Döküman Karşılaştır: iki sürüm arasındaki farkları ve ortak noktaları tek raporda gösterir. | **KARŞILAŞTIR** |
| a10 | 2:05 | AI · Tablo | 8 sn | `20-tablo.jpg` | Tablo satırları tek tek belirir; 'Excel olarak indir' butonu parlar | Tabloya Çıkar: PDF'teki tabloları bulur, Excel'e aktarmaya hazırlar. | **TABLOYA ÇIKAR** |
| a11 | 2:13 | AI · Çalışma Seti | 9 sn | `21-calisma-seti.jpg` | Özet / Test / Kartlar sekmeleri sırayla seçilir | Çalışma Seti: tek PDF'ten özet, test ve kartlar tek seferde. Sınava hazırlanmanın en hızlı yolu. | **ÇALIŞMA SETİ** |
| a12 | 2:22 | AI · Çalışma Asistanı | 9 sn | `22-calisma-asistani.jpg` | 'Ana Fikir' kutusu, ardından kavramlar sırayla açılır | Çalışma Asistanı: konuyu özel bir öğretmen gibi adım adım anlatır, sonunda seni sınar. | **ÇALIŞMA ASİSTANI** |
| d1 | 2:31 | Belge araçları | 12 sn | `30-tara.jpg` `31-img2pdf.jpg` `33-word.jpg` `34-pptx.jpg` | Hızlı montaj: her ekran 3 sn, kart çevirme geçişi | Belge araçları da cebinde: kâğıdı tara, fotoğrafı PDF yap, Word'e ve PowerPoint'e dönüştür… | **TARA · DÖNÜŞTÜR** |
| d2 | 2:43 | Belge araçları | 10 sn | `35-birlestir.jpg` `36-ayir.jpg` `37-sifrele.jpg` `38-imza.jpg` | Hızlı montaj; imza ekranında imza kendini çizer | …birleştir, ayır, şifrele ve tek dokunuşla imzala. İmzan yalnızca cihazında işlenir. | **BİRLEŞTİR · İMZALA** |
| k1 | 2:53 | Kütüphane | 8 sn | `40-kutuphane.jpg` `41-gecmis.jpg` | İki telefon yan yana kayar | Tüm belgelerin kütüphanende, yaptığın her işlem geçmişinde; sonuçlara istediğin an dön. | **KÜTÜPHANE · GEÇMİŞ** |
| k2 | 3:01 | Ayarlar | 6 sn | `44-ayarlar.jpg` `45-sss.jpg` | Yan yana; 'Dil Seçimi' ve SSS başlıkları vurgulanır | Türkçe ve İngilizce arayüz, tema seçimi ve yardım merkezi. | **TR · EN** |
| f1 | 3:07 | Ücretsiz · Pro | 10 sn | `01-ana-ekran.jpg` | Ana ekrandaki Pro kartına yakınlaşma; yanında Ücretsiz/Pro tablo animasyonu | Ücretsiz başla: ilk kullanım hediye, sonrası kısa bir reklamla. Pro ile reklamsız, sınırsız ve daha büyük belgeler. | **ÜCRETSİZ BAŞLA** |
| c1 | 3:17 | Kapanış | 8 sn | `13-test-soru.jpg` | Açılıştaki maskot şimdi PDF yığınının tepesinde oturuyor; telefon küçülür, logo | Yüz sayfa artık iki dakika. PDF Mind'ı indir, ilk analizin bizden. | **PDF MIND · App Store · Google Play** |

**YouTube bölümleri** (`BOLUMLER.txt`'yi gerçek render süresinden üret): Giriş · Tanışma · Yapay zekâ araçları · Belge araçları · Kütüphane ve ayarlar · Ücretsiz ve Pro · Kapanış.

## 2) Dikey tanıtım (teaser) — 1080×1920, ~55 sn
Telefon ekranı kadrajın %80'ini kaplar; altyazı alt bantta, ekran yazısı üstte kısa.

| # | Bölüm | Süre | Ekran | Seslendirme |
|---|---|---|---|---|
| h | Hook | 3 sn | `13-test-soru.jpg→14-test-cevap.jpg` | Yüz sayfalık PDF'i iki dakikada öğren. |
| 1 | Özetle | 7 sn | `10-ozet-sonuc.jpg` | Önce özet: en önemli noktalar madde madde. |
| 2 | Test | 8 sn | `13-test-soru.jpg→14-test-cevap.jpg` | Sonra test: belgeden sorular, cevap anında. |
| 3 | Kartlar | 7 sn | `15-bilgi-karti.jpg→15b-bilgi-karti-arka.jpg` | Bilgi kartlarıyla çevir, ezberle. |
| 4 | Risk | 8 sn | `18-risk-analizi.jpg` | Sözleşme mi? Riskli maddeleri bulup puanlar. |
| 5 | Çalışma Seti | 8 sn | `21-calisma-seti.jpg` | Hepsi tek seferde: Çalışma Seti. |
| 6 | Belge araçları | 8 sn | `30-tara.jpg|35-birlestir.jpg|38-imza.jpg` | Üstelik tara, birleştir, imzala. |
| c | Kapanış | 6 sn | `01-ana-ekran.jpg` | PDF Mind. İndir, ilk analizin bizden. |

## 3) Kontrol listesi
- [ ] Her sahnede anlatılan özellik o anda ekranda görünüyor
- [ ] Yakınlaşmalarda yazılar telefonda okunuyor (en az 28 px)
- [ ] Altyazı arayüzün önemli kısmını kapatmıyor
- [ ] En az 4 farklı kamera hareketi + 1 imza çekim (açılış/kapanış maskot yığını)
- [ ] Ses −14 LUFS, Whisper kontrolü temiz
- [ ] Yasak içerik yok (yorumlar, kapasite rakamları, fiyat)
