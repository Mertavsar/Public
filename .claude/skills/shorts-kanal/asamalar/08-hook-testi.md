# Aşama 8 — Hook'u yeniden yaz ve test et

**Girdi:** `videolar/<no>/metin.md` (Aşama 7), Aşama 1'deki çekirdek izleyici
**Çıktı:** `videolar/<no>/hook.md` + final `videolar/<no>/metin.txt`

> Kaynak prompt: *"Here is the first 30 seconds of my script: [paste]. Rewrite it 7
> different ways, each using a different opening angle such as a bold claim, a
> question, a story, a contradiction, a visual moment, a stat or a warning. Then
> simulate 5 different viewers from my target audience and have each one react
> honestly to all 7 versions. Show me which version each viewer would keep watching
> and why. Finish by combining the strongest elements into 1 final hook."*

---

## Shorts ölçeği

Kaynakta "ilk 30 saniye". Shorts'ta kaydırma kararı **ilk 1–2 saniyede** verilir.
Test edilen parça: **ilk cümle (≤4 kelime) + ilk kare yazısı + ilk karede görünen an**.
Üçü birlikte bir "açılış"tır; sadece cümleyi test etmek yarım test.

## 1. 7 açılış

Her biri farklı açı:

| # | Açı | Örnek kalıp |
|---|---|---|
| 1 | Cüretkâr iddia | `Bu bank seni oturtmak için yapılmadı.` |
| 2 | Soru | `Neden hiç kıpırdamıyor?` |
| 3 | Hikâye | `Üç saniye sonra her şey bitti.` |
| 4 | Çelişki | `En büyüğü, en kör olanı.` |
| 5 | Görsel an | Kare sıfırdaki görüntüyü işaret eden cümle |
| 6 | Sayı | `İki ton. Karşısında seksen kilo.` |
| 7 | Uyarı | `Bunu görürsen sakın koşma.` |

Her açılış için: ilk cümle · ilk kare yazısı (2–4 kelime) · ilk karede görünen an.

## 2. 5 izleyici simülasyonu

Aşama 1'deki çekirdek izleyiciden **5 farklı kişi** kur — sadece demografi değil,
**kaydırma alışkanlığı** farklı olsun:

- Hızlı kaydıran (her videoya 1 sn verir)
- Konuyu zaten bilen (kolay bilgiyle kandırılmaz)
- Konuya yabancı (nişi bilmiyor — kitle büyüklüğü testi)
- Sesi kapalı izleyen (sadece ilk kare yazısını görür)
- Şüpheci (clickbait'e alerjisi var)

Her izleyici 7 açılışın her birine **dürüstçe** tepki verir: `KALIR` / `KAYDIRIR`
+ bir cümle neden. Simülasyon kibar olmaz — gerçek izleyicinin çoğu kaydırır.

```
| Açılış | Hızlı | Bilen | Yabancı | Sessiz | Şüpheci | KALIR |
```

> Bu bir **simülasyondur, veri değildir** (HYPOTHESIS). Gerçek cevabı Aşama 9'daki
> "izlemeye devam eden" oranı verir. Tahmin ile gerçek ayrışırsa `kurallar.md`'ye
> hangi izleyici tipinin yanıltıcı olduğunu yaz.

## 3. Final hook

En güçlü öğeleri **birleştir** (ör. #6'nın sayısı + #4'ün çelişkisi). Final:

- İlk cümle ≤ 4 kelime
- İlk kare yazısı (2–4 kelime, ilk cümleyi tekrar etmez ya da kısaltır)
- İlk karede hangi an (kaynak saniyesi)
- **Döngü kontrolü:** metnin son cümlesi bu yeni ilk cümleye hâlâ bağlanıyor mu?
  Bağlanmıyorsa son cümleyi de yeniden yaz.

## Teslim

Final metni `videolar/<no>/metin.txt` olarak yaz — sadece seslendirilecek metin
(viral-edit Tur 2 `--script` olarak kullanır). Kullanıcıya kopyalanacak bloğu ver,
ElevenLabs'te ses üretmesini iste. Ses gelince **viral-edit Tur 2**.
