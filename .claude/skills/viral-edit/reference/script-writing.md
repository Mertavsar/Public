# Seslendirme Metni Yazımı

> ⛔ **Bu dosya metin YAZMAK için değil.** Seslendirme metnini kullanıcı yazar —
> sebebi `SKILL.md` §0'da: video izleyemiyorsun, kareden hikâye uydurmak yanlış
> çıkıyor. Burası kullanıcının getirdiği metni değerlendirmek, uzunluğunu
> doğrulamak ve ElevenLabs biçimine sokmak için.


Kullanıcı ham video atar, metni sen yazarsın. Metin **doğrudan ElevenLabs'e
yapıştırılacak** — düzeltme gerektirmeyecek halde teslim et.

---

## 1. Önce videoyu oku, sonra yaz

Metni videoyu görmeden yazma. Kontak sayfası çıkar (`SKILL.md` §1), kareleri gözle
incele ve şunları tespit et:

- Konu ne, kim/ne var, nerede geçiyor
- En çarpıcı görüntü hangi saniyede — hook oraya yazılır
- Kaç ayrı "sahne" veya "madde" var — sayaç kullanılacaksa gerçek sayı budur
- Videoda gömülü altyazı varsa oku; ama **çeviri yapma**, kendi açını kur

## 2. Uzunluk — ölçülmüş formül

Referans videodan ölçüm: **2.18 kelime/saniye**, 4.8 hece/saniye.

| Hedef süre | Kelime sayısı |
|---|---|
| 30s | ~65 |
| 40s | ~87 |
| 45s | ~98 |
| 60s | ~131 |

Metni yazdıktan sonra kelimeleri say. Uzunsa kes — ses uzarsa kurgu şişer, kısa
kalırsa sonda boşluk oluşur. **Boşluk bu formatta ölümcül.**

## 3. Yapı

```
0–3s    HOOK        Sert iddia veya merak. En çarpıcı görüntünün üstüne.
3–10s   KURULUM     Konuyu tek cümlede oturt. "Bu şu."
10–30s  TIRMANMA    Madde madde ilerle. Her cümle bir öncekinden ağır olsun.
30–38s  DÖNÜŞ       "Ama" anı. İzleyicinin beklemediği bilgi veya bakış.
38–42s  SORU        İkiye bölen ikilem. Yorumu tetikleyen yer burası.
42–45s  DÖNGÜ       Sebebi yarım bırak — ilk cümle onu tamamlasın.
```

### Kapanış iki parçadır

**1. İkiye bölen soru.** İzleyicinin kendi cevabı olan, basit bir ikilem.
Bilgi sormaz, taraf tutturur.

| Zayıf | Güçlü |
|---|---|
| `Sence bu bir çözüm mü?` | `Sen olsan kaçar mıydın, beklerdin mi?` |
| `Ne düşünüyorsun?` | `Haklı olan hangisi?` |
| `Yorumlara yaz` | `Kaç saniye dayanırdın?` |

**2. Döngü cümlesi.** Son cümle videonun İLK cümlesine anlamca bağlanır.
İzleyici bittiğini fark etmeden ikinci tura başlar.

En sağlam kalıp: son cümle **sebebi yarım bırakır**, ilk cümle sebebi verir.

```
ilk:  "Gergedan onu görmüyor."
...
son:  "Ve o domuz hâlâ hayatta. Sebebi tek şey:"
```

Metni yazdıktan sonra **son cümleyi ilk cümlenin önüne koyup oku.** Cümle
gibi akmıyorsa döngü yoktur, yeniden yaz.

Yasak: kapanışta "abone ol", "beğen", "takip et". İzlenme yüzdesini düşürür
ve döngüyü kırar.

## 4. Cümle biçimi

Bu format **kısa cümle** ister. Tek kelimelik altyazıda uzun cümle dağılır.

- Cümle başına **3–8 kelime**
- Yan cümle kurma, virgülle uzatma
- Edilgen değil etken: "yapıldı" değil "yaptılar"
- Sıfat yığma: "çok büyük korkunç bir" → "korkunç"

**Kötü:** `Şehirlerde yaşayan evsiz insanların karşılaştığı ve genellikle fark edilmeyen bu tasarım engelleri aslında bilinçli bir tercihtir.`

**İyi:** `Bunu fark etmedin. Ama bilerek yapıldı. Her biri bir insanı uzaklaştırmak için.`

## 5. Hook kalıpları

| Kalıp | Örnek |
|---|---|
| Sayı + dönüş | `Bunların yüzde doksanı başarısız. Yine de devam ediyor.` |
| Doğrudan iddia | `Bu bank seni oturtmak için yapılmadı.` |
| İnkâr | `Gördüğün şey tesadüf değil.` |
| İkinci tekil | `Her gün yanından geçiyorsun. Hiç bakmadın.` |
| Zaman baskısı | `On saniye. Sonra bir daha aynı gözle bakamayacaksın.` |

İlk cümle **dört kelimeden uzun olmasın**. İzleyici ilk saniyede karar veriyor.

### Hook'un ekranda da olması gerekir

Seslendirme tek başına yetmez: kitlenin büyük kısmı sessiz izliyor. İlk
cümlenin kısaltılmış hâli **kare sıfırdan itibaren banner olarak** ekranda
durur (`spec.banners[0]`, `t: 0`). İki–üç kelime, büyük, yüksek kontrast.

İlk kare ayrıca **hareketli** olmalı ve üstünde bir vuruş sesi bulunmalı.
Durağan, sessiz açılış kaydırma oranını yükseltiyor.

### Girişte yasak

`Merhaba`, `Bugün size`, `Bu videoda`, `Biliyor muydunuz` — hepsi zaman
harcar ve hiçbir vaat taşımaz. Olayın ortasından başla.

## 6. ElevenLabs'e hazır olma kuralları

Kullanıcı metni **kopyalayıp yapıştıracak**. Aşağıdakiler seslendirmede bozulur:

| Yazma | Yaz |
|---|---|
| `%90` | `yüzde doksan` |
| `30'u` | `otuzu` |
| `2024` | `iki bin yirmi dört` |
| `vb.`, `örn.`, `yy.` | açık yaz |
| `(parantez içi)`, `*vurgulu*` | yazma — sesli okunur |
| `[whispers]` gibi ses etiketleri | **sadece v3'te** — aşağıya bak |
| `BÜYÜK HARF` | normal yaz, vurgu için cümleyi kısalt |
| `emoji` | yazma |

**Noktalama tempoyu belirler:** nokta tam duraklama, virgül kısa nefes, üç nokta
dramatik bekleme. Bu format duraklama istemez — **nokta kullan, üç noktayı seyrek kullan.**

Metni tek blok halinde ver. Başlık, madde işareti, açıklama ekleme — yapıştırılan
her karakter seslendirilir.

### Ses etiketleri — model sürümüne bağlı

**Eleven v3** köşeli parantezli ses etiketlerini yönerge olarak yorumlar:
`[whispers]`, `[curious]`, `[excited]`, `[nervous]`, `[sad]`, `[angry]`,
`[sarcastic]`, `[laughs]`, `[sighs]`, `[gasps]`.

**v2, Turbo ve Multilingual v2 bunları desteklemez — sesli okur.** Kullanıcı hangi
modeli kullandığını söylemediyse **iki sürümü birden ver**: etiketli ve etiketsiz.
Yanlış modelde etiketli metin sesi tamamen bozar.

Kurallar:

- Etiketler **İngilizce** yazılır, metin Türkçe olsa bile
- Cümlenin **başına** konur, ortasına değil
- `[whispers]`, `[curious]`, `[excited]` güvenilir; `[urgent]`, `[softly]`, `[warmly]`
  gibi standart dışı olanlar yok sayılabilir — tutmazsa silinir, cümle bozulmaz
- Her cümleye etiket koyma; tonlama düzleşir. İniş çıkış yaratacak yerlere koy.

**Süreyi etkiler.** Etiketler seslendirilmez, kelime sayısı değişmez; ama heyecanlı
okuma hızlanır, fısıltı yavaşlar. 2.18 kelime/saniye tahmini ±%10 kayabilir —
ses geldiğinde gerçek süreyi ölç, kurguyu ona göre kur.

Tonlama yayı: fısıltıyla aç, merakla kur, ortada yükselt, dönüş anında düşür,
kapanışta tekrar fısıltıya in.

## 7. Tek kelimelik altyazıya uygunluk

Her kelime ayrı ekranda görünecek. Kart genişliği sınırlı:

- **14 harften uzun kelimelerden kaçın** — karta sığmaz veya küçülür
  (`değerlendirilmesi`, `gerçekleştirilebilir`)
- Kısa ve vurgulu kelimeler seç: `durdu`, `bitti`, `kimse`, `hiçbir`
- Aynı kelimeyi arka arkaya tekrarlama, ekranda takılı kalmış gibi durur

## 8. Özgünlük

Metin **tamamen senin ürettiğin** olmalı: kaynak videonun altyazısını çevirme,
cümle sırasını kopyalama. Kendi açını kur — farklı giriş, farklı vurgu, farklı sonuç.

Kurgu tarafında da özgünleştirme yapılır: yeniden kesim, kadraj değişikliği, renk,
tempo, orijinal altyazı ve watermark'ın kaldırılması, sıralamanın değişmesi.

> Bunlar **sunumu** değiştirir. Kaynak görüntünün telif hakkı yine sahibindedir ve
> platformların özgünlük filtreleri görsel içeriğe bakar. Kullanıcı bunu biliyorsa
> karar onun; sen işi yap ve gerekirse bir cümleyle hatırlat, tartışmaya girme.

## 9. Teslim biçimi

İki şey ver:

1. **Yapıştırılacak metin** — tek blok, temiz, başka hiçbir şey içermeyen
2. Altında ayrı olarak: kelime sayısı, tahmini süre, hangi cümlenin hangi görüntüye
   denk geleceği

Metni kod bloğu içinde ver ki kopyalaması tek hareket olsun.
