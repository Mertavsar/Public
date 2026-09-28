# Sahne tipleri — parametreler

Her sahne: `{ "bolum", "tip", "say", "p": {...}, "kaynak", "etiket" }`. Aşağıdaki alanlar `p` içindir.
Metin alanlarında `*sarı*` `~kırmızı~` `+yeşil+` ve `\n` çalışır.
Renk adları: `sari` `kirmizi` `yesil` `mavi` `mor` `turuncu` `beyaz`.

Zamanlama kuralı: giriş animasyonu sahnenin ilk ~%15'inde, sıralı öğeler en geç
%75–80'de biter. Yani sahne uzadıkça öğeler cümleye yayılır; kısa sahnede sıkışır.
Bir sahneye 4'ten fazla sıralı öğe koyma — cümle bitmeden gösterilemez.

---

### `sayi` — tek çarpıcı sayı
```json
{ "ikon": "⛽", "etiket": "Benzine beklenen zam (litre)", "deger": 12.48,
  "baslangic": 0, "onek": "+", "sonek": " ₺", "ondalik": 2,
  "yon": "up", "renk": "kirmizi", "not": "ÖTV + KDV dahil", "sayma": false }
```
- `yon`: `up` (kırmızı ▲) / `down` (yeşil ▼) / yok. `ok_renk` ile değiştir (düşüş iyi haberse vb.).
- `sayma: false` → sayı sayarak değil, doğrudan belirir. **İlk sahnede kullan** —
  akıştaki ilk kare yarıda kalmış yanlış bir sayı göstermesin.
- Sayı tek satıra sığdırılır, taşarsa küçülür.

### `karsilastir` — önce / sonra
```json
{ "baslik": "⛽ Benzin · İstanbul · 1 litre",
  "sol": { "etiket": "BUGÜN", "deger": 80.40, "renk": "beyaz" },
  "sag": { "etiket": "PERŞEMBE\n(tahmini)", "deger": 92.88, "renk": "kirmizi" },
  "onek": "", "sonek": " ₺", "ondalik": 2, "fark": "+12,48 ₺", "not": "" }
```
Çubuklar **sıfırdan** başlar (ölçek dürüst). Fark küçük görünüyorsa küçüktür —
`fark` rozeti vurguyu taşır. Sıra: sol çubuk → sağ çubuk → fark rozeti.

### `liste` — 2–4 kalem
```json
{ "baslik": "Beklenen zamlar · litre",
  "satirlar": [ { "ikon": "⛽", "metin": "Benzin", "deger": "+12,48 ₺", "renk": "kirmizi" } ],
  "not": "ÖTV + KDV dahil" }
```
`deger` metindir (biçimi sen verirsin). Satırlar sağdan kayarak sırayla gelir.

### `akis` — sebep → sonuç
```json
{ "baslik": "", "adimlar": [ { "ikon": "💥", "metin": "Mart: Orta Doğu'da savaş" },
                             { "ikon": "🛢️", "metin": "Petrol fiyatı *fırladı*" } ] }
```
Adımlar sahneye eşit yayılır; o an anlatılan adım sarı çerçeveyle öne çıkar,
öncekiler söner. 2–4 adım. Adım metni 6 kelimeyi geçmesin.

### `yigin` — bir bütünün parçaları
```json
{ "baslik": "Benzin fiyatının içi", "toplam_etiket": "Pompa fiyatı:",
  "durumlar": [
    { "etiket": "Savaştan önce", "toplam_metin": "SABİT", "renk": "beyaz",
      "parcalar": [ { "ad": "Petrol", "deger": 50, "renk": "mavi" }, { "ad": "Vergi", "deger": 50, "renk": "sari" } ] },
    { "etiket": "Petrol ~↑~ vergi +↓+", "toplam_metin": "SABİT", "renk": "yesil",
      "parcalar": [ { "ad": "Petrol", "deger": 68 }, { "ad": "Vergi", "deger": 32 } ] } ],
  "temsili": true, "onek": "", "sonek": "", "ondalik": 0 }
```
- Durumlar arasında parçalar yumuşakça büyür/küçülür. Parça renkleri ilk durumdan alınır.
- `toplam_metin` yoksa toplam sayı olarak yazılır (`onek`/`sonek`/`ondalik`).
- `temsili` varsayılan **true** → köşede "temsili" yazısı. Gerçek oranları kaynaktan
  aldıysan `false` yap. **Temsili oranlara gerçek sayı yazma.**

### `grafik` — zaman içinde değişim
Değerler aşağıda yer tutucu — her nokta kaynaktan gelir.
```json
{ "baslik": "Gram altın (TL)",
  "noktalar": [["Oca", 100], ["Şub", 110], ["Mar", 140, true], ["Nis", 125]],
  "onek": "", "sonek": " ₺", "ondalik": 0, "renk": "sari", "y_min": 90, "y_max": 150, "not": "" }
```
Çizgi kendini çizer, ucunda değer etiketi sayar. İlk ve son nokta etiketlenir;
üçüncü eleman `true` olan noktalar da. `y_min`/`y_max` vermezsen veri aralığının
±%4'ü — **eksen sıfırdan başlamaz**, bunu `not`'ta belirtmek gerekebilir.

### `hesap` — somut etki
```json
{ "baslik": "Bir depo benzin", "ikon": "🚗", "ogeler": ["50 litre", "×", "12,48 ₺", "=", "+624 ₺"] }
```
Öğeler sırayla belirir; son öğe büyük ve sarı. Tek karakterlik `× + − = ÷` işlem sayılır.
**Hesabı kendin doğrula** ve `kaynak`'a formülü yaz.

### `takvim` — tarih
```json
{ "gun": "30", "ay": "EYLÜL", "gunadi": "ÇARŞAMBA", "saat": "GECE", "not": "*Eşel mobil* sistemi bitiyor" }
```

### `baslik` — büyük ikon + satırlar
```json
{ "ikon": "🧩", "satirlar": ["EŞEL MOBİL", "= *KAYAN VERGİ*"], "boy": 104, "ikon_boy": 250,
  "not": "Fransızca: échelle mobile" }
```
Satır başına en fazla ~14 karakter (104 px'te). Uzunsa `boy` düşür.

### `soru` — geçiş
```json
{ "ikon": "🤔", "metin": "NEDEN?\n*3 SORUDA*", "boy": 120 }
```

### `kapanis`
```json
{ "metin": "TIKLA *BAKALIM*", "alt": "Gündemi basitçe öğrenmek için takip et" }
```

### `kapak` — sadece `bolum.json` → `kapak` alanı
```json
{ "ikon": "⛽", "ust": "BENZİNE", "buyuk": "+12,48 ₺", "alt": "NEDEN?" }
```
Tek fikir: bir sayı + bir soru. `buyuk` tek satıra sığdırılır.
