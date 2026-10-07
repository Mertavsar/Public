# Pulse Tales Shorts Formatı — sonuna kadar izletme

Kullanıcı istedi: "etkili hook cümlesi ve cümle içinde dikkat çekici metinlerle
sonuna kadar izletecek bir format". Metin, ekran yazısı ve kurgu tek bir iskelete
bağlanır. Yazım kuralları (`script-writing.md`) ve kanıt kuralı (`SKILL.md` §0)
geçerli: her cümle bir kareye, her bilgi bir kaynağa bağlı.

## İskelet (25–35 sn)

| Zaman | Blok | Seste | Ekranda |
|---|---|---|---|
| 0–2 sn | **HOOK** | Soru veya olay + merak, ≤ 7 kelime. Sonucu söyleme. | Büyük hook yazısı (2 satır, beyaz + sarı). Görüntü: gerilimin başladığı an, **sonuç değil** |
| 2–5 sn | **VAAT** | İzleyiciye bir hedef ver: kaç adım, ne bekleniyor | Sayaç belirir: `1/5` |
| 5–20 sn | **TIRMANMA** | Her 4–6 sn bir vuruş: olay → mini merak → sonuç | Her vuruşta sayaç ilerler, ok + clink |
| her 6–8 sn | **YENİDEN KANCA** | Cümle içi dikkat ifadesi (aşağıdaki banka) | Tek kelimelik pop yazı (`DİKKAT ET`) |
| ~%70 | **BİLGİ BOMBASI** | Kaynaklı tek bilgi, sayıyla | Sayı büyük pop (`4 AYLIK`) |
| son 3–5 sn | **DORUK** | Son adım, "ve…" ile gecikmeli | Sayaç tamamlanır (`5/5 ✓`), vuruş sesi |
| son 1–2 sn | **KAPANIŞ** | İkiye bölen soru **veya** ilk cümleye bağlanan döngü | Yazı yok, görüntü akar |

## Neden çalışıyor

- **Sayaç / hedef** izleyiciye bitiş çizgisi verir: "5'in 3'ü oldu" diyen kişi
  kalan ikiyi görmeden kaydırmaz. Sayılabilir bir şey yoksa hedef cümleyle
  verilir ("son hamleyi kaçırma").
- **Yeniden kanca**: Shorts'ta düşüş 5–8 sn aralığında ve ortada olur. Her
  aralıkta yeni bir açık döngü açılır, öncekinin cevabı verilir.
- **Gecikmeli doruk**: "Ve… kırmızı." Üç nokta yalnız burada.
- **Kapanışta CTA yok.** "Abone ol / beğen" izlenme yüzdesini düşürür. Soru
  yorum getirir, döngü tekrar izletir.

## Yeniden kanca bankası (cümle içi dikkat ifadeleri)

Videoda gerçekten olan bir şeye bağlanmayan ifade kullanılmaz ("bunu kimse
beklemiyordu" ancak kare bunu gösteriyorsa).

| Amaç | İfade |
|---|---|
| Dikkati bir ana çek | `Şimdi şuraya dikkat et.` · `Buraya bak.` |
| Devamı vaat et | `Ama durmuyor.` · `Asıl ilginç kısım şimdi.` · `Bu daha başlangıç.` |
| Sahte son | `Bitti sandın, değil mi?` (kare gerçekten boşalıyorsa) |
| Sona çek | `Ve sıra sonuncusunda.` · `Son hamleyi kaçırma.` |
| Ters köşe | `Ama dikkat et, bu aynı ... değil.` (yalnız kanıtlıysa) |
| Bilgiye geçiş | `Bilim insanlarına göre…` · `Bunun bir açıklaması var.` |

## Ekran yazısı katmanları (giydir.py)

1. **Hook** (`big`, 0–2.5 sn): 2 satır, üst satır beyaz, alt satır sarı, üst
   güvenli bölgede (y 0.13 / 0.21).
2. **Sayaç** (`counters` veya `big`): `1/5` … `5/5`, üst köşe, olay anında değişir.
3. **Pop kelime** (`big`, ≤ 1 sn): yeniden kanca anlarında 1–2 kelime. Video
   başına en fazla 3 — fazlası altyazıyla yarışır.
4. **Altyazı**: kelime söylendikçe belirir (reveal), cap_y 0.80–0.82, anahtar
   kelimeler sarı.
5. **Ok + clink**: yalnız sayılan olaylarda (parça girdi, hamle yapıldı).

## Kapanış kalıpları

| Tür | Örnek |
|---|---|
| İkiye bölen soru | `Sence bunu bir çocuk mu daha hızlı yapar, bu kuzgun mu?` |
| Döngü | son: `Şimdi bir daha izle. Bu sefer gagasına bak.` (tekrar izletir) |

## Kontrol listesi (metni teslim etmeden önce)

- [ ] İlk cümle ≤ 7 kelime, sonucu söylemiyor
- [ ] Hedef / sayaç 5. saniyeden önce verildi
- [ ] Her 6–8 sn'de bir yeniden kanca var
- [ ] Bilgi cümlesi kaynaklı, sayı yazıyla ("dört aylık")
- [ ] Son cümle soru veya döngü; "abone ol" yok
- [ ] Her cümlenin kanıt karesi tabloda

## Viral anlatım dili (kullanıcı: "milyonlarca izlenen kanallardaki metinler gibi")

Format aynı kalır; söyleyiş sertleşir. Kanıt kuralı değişmez — iddia büyümez.

1. **Karşıtlıkla aç**: `Bu oyuncak çocuklar için yapıldı. Şimdi bir kuzgunun önünde.`
2. **Kesik cümle**: 2–5 kelime, yer yer tek kelime (`Üç.` `Dört.`).
3. ⛔ **Hamle hamle anlatma.** `İlki yeşil. Bir delik… bir başkası… ve içeride.`
   kullanıcıya "berbat" geldi: görüntünün zaten gösterdiğini spiker gibi sayıyor.
   Hamleyi ekrandaki sayaç/ok gösterir; ses hikâye ve anlam katar (soru, sahte son,
   ters köşe, bilim cevabı, bekletilen son, "bir daha izle" döngüsü).
4. **Orta köprü**: `Asıl çılgın kısım şu:` — ikinci yarıya taşır.
5. **Bilgi = ters köşe**: `Bilim insanları … test etti. Sonuç: …`
6. **Döngü final**: son cümle ilk cümleyi tekrar eder
   (`Ve unutma… bu oyuncak çocuklar için yapıldı.`).

## Teşhis: "milyonluk Shorts gibi değil" (kedi–fare, kullanıcı: "berbat")

Kaynak olduğu gibi + sabit yazı + renk ayarı yetmedi. Eksikler ve çözüm:

1. **Sesi takip eden altyazı yoksa video ölü görünür.** 21 sn sabit iki satır
   en büyük hataydı. Seslendirme metni yoksa İLK iş metni istemek.
2. **Soğuk açılış**: en gergin an, ağır çekim, sonuçtan hemen önce DONMA +
   hook sorusu + `pop` + 0.4 sn müzik sessizliği → `rewind` ile başa dön.
   (cutter: `slow: 200` donma, `rewind` planı; sounddesign `--pop --mute --rewind`)
3. **Ölü an hızlanır** (1.5x), olay anı ağır çekime alınır (≈1.6x) + ok + clink.
4. Kaynağın kendi yazısı: kutu tüm video boyunca → silinir (alttaki zemini
   kaydırarak kopyala; ProPainter kamerayla birlikte giden kutuda gri yama bıraktı),
   cümle yalnız ilgili 3–4 sn'de altyazı olarak geçer.

## Başkasının dikey editini yeniden kurgulama (LoL, kamera üstte / oyun altta)

Kullanıcı: "profesyonel şekilde değiştir", "globale hitap etsin, TR bir şey yazma".

- Ekran yazıları İngilizce (oyun/esports klipleri global kitleye). Oyunun kendi
  arayüzü (kill feed vb.) kaynak dilinde kalır.
- Panel sınırındaki başlık yazısı silinmez, yerleşim yeniden kurulur: kamera
  paneli yazının üstüne kadar kırpılıp kendi alanını doldurur (≤ %3 ölçek),
  araya kendi ayraç çizgimiz, oyun paneli ölçeksiz. Oyun paneli zoomlanmaz.
- Zamanlar hızlı arama (`-ss` girişte) ile değil, kare kare ölçülür
  (parlaklık/sarı alan eşikleri): hızlı aramada ~0.3 sn kayma oldu.
- Kurgu: son vuruştan hemen önce donan soğuk açılış + soru hook → geri sarma →
  ölü kısım 1.25x → olay (kalkan) anında soru + ok + clink → sahte son → kill
  ağır çekim + boom + sarsıntı → kill feed görünürken donma + sonuç kelimesi.
- "Tekrarlanan içerik olmasın" (v2): yerleşim tersine (oyun üstte, kamera
  altta yuvarlak köşeli küçük kart, kaynak boyutunun altında), ayrı renk
  (gece mavisi oyun, soluk kamera), soğuk açılış başka anda (kalkan), kill sonrası
  nişangahlı `REPLAY` (0.3x), sonda yorum sorusu. Nişangah: can barı
  matchTemplate ile izlenir, yalnız doğrulanmış aralıkta çizilir (barın
  kaybolduğu/kameranın kaydığı yerde kilit kaçtı).
- Görsel değişiklik tek başına YouTube'un "reused content" kuralını aşmaz;
  asıl fark özgün seslendirme/yorum. Seslendirme metnini öner, ses gelince senkronla.
