# EP05 Caviar — sahne planı ve PC devir notu

## Format (Sea Secrets kuralları)
- Dikey 1080×1920, 3D (three.js 0.169), parlak, aşırı yakın değil: HER SAHNE KADRAJA TAM SIĞAR.
- Gırgır kancası: çarpıcı sonuç → gizli sır → "step by step" → cevap sonda. Döngü: son cümle kancaya bağlanır.
- CTA: paylaş+abone başta (cta sahnesi), beğen ortada (chip "like"), yorum sonda (chip "comment").
- Sahne içinde yazı yok; sadece harita etiketleri ve BÜYÜK SAYILAR (bigTxt): "$120/g vs $10/g", "18 YEARS", "7 YEARS", "1–2 / 10", "8%".
- Altyazı ASS ile (bitir.py), kareler NOCAP ile çizilir. Logo: logo_en.jpg (EN=1).

## Motor
Hazır motor: `tikla-bakalim/bolumler/2026-11-26-ciftlik-istakozu/3d/` → head_part.html + ek_part.js + cekim_is.js + tail_part.html
(film.html = bu dördünün `cat` ile birleşimi). Yeni bölüm için `cekim_cv.js` yaz (cekim_is.js'i şablon al: setler, kamera
fonksiyonları, S4 çekimleri, apply2, bigTxt). Render/bitir: ep04 render paketiyle aynı (cap.cjs, render.cjs, bitir.py, gpu-test.cjs).
Ses gelince: sentalign (viral-edit/scripts/sentalign.py) → timeline.json (her cümle bir id) → render → `python bitir.py vo.mp3`.

## Cümle → sahne (id)
| id | cümle | sahne |
|---|---|---|
| hook | People say caviar costs more than gold. | Siyah zemin, altın külçe + küçük havyar kutusu yan yana, terazi |
| myth | It doesn't. Gram for gram… ten times more. | Terazi altın tarafına ağır basar; bigTxt "$120/g" (altın) – "$10/g" (havyar) |
| years | But one small tin… eighteen years | Açık havyar kutusu (siyah inci taneler, InstancedMesh) + bigTxt "18 YEARS" |
| step / step2 | I'll show you why… / The answer… | Çiftlik salonu geniş plan: büyük yuvarlak mavi tanklar, içinde mersin balıkları |
| cta | Share… subscribe | Tank üstten, CTA kartı |
| what | Caviar is the salted eggs of… sturgeon. | Mersin balığı yakın-orta plan (uzun, sırtında kemik plakalar, sivri burun, bıyıklar) |
| farms | Today, most of it comes from farms. | Salon geniş plan, tank sıraları |
| china1 / china2 | biggest producer isn't Russia or Iran. / It's a lake in China. | Harita (Avrasya): önce Hazar çevresi soluk, sonra Çin'de Qiandao Gölü kırmızı nokta + "CHINA" |
| baby | baby sturgeon, smaller than your finger | Küçük tankta minik yavrular (sürü) |
| tanks | big round tanks, cold clean water | Yuvarlak tanklar, su akışı parçacıkları |
| wait | Then comes the hard part: waiting. | Zaman atlama: tank üstünde güneş/ay döngüsü, balıklar büyür |
| ages1 / ages2 | Siberian ~seven years. / beluga up to eighteen. | bigTxt "7 YEARS" → "18 YEARS", balık boyu büyür |
| like | hit like | Tank, chip like |
| ultra | ultrasound | Teknisyen eli/prob balığın karnında, ekranda (3D panel) yumurta görüntüsü |
| ready1 / ready2 | 1–2 of 10 ready / rest back | 10 balık sırada, 2'si yeşil halka, 8'i tanka geri kayar; bigTxt "2 / 10" |
| process | sieved, rinsed, lightly salted | Elek üstünde siyah taneler, su damlaları, tuz serpme |
| nonlethal | without harming the fish | Balık tanka geri yüzer (yumuşak, olumlu) |
| ship | packed into tins, ice cold, shipped | Teneke kutular buz üstünde, uçak/kamyon silüeti haritada çizgi |
| whyq | So why is caviar so expensive? | Açık kutu + kaşık |
| answer1 | wait up to eighteen years | bigTxt "18 YEARS" |
| answer2 | only about eight percent… | Balık silüeti, %8'i siyah dolu (doluluk çubuğu) + bigTxt "8%" |
| care | years of feed, cold water and care | Sedef kaşık üstünde havyar, yavaş dönüş |
| comment / comment2 | Have you ever tried caviar? / tell me… | Blini + krema + havyar tabağı, chip comment |
| loop | one of the most expensive foods on Earth | Kancadaki altın + havyar sahnesine döner |
