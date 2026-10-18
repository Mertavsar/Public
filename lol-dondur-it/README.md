# Dondur mu, it mi? — LoL dalga yönetimi

Dikey (1080×1920), 66 saniye, tamamen animasyon. Koridorda dalgayı **dondurmayı** ve
**itmeyi** adım adım anlatır, sonunda ikisini karşılaştırır.

İlk LoL videosuna gelen geri bildirim ("çok hızlı, bilgi yok, animasyonlar birbirine
girmiş") üzerine düzen değiştirildi:

- Harita kendi çerçevesinde (üstte), açıklama altındaki ayrı panelde. Yazı haritanın
  üstüne binmiyor.
- Her adım 6–8 saniye ekranda kalıyor. Hızlı akan kelime altyazısı yok.
- Haritada aynı anda tek olay ve en fazla tek etiket var.

| Süre | Adım | Haritada |
|---|---|---|
| 0–6 | Dalgayı iki şekilde yönetirsin | DONDUR ve İT yön okları |
| 6–13 | Dondurma 1/3: dalga kulenin önünde durur | Kule menzili (kırmızı kesik çizgi), menzil dışında bekleyen dalga |
| 13–20 | Dondurma 2/3: sadece son vuruş | 2 sn arayla 3 son vuruş, fazla 4 büyücü sarı halkada |
| 20–29 | Dondurma 3/3: rakip sana gelmek zorunda | Rakip derine giriyor, ormancı çalıdan çıkıp yakalıyor |
| 29–35 | İtme 1/3: dalgayı hızla temizle | İki alan yeteneği, kırmızı dalga eriyor |
| 35–43 | İtme 2/3: dalga rakip kuleye çarpar | Mavi dalga ilerliyor, kule minyonları yiyor |
| 43–50 | İtme 3/3: sen zaman kazanırsın | Üsse dönüş; Üsse dön / Dolaş / Ejderha |
| 50–60 | Karşılaştırma tablosu | Ne zaman? Ne kazanırsın? Risk |
| 60–66 | Sen hangisini daha çok yapıyorsun? | A: Dondurmak · B: İtmek |

## Açıklama önerisi

```
Dondur mu, it mi? Dalga yönetimini 1 dakikada öğren ❄️➜
Sen hangisini daha çok yapıyorsun? A mı B mi? 👇

#leagueoflegends #lol #loltr #lolturkiye #dalgayönetimi #gaming
```

## Kaynaklar

- Dondurma (menzil dışı, sadece son vuruş, ~4 fazla büyücü): [LoL Theory – How to freeze](https://blog.loltheory.gg/how-to-freeze-lane), [Dignitas – Freezing your lane](https://dignitas.gg/articles/Blogs/League%20of%20Legends/1223/Advanced-guide-Freezing-your-lane)
- İtme (kuleye çarptırma, üsse dönüş, dolaşma, hedef): [LoL Theory – Fast push](https://blog.loltheory.gg/fast-push-lol/), [LoL Theory – Wave management](https://blog.loltheory.gg/wave-management-league-of-legends/)

Kaynaklar dondururken son vuruşun dalgayı ne kadar ittiği konusunda tam anlaşmıyor.
Videoda en çok tekrar edilen kural anlatıldı. Süreler temsilîdir.

## Yeniden üretme

```bash
python3 build/soundtrack.py
node build/render.mjs                    # out/video-silent.mp4
ffmpeg -i out/video-silent.mp4 -i assets/soundtrack.m4a -map 0:v -map 1:a -c copy -shortest -movflags +faststart dondur-mu-it-mi.mp4
```
