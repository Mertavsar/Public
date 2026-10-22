# PHP2Shell alarmı (22 Ekim 2026)

~52 sn dikey (1080×1920) animasyon. Hook girişli, teknik terimsiz anlatım: 21 Ekim 2026 PHP güvenlik güncellemesi
(CVE-2026-109618 / 109619, "PHP2Shell"), güncellemeden önce görülen saldırılar
(Cloudflare, 07:43 UTC) ve aynı hafta Rank Math PRO 3.0.123'e konan arka kapı.

- `seslendirme.txt`: okunacak metin (yabancı kelimeler okunuşla); `altyazi.txt`: ekrandaki yazım.
- `php2shell-onizleme.mp4`: müzik + tahmini zamanlı altyazı (seslendirme gelmeden).

## Ses gelince

```
python3 build/vo_clean.py vo/ham.mp3          # boşluk/nefes/burun sesi temizliği -> vo/temiz.wav
python3 ../.claude/skills/viral-edit/scripts/align.py vo/temiz.wav seslendirme.txt vo/captions.json
python3 build/captions.py                      # sahne + altyazı zamanları gerçek sese oturur
python3 build/soundtrack.py && python3 build/mix.py
node build/render.mjs                          # -> out/video-silent.mp4, sonra ses ile birleştir
```

Kaynaklar: PHP Foundation, CISA, Qualys, Sansec, Recorded Future (PHP2Shell);
Patchstack, The Hacker News, Wordfence (Rank Math PRO).
