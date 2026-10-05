# Aşama 6 — Tıklatan kapaklar tasarla

**Girdi:** video başlığı (Aşama 5), `[niche]`, kaynak klip (varsa)
**Çıktı:** `06-kapaklar.md` (kanal geneli kalıp) ya da `videolar/<no>/kapak.md` (video başına)

> Kaynak prompt: *"Act as a thumbnail designer for a faceless channel in [niche]. For
> the video titled [title], give me 5 completely different thumbnail concepts. For
> each one, describe the main subject, the background, the colour palette, the emotion
> it should trigger, and the 3 words maximum of overlay text. Tell me what the eye
> lands on first in each concept. Then explain which one pairs best with the title and
> which one would fight against it."*

---

## Shorts'ta "kapak" iki şeydir

| | Nerede görünür | Boyut | Kim üretir |
|---|---|---|---|
| **İlk kare** | Akış — video otomatik oynar, ilk kare kapaktır | Tam ekran, ama karar 1 sn'de | viral-edit (EDL plan 0 + banner) |
| **Raf kapağı** | Kanal sayfası, Shorts rafı, arama | ~**150 px** genişlik | `viral-edit/scripts/cover.py` |

Bu aşama **konsept** üretir; görseli viral-edit üretir. Kapak kuralları
viral-edit `SKILL.md` §5 "Kapak görseli" — tekrar yazılmaz, uyulur.

## 5 tamamen farklı konsept

"Farklı" = farklı ana özne ya da farklı duygu. Aynı karenin 5 renk varyasyonu değil.

Her konsept:

| Alan | Not |
|---|---|
| Ana özne | Klipte **gerçekten var olan** bir an — saniyesiyle, bilinmiyorsa "klipten seçilecek: <ne>" |
| Arka plan | Sade mi, bağlam mı; gökyüzüyse `top_shade` gerekir |
| Renk paleti | Kanalın imzası (kırmızı ok, sarı sayı) ile uyumlu |
| Tetiklenen duygu | Tek kelime: korku, şaşkınlık, tiksinti, hayranlık, öfke |
| Yazı | **En fazla 3 kelime**; ilk kare yazısını tekrar etmez |
| Gözün ilk düştüğü yer | Tek nokta. İki nokta varsa konsept dağınıktır |
| 150 px testi | Bu boyutta özne ve yazı okunur mu — tahmin değil, gerekçe |

## Kapanış

- **Başlıkla en iyi eşleşen** konsept ve neden (başlık soruyu sorar, kapak cevabın
  yarısını gösterir → merak boşluğu büyür)
- **Başlıkla çatışan** konsept ve neden (aynı şeyi söylüyor ya da başka vaat veriyor)
- Seçilen konseptin `cover.py` için kısa spec taslağı: kare saniyesi, yazı, ok yeri

## Kanal geneli kalıp

İlk kez yapılıyorsa `06-kapaklar.md`'ye kanalın **sabit kapak kalıbını** da yaz:
yazı konumu, renkler, ok kullanımı. Kanal sayfasında kapaklar yan yana durur;
tutarlı bir dil kanalı tanınır kılar.
