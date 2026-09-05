# VALENSTREND — Strateji

> `clients/valenstrend/strategy.md`. 3-6 aylık plan ve açık testler burada durur.
> `client.md` değişmeyen bağlamdır; bu dosya her ay gözden geçirilir.

**Son güncelleme:** 2026-09-05
**Durum:** İlk strateji dosyası. Marj bilinmediği için ticari hedefler henüz kilitlenemedi.

## 1. Ana hedef (3-6 ay)

**Birincil:** Hesabın satın alma hacmini, retargeting'e bağımlı olmaktan çıkararak büyütmek.
Bugün ciro büyük ölçüde mevcut kitlenin yeniden hasadıyla geliyor; kitleyi besleyen soğuk
katman kapalı. Bu yapı kısa vadede iyi ROAS gösterir, orta vadede tükenir.

**Ölçülebilir hedef:** MARJ GİRİLDİKTEN SONRA YAZILACAK.
Marj olmadan "ROAS 2,06 iyi mi kötü mü" sorusunun cevabı yoktur. Başabaş ROAS = 1 ÷ marj.
- Marj %30 ise başabaş ROAS 3,33 → bugünkü 2,06 **zarar**.
- Marj %55 ise başabaş ROAS 1,82 → bugünkü 2,06 **kâr**.
İki senaryo arasındaki fark, hesabı büyütmek ile durdurmak arasındaki farktır.

## 2. Kanal stratejisi

| Kanal | Bugünkü rol | Hedef rol |
|---|---|---|
| Meta — retargeting | Bütçenin %49,5'i | %15-20 |
| Meta — soğuk satın alma | Bütçenin %0,9'u | %50-60 |
| Meta — mesaj (WhatsApp/DM) | Bütçenin %23,4'ü | Satış kapanış oranı ölçülene kadar sabit |
| Meta — profil ziyaret / trafik | Bütçenin %10,2'si | %0-5 (marka amaçlı bilinçli ayrılan pay dışında) |
| Google Ads | Yok / bilinmiyor | Değerlendirilecek |

## 3. Açık testler

> Aynı anda en fazla 2-3 test. Her testin başarı kriteri ve süresi önceden yazılır.

### TEST-01 — AddToCart olayının doğrulanması (test değil, **düzeltme**; her şeyin önünde)
- **Bulgu:** Site geneli ViewContent→AddToCart %45,9, AddToCart→InitiateCheckout %6,5.
  Bu ikili birlikte gerçek satın alma davranışı olamaz.
- **Hipotez:** AddToCart, gerçek sepete ekleme dışında bir eylemde (sayfa yükleme, hızlı ekle,
  kategori etkileşimi, varyant seçimi) de ateşleniyor.
- **Neden kritik:** Bu sinyal (a) algoritmayı eğitiyor, (b) ₺5.976'lık bir ad set doğrudan bu olaya
  optimize ediliyor, (c) "Sepete Ekleyenler" retargeting kitleleri bu olaydan besleniyor.
- **Doğrulama:** Meta Events Manager Test Events + sitede elle tıklama testi. 1 gün.
- **Başarı kriteri:** Düzeltme sonrası ViewContent→AddToCart %5-15 bandına iner, ATC→IC %25 üstüne çıkar.

### TEST-02 — Soğuk prospecting'in yeniden açılması
- **Hipotez:** "Alışveriş - adv" (ROAS 2,71 / CPA ₺421) durdurulmasaydı hesap bugün daha sağlıklı olurdu.
- **Değişken:** Yalnızca bütçe kaydırma — retargeting'den soğuğa. Kreatif ve teklif sabit.
- **Süre:** 7 gün. **Bütçe:** Günlük ₺1.500-2.000.
- **Başarı kriteri:** Soğuk katmanda CPA ≤ ₺600 ve hesap toplam satın alma sayısı düşmeden devam.
- **Karar kuralı:** Kriter tutarsa 7 gün daha ölçekle; tutmazsa kreatif katmanına in (TEST-03).

### TEST-03 — Ad set başına çoklu kreatif (3-5 açı)
- **Bulgu:** Hemen her ad set'te **tek reklam** var. Ana retargeting kreatifi 30.01.2026'da
  oluşturulmuş — 7 aydır aynı, frequency 6,29.
- **Hipotez:** Kreatif çeşitliliği yokluğu, retargeting CPM'ini ve yorulmayı büyütüyor.
- **Değişken:** Kazanan ad set'e 3 yeni açı eklenir (kreatif briefleri 2026-09-05 raporunda).
- **Süre:** 7 gün. **Başarı kriteri:** Ad set frequency 6,29 → 4,0 altına inerken CPA bozulmaz.

## 4. Yapısal kararlar (test değil, uygulama)

1. **Konsolidasyon.** 3 adet neredeyse aynı "Folk Costume/Toptan-İşletme -TOPTAN" ad set'i paralel
   çalışıyor (₺17.879). Meta'nın kendi fragmentation uyarısı da bunu işaret ediyor. Tek ad set'e indirilir.
   (Hesapta zaten "Remarketing/45 - KONSOLİDE (TASLAK)" hazırlanmış — doğru yön.)
2. **Atıfsız hedefler.** Profil ziyaret + trafik = ₺15.056 (%10,2), 0 satın alma atfı.
   Marka amaçlı bilinçli bir yatırım değilse kesilir; bilinçliyse `client.md`'ye gerekçesiyle yazılır.
3. **ATC'ye optimizasyon durdurulur.** "Tesettür/Genel Demografi - Hariç" ad set'i satın almaya çekilir
   — ama **önce TEST-01 bitmeli**, yoksa bozuk sinyalle yeniden kurmuş oluruz.

## 5. Bu markada geçerli olmayan / henüz açılmamış alanlar

- **Google Ads:** Kanal kullanılıyor mu bilinmiyor. Kullanılmıyorsa `google-ads` bu markada geçerli değildir.
- **CRO:** Site URL'si ve analitiği elimizde yok. Funnel sayılarından kaybın **hangi adımda** olduğu
  biliniyor (FACT), nedeni bilinmiyor (HYPOTHESIS).
- **Sales:** 3.003 konuşma var, tek bir döküm yok. `conversations/` klasörü boş.

## 6. Bir sonraki gözden geçirme

**2026-09-12.** O tarihte bakılacaklar: TEST-01 kapandı mı, soğuk katman açıldı mı, marj geldi mi.
