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
