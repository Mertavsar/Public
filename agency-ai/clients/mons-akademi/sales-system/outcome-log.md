# Sonuç logu — sistemin öğrenmesini sağlayan tek şey

Kart üretmek kolaydır. Kartın **işe yarayıp yaramadığını bilmek** zordur ve asıl değer
oradadır. Bu log tutulmazsa sistem hiçbir zaman tahminden öteye geçmez.

## Tutulacak alanlar

| Alan | Neden |
|---|---|
| tarih | Dönem karşılaştırması |
| lead_id | Tekrarları ayırmak |
| egitim | Dört eğitimden hangisi — en güçlü kırılım |
| kaynak | Hangi reklam/kampanya — beklenti oradan gelir |
| meslek | Profil hipotezini doğrulamak |
| yas | Aynı |
| sehir | Aynı |
| ilk_cevap_dk | **En kritik alan.** Leade kaç dakikada dönüldü |
| temsilci | Kişi bazlı fark var mı |
| kart_kullanildi | E/H — sistemin etkisini ölçen alan |
| ilk_itiraz | Hangi itiraz en çok geliyor |
| dokunus_sayisi | Takip disiplini ölçüsü |
| sonuc | satildi / kayip / ulasilamadi / takipte |
| tutar | Satıldıysa |
| kayip_sebebi | Fiyat / zaman / ilgisiz / ulaşılamadı / sessiz |

## CSV başlığı (kopyala, Sheets'e yapıştır)

```
tarih,lead_id,egitim,kaynak,meslek,yas,sehir,ilk_cevap_dk,temsilci,kart_kullanildi,ilk_itiraz,dokunus_sayisi,sonuc,tutar,kayip_sebebi
```

## Sıfırdan projede: önce log, sonra test

Marka yeni. İlk 150 leadde kartlı/kartsız testi **kurulmaz** — hacim yok ve gelen az
sayıda leadin yarısını hazırlıksız harcamak pahalıdır. Bu fazda kart **herkese**
uygulanır, log **lead #1'den** itibaren tutulur.

Logun ilk işi kartı ölçmek değil, şu dört sayıyı hiç yoktan var etmek:
lead maliyeti · lead kalitesi · ilk cevap süresi · lead→satış dönüşümü.
Bu dördü elde olmadan hiçbir karar veriye dayanmaz.

İlk 30 günün en değerli çıktısı ise bir sayı değil, bir liste: **en sık gelen üç
itiraz.** Teklif ve reklam mesajı ona göre yeniden yazılır.

## Kart etkisini ölçme (T1 testi — 150 lead biriktikten sonra)

İki hafta boyunca leadler ikiye ayrılır: **tek numaralı lead_id → kartlı**,
**çift numaralı → kartsız.** Temsilciler karışık olmalı, yoksa ölçtüğün şey kart değil
temsilcidir.

Sonunda tek soru: kartlı grubun dönüşümü kartsız gruptan yüksek mi?
- Yüksekse → sistem işe yarıyor, Seviye 2'ye geçilir.
- Fark yoksa → kartın içeriği yanlış; profiller değişir, sistem değil.
- Düşükse → kart temsilciyi script'e hapsediyor; kısaltılır.

## Uyarı

150 leadin altında çıkan fark **gözlemdir, kanıt değildir.** Küçük örneklemde iki-üç
satışın yeri değişince sonuç tersine döner. Erken karar verme.

## KVKK notu

Bu log kişisel veri içerir. Telefon ve tam isim **analiz tablosunda tutulmaz** —
lead_id ile eşleştirilir. Ham lead verisi satış panelinde/CRM'de kalır, analiz kopyası
kimliksizleştirilir.
