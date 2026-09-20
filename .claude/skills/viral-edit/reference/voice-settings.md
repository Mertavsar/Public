# Seslendirme — ses seçimi ve ayar standardı

Her videoda yeniden karar verilmez. Standart budur; sapılacaksa sebebi yazılır.

---

## 1. Ses seçimi

**Türkçe ana dili olan ses kullan.** ElevenLabs Voice Library → Language: Turkish,
Use Case: Narrative / Informative.

İngilizce preset sesler (Liam, Adam, Josh, Brian, Antoni…) Türkçe okurken vurguyu
yanlış heceye koyuyor. Türkçede vurgu çoğunlukla **kelimenin son hecesinde**;
İngilizce sesler baştan vuruyor. Bu ayarla düzelmez, model sürümüyle de düzelmez —
ses değiştirmek gerekir.

Bu ölçülemez, sadece duyulur. Ölçüm ne diyor:

| Dosya | Perde | Dağılım | Gerçek perde sıçraması |
|---|---|---|---|
| Liam v3 (gergedan) | 115 Hz | %22 | %2.5 |
| Liam v3 (saksağan) | 107 Hz | %22 | %1.8 |
| v2 (motivasyon) | 78 Hz | %16 | %2.2 |

Üçü de **teknik olarak temiz** — bozulma yok, %2 sıçrama normal konuşmada da var.
Kullanıcı yine de "berbat" dedi. Demek ki sorun üretimde değil, aksanda.

> **Ders:** "ses kötü" şikâyetinde önce ölç. Ölçüm temizse ayar kurcalama,
> sesi değiştir.

### En iyi çözüm: kanalın kendi sesi

Instant Voice Cloning, 1–2 dakika temiz kayıt (sessiz oda, ağızdan 15–20 cm).
Aksan sorunu biter, ses kanalın markası olur, her videoda ses arama derdi kalkar.

## 2. Ayarlar

| Ayar | Değer | Neden |
|---|---|---|
| **Speed** | **1.00** | Üstü sesi zaman olarak geriyor. 1.14'te ölçülen hız 5.05 hece/sn — Türkçe anlatım için hızlı. Tempo kurguda kesimden gelir. |
| **Stability** | **65–70** | 50 "expressive" tarafta, cümleden cümleye ton geziniyor. 65–70 anlatıcı tonunu sabitler. |
| **Similarity** | **75** | Varsayılan iyi çalışıyor. |
| **Model** | v3, etiketler bozarsa `eleven_multilingual_v2` | v2 Türkçede daha oturaklı, v3 daha ifadeli ama daha oynak. |

Hedef hece hızı **4.0–4.5 hece/sn** (toplam süre üzerinden). Ölç:
`scripts/align.py --check` çıktısındaki tepe sayısını süreye böl.

## 3. Test protokolü

30 saniyelik metnin tamamını üç sesle üretme. **Sadece ilk iki cümleyi** üret —
karar ilk 3 saniyede veriliyor, orada tutmuyorsa gerisi önemsiz.

Üç adayı da aynı ayarla üret (speed 1.0, stability 68, similarity 75), yan yana
dinle. Teknik temizlik ölçülebilir, aksan kararını kullanıcı verir.

## 4. Ses geldiğinde zorunlu kontrol

```bash
python3 - <<'EOF'
import subprocess, numpy as np
raw=subprocess.run(["ffmpeg","-v","error","-i","vo.mp3","-ac","1","-ar","48000","-f","f32le","-"],
                   capture_output=True,check=True).stdout
x=np.frombuffer(raw,dtype=np.float32)
print(f"tepe {20*np.log10(np.abs(x).max()):+.2f} dBFS · kırpık {int((np.abs(x)>=0.999).sum())}")
EOF
```

Kaynak seste kırpılma varsa **yeniden ürettir**; masterda düzelmez.

## 5. ⛔ Sesi kesme

Gelen seslendirme olduğu gibi kullanılır. Sebebi `SKILL.md` §3'te.
