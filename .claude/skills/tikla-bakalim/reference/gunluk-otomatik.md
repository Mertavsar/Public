# Günlük otomatik video — konu → format → ses → video → kapak

Zamanlanmış rutin her sabah bunu uçtan uca yapar; kullanıcı uyanınca hazır
video bulur. (Eski akış — metin + kareler, ses kullanıcıdan — sabah-rutini.md;
vidIQ kredisi bittiğinde ona düşülür, aşağıda §5.)

```
1 ortam  →  2 gündem tarama + rakip sinyali  →  3 konu (1 tane)  →  4 format (format-secimi.md)
→  5 araştırma + metin  →  6 bolum.json + kareler (her kareye bak)  →  7 ses (vidIQ)
→  8 final render (--sikistir)  →  9 Reels kapağı  →  10 commit/push + teslim mesajı
```

## 1. Ortam
`git fetch origin claude/viral-video-editing-n4kvkh && git checkout claude/viral-video-editing-n4kvkh && git pull`
ffmpeg, numpy/scipy (`python3 -m pip`). Chromium + Playwright hazır; 3D için WebGL
(SwiftShader) `capture.mjs`'de açık.

## 2. Gündem tarama
- `WebSearch` (mode extended): `"<tarih> breaking news"`, `"<tarih> gündem son dakika"`,
  `"<tarih> ekonomi"`, `"<dün tarihi> news"`. Haber sitelerinin çoğu WebFetch'e kapalı;
  iki bağımsız arama sonucunda aynı sayıyı ara.
- **Rakip sinyali (vidIQ, 10 kredi):** `vidiq_ig_profile_reels` → `bpthaber` ve
  `onediocom`. Son 48 saatte 1M+ izlenme veya 500+ yorum alan konular sıcaktır.
  Kredi < 40 ise bu adımı atla (ses kredisini koru).
- Son 7 günde `tikla-bakalim/bolumler/` altında işlenmiş konuyu seçme.

## 3. Konu seçimi
sabah-rutini.md §2 puan tablosu + rakip sinyali (sıcaklık) + **görsellik**.
Tek konu seç. Siyasi polemik / suç iddiası / sağlık tavsiyesi seçme.

## 4. Format
`reference/format-secimi.md` tablosu. Gerekiyorsa yeni 3D/çizim dünyası yaz
(engine/siklon3d.js, engine/cizim.js örnek). 30 dk'yı aşacaksa 2D'ye düş.

## 5. Araştırma ve metin
SKILL.md Tur 2 + kimlik.md. Dikey: **150–200 kelime** (≈ 60–75 sn ses).
Kaynak tablosu (K1…), her sayı iki kaynakta. Seste rakam yok, `altyazi` eşlemesi.
Hook ilk cümle (tek şok bilgi), 2. cümle merak ("Peki neden? …").

## 6. bolum.json + kareler
`render.py --bolum … --kareler` → **her kareyi Read ile aç**, taşma/çakışma düzelt.

## 7. Ses (vidIQ)
1. `vidiq_balance` → `totalCredits`. Gerekli: `ceil(karakter/1000) × 14` (~28).
2. Yeterliyse `vidiq_voiceover_generate` (voiceId `onwK4e9ZLuTAKqWW03F9`, metin =
   `cikti/metin.txt` birebir) → `vidiq_job_poll` → mp3'ü indir →
   `ses/vo_yapayzeka.mp3`, `ffmpeg -af atempo=1.1 → ses/vo.wav`.
3. **Yetersizse:** ses üretme. Sessiz taslak + metin + kareler teslim et
   (sabah-rutini.md mesajı), mesajda "vidIQ kredisi bitti — sesi yükle ya da
   kredi ekle" yaz. Dur.

## 8. Final
`render.py --bolum … --vo ses/vo.wav --sikistir` (müzik/efekt yok, kullanıcı
istemedikçe). Çıktıda `ŞÜPHELİ HIZ` varsa ilgili cümleyi kontrol et. Videonun
6 sn'de bir karesinden kontak sayfası çıkar, bak.

## 9. Reels kapağı
Videodan temiz bir arka plan karesi (`capture.mjs --still … --cover`, üst yazı
yok) → `tikla-bakalim/markalama/reels/foto/` → `kapaklar.json`'a ekle →
`node scripts/reels_kapak.mjs kapaklar.json`.

## 10. Teslim
Commit + push. Kullanıcıya **tek mesaj**:
```
## Bugünün videosu: <konu>   (format: <3D / çizim / 2D / foto> — neden: <tek cümle>)
[video.mp4] [kapak]
Başlık önerileri: 1 … ← önerim · 2 … · 3 …
Açıklama (kopyala): <2–3 cümle + kaynaklar + 5 hashtag>
Rakip sinyali: <bpt/onedio'da bu konu kaç izlenme aldı>
Kontrol et: <canlı haberse "yayından önce son durumu kontrol et">
vidIQ kredisi: <kalan>
```
Video ve kapağı `SendUserFile` ile gönder.
