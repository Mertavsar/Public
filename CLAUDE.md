# Public

Bu repo **AI Agency Operating System**'i barındırır.

Ajans, müşteri, reklam, satış veya haftalık rapor ile ilgili her işte önce
`agency-ai/CLAUDE.md` dosyasını oku — sistemin çalışma prensipleri, sorumluluk
sınırları ve kanıt disiplini oradadır. Uzmanlık modülleri `.claude/skills/` altındadır.

Video kurgusu ajans akışının dışındadır: kullanıcı klip veya seslendirme attığında
`.claude/skills/viral-edit/` kullanılır.

OpenMontage (açık kaynak, AGPL-3.0, yapay zekâ destekli video üretim sistemi) depoya
kopyalanmaz; bulut oturumu başında `.claude/hooks/session-start.sh` onu
`$OPENMONTAGE_DIR` (`../calesthio/openmontage`) altına kurar. Remotion, ortamdaki
Playwright Chromium'u kullanır (`remotion.media` ağda kapalı). Bu ortamdan erişilebilen
servisler: Google (Gemini, Veo, Imagen, Lyria; `GOOGLE_API_KEY` gerekir). Kapalı olanlar:
Pexels, Pixabay, archive.org, Wikimedia, OpenAI, ElevenLabs, fal, Replicate, Hugging Face.

## Video tercihleri (kullanıcının kalıcı istekleri)

Her seslendirmeli videoda varsayılan olarak uygula, kullanıcıya tekrar sordurma:
- Ses hızlı ve sıkı: boşluklar/nefesler alınır, tempo ~%12 artırılır (perde korunur),
  kelimeler arası sessizlik en fazla ~0.15 sn (`php-saldiri/build/vo_clean.py`).
- Altyazı ve animasyon kelime senkronlu; önemli animasyon anları kelimeye kilitlenir.
- Müzik etkili ama konuşmanın altında (-24 LUFS, sidechain); sert alkış/hi-hat yok.
- Efekt sesleri kullanılır (glitch, tık, alarm, damga, pop, zil); whoosh geçiş sesi yok.
- Dikey tam ekran, renkli; içerik ekranı doldurur, ortada sıkışmaz.
- Hook girişi, basit ve anlaşılır dil, ≤ 1 dk, sonda takip/paylaş çağrısı.
- Yabancı kelimeler seslendirme metninde okunuşla yazılır.
