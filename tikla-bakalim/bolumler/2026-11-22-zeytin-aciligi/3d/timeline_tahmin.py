# Sessiz taslak için tahmini zaman çizelgesi (ses gelince sentalign ile değişir).
import json, re, sys
S = [
 ("bite", "Dalından kopardığın zeytini ısırırsan yiyemezsin; o kadar acı."),
 ("table0", "Ama sofradaki zeytin tatlı."),
 ("secret0", "Asıl sır tuzda değil, zeytinin içinde olan bir değişimde."),
 ("step", "Adım adım göstereyim."),
 ("cta", "Bu videoyu paylaş ve abone ol ki herkes sofrasındaki zeytinin hikâyesini öğrensin."),
 ("oleu", "Zeytinin acısını veren maddenin adı oleuropein."),
 ("ripe", "Yeşil zeytinde daha çok bulunuyor, zeytin olgunlaştıkça azalıyor ama yine de yenmeyecek kadar acı kalıyor."),
 ("howq", "Peki bu acılık nasıl çıkıyor?"),
 ("water0", "İlk yol su."),
 ("water", "Zeytin suda bekletildikçe acı madde yavaş yavaş suya geçiyor ve su değiştiriliyor."),
 ("push", "Şimdi işin en akıllıca kısmı geliyor!"),
 ("like", "İşine yaradıysa bir beğen bırak."),
 ("crackq", "Zeytin neden kırılıyor ya da çiziliyor?"),
 ("crack", "Çünkü kabuk açılınca acı, suya çok daha hızlı geçiyor."),
 ("magic", "Asıl sihir ise salamurada oluyor."),
 ("microbe", "Tuzlu suyun içindeki küçük canlılar acı maddeyi parçalıyor ve onu acı olmayan bir maddeye dönüştürüyor."),
 ("months", "Bu yüzden salamura zeytin aylarca bekliyor."),
 ("factory", "Fabrikalarda yeşil zeytin bazen önce hafif bir çözeltide birkaç saat bekletiliyor, yıkanıyor ve sonra yine salamurada aylarca dinlendiriliyor."),
 ("patience", "Yani hangi yöntem olursa olsun, sofradaki her zeytin bir sabır işi."),
 ("outro", "Sıradaki konu hangisi olsun?"),
 ("comment", "Yorumlarda sen seç."),
 ("sign", "Merak ettiysen, tıkla bakalım!"),
 ("loop", "Ve şu an Ege'de bir küpün içinde, bir zeytin yavaş yavaş tatlanıyor."),
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
