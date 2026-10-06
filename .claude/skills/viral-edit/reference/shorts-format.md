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
| Tekrarı ödüllendir | `Yine deniyor… ve oldu.` · `Bir kez daha.` |
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
| Döngü | son: `Ve hâlâ tek bir soru var:` → ilk: `Bu kuzgun beş parçayı da sokabilecek mi?` |

## Kontrol listesi (metni teslim etmeden önce)

- [ ] İlk cümle ≤ 7 kelime, sonucu söylemiyor
- [ ] Hedef / sayaç 5. saniyeden önce verildi
- [ ] Her 6–8 sn'de bir yeniden kanca var
- [ ] Bilgi cümlesi kaynaklı, sayı yazıyla ("dört aylık")
- [ ] Son cümle soru veya döngü; "abone ol" yok
- [ ] Her cümlenin kanıt karesi tabloda
