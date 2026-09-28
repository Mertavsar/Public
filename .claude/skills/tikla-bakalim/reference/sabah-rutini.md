# Sabah rutini — her sabah bir bölüm, ses gelince final video

Bu dosya zamanlanmış rutin (claude.ai → Routines) her sabah çalıştığında
izlenecek sıradır. Rutin her seferinde **yeni bir oturum** açar; oturum
kullanıcı sesi yükleyene kadar açık kalır. Kullanıcı sabah oturumu açar,
metni ElevenLabs'a yapıştırır, sesi aynı oturuma yükler; final video o
oturumda çıkar.

```
SABAH (rutin, kullanıcı uyurken)            KULLANICI                 AYNI OTURUM
1 ortamı hazırla                             metni okur/düzeltir        6 sesi kontrol et
2 gündemi tara → 3 aday → 1 seç              ElevenLabs'ta seslendirir  7 final render
3 araştır (kaynak tablosu)                   mp3'ü oturuma yükler       8 teslim
4 metni yaz (etkileşim cümleleri dahil)
5 bolum.json + kareler + kapak → teslim, commit
```

---

## 1. Ortam

```bash
which ffmpeg || (apt-get update -q && apt-get install -y -q --no-install-recommends ffmpeg)
python3 -c "import numpy, scipy" || pip install -q numpy scipy
```

Ortamın kurulum betiği (setup script) bunu zaten yapıyorsa atlanır.
Kurulum başarısız olursa dur ve kullanıcıya hangi komutun düştüğünü yaz.

## 2. Konu

**Tür: YouTube uzun video (yatay, 3–5 dk).** Kanalın vaadi: *insanların merak
ettiği ama karmaşık olduğu için anlamadığı gündem.*

Tara:
- Google Trends (`trends.google.com/trending/rss?geo=TR`) — ağda açıksa önce bu.
- `WebSearch`: `"<bugünün tarihi> gündem"`, `"<tarih> ekonomi son dakika"`,
  `"<tarih> en çok aranan"`, `"<tarih> teknoloji gündem"`.
- Son 7 günde `tikla-bakalim/bolumler/` altında işlenen konuları **tekrar seçme**.

Üç aday çıkar, her birine 1–5 puan ver:

| Ölçüt | Soru |
|---|---|
| Merak × zorluk | Herkes konuşuyor ama "tam olarak ne oldu" bilmiyor mu? (en önemli) |
| Cebe dokunma | Sıradan birinin parasına, gününe, telefonuna dokunuyor mu? |
| Görsel | Sayı, karşılaştırma, mekanizma var mı? (animasyonun yakıtı) |
| Ömür | Bir hafta sonra da izlenir mi? (arama trafiği) |
| Kaynak | Rakamları iki bağımsız kaynakta doğrulanabiliyor mu? |

En yüksek puanlıyı seç. Siyasi polemik, suç haberi, kişiler hakkında iddia,
sağlık tavsiyesi → **seçme** (kanıt disiplini, SKILL.md §2).

## 3. Araştırma

SKILL.md Tur 2. Kaynak tablosu önce (`K1 … — url`), her sayı en az iki
kaynakta. Kesinleşmemiş olan "bekleniyor / tahmini". Tarihi yaz.

## 4. Metin

`reference/kimlik.md` dil kuralları + **Etkileşim cümleleri** bölümü (zorunlu).

- Uzunluk: **800–1100 hece** (≈ 3–4 dk). Yapı: hook → ne oldu → neden oldu →
  bizi nasıl etkiler → kapanış. Her cümle bir sahne, cümle ≤ 12 kelime.
- Seste rakam yok ("seksen lira"); ekranda rakam için `altyazi` eşlemesi.
- Etkileşim cümleleri metnin **içinde**, kendi sahneleriyle (aşağıda).

## 5. Bölüm dosyası ve teslim

Klasör: `tikla-bakalim/bolumler/<YYYY-AA-GG>-<kisa-konu>/`

1. `bolum.json` — `"format": "yatay"`, `"durum": "ses bekliyor"`, sahneler,
   `altyazi`, `vurgu`, `kapak`, `kaynaklar`, ve orta etkileşim cümlesine denk
   gelen `cta` (`{"sahne": N, "gecikme": 0.3, "sure": 5.5}` — N o cümlenin sahnesi).
2. `python3 .claude/skills/tikla-bakalim/scripts/render.py --bolum <bolum.json> --kareler`
   → **her kareyi aç ve bak**, taşma/çakışma varsa düzelt, tekrar çalıştır.
3. Kapak: `--kareler` kapak üretmez; tek kare için kapak zaman çizelgesiyle
   `capture.mjs --cover` (render.py'deki 6/7 adımı) ya da tam taslak render.
   Sabah tam taslak video **üretme** — ses gelmeden zamanlama tutmaz, 15–20 dk yer.
4. `metin.txt` (render.py yazar: `cikti/metin.txt`) — bölüm klasörüne de kopyala:
   `tikla-bakalim/bolumler/<…>/metin.txt`.
5. Commit + push (`cikti/` git dışı). Kareler kontak sayfasını ve kapağı
   kullanıcıya dosya olarak gönder.

### Sabah mesajı — bu biçimde, bu sırayla

```
## Bugünün konusu: <konu>
Neden bu: <tek cümle — merak × zorluk>
(Diğer adaylar: <aday 2>, <aday 3> — istersen onlarla değiştiririm)

## ElevenLabs metni (aynen yapıştır)
<metin.txt — paragraf = sahne>

Ayarlar: Türkçe ana dilli ses · speed 1.0 · stability 65–70 · similarity 75
Tahmini süre: ~X dk

## Başlık önerileri
1. <sayısız, merak uyandıran>   ← önerim
2. <sayısız>
3. <aramaya dönük, anahtar kelimeli>

## Açıklama (kopyala)
<2–3 cümle + kaynak notu + etkileşim cümlesi + 5 hashtag>

## Kaynaklar
<K1 … markdown link>

➡ Sesi bu sohbete yükle, videoyu altyazısıyla çıkarayım.
```

## 6–8. Ses geldiğinde (aynı oturum)

1. Sesi `bolumler/<…>/ses/vo.mp3` olarak kaydet. Kontrol: süre, tepe/kırpılma
   (viral-edit voice-settings §4), LUFS.
2. `render.py … --vo ses/vo.mp3 --kareler` → `sentalign` çıktısında
   `ŞÜPHELİ HIZ` varsa kullanıcı metni değiştirmiş demektir: farkı bul,
   `bolum.json`'u sese uydur (sesi değil).
3. Final: `render.py --bolum <…> --vo <…>` — müzik/efekt **sadece rutin
   talimatında veya kullanıcı mesajında isteniyorsa** (`--muzik etkili --efekt`).
   Kullanıcı "boşluksuz" istediyse `--sikistir`.
4. `kontrol.jpg`'i aç, bak. Videoyu ve `kapak_youtube.jpg`'i gönder.
   `bolum.json` → `"durum": "yayına hazır"`, ses dosyasıyla commit + push.

Sorun çıkarsa (hizalama tutmuyor, kırpık ses) videoyu gönderme; sorunu ve
çözümü tek paragrafta yaz.
