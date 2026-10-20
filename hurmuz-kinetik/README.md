# Hürmüz — kinetik tipografi sürümü

Dikey (1080×1920), 52 saniye, seslendirmesiz. `../hurmuz/` ile aynı içerik, tamamen farklı
tarz: her vuruşta zemin rengi bir köşeden dairesel açılarak değişir (sarı, siyah, mavi,
krem, kırmızı), dev kelimeler "çarparak" girer. Düz ikonlar: tanker, varil, pompa,
gerçek kıyı çizgisinden boğaz kesiti.

| Süre | Vuruş |
|---|---|
| 0–3,6 | BENZİN NEDEN BU KADAR PAHALI? (sarı) |
| 3,6–8 | Cevap: 33 km genişliğinde bir su yolu, iki kara birbirine yaklaşır (siyah) |
| 8–12,4 | HÜRMÜZ BOĞAZI, gerçek kıyı çizgisi, akan rota, pin (mavi) |
| 12,4–17,4 | 20 MİLYON VARİL, akan tanker konvoyu, deniz petrolünün dörtte biri (krem) |
| 17,4–22,6 | 85 → 4: 85 tankerlik ızgara erir, 4 sarı tanker kalır (kırmızı) |
| 22,6–28 | NEDEN? SAVAŞ. ABLUKA. SALDIRI. (siyah) |
| 28–33 | Boru hatları? 20'ye karşı 5,5: YETMİYOR. (sarı) |
| 33–38 | 1 varil petrol: varil dolar, 110 $ (siyah) |
| 38–43,5 | Benzin 79,60 TL, motorin 96,70 TL (krem) |
| 43,5–48,2 | İran: "AÇARIZ EĞER…" 3 şart, anlaşma yok (mavi) |
| 48,2–52 | SENCE AÇILIR MI? A/B, takip et (siyah) |

Kaynaklar `../hurmuz/README.md` ile aynı.

```bash
python3 build/soundtrack.py && python3 build/mix.py
node build/render.mjs
ffmpeg -i out/video-silent.mp4 -i assets/mix.m4a -map 0:v -map 1:a -c copy -shortest -movflags +faststart hurmuz-kinetik.mp4
```
