# Eksiksiz örnek — "Gergedan onu görmüyor"

Yayınlanmış bir videonun her parçası. **Biçim burada donmuş durumda**: yeni
videoda bu dosyaları kopyala, sayıları değiştir, yapıyı bozma.

| | |
|---|---|
| Kaynak | 576x1024, 24 fps, 17.08s — kullanılabilir son 13.0s (sonrası TikTok end card) |
| Seslendirme | ElevenLabs, Türkçe ses, `speed 1.00 · stability 50 · similarity 75 · v3` |
| Çıktı | 1080x1920, 30 fps, 32.97s, 25 plan |
| Ses | −14.3 LUFS, tepe −3.11 dBFS, kırpılma sıfır |
| Hizalama | metinde 159 hece / seste 161 tepe — %1.3 sapma |

---

## 1. Metin (`script2.txt`)

Cümle başına 3–8 kelime. Son cümle ilk cümleye bağlanıyor — döngü kapanıyor.

```
Gergedan onu görmüyor.
Bir karış ötesinde duruyor. İki ton, karşısında seksen kilo.
Çünkü gergedanın gözü neredeyse kör. Otuz metre ötesini seçemiyor.
Domuz kıpırdamadığı sürece onun için orada yok.
Görseydi de bir şey değişmezdi. Gergedan ot yiyor.
Asıl mesele bu çukur.
Gergedan terleyemiyor. Çamur onun tek serinliği. Domuz için böcek kalkanı.
Ve o çukur artık büyük olanın.
Sen olsan kaçar mıydın, yoksa beklerdin mi?
O domuz hâlâ hayatta. Sebebi tek şey:
```

Kapanış iki parça: **ikiye bölen soru** (`kaçar mıydın, yoksa beklerdin mi?`)
yorumu tetikler, **döngü cümlesi** (`Sebebi tek şey:`) ilk cümleye bağlanır.
Arka arkaya oku: *"…Sebebi tek şey: Gergedan onu görmüyor."*

## 2. EDL (`edl.tsv`)

25 plan, ortalama 1.32s, saniyede 0.76 kesim. Plan sınırları cümle sınırlarına
oturuyor. `cropx` 5.20 sonrası `40`, öncesi `160` — filigran 5.00'te taraf
değiştiriyor (§4).

```
# out0	out1	src	slow	z0	z1	cx	cy	cropx	beat	not
0.00	1.73	5.55	1.60	1.45	1.58	0.32	0.76	40	R	HOOK gormuyor - burun buruna
1.73	3.10	5.90	2.00	1.55	1.70	0.34	0.78	40	m	bir karis otesinde
3.10	4.47	6.25	2.00	1.70	1.55	0.36	0.78	40	m	duruyor
4.47	5.68	8.10	1.00	1.12	1.04	0.45	0.58	40	M	iki ton - tum govde
5.68	6.89	10.95	1.00	1.85	2.00	0.92	0.48	40	m	seksen kilo - domuz yalniz
6.89	8.16	7.55	1.00	1.50	1.62	0.42	0.70	40	M	gergedanin gozu
8.16	9.44	8.60	1.00	1.75	1.90	0.46	0.68	40	m	neredeyse kor
9.44	10.50	1.60	1.00	1.05	1.00	0.50	0.55	160	m	otuz metre - uzak
10.50	11.55	2.55	1.00	1.00	1.08	0.48	0.58	160	m	otesini secemiyor
11.55	12.76	6.55	1.00	1.45	1.55	0.30	0.78	40	M	domuz kipirdamadigi
12.76	13.97	7.80	1.00	1.55	1.45	0.34	0.76	40	m	surece onun icin
13.97	15.18	9.00	1.40	1.60	1.75	0.36	0.74	40	m	orada yok - boynuz ustunde
15.18	16.21	11.35	1.00	1.25	1.15	0.55	0.66	40	M	gorseydi de
16.21	17.25	11.90	1.00	1.15	1.25	0.50	0.68	40	m	degismezdi
17.25	18.64	11.75	1.20	1.40	1.52	0.50	0.80	40	m	ot yiyor - bas yerde
18.64	20.08	2.10	1.00	1.30	1.45	0.44	0.90	160	R	ASIL MESELE CUKUR
20.08	21.66	6.90	1.00	1.20	1.10	0.38	0.80	40	m	terleyemiyor
21.66	23.42	1.95	1.00	1.55	1.70	0.42	0.96	160	m	camur - serinlik
23.42	25.22	3.05	1.00	1.35	1.50	0.20	0.72	160	m	domuz icin bocek kalkani
25.22	26.33	11.55	1.00	1.20	1.30	0.48	0.68	40	M	ve o cukur
26.33	27.44	11.85	1.00	1.30	1.18	0.52	0.66	40	m	buyuk olanin
27.44	28.78	10.35	1.00	1.30	1.42	0.62	0.55	40	R	SORU - domuz cekiliyor
28.78	30.11	5.35	1.50	1.40	1.52	0.32	0.76	40	m	yoksa beklerdin mi
30.11	31.75	6.60	1.00	1.50	1.62	0.30	0.78	40	M	hala hayatta
31.75	32.95	5.55	1.50	1.58	1.45	0.32	0.76	40	m	DONGU - ilk kareye baglanir
```

## 3. spec.json

```json
{
 "caption_size": 94,
 "caption_y": 0.80,
 "caption_pop": 0.16,
 "banners": [{"t": 0.0, "dur": 1.73, "text": "GERGEDAN ONU|GÖRMÜYOR", "y": 0.135, "size": 104}],
 "arrows": [{"t": 0.28, "dur": 1.40, "x": 0.295, "y": 0.555, "angle": 135,
             "len": 410, "draw": 0.20, "pulse": 0.07, "pulse_hz": 3.2}]
}
```

## 4. Komut

```bash
python3 scripts/build.py \
  --src ham.mp4 --edl edl.tsv --vo ses.mp3 --script script.txt \
  --spec spec.json --out gergedan.mp4 \
  --usable-end 13.0 --banner-words 3 --emphasis kör kıpırdamadığı hayatta
```

`--banner-words 3` çünkü banner ilk cümleyi (`Gergedan onu görmüyor.` = 3 kelime)
kapsıyor; o kelimeler altyazıdan düşülüyor, yoksa ekran kalabalık oluyor.

## 5. Doğrulama çıktısı

```
EDL: 25 plan · 32.95s · ortalama 1.32s · 0.76 kesim/s
hece: metinde 159, seste 161 tepe · DP maliyeti 20.1
vurgulu kelime: 9/70                        (hedef %10–20)
sfx.wav  9 vuruş + 16 klink + 3 riser
cikis: -14.3 LUFS, tepe -3.50 dBFS, >tavan ornek: 0
tepe -3.24 dBFS · 1.0 aşan 0 · kırpık plato 0 · -14.3 LUFS
ses: TEMİZ
```

Bu satırların hepsini gör. Biri eksikse veya `UYARI` varsa teslim etme.

## 6. Kapak (`kapak.json`)

```json
{
 "headline": "NEDEN|KAÇMIYOR?",
 "headline_y": 0.105,
 "headline_size": 152,
 "top_shade": 0.34,
 "labels": [
  {
   "text": "2 TON",
   "x": 0.78,
   "y": 0.345,
   "size": 96,
   "color": "yellow"
  },
  {
   "text": "80 KİLO",
   "x": 0.31,
   "y": 0.705,
   "size": 96,
   "color": "yellow"
  }
 ],
 "arrows": [
  {
   "x": 0.285,
   "y": 0.545,
   "angle": 135,
   "len": 300
  }
 ]
}```

```bash
python3 scripts/cover.py --frame kare.png --spec kapak.json --out kapak.png
```

Kare: 8.45. saniye — en güçlü an değil, **en okunabilir** an. Kadraj
`crop=340:604:50:146` + `unsharp=5:5:0.9` (3.2x büyütme yumuşatıyor).

## 7. Yayın metinleri

**Başlık** — 45 karakteri geçme, ekrandaki yazıyı tekrar etme:
```
Bu domuz neden kaçmıyor?
```

**Açıklama ilk satırı:**
```
Beyaz gergedanın gözü 30 metre ötesini seçemiyor. Domuz da bunu biliyor gibi duruyor.
```

**Sabitlenmiş yorum** — yayına girer girmez:
```
Domuz mu daha cesur, gergedan mı daha umursamaz? 👇
```

---

## Bu videoda öğrenilen üç şey

**Metni videodan çıkar, videoya giydirme.** Kullanıcı önce "gergedan boynuzuyla
odunu kaldırıp domuzu kurtardı" diye bir metin gönderdi. Kareler bunu yalanladı:
domuz 2.2–4.6s'de odunun *yanında* duruyor, 9.4s'de kendi yürüyerek gidiyor,
odunun açısı 2.2s ile 12.2s'de birebir aynı. Klibe sonradan yazılmış bir yalandı.
**Metin yazmadan önce kareleri oku** — uymuyorsa kanıtı göster.

**Tek kırpma her planı kurtarmaz.** İlk kurguda `cropx` sabitti ve domuz kadrajın
sol kenarına düşüyordu; hook okunmuyordu. Plan başına kırpma orijini seçilince
özne ortaya geldi.

**Kendi kuralını da denetle.** "Gergedan ot yiyor" cümlesinin altında domuz
yürüyordu — "her cümle anlattığı şeyi göstermeli" kuralının ihlali. Kontakt
sayfasını altyazıyla birlikte bas, cümle-görüntü eşleşmesini gözle kontrol et.
