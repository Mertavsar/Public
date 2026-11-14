---
name: format-kopyala
description: Beğenilen bir Shorts/Reels'in formatını analiz edip aynı formatta yeni konu için animasyon üretir. Kullanıcı bir video (dosya veya link) atıp "bunu analiz et", "bu formatta yap", "buna benzer video yap", "şu videodaki gibi ama X konusunda" dediğinde kullan. Çıktı: format kartı → yeni konunun planı → 3 stil karesi (onay) → Lemo-Opuscar (veya Tıkla Bakalım motoru) ile 1080×1920 animasyon. Yapıyı ve tempoyu öğrenir; karakter, çizim, müzik ve birebir sahne KOPYALAMAZ.
---

# Format Kopyala — "bu Shorts'un formatında, şu konuyu yap"

Girdi: **örnek video** (tercihen kullanıcının attığı dosya / ekran kaydı; link verilirse aşağıya bak) + **yeni konu**.
Kullanıcı tek mesajda ikisini verir. Eksik varsa tek mesajda sor, sonra durmadan ilerle.

## 1. Videoyu al
- **Dosya geldiyse** onu kullan (en temiz yol).
- **Link geldiyse:** önce vidIQ (`vidiq_video_transcript`, `vidiq_video_stats`, gerekirse `vidiq_watch_shortform_content`) —
  kredi harcayan çağrılardan önce kullanıcıya maliyeti söyle. İndirme (yt-dlp) gerekiyorsa kullanıcıya YouTube kurallarının
  başkasının videosunu indirmeye izin vermediğini bir satırla söyle; onaylarsa sadece analiz için indir, analizden sonra sil,
  hiçbir parçasını yeni videoda kullanma.

## 2. Ölç (tahmin etme)
```sh
mkdir -p ornek/kare
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of json ornek.mp4
ffmpeg -i ornek.mp4 -vf fps=2,scale=360:-1 ornek/kare/%04d.jpg                  # 0,5 sn'de bir kare
ffmpeg -i ornek.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep pts_time   # kesme anları
ffmpeg -i ornek.mp4 -af ebur128 -f null - 2>&1 | tail -12                          # ses seviyesi
```
Sesi Whisper ile yazıya çevir (kelime zamanlı). Kareleri 4×4 kontak sayfası yapıp **gerçekten bak** (Read).

## 3. Format kartı (`FORMAT.md`) — tablo halinde
| Alan | Ne yazılır |
|---|---|
| Süre, en-boy, fps | ölçülen |
| Hook (0–2 sn) | ilk kare ne gösteriyor, ilk cümle ne diyor, neden durduruyor |
| Yapı | bölümler ve saniyeleri (ör. soru → 3 adım → ters köşe → soru ile kapanış) |
| Kesme temposu | ortalama çekim süresi, en kısa/en uzun, hızlanma/yavaşlama anları |
| Kamera dili | yaklaşma, uzaklaşma, kaydırma, sarsıntı, ölçek açılışı — hangi anda |
| Görsel dil | stil, palet, karakter var mı, yazı/altyazı tasarımı ve konumu |
| Ses | ses tonu ve hızı (hece/sn), müzik türü, efektler, sessizlikler |
| Etkileşim tetikleri | soru, sayaç, "bekle…", döngü (son → baş) |
| **Alınacaklar** | yapı, tempo, hook kalıbı, kamera dili, ses kullanımı |
| **Alınmayacaklar** | karakterler, çizimler, logo, müzik, birebir sahneler, cümleler |

## 4. Yeni konuya uyarla
- Yeni konunun her bilgisini iki bağımsız kaynakla doğrula; `KAYNAKLAR.md`. Doğrulanamayan metne girmez.
- Format kartındaki yapıyı **saniye saniye** yeni konuya eşle (aynı bölüm süreleri, aynı kesme temposu, hook kalıbı aynı ama
  içerik yeni). Metni Türkçe yaz; sayılar seste yazıyla, altyazıda rakamla.
- Stil seç: örnek videonun görsel diline en yakın **Lemo-Opuscar** stili (`styles/README.md`) — birebir kopya değil,
  aynı ailedeki stil. Uygun stil yoksa Tıkla Bakalım motoru (`.claude/skills/tikla-bakalim/`).

## 5. Onay — sonra üret
Kullanıcıya göster: format kartı (kısa), yeni metin, saniye saniye akış, **3 stil karesi** (gerçek çizim koduyla). Onay gelince:
- Lemo-Opuscar: `/lemo-opuscar:lemo-opuscar` — DIRECTOR.md + TECHNIQUE.md + seçilen STYLE.md; `--size 1080x1920`, 30 fps.
- Ses: kullanıcının kaydı > vidIQ Daniel (`onwK4e9ZLuTAKqWW03F9`, kredi varsa) > edge-tts `tr-TR-AhmetNeural`.
- Müzik + efekt + ortam sesi varsayılan açık; −14 LUFS.

## 6. Teslim
- Video, kapak (`scripts/reels_kapak.mjs`), 3 başlık, açıklama + kaynaklar + 5 hashtag.
- Son kontrol: örnek videoyla kendi kontak sayfanı yan yana koy — yapı ve tempo benzer, **görüntülerin hiçbiri aynı değil**.

## Marka kuralları (Tıkla Bakalım)
Kırmızı #e3141b / beyaz / siyah; logo sadece sonda; ekran üstünde kalıcı bant yok; kapanış "Merak ettiysen, tıkla bakalım."
(ölümlü kaza/afette "Gelişmeleri takip etmek için abone ol."); temsili görüntüde "temsili" notu.
