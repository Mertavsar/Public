# PHP2Shell alarmı (22 Ekim 2026)

~52 sn dikey (1080×1920) animasyon. Hook girişli, teknik terimsiz anlatım: 21 Ekim 2026 PHP güvenlik güncellemesi
(CVE-2026-109618 / 109619, "PHP2Shell"), güncellemeden önce görülen saldırılar
(Cloudflare, 07:43 UTC) ve aynı hafta Rank Math PRO 3.0.123'e konan arka kapı.

- `seslendirme.txt`: okunacak metin (yabancı kelimeler okunuşla); `altyazi.txt`: ekrandaki yazım.
- `php2shell.mp4`: son video (47 sn) — temizlenmiş seslendirme, kelime senkronlu altyazı, müzik ve bas vurguları.
- Animasyonun önemli anları kelimelere kilitli (`build/captions.py` → `ANCHORS`): kilit "açık"ta açılır, damga "PHP2Shell"de vurur, kapı "gizli"de açılır, takip butonu "takip"te çıkar.

## Ses gelince

```
ffmpeg -i vo/ham.mp3 -ac 1 -ar 48000 vo/ham.wav
python3 build/vo_clean.py vo/ham.wav          # boşluk/nefes/burun sesi temizliği, %5 tempo -> vo/temiz.wav
python3 ../.claude/skills/viral-edit/scripts/align.py --audio vo/temiz.wav --text seslendirme.txt --out vo/captions.json --check
python3 build/captions.py                      # sahne + altyazı zamanları gerçek sese oturur, vo/son.wav
python3 build/soundtrack.py && python3 build/mix.py
node build/render.mjs                          # -> out/video-silent.mp4
ffmpeg -i out/video-silent.mp4 -i assets/mix.m4a -filter_complex "[1:a]apad[a]" -map 0:v -map "[a]" \
       -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart php2shell.mp4
```

Kaynaklar: PHP Foundation, CISA, Qualys, Sansec, Recorded Future (PHP2Shell);
Patchstack, The Hacker News, Wordfence (Rank Math PRO).
