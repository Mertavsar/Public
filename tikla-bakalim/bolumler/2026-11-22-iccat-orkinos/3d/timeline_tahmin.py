# Sessiz taslak için tahmini zaman çizelgesi (ses gelince sentalign ile değişir).
import json, re, sys
S = [
 ("hook", "Takipçimizden gelen soru: ICCAT orkinos avcılığı!"),
 ("giant", "Akdeniz'de yakalanan dev orkinoslar tekneye alınmıyor."),
 ("tow0", "Canlı canlı, denizin ortasında günlerce taşınıyor."),
 ("step", "Adım adım göstereyim."),
 ("cta", "Bu videoyu paylaş ve abone ol ki herkes bu zor işi görsün."),
 ("map1", "ICCAT, Atlantik orkinoslarını koruyan uluslararası bir komisyon."),
 ("map2", "Mavi yüzgeçli orkinosu kimin, ne kadar avlayacağına o karar veriyor."),
 ("quota", "Türkiye'nin payı yılda yaklaşık üç bin ton."),
 ("fleet", "Bu kota sadece izinli gırgır gemileri arasında paylaştırılıyor."),
 ("season", "Av, mayıs ortasından temmuz başına kadar Akdeniz'in açıklarında yapılıyor."),
 ("encircle", "Gırgır, sürünün etrafını dev bir ağla çeviriyor."),
 ("purse", "Ama balık tekneye çekilmiyor."),
 ("purseq", "Peki ne oluyor?"),
 ("transfer", "Ağın yanına yüzen bir kafes getiriliyor ve orkinoslar canlı olarak bu kafese geçiriliyor."),
 ("gate", "Şimdi işin en sıkı kısmı geliyor!"),
 ("like", "İşine yaradıysa bir beğen bırak."),
 ("observer", "Her gemide bir ICCAT gözlemcisi var."),
 ("camera", "Her transfer videoya kaydediliyor, kafese giren balıklar özel kameralarla sayılıyor ve ölçülüyor."),
 ("small", "Otuz kilodan küçük orkinos avlamak yasak."),
 ("release", "Kota aşılırsa fazla balık, canlıysa denize geri bırakılıyor."),
 ("tow", "Sonra kafes, çekici teknelerle çok yavaş, günlerce çekilerek çiftliklere götürülüyor."),
 ("farm", "İzmir'deki tesislerde orkinoslar yaklaşık yedi ay boyunca sardalya, hamsi ve uskumruyla besleniyor."),
 ("export", "Aralık ve ocakta hasat ediliyor ve büyük kısmı Japonya ile Güney Kore'ye gidiyor."),
 ("outro", "Sıradaki avcılık hangisi olsun?"),
 ("comment", "Yorumlarda sen seç."),
 ("sign", "Merak ettiysen, tıkla bakalım!"),
 ("loop", "Ve şu an Akdeniz'de bir yerde, dev bir kafes yavaşça yol alıyor."),
]
t = 0.25; out = []
for sid, txt in S:
    w = txt.split()
    d = max(1.3, len(w) / 2.75 + 0.35)
    words = []; k = t
    for x in w:
        dw = d * (len(x) + 2) / sum(len(y) + 2 for y in w)
        words.append({"w": x, "s": round(k, 3), "e": round(k + dw, 3)}); k += dw
    out.append({"id": sid, "text": txt, "s": round(t, 3), "e": round(t + d, 3), "words": words})
    t += d + 0.18
json.dump({"END": round(t + 0.4, 2), "S": out}, open(sys.argv[1], "w"), ensure_ascii=False, indent=0)
print("toplam", round(t, 1), "sn")
