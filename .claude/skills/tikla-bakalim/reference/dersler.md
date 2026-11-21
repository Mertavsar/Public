# Öğrenilen dersler (Kasım 2026 oturumları)

Yeni sohbette önce bunu ve `kimlik.md`'yi oku.

## Beğenilenler
- **Gırgır videosu (700 bin+)** referans format: şaşırtan sonuç → sırrı saklayan yarım cevap →
  "Baştan anlatayım" → adımlar → cevap en sonda. Ayrıntı `kimlik.md` "Hook kuralı".
- **Fanyalı ağ / çökertme dalyan**: three.js gerçekçi 3D sahne (su altı + kesit görünüm + yüzey + tekne),
  kare kare Playwright ile yakalama. Mekân her adımda değişir.
- **Dünyadan yakınlaşma girişi** (çökertme v2): video doğrudan uzaydan Dünya ile açılır, gerçek haritayla
  (NASA Blue Marble + Natural Earth sınırları) İzmir Karaburun'a iner; son kare yine Dünya'ya döner (döngü).
  Başlık fontu: Inter Display Black Italic.
- **PDF Mind (uygulama tanıtımı, gerçek çekim)**: `uygulama-tanitim/pdfmind/`. Sabitleme (vidstab),
  minimal cam çip yazılar, ortalı, tek vurgu rengi #FFD54A, 2–3 kelimelik altyazı, ses temizleme zinciri,
  −14 LUFS. Kullanıcı "son saniyede indirin" kısmını istemedi.

## Beğenilmeyenler (tekrarlama)
- Üstte "1 · AĞI KUR / 2 · BEKLE" bölüm şeridi → "çok Claude olduğu belli oluyor".
- Sürekli su altı → "hep aynı yer". Süreci gerçek mekânlarında göster.
- Fotoğraf + yakınlaşma + dalgalanma ("canlı fotoğraf") → "berbat, iptal".
- Meta girişler ("700 bin izlendi", "çok sordunuz", "merak ettiniz").
- Kaba manken/CGI karakter denemesi → gerçekçi sahne stili tercih edildi.
- Ses efekti çok hafif değişince "hepsi aynı" → ses değiştirmede belirgin fark (pitch 0.76–1.22, telsiz bandı).

## Teknik notlar
- Konuşma müziğin net üstünde: master −14 LUFS; müzik Kevin MacLeod (CC BY, künye ekle).
- Bilgi uydurma yok; her sayı iki kaynakta (bölüm klasöründe `analiz.md`).
- Kullanıcı videolarını / ham çekimleri repoya commit etme (repo herkese açık).
- Mağaza/marka logosu kullanma; yazılı kart yeter.
- Lemo-Opuscar (99 kod-animasyon stili) bulut oturumda kurulamadı; kullanıcının Windows bilgisayarında
  yerel Code oturumunda kullanılır: `claude plugin marketplace add lemomo-ai/lemo-opuscar` →
  `claude plugin install lemo-opuscar@lemolab` → `/effort high` → `/lemo-opuscar:lemo-opuscar <istek>`.

## Karma stil sistemi (kullanıcı kararı, "nasıl çalışıyor" videoları)

Tek filmde, sahnenin işine göre dört Lemo-Opuscar stili:

| Sahne işi | Stil (klasör) | Ne zaman |
|---|---|---|
| Yer / giriş / döngü kapanışı | 3D Map Explainer (`map-explainer`) | Hook: Dünya/harita → köye iniş; son kare aynı haritaya döner |
| Köy, deniz, insanlar, gündelik an | Low-poly Isometric Island (`lowpoly-island`) | Tekne çıkıyor, balıkçı bekliyor, toplama |
| Mekanizma / asıl sır | Line-Art Cutaway (`hardcore-info`) | Su üstü + su altı + düzenek aynı karede, yavaş |
| Sayı, kıyas, sonuç | Isometric Infographic (`iso-infographic`) | "günde yüz balık", ölçüler, karşılaştırma |

Tek film gibi durması için:
- Ortak palet: marka kırmızısı `#e3141b`, beyaz, siyah + deniz mavisi. Her stil bu paletle boyanır.
- Stil değişimi **eşleşen kadrajla** yapılır (morph/match cut): low-poly tekne → aynı açıdan çizgi kesite
  dönüşür; kesitten geri low-poly'ye. Sert kesme yok.
- Tek font ailesi, tek altyazı stili; üstte bölüm şeridi yok.
- Stil sayısı en fazla 4; her stil en az 2 sahne sürer (sürekli zıplama olmasın).
- Ses/müzik tüm film boyunca kesintisiz; stil değişimi seste whoosh ile vurgulanmaz.

## Kapak (kullanıcı kararı, Kasım 2026)
- Seçilen: **B / belgesel** — `scripts/seri_kapak.mjs`. Dev Anton başlık sola yaslı, altında 1–2 satır
  gerçek bilgi cümlesi (Poppins SemiBold, vurgu kırmızı alt çizgi).
- Reddedilen: Montserrat + kırmızı kutu + sarı soru kutusu + seri rozeti + imleç + köşe logo → "berbat".
  "Denizin Sırları" rozeti de istenmedi.
- Alt cümle soru değil, kaynaklı vurucu gerçek: "Tek bir ipe yüzlerce iğne diziliyor, hepsi tek tek yemleniyor."
- Kapak görseli (kullanıcı: "bu tarz realistik görseller lazım", dip trolü örneği): **gerçekçi yarı su üstü /
  yarı su altı kesit fotoğraf**. Üst yarı: tekne ve gökyüzü (başlık buraya). Alt yarı: düzenek su altında,
  balıklar. Görsel yazısız üretilir, yazıyı `seri_kapak.mjs` ekler. İstem kalıbı:
  "Vertical 9:16 photorealistic split-level shot, half above / half below the waterline, upper half: <tekne/kıyı>,
  calm sky with empty space at the top for a title, lower half underwater: <mekanizma>, clear water, sun rays,
  fish, cinematic, high detail, no text, no labels, no arrows"
