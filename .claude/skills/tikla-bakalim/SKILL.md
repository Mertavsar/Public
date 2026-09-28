---
name: tikla-bakalim
description: Tıkla Bakalım kanalı için gündem anlatım videosu (dikey, animasyonlu, 45–60 sn). "Gündemden video yap", "şu konuyu anlat", "Google Trends'te ne var", "Tıkla Bakalım videosu", "bu haberi basitçe anlat", "animasyonlu anlatım", "ne oldu neden oldu" dendiğinde kullan. Konu önerir, kaynaklı araştırır, ne oldu / neden oldu / bizi nasıl etkiler metnini TASLAK olarak yazar, sahne planını (bolum.json) kurar ve animasyonu sıfırdan render eder. Ham klip kurgusu bu skill değil — o viral-edit.
---

# Tıkla Bakalım — Gündem Anlatım Videosu

> Gündemde herkes konuşuyor ama kimse düzgün anlatmıyor.
> **Ne oldu, neden oldu, bizi nasıl etkiliyor?** Karmaşık terim yok, uzatma yok.

Kaynak görüntü yok. Her kare kodla çizilir: sayaçlar, grafikler, karşılaştırmalar,
sebep–sonuç zincirleri. Kullanıcı sadece seslendirmeyi getirir.

`viral-edit`'ten farkı: orada kullanıcının klibi kurgulanır ve metni kullanıcı yazar
(kareden hikâye çıkarılamaz). Burada metin **kaynaklardan** çıkar. O yüzden taslağı
sen yazarsın, ama kullanıcı onaylamadan ses ürettirilmez (§2).

---

## Dosyalar

| Dosya | İş |
|---|---|
| `scripts/render.py` | **Giriş noktası.** bolum.json → video, kapak, kontrol sayfası |
| `scripts/capture.mjs` | Chromium'da kare kare yakalama (render.py çağırır) |
| `engine/engine.js` | Animasyon motoru + sahne tipleri. Deterministik: `seek(t)` |
| `engine/style.css` | Görsel kimlik: renkler, font, yerleşim |
| `reference/sahneler.md` | **Her sahne tipinin parametreleri** — bolum.json yazarken aç |
| `reference/kimlik.md` | Kanal tonu, dil kuralları, görsel kimlik ölçüleri |
| `tikla-bakalim/bolumler/*/bolum.json` | Bölümler (repo kökünde). İlk örnek: `2026-09-30-esel-mobil` |

Ses zinciri (hizalama, efekt, müzik, master) `viral-edit/scripts`'ten gelir:
`align.py`, `audiobed.py`, `master.py`. Oradaki ölçümler burada da geçerli.

---

## 1. Akış — dört tur

```
TUR 1  KONU        gündemi tara → 3 aday öner → kullanıcı seçer
TUR 2  METİN       araştır, kaynak tablosu + metin taslağı → kullanıcı onaylar/düzeltir
TUR 3  TASLAK      bolum.json + sessiz taslak video (tahmini zaman) → kullanıcı akışa bakar
TUR 4  FİNAL       kullanıcı ElevenLabs sesini atar → --vo ile render, kapak, kontrol
```

Kullanıcı konuyu kendisi verdiyse Tur 1 atlanır. Metni kendisi verdiyse Tur 2'de
sadece kaynak kontrolü yapılır.

### Tur 1 — Konu

Google Trends (`trends.google.com`) bu ortamın ağ politikasında kapalı olabilir.
Önce dene; kapalıysa:

- `WebSearch`: `"gündem <tarih>"`, `"en çok aranan <tarih>"`, `"<tarih> son dakika ekonomi"`
- veya kullanıcıdan Trends listesinin ekran görüntüsünü / metnini iste.

Üç aday öner. Her biri için tek satır:

| Ölçüt | Soru |
|---|---|
| Dokunma | Sıradan birinin cebine, gününe, telefonuna dokunuyor mu? |
| Kafa karışıklığı | İnsanlar konuşuyor ama "tam olarak ne oldu" bilmiyor mu? |
| Görsel | Bir sayı, karşılaştırma veya mekanizma var mı? (animasyonun yakıtı) |
| Süre | 60 saniyede üç soru cevaplanır mı? |

Siyasi polemik, suç haberi, kişiler hakkında iddia → **önerme**. Kanalın işi
açıklamak, taraf tutmak değil.

### Tur 2 — Araştırma ve metin

**Kaynak tablosu önce, metin sonra.** Her sayı bir kaynağa bağlanır:

```
K1  Eşel mobil 30 Eylül gecesi bitiyor          — cumhuriyet.com.tr/...
K2  Benzin +12,48 TL (ÖTV 10,40 + %20 KDV)       — yatirimx.com.tr/... ; t24.com.tr/...
```

- Sayıyı **en az iki kaynakta** gör. `WebSearch` özeti ikincil kaynaktır — mümkünse
  haberin kendisini `WebFetch` ile aç (Türk haber sitelerinin çoğu ağda kapalı;
  kapalıysa iki bağımsız arama sonucunda aynı sayıyı ara).
- **Kesinleşmemiş** bilgi kesin dille söylenmez: "gelecek" değil "gelebilir",
  ekranda "(tahmini)".
- Tarihi yaz. Gündem videosu bir hafta sonra yanlış olabilir.

Metin yapısı — her cümle bir sahne:

| Bölüm | Süre | İş |
|---|---|---|
| `hook` | 0–7 sn | Tek şok bilgi (sayı!) + "Peki neden? Üç soruda anlatayım." |
| `ne` | ~12 sn | Ne oldu: tarih, sayı, önce/sonra |
| `neden` | ~20 sn | Mekanizma. Terimi **bir cümlede** sadeleştir, sonra göster |
| `etki` | ~15 sn | Senin cebine/gününe etkisi. Somut hesap (bir depo, bir ay, bir fatura) |
| `kapanis` | ~3 sn | "Merak ettiysen, tıkla bakalım. Takip et." |

Dil kuralları `reference/kimlik.md`'de. En önemlileri: cümle 12 kelimeyi geçmez,
terim açıklanmadan kullanılmaz, **seslendirmede rakam yok** (sayılar yazıyla:
"seksen lira"). Ekranda kesin sayı (80,40 ₺), seste yuvarlak (seksen lira).

Hedef **220–250 hece** (≈ 50–58 sn). `render.py` süreyi ve sahne başına tempoyu basar.

Taslağı kullanıcıya **kaynak tablosuyla birlikte** göster ve onay iste. Onaylanmamış
metinle ses ürettirme.

### Tur 3 — bolum.json ve taslak video

Şablon: `tikla-bakalim/bolumler/2026-09-30-esel-mobil/bolum.json`. Kopyala, değiştir.

```json
{
  "baslik": "...", "tarih": "YYYY-AA-GG",
  "vurgu": ["zam", "fırladı"],
  "kapak": { "ikon": "⛽", "ust": "BENZİNE", "buyuk": "+12,48 ₺", "alt": "NEDEN?" },
  "sahneler": [
    { "bolum": "hook", "tip": "sayi", "say": "Seslendirme cümlesi.", "p": { ... }, "kaynak": "K2" }
  ],
  "kaynaklar": { "K1": "açıklama — url" }
}
```

| Alan | Anlam |
|---|---|
| `bolum` | `hook` / `ne` / `neden` / `etki` / `kapanis` — üstteki bölüm şeridini sürer |
| `tip` | Sahne tipi (aşağıda) |
| `say` | Bu sahnede okunan cümle. Sahne süresi buna oturur. Rakam yok. |
| `p` | Sahnenin görsel parametreleri — `reference/sahneler.md` |
| `kaynak` | Ekranın altında küçük "Kaynak: …" satırı |
| `sure` | Sadece `say` boşsa (sessiz son sahne) |
| `vurgu` | Altyazıda kırmızı kelimeler (3–5). Sayılar kendiliğinden sarı. |

Metin içi renk: `*sarı*` `~kırmızı~` `+yeşil+`, satır sonu `\n`.

**Sahne tipleri** (ayrıntı: `reference/sahneler.md`)

| Tip | Ne zaman |
|---|---|
| `sayi` | Tek çarpıcı sayı. Sayarak büyür, yön oku. Hook için ideal (`sayma:false`) |
| `karsilastir` | Önce / sonra, bugün / yarın. Sıfırdan başlayan dürüst ölçek |
| `liste` | 2–4 kalem: ikon + ad + değer |
| `akis` | Sebep → sonuç zinciri, 2–4 adım, sırayla yanar |
| `yigin` | Bir bütünün parçaları ve değişimi (fiyatın içi: maliyet + vergi) |
| `grafik` | Zaman içinde değişim (altın, dolar, enflasyon) |
| `hesap` | "50 litre × 12,48 ₺ = 624 ₺" — etkiyi somutlaştırır |
| `takvim` | Son tarih, yürürlük günü |
| `baslik` | Büyük ikon + 2–4 satır. Terim tanımı, bölüm vurgusu |
| `soru` | "Peki neden?" geçişi |
| `kapanis` | Kanal adı + takip çağrısı |

Önce hızlı kareler, sonra taslak video:

```bash
python3 .claude/skills/tikla-bakalim/scripts/render.py --bolum <bolum.json> --kareler   # ~10 sn
python3 .claude/skills/tikla-bakalim/scripts/render.py --bolum <bolum.json>             # ~5 dk / 60 sn video
```

`--kareler` her sahneden bir kare çıkarır (`cikti/kareler/`). **Her kareyi Read ile
aç ve bak**: taşan yazı, üst üste binen öğe, yanlış sayı. Video render etmeden önce
düzelt — 5 dakikalık render'ı taşan bir etiket için tekrarlama.

Taslak video sessizdir (sadece müzik + efekt), zamanlama hece sayısından tahmindir.
Kullanıcı akışı ve görselleri onaylasın; zamanlama ses gelince oturur.

### Tur 4 — Final

Kullanıcı sesi atar (ses seçimi ve ayarlar: `viral-edit/reference/voice-settings.md`).
Metin `cikti/metin.txt`'te — ElevenLabs'a birebir bu metin girilmeli, yoksa hizalama kayar.

```bash
python3 .claude/skills/tikla-bakalim/scripts/render.py --bolum <bolum.json> --vo ses.mp3
```

Çıktılar `cikti/` altında: `video.mp4`, `kapak.png`, `kontrol.jpg` (her sahneden
bir kare), `cizelge.json` (sahne zamanları), `metin.txt`.

---

## 2. Kanıt disiplini

Bu kanalın tek sermayesi güven. Bir yanlış sayı yorumlarda videoyu bitirir.

1. **Kaynaksız sayı ekrana çıkmaz.** `kaynaklar` boşsa `render.py` durur.
2. **Beklenti ≠ gerçekleşen.** "bekleniyor", "tahmini", "gelebilir" ekranda da seste de.
3. **Temsili grafik etiketlenir.** Gerçek oranı bilmediğin `yigin` sahnesi
   "temsili" yazısıyla çıkar (varsayılan). Temsili çubuğa gerçek sayı yazma.
4. **Yorum haber gibi sunulmaz.** "Market fiyatlarına yansır" değil "yansıyabilir".
5. **Siyasi dil yok.** Kararı veren kurumu söyle, kararı yargılama.
6. **Metin kullanıcı onayından geçer.** Sen taslaklarsın; ses üretimi onaydan sonra.

---

## 3. Kalite kontrol (render.py otomatik yapar)

| Kontrol | Eşik | Neden |
|---|---|---|
| Bölüm sırası | ne → neden → etki | Formatın omurgası |
| Seslendirmede rakam | uyarı | ElevenLabs okuyuşu + hece sayımı bozulur |
| Sahne tempo | 5 sn'den uzun durağan ekran | İzleyici kaydırır |
| Toplam süre | > 75 sn uyarı | Shorts hedefi 45–60 sn |
| Ses | −14 LUFS, tepe < 0 dBFS | viral-edit master zinciri |
| Süre eşleşmesi | video = çizelge ± 0.2 sn | |

Elle kontrol: `kontrol.jpg`'i aç. Her karede ana mesaj 1 saniyede okunuyor mu?

---

## 4. Motor hakkında

- Her kare `seek(t)` ile kurulur; CSS animasyonu, zamanlayıcı yok. Aynı `t` her
  zaman aynı kareyi verir → 4 paralel parça, tek kare önizleme.
- Arka plan sürekli hareket eder (kayan ışık lekeleri + ızgara) — hiçbir kare
  tamamen durağan değil.
- Yerleşim (1080×1920): bölüm şeridi 150–280, sahne 310–1240, altyazı 1270–1430,
  kaynak 1440. **1480 altı** Shorts/Reels arayüzünün (başlık, açıklama) altında
  kalır — oraya bilgi koyma.
- Yeni sahne tipi: `engine.js`'te `SCENES.yeni = (p, r) => (lt, d) => {...}`.
  `lt` sahne içi zaman, `d` sahne süresi. Girişler `pop`/`slide`, sıralama `stagger`.
  Sonra `reference/sahneler.md`'ye ekle.
- İkonlar Noto Color Emoji. Fotoğraf, harita, logo yok (henüz).

## 5. Bilinen sınırlar

- **Google Trends ağda kapalı olabilir** → Tur 1'deki yedek yol.
- **TTS yok.** Taslak sessiz; ses kullanıcıdan gelir.
- Render ~5 dk / 60 sn (4 çekirdek). Önce `--kareler`.
- Hizalama ASR'siz (hece tepesi). `LPG`, `ÖTV` gibi kısaltmalar hece sayımını
  şaşırtabilir — seslendirmede okunduğu gibi yaz ("elpiji") ya da ekranda bırak.
