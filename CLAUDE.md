# Public

Bu repo **AI Agency Operating System**'i barındırır.

Ajans, müşteri, reklam, satış veya haftalık rapor ile ilgili her işte önce
`agency-ai/CLAUDE.md` dosyasını oku — sistemin çalışma prensipleri, sorumluluk
sınırları ve kanıt disiplini oradadır. Uzmanlık modülleri `.claude/skills/` altındadır.

Beğenilen bir Shorts formatında yeni video için `.claude/skills/format-kopyala/` kullanılır.

Video kurgusu ajans akışının dışındadır: kullanıcı klip veya seslendirme attığında
`.claude/skills/viral-edit/` kullanılır.

**Tıkla Bakalım** kanalı (gündem, ekonomi, teknoloji konularını animasyonla
anlatan videolar; "ne oldu, neden oldu, bizi nasıl etkiliyor") için
`.claude/skills/tikla-bakalim/` kullanılır. Ham klip yoktur, her şey sıfırdan
çizilir. Bölümler `tikla-bakalim/bolumler/` altında durur.

## Konuşma kuralı (token tasarrufu)
- Kısa yaz: sonuç + gerekiyorsa tek satır sonraki adım. Giriş cümlesi, tekrar, uzun özet yok.
- Araç çıktısını kullanıcıya baştan anlatma; sadece önemli olanı (hata, karar, sonuç) söyle.
- Ara durum mesajı ancak uzun bir iş başlarken veya biterken.
- Büyük dosyaları baştan sona okuma; gereken bölümü oku (grep, satır aralığı).
- Görsel kontrolde tek kontak sayfası yeterli; her kareyi ayrı ayrı açma.
- Her video için yeni sohbet önerilir; uzun sohbet her mesajda geçmişi yeniden okur.
