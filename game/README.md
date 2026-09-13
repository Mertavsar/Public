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
