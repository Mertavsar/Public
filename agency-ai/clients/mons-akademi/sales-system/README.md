# Mons Akademi — Lead Ön-Analiz Sistemi

Satış temsilcisinin **leade dokunmadan önce** 30 saniyede okuduğu hazırlık kartını
üreten kural seti.

## Bu sistem ne yapar, ne yapmaz

Satış kanalı: **Meta lead formu → telefonla arama.** Kişi bir mesaj yazmadı, form
doldurdu ve tanımadığı bir numaradan aranacak. Kart bu aramanın hazırlığıdır.

**Yapar:** Lead bilgisinden (eğitim, meslek, yaş, şehir, kaynak, kaçıncı arama)
bir *hazırlık kartı* üretir: muhtemel motivasyon, açılış cümlesi, sorulacak iki soru,
beklenen itirazlar ve cevapları, fiyatın ne zaman söyleneceği, takip planı.

**Yapmaz:** Kişilik analizi yapmaz, "bu kişi alır / almaz" demez, fiyat veya indirim
kararı vermez, konuşmanın tamamını yazmaz.

## Neden bu sınır var

Elimizdeki alanlar (telefon, ad, soyad, meslek, yaş, şehir) **zayıf sinyallerdir.**
Tahmin gücü sırası:

1. **Hangi eğitim** — en güçlü sinyal. Dört eğitimin alıcısı dört ayrı insan.
2. **Hangi reklam / hangi kreatif** — kişinin kafasındaki vaat oradan gelir.
3. **İlk mesajında ne yazdığı** — varsa, mesleğinden daha değerlidir.
4. **Meslek** — orta.
5. **Yaş** — zayıf.
6. **Şehir** — en zayıf. Tek başına hiçbir kararı değiştirmez.

Sistem bu sırayla çalışır. Yaş ve şehirden karakter çıkaran bir kart, kendinden emin
ama yanlış cümleler üretir; bu satışı kaybettirir.

Kartın her satırı **hipotezdir.** Kişi konuşmaya başladığı an kart güncellenir veya
çöpe atılır. Kartın söylediği ile kişinin söylediği çelişirse **kişi haklıdır.**

## Değişmez kurallar (guardrail)

1. **Etiket fiyatı değiştirmez.** Hiçbir profil "indirim yap" demez. İndirim yetkisi
   yalnızca marka sahibinden gelir.
2. **İlk mesajda fiyat verilmez.** Önce ihtiyaç tespiti. (Fiyatın erken verilmesi en
   yaygın satış hatasıdır.)
3. **Kart ilk iki mesajı ve itiraz cevaplarını şekillendirir**, konuşmanın tamamını değil.
   Metni olduğu gibi okuyan temsilci robot gibi duyulur, dönüşüm düşer.
4. **Yasak vaatler:** iş garantisi, gelir garantisi, "devlet onaylı", sahip olmadığımız
   bir akreditasyon, "kesin sonuç". Sertifikanın tam olarak ne olduğu `objections.md`
   içinde yazılı — orada yazmayan hiçbir şey söylenmez.
5. **Kişi hakkında yargı notu yazılmaz.** Nota yalnızca davranış ve olgu yazılır
   ("3 gün cevap vermedi", "taksit sordu"), yorum değil ("parası yok").
6. **KVKK:** bu alanlar kişisel veridir. Profil notu üretmek bir işleme faaliyetidir;
   aydınlatma metni ve rıza kaydı olmadan sistem canlıya alınmaz.

## Dosyalar

| Dosya | İçerik |
|---|---|
| `lead-brief.md` | Kartın formatı ve nasıl doldurulacağı |
| `call-flow.md` | Telefon akışı: hız, ilk 10 saniye, açmayan lead, numara itibarı, KVKK |
| `profiles.md` | Eğitim bazlı alıcı hipotezleri + meslek/yaş/şehir düzelticileri |
| `objections.md` | İtiraz → cevap kalıpları ve yasak vaatler |
| `outcome-log.md` | Sonuç logu — sistemin öğrenmesini sağlayan tek şey |

## Olgunluk seviyeleri

**Sıfırdan projede kartın asıl işi:** ekip de yeni olduğu için kart bir satış hilesi
değil, **onboarding materyalidir.** Yeni temsilci ilk günden dört eğitimin farkını,
hangi itirazın nereden geldiğini ve neyin söylenemeyeceğini buradan öğrenir. İlk 20
konuşma kaydedilir veya dökülür (`conversations/`) ve kartla karşılaştırılır — gerçek
eğitim orada olur.

- **Seviye 0 (bugün, maliyetsiz):** `profiles.md` + `objections.md` basılı/açık durur,
  temsilci leadin eğitimine ve mesleğine bakıp kartı kendi doldurur.
- **Seviye 1:** Tek sayfalık araç — bilgiler girilir, kart otomatik çıkar. Kural tabanlı,
  internet ve model gerektirmez.
- **Seviye 2:** Lead + ilk mesaj metni modele verilir, kişiye özel kart üretilir; sonuç
  logu geri beslenir ve hipotezler zamanla FACT'e döner.

Seviye 2'ye **sonuç logu 100-150 satıra ulaşmadan geçilmez.** O veri olmadan model de
tahmin üretir, sistem sadece daha pahalı bir tahmin makinesi olur.
