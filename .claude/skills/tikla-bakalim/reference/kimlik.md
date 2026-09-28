# Tıkla Bakalım — kanal kimliği

## Vaat

> Gündemde herkes konuşuyor ama kimse düzgün anlatmıyor mu?
> Tıkla Bakalım'da Türkiye ve dünyada gündem olan olayları, ekonomi ve teknoloji
> gelişmelerini, internetin konuştuğu konuları ve merak uyandıran hikâyeleri basit,
> anlaşılır ve görsel bir dille anlatıyoruz.
> Karmaşık terimler yok. Gereksiz uzatma yok.
> **Ne oldu, neden oldu, bizi nasıl etkiliyor?**
> Merak ettiysen, tıkla bakalım. 👆

Her video bu üç soruyu **bu sırayla** cevaplar. Ekranın üstündeki üç parçalı
şerit ("1 · NE OLDU?" → "2 · NEDEN OLDU?" → "3 · BİZİ NASIL ETKİLER?") izleyiciye
nerede olduğunu ve daha ne kadar kaldığını gösterir — açık döngü. Üçüncüyü görmeden
kaydırmak zor.

## Dil

| Kural | Örnek |
|---|---|
| Cümle ≤ 12 kelime | "Devlet, zam pompaya yansımasın diye vergiyi düşürdü." |
| "Sen" dili, sohbet tonu | "Deponu doldurursan…", "Merak ettiysen…" |
| Terim bir kez, hemen açıklanır | "Sebep eşel mobil. Adı karışık, mantığı basit." → sonra göster |
| Seste yuvarlak, ekranda kesin | ses: "seksen lira" · ekran: 80,40 ₺ |
| Seste rakam yok | "on iki buçuk" — ElevenLabs ve hece sayımı için |
| Kesin değilse kesin konuşma | "gelebilir", "bekleniyor", "(tahmini)" |
| Somut etki | "yüzde 15" değil "bir depo 624 lira daha pahalı" |
| Yasak | "Şok!", "Bomba!", "Herkes yanılıyor" — gündem kanalında güveni yer |

Hook tek bilgi taşır ve bir **sayı** içerir. Soru ile açılan hook ikinci cümle
olur: "Peki neden? Üç soruda anlatayım."

## Etkileşim cümleleri — metnin içine giydirilir (kullanıcı kuralı)

Her metinde **üç** etkileşim anı var. Reklam gibi değil, anlatının parçası gibi:
bir önceki cümleye bağlanır, izleyiciye bir sebep verir. Her biri kendi
sahnesinde (`baslik` veya `soru` tipi, büyük ikon: 🔔 / ❤️ / 💬).

| Yer | Amaç | Örnek kalıplar (her videoda değiştir, aynısını tekrarlama) |
|---|---|---|
| **Hook'tan hemen sonra** (ilk ~20 sn) | Abone | "Bu tür konuları basitçe anlatıyoruz; kaçırmamak için abone ol." · "Gündemi her gün sade dille anlatıyoruz, abone olmayı unutma." |
| **Ortada, en ilginç kısmın başında** (`cta` kartı buraya) | Beğen | "Asıl ilginç kısım şimdi geliyor. Buraya kadar işine yaradıysa bir beğen bırak." · "Videoyu beğenirsen daha çok kişiye ulaşıyor; kalbe dokunmayı unutma." |
| **Kapanışta** | Yorum + abone | "Öğrenmek istediğin başka bir konu varsa yorumlara yaz; bir sonraki videoda biz anlatalım." · "Sen ne düşünüyorsun? Yorumlarda buluşalım. Merak ettiysen, tıkla bakalım." |

Kurallar:
- Toplam etkileşim süresi metnin **%8'ini** geçmez; her biri tek, en fazla iki cümle.
- İlk 5 saniyede etkileşim cümlesi **yok** — hook bozulmaz.
- Kapanış her zaman "Merak ettiysen, tıkla bakalım." ile biter (kanal imzası).
- Orta cümle `bolum.json`'daki `cta` kartıyla aynı sahneye denk gelir.

## Görsel

| Öğe | Değer |
|---|---|
| Tuval | yatay 1920×1080 (varsayılan, altın videosu) · dikey 1080×1920 — 30 fps |
| Zemin | lacivert radyal (`#13294a` → `#0b1626`), kayan renkli ışık lekeleri, ince ızgara |
| Font | Montserrat 600/800/900 (OFL, `engine/fonts/`) |
| Vurgu | sarı `#ffc83d` (ana), kırmızı `#ff4d5e` (artış/zarar), yeşil `#2ee59d` (düşüş/iyi) |
| İkinci renkler | mavi `#4db8ff`, turuncu `#ff9b3d`, mor `#b58cff` |
| Altyazı | yatay: alt satır, 42 px, koyu hap zemin, konuşulan kelime altın · dikey: tek kelime 96 px, kontur |
| Geçiş | sahne→sahne: 0.35 sn çözülme (eski bulanıklaşıp yukarı söner, yeni 0.08 sn sonra gelir) · bölüm başı: koyu panel + "2 · NEDEN OLDU?" kartı, ~1 sn |
| Güvenli alan | dikey: bilgi 150–1450 arası; 1480 altı platform arayüzü |
| İkon | Noto Color Emoji |

Renk anlamı sabit: **kırmızı = cebimizden çıkan**, yeşil = lehimize, sarı = dikkat/vurgu.
Bir videoda anlamı değiştirme.

## Ses

Varsayılan **sadece seslendirme** — kullanıcının kuralı: efekt ve müziği o ekler.
İsterse `--muzik` / `--efekt`: müzik ölçülerek seslendirmenin 21 LU altında,
efekt yalnız bölüm geçişi + abone/beğen tıkı. Seslendirme ayarları: `viral-edit/reference/voice-settings.md`
(Türkçe ana dilli ses, speed 1.0, stability 65–70).
