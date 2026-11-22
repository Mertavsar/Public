# Ortasu trolü — 3D film kaynağı
three.js 0.169 (npm i three@0.169.0 → lib/), Playwright + SwiftShader ile kare kare.
Gerekenler yanına: lib/, fonts/ (Anton, Poppins SemiBold/BlackItalic), logo.jpg, harita.json (Natural Earth 50m, bbox 18–46E 30–48N).
- `python3 timeline_tahmin.py timeline.json` (sessiz taslak) ya da sentalign çıktısından timeline.json
- `node cap.cjs at t1,t2 kontrol` kontak kareleri · `node cap.cjs frames A B fr` (4 paralel)
- ffmpeg: fr/f_%05d.jpg + mix.wav → mp4 (crf 23, maxrate 3500k)
Müzik: Kevin MacLeod "Inspired" (incompetech.com, CC BY 4.0) — açıklamaya künye.
