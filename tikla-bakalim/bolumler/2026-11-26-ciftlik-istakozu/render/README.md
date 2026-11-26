# Çiftlik ıstakozu — bilgisayarda render paketi

Her şey hazır: sahneler (`film.html`), ses (`vo.mp3`), sesle hizalanmış zamanlama (`timeline.json`, `caps.json`).
Bu klasörde sadece kareleri çizip videoyu birleştirmek kalıyor. Ekran kartı olan bilgisayarda dakikalar sürer.

## Gerekenler (bir kez)
- Node.js 18+ · Python 3 · ffmpeg (libass'lı; Windows'ta `winget install Gyan.FFmpeg`)
- Bu klasörde:
  ```
  npm install playwright
  npx playwright install chromium
  cd lib && npm install && cd ..
  ```

## Çalıştır
```
node render.cjs 4          # kareler → fr/   (yaklaşık 3011 kare)
python bitir.py vo.mp3     # → final.mp4 (altyazı + müzik + ses)
```
- İlk önce tek kare deneyip hızı gör: `node cap.cjs at 1,40 deneme` → `deneme/` klasörüne bak.
- GPU açılmazsa (kareler siyah/boş): `set CPU=1` (Windows) / `CPU=1` ile yazılımsal çizime düşer (yavaş).
- Altyazı fontu `fonts/` içinde; ffmpeg bulamazsa Poppins SemiBold'u sisteme kur.

Claude Code ile: bu klasörü açıp "README'deki adımlarla ıstakoz videosunu render et" demen yeter.
