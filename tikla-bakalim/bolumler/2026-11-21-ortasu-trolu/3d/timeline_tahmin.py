# Sessiz taslak için tahmini zaman çizelgesi (ses gelince sentalign ile değişir).
import json, re, sys
S = [
 ("title", "En çok merak edilen konu: ortasu trolü!"),
 ("apart", "Bu iki tekne birbirinden uzaklaştıkça, aradaki hamsiler kaçamıyor."),
 ("dive", "Çünkü aralarında, suyun ortasında asılı duran görünmez bir tuzak var."),
 ("school", "Adım adım göstereyim."),
 ("school2", "Bu videoyu paylaş ve abone ol ki herkes, sofrasındaki balığın ne kadar zor bir işle geldiğini görsün."),
 ("bridge", "Her şey bir ekranla başlıyor."),
 ("sonar", "Ana teknedeki sonar, suyun altındaki sürüyü bir leke gibi gösteriyor."),
 ("depth", "Ama hamsi dipte değil, suyun ortasında."),
 ("depthq", "Ağ oraya nasıl ulaşıyor?"),
 ("deploy", "Dev bir ağ denize bırakılıyor ve iki ucu, iki ayrı tekneye bağlanıyor."),
 ("push", "Şimdi işin en akıllıca kısmı geliyor!"),
 ("like", "İşine yaradıysa bir beğen bırak."),
 ("nodoor", "Bu ağın ağzını açık tutan ne bir kapı var, ne bir makine."),
 ("secret", "Ağzı, iki teknenin arasındaki mesafe açıyor."),
 ("widen", "Tekneler açıldıkça ağın ağzı genişliyor!"),
 ("levelq", "Peki ağ, sürünün hizasına nasıl iniyor?"),
 ("level", "Teknelerin hızı ve halatın boyu ayarlanarak."),
 ("hard", "Ama bu iş hiç kolay değil."),
 ("radio", "İki tekne sürekli haberleşip aynı hızda gitmek zorunda."),
 ("narrow", "Birbirlerine yaklaşırlarsa ağın ağzı daralır, sürü kaçar."),
 ("storm", "Üstelik av sezonu sonbahar ve kış; yani Karadeniz'in en sert aylarında, dalgaların arasında."),
 ("haul", "Sonunda sürü, ağın daralan ucunda toplanıyor ve ağ tekneye çekiliyor."),
 ("map", "Bu ağ sadece iki gemiyle ve izinle çekilebiliyor; Marmara'da, Ege'de ve Akdeniz'de ise genel olarak yasak."),
 ("outro", "Sıradaki avcılık hangisi olsun?"),
 ("comment", "Yorumlarda sen seç."),
 ("sign", "Merak ettiysen, tıkla bakalım!"),
 ("loop", "Ve şu an Karadeniz'de bir yerde, iki tekne yine birbirinden uzaklaşıyor."),
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
