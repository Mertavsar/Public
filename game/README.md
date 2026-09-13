# Survivor3D

3D roguelite survivor, Godot 4.3, Android + iOS hedefli.

## Neden bu mimari

Oyunun savaş matematiği render'dan tamamen ayrı (`scripts/combat/`). Aynı
sayıları hem başsız simülasyon hem de canlı oyun okur. Bunun pratik sonucu:
**dengeyi kimsenin oyunu oynamasına gerek kalmadan ayarlayabiliyoruz.**

## Çalıştırma

Denge raporu — mevcut ayarların sağlıklı olup olmadığını söyler:

    godot --headless --path game --script res://sim/balance_sim.gd

Otomatik ayarlayıcı — doğru zorluk değerini ikili aramayla bulur:

    godot --headless --path game --script res://sim/tune.gd

Çıkan `hp_growth_per_10s` değeri `autoload/balance.gd` dosyasına yazılır.
Bu değeri elle değiştirme; tuner'ı çalıştır.

## Mevcut denge durumu

Son ayarlama sonrası, meta seviyesine göre kazanma oranı:

| Meta seviyesi | Kazanma | Medyan hayatta kalma |
|---|---|---|
| 0 (yeni oyuncu) | 7.3% | 274s / 300s |
| 5 | 32.5% | 291s |
| 10 | 52.2% | 300s |
| 20 | 76.1% | 300s |

Hedef bant meta 5'te %25-40. Yeni oyuncunun bitişe 26 saniye kala kaybetmesi
kasıtlı: "az kalmıştı" hissi bu türde en güçlü geri dönüş sebebi.

## Yapı

    autoload/balance.gd            Tüm ayarlanabilir sayılar. Tek doğruluk kaynağı.
    scripts/combat/combat_model.gd Başsız run modeli. Node yok, fizik yok.
    scripts/combat/upgrade_pool.gd Seviye atlama draftı ve yapay oyuncu seçimi.
    sim/balance_sim.gd             Denge raporu.
    sim/tune.gd                    Otomatik zorluk ayarlayıcı.

## Sıradaki adımlar

- [ ] Oynanabilir 3D sahne: oyuncu, düşman sürüsü, otomatik silah, XP küresi
- [ ] Sanal joystick, tek parmak kontrol
- [ ] Seviye atlama UI'ı (3 kart seçimi)
- [ ] Meta upgrade ekranı ve kayıt sistemi
- [ ] Firebase: analytics, remote config, cloud save, push
- [ ] Reklam (rewarded revive) + IAP
- [ ] Android CI, sonra iOS build

## Oynanabilir sahne (Aşama 2)

    godot --headless --path game --script res://sim/play_test.gd   # gerçek sahneyi bot oynar
    godot --headless --path game --script res://sim/tune_game.gd   # oyunu oynayarak ayarlar

Düşmanlar, mermiler ve XP küreleri düğüm değil, düz dizilerde tutulup tek
MultiMesh ile çiziliyor. Her düşman ayrı düğüm olsaydı orta seviye Android'de
600 düşman çizilemezdi.

Tarayıcı önizlemesi (aynı sayılar, three.js ile):
https://claude.ai/code/artifact/b42f8fdf-8ca3-4b8b-9eb3-0c8b7dcc7685

### Play test'in yakaladığı hatalar

1. Silah hedefin **durduğu** yere ateş ediyordu; 9 metrede mermiler %77 ıskalıyordu.
   Artık varış anındaki konuma nişan alıyor.
2. Arena sınırsızdı ve düşmanlar oyuncudan yavaştı — düz çizgide koşmak
   kusursuz stratejiydi. Arena 28 m, doğumların %65'i gidilen yöne.

### Açık sorun: tune_game.gd yanlış kolu çeviriyor

Düşman hızını arıyor ama kazanma oranı hızla birlikte **artıyor** (%83 → %100):
hızlı düşmanlar topluca geliyor, silah onları daha verimli biçiyor. İkili arama
tek yönlü değişim varsayar, o yüzden bu kol geçersiz. Zorluk kolu düşman canı
olmalı — model tarafında zaten öyle çalışıyor.

## Kadro (Aşama 2b)

Dört oynanabilir karakter, her biri tek bir dürüst takas üzerine kurulu.
"Dengeli ama farklı tatta" bir kadro oyuncuya kilit açacak bir sebep vermez,
o yüzden her karakter bir şeyde gerçekten iyi, başka bir şeyde gerçekten kötü.

| Karakter | Takas | Kilit |
|---|---|---|
| Nöbetçi | Dengeli başlangıç. Hiçbir yönü uç değil. | Açık |
| Avcı | Uzun menzil, hızlı hafif atış. Düşman sertleşince zorlanır. | 800 |
| Koruyucu | Yavaş ve dayanıklı, mermileri sırayı deler. | 1600 |
| Sürgün | Çok hızlı, çok kırılgan, geniş saçma. | 2600 |

Modeller `art/roster.glb` içinde, Blender'da prosedürel olarak üretildi.
Her biri 130-300 poligon. Okunabilirlik bütün oranları belirledi: oyuncu
kalabalık bir arenaya yukarıdan bakarken yüz değil siluet ve renk görür.

    godot --headless --path game --script res://sim/roster_test.gd    # kadro dengeli mi
    godot --headless --path game --script res://sim/tune_roster.gd    # her karakteri ayrı ayarla

### Kadroyu elle dengelemek iki kez başarısız oldu

Birinci denemede Koruyucu dört stat birden kaybetti ve %88'den %38'e düştü;
Sürgün üç stat birden kazandı ve %50'den %100'e çıktı. Aynı anda birden fazla
kolu çevirince hiçbir değişiklik tek bir sebebe bağlanamıyor.

Karakterler bir run'da birbirleriyle hiç karşılaşmadığı için her biri bağımsız
tek boyutlu bir problem, ve hasar kazanma oranını tek yönde hareket ettiriyor.
`tune_roster.gd` bu yüzden her karakteri ayrı ayrı, aynı hedefe ayarlıyor.

## Juice katmanı (Aşama 2c)

Modeller hâlâ blockout, ama geri bildirim katmanı eklendi. Bir oyunun
profesyonel hissettirmesinin çoğu modelden değil buradan gelir:

- İsabet eden düşman bir kare beyaza patlıyor ve %35 büyüyor (MultiMesh
  instance rengi). Bu olmadan isabet eden atışla ıskalayan atış aynı görünüyor.
- Ölen düşman parçalanıyor — `debris.gd`, havuzlanmış, yerçekimli, tek draw call.
- Silah her atışta zemine ışık düşürüyor (`Player/Muzzle`).
- Hasar alınca kamera sarsılıyor ve oyun 50 ms duraklıyor (hit-stop).
- Ortamda glow, ACES tonemap ve hafif kontrast/doygunluk ayarı var.

Hiçbiri tek bir denge sayısını değiştirmiyor; hepsi oyunun okunuşunu değiştiriyor.

### Karakter modelleri için engel

`quaternius.com` ve `poly.pizza` ortamın ağ politikası tarafından engelli
(proxy 403 döndürüyor). Hazır riglenmiş/animasyonlu paket buradan indirilemiyor.
İki yol var: paketi indirip repoya koymak, ya da ortamın ağ erişimini
genişletmek. Paket geldiğinde bağlanacak sıra: animasyon state machine
(idle / koşu / atış / hasar / ölüm), sonra kalıcı upgrade ekranı.
