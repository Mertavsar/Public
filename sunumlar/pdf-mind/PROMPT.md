# PDF Mind — detaylı sunum videosu + ekran görüntülü sunum dosyası

Sen bu bilgisayarda çalışan Claude Code'sun. Görevin: **PDF Mind** ürününü baştan sona inceleyip
(1) ekran görüntülü, detaylı bir sunum dosyası `SUNUM.md` ve (2) bu sunumu anlatan profesyonel bir
**sunum videosu** üretmek. Soru sorman gerekirse hepsini TEK mesajda sor, sonra durmadan ilerle.
Kısa konuş (CLAUDE.md "Konuşma kuralı"). Çalışma klasörü: `Public/sunumlar/pdf-mind/`.

## 0. Ürün ve hazır içerik
- **Ürün:** PDF Mind — Flutter mobil uygulaması (Android/iOS, paket `com.docubrain.ai`), kod: GitHub `Mertavsar/PDF-Mind`
  (bu bilgisayara klonla: `git clone https://github.com/Mertavsar/PDF-Mind` — Public'in yanına).
- **Sunum metni hazır:** `SUNUM.md` koddan çıkarıldı (22 araç, planlar, teknik yapı). Sen kodla tekrar doğrula,
  eksik/yanlışı düzelt; yoksa sıfırdan yazma.
- **Ekran görüntüleri:** kullanıcı telefondan çekip `ekran/` klasörüne koyacak (`EKRAN_LISTESI.md`); ekran kayıtları `ekran/kayit/`.
  Eksik olanları kullanıcıya tek listede bildir. Kendin çekmen gerekirse: Flutter SDK + Android emülatörü kur,
  uygulamayı çalıştır (Firebase/RevenueCat yapılandırması gerekiyorsa kullanıcıdan iste, uydurma).
- **Uygulama içindeki örnek yorumlar** ("Ahmet K.", "Zeynep A.") ve "Toplam X kişi Pro'ya geçti" gibi sayılar sunuma/videoya GİRMEZ.

## 1. Özellik envanteri (`ENVANTER.md`)
Ürünü gerçekten kullanarak çıkar; tahmin yok:
- Tüm ekranlar/sayfalar (ad, adres, ne işe yarar)
- Her ekrandaki tüm özellikler, butonlar, ayarlar, menüler, boş/hata/yükleniyor durumları
- Kullanıcı akışları uçtan uca: kayıt/giriş → PDF yükleme → işleme → sonuç (özet, soru-cevap, zihin
  haritası, not, dışa aktarma… ürün ne yapıyorsa) → paylaşma/indirme → ayarlar/plan
- Desteklenen dosya türleri, sınırlar (boyut, sayfa), dil desteği, fiyat/planlar (sadece üründe veya
  resmî sayfasında yazanı yaz)
- Kod deposuysa: mimari (ön yüz, arka uç, yapay zekâ modeli/servisi, veritabanı, depolama) — dosya yollarıyla
Bilinmeyeni "bilinmiyor" diye işaretle. Pazarlama iddiası, rakip kıyası, kullanıcı sayısı UYDURMA.

## 2. Ekran görüntüleri (`ekran/`)
- Playwright ile çek: masaüstü **1920×1080** ve mobil **390×844**; her akışın her adımı ayrı kare.
  Masaüstü uygulamasıysa pencere görüntüsü al (Windows: PowerShell/`nircmd` yoksa Playwright'ın
  yapamadığı yerde kullanıcıdan ekran görüntüsü iste).
- Adlandır: `ekran/NN-akis-adim.png` (ör. `03-yukleme-surukle-birak.png`).
- Her görüntünün işaretli bir kopyası: önemli butona kırmızı (#e3141b) çerçeve + numaralı balon
  (`ekran/isaretli/…`; Python Pillow ile).
- **Gizlilik:** gerçek kişisel veri/e-posta/fatura görünmesin; demo hesap ve örnek PDF kullan
  (örnek PDF'i kendin üret: 3–4 sayfalık, telifsiz bir makale/rapor). Görünen kişisel veriyi bulanıklaştır.

## 3. Sunum dosyası (`SUNUM.md`) — hazır taslağı doğrula, görselleri bağla
Her özellik bölümü: **ne yapar → neden önemli → adım adım nasıl kullanılır (numaralı) → ekran görüntüsü
(işaretli) → ipucu/sınır**. Görüntüler göreli yolla: `![Yükleme ekranı](ekran/isaretli/03-yukleme.png)`.
Dil: sade Türkçe, kısa cümleler. Sonunda: SSS, sınırlar, sözlük, kaynaklar (ürün içi + resmî sayfalar).
Ayrıca `SUNUM.pdf` üret (Markdown → HTML → Playwright ile PDF; A4, kapak sayfası, içindekiler, sayfa numarası).

## 4. Video
**Hazır plan:** `VIDEO_PLANI.md` (sahne sahne ekran, kamera, seslendirme, ekran yazısı) + `video_sahneler.json` + `seslendirme_uzun.txt` / `seslendirme_teaser.txt`. Planı uygula; sadece gerekirse süreleri gerçek ses süresine göre ayarla.
Lemo-Opuscar kütüphanesini kullan (`~/lemo-opuscar`; eklenti komutu tanınmıyorsa `SKILL.md`, `DIRECTOR.md`,
`TECHNIQUE.md` ve stil dosyasını doğrudan oku).
- **Stil: `living-screencast`** (gerçek arayüz + imleç takibi, tıklamada yakınlaşma, pencere duvar kâğıdı
  üstünde, arayüzün içinde yaşayan bir maskot). Ürünün **gerçek ekran görüntülerini** kullan; arayüzü
  yeniden çizme, yalnızca kırp/yakınlaştır/vurgula. Maskot özgün olsun (ör. küçük bir PDF sayfası
  karakteri: katlanan köşe, göz, ezilip esneme), hiçbir bilinen markayı andırmasın.
- **İki çıktı:**
  1. `pdf-mind-sunum.mp4` — yatay **1920×1080**, 30 fps, **3–5 dk**, bölümlü: Giriş/problem → Ne yapar →
     her ana özellik ayrı bölüm (45–60 sn) → kullanım akışı uçtan uca → (varsa) planlar → Sonuç/CTA.
     Her bölüm başında kısa başlık kartı; bölüm zaman damgalarını `BOLUMLER.txt`'ye yaz (YouTube için).
  2. `pdf-mind-teaser.mp4` — dikey **1080×1920**, **45–60 sn**, en etkileyici 3 özellik, hook ilk 2 sn.
- **Hikâye:** Tek kahraman (öğrenci veya çalışan) + tek sorun ("100 sayfalık PDF'i okumaya vaktim yok")
  + dönüm noktası (PDF Mind) + başa dönen son (aynı kişi artık 2 dakikada hâkim). Her cümle bir ekrana
  karşılık gelsin; anlatılan özellik o anda ekranda görünsün.
- **Kamera:** imleç takibi, tıklamada itme, bölüm geçişlerinde ürünün kendi hareketi (sayfa çevirme,
  PDF'in zihin haritasına dönüşmesi gibi) — en az 4 farklı kamera hareketi, 1 imza çekim.
- **Ses:** Türkçe anlatım (kullanıcı kaydı varsa o; yoksa edge-tts `tr-TR-AhmetNeural`), Whisper ile
  her satırı doğrula. Müzik + efekt (tık, kaydırma, sayfa çevirme, maskot sesleri) + kısa sessizlik
  dönüm noktasından önce. −14 LUFS. Altyazı gömülü + `.srt`.
- **Görsel:** ürünün kendi renkleri esas; vurgu ve işaretler kırmızı #e3141b. Yazılar telefonda
  okunacak boyutta. Altyazı arayüzün önemli kısmını kapatmasın.

## 5. Onay noktası (tam render'dan önce)
Göster ve onay bekle: ENVANTER.md özeti (özellik listesi), SUNUM.md taslağı, seçtiğin hikâye,
bölüm/saniye akışı, maskot karakter kağıdı + 2 stil karesi. Onaydan sonra üret.

## 6. Kalite kontrol ve teslim
- Kontak sayfası (her bölümden kare), maskot ve imleç hareketlerine 0,2 sn şerit bakışı, bir tam
  sesli izleme; bulunanları tek turda düzelt.
- Her iddia ürün içinden veya resmî kaynaktan; `KAYNAKLAR.md`.
- Teslim listesi: `SUNUM.md`, `SUNUM.pdf`, `ENVANTER.md`, `KAYNAKLAR.md`, `ekran/`, `pdf-mind-sunum.mp4`,
  `pdf-mind-teaser.mp4`, `.srt` dosyaları, `BOLUMLER.txt`, `CREDITS`, kaynak kod + `build.sh`.
- Git'e sadece bu klasördeki kaynakları, md/pdf'leri ve son videoları ekle; kopyalanan motor,
  fontlar, `node_modules`, geçici render kareleri ekleme.
