# Sea Secrets EP04 — Why Is Lobster So Expensive? · bilgisayarda render paketi

İngilizce sürüm (Sea Secrets logosu, °F/LB/OZ, Cornwall haritası, somon kafesleri, lobster roll, "$$$").
Ses (`vo.mp3`, James) ve sesle hizalanmış zamanlama (`timeline.json`, `caps.json`) hazır. 33 cümle, ~118 sn.
`cap.cjs` varsayılan olarak İngilizce (`&en=1`) çizer.

## Gerekenler (bir kez)
Node.js 18+ · Python 3 · ffmpeg (libass'lı). Bu klasörde:
```
npm install playwright
npx playwright install chromium
cd lib && npm install && cd ..
```

## Çalıştır
```
node gpu-test.cjs                       # ekran kartı kullanılıyor mu?
node cap.cjs at 1,5,30,60,80,90,93,108,116 kontrol   # ÖNCE KONTROL: kontrol/ karelerine bak
node render.cjs 4                       # tüm kareler → fr/  (~3570 kare)
python bitir.py vo.mp3                  # → final.mp4
```

## Kontrol listesi (bu sahneler bulutta kare kontrolünden geçmedi)
- 1 sn ve 116 sn: tabakta 2 lobster roll + büyük sarı "$$$" — roll'lar tabağa sığıyor mu?
- 5 sn: kayalar üstünde ıstakoz + "WILD"
- 30 sn: İngiltere haritası, CORNWALL etiketi ekran içinde mi?
- 93 sn: denizde balık kafesleri (somon karşılaştırması) — kafesler kadraja sığıyor mu, balıklar görünüyor mu?
- 108 sn: salon + "$$$"
Sığmayan/hatalı bir şey varsa `film.html` içinde `// ================= EN (Sea Secrets) ek sahneler` bölümündeki
kamera değerlerini düzelt (camSet konumu uzaklaştır / fov büyüt). Kural: her sahne kadraja tam sığmalı, aşırı yakın olmamalı.
