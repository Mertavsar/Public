# Format seçimi — konuya göre en etkili video biçimi

Günlük otomatik akışta (reference/gunluk-otomatik.md) konu seçildikten sonra
bu tablodan format seçilir. Amaç: o konuyu **en çok izletecek** görsel dil.
Ölçüt rakip veriden geliyor (BPT Haber / Onedio, Kasım 2026): başlık ilk
kareden ekranda; tartışma ve "neden?" yorum getirir; kaza/afet ve nostalji
yüksek izlenir.

## 1. Karar tablosu

| Konu türü | Örnek | Format | Motor | Tema |
|---|---|---|---|---|
| Takip verisi olan olay (uçak, gemi, araç) | Learjet kazası | **3D veri** | `stil: 3d`, `dunya: learjet` (yeni araç için yeni dünya) | `kagit` (analiz) · gece (son dakika) |
| Doğa olayı (siklon, deprem, sel, yangın) | Murasu siklonu | **3D dünya** | `stil: 3d`, `dunya: siklon` (deprem/sel için yeni dünya yaz) | gece |
| "Nasıl çalışır?" (makine, altyapı, teknoloji) | Baraj elektrik | **Çizim** | `stil: cizim`, `dunya: baraj` (konuya yeni dünya) | `kagit` |
| Ekonomi, fiyat, hayat pahalılığı | Benzin, yağ, emekli zammı | **2D açıklayıcı** | varsayılan sahneler: `sayi`, `karsilastir`, `grafik`, `hesap`, `yigin` | varsayılan |
| Nostalji / "eskiden" | 90'lar harçlık, düğün | **Gerçek foto + sayı** | `foto` sahneleri (Commons, `scripts/commons.py`) + `karsilastir` | varsayılan, `ton: eski` |
| Toplumsal tartışma (kavga, yasak, kural) | Taksi–Martı TAG | **2D açıklayıcı + akış** | `akis`, `liste`, `karsilastir`; tarafları eşit anlat | varsayılan |
| Dünya gündemi (zirve, seçim, anlaşma) | COP31, ABD seçimi | **2D + harita/sayı** | `sayi`, `liste`, `takvim`; siyasi taraf tutma | varsayılan |

Yeni bir "dünya" (3D veya çizim) gerekiyorsa ve 30 dakikada yazılamayacaksa
→ 2D açıklayıcıya düş. Kötü 3D, iyi 2D'den kötüdür.

## 2. Her formatta değişmeyenler

- **Dikey (1080×1920), 55–75 sn.** Reels + Shorts. (Yatay uzun video sadece
  kullanıcı isterse.)
- **Hook ilk 2 sn'de:** tek şok bilgi + ekranda büyük başlık/sayaç. Kalıplar:
  dev sayaç (irtifa, rüzgâr, fiyat), "geri saralım", ters köşe soru.
- **Ses:** yapay zekâ (vidIQ, Daniel `onwK4e9ZLuTAKqWW03F9`) `atempo=1.1`,
  render `--sikistir` (hizalama özgün seste, düzeltildi). Tempo hiç durmaz.
- **Üst bant yok** (bölüm şeridi, etiket, kaynak satırı — `ust_bant` kapalı).
- **Kapanış:** "Merak ettiysen, tıkla bakalım." — ölümlü kaza/afette yerine
  sadece "Gelişmeleri takip etmek için abone ol."
- **Reels kapağı:** `scripts/reels_kapak.mjs` (logo, kırmızı çerçeve, kategori
  etiketi, kırmızı vurgu satırı). Kategoriler: GÜNDEM · DÜNYA · NOSTALJİ ·
  NASIL ÇALIŞIR? · EKONOMİ.

## 3. Hassas konular

- Ölüm/afet: çarpma/ceset/yaralı görüntüsü yok; neden için spekülasyon yok
  ("henüz bilinmiyor"); beğen/yorum çağrısı yok.
- 3D rota/çizim gerçeği birebir göstermiyorsa ekranda **"temsili"**.
- Siyasi polemik, suç iddiası, kişi hedefleme → **konu seçme**.
