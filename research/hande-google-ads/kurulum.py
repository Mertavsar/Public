"""Psikoterapi, Hipnoterapi, Çift Terapisi kampanyaları için Google Ads Editor CSV'leri üretir."""
import csv, os, sys
OUT=sys.argv[1]; os.makedirs(OUT,exist_ok=True)
SITE="https://handecelikmehmetoglu.com.tr"
K={  # kampanya -> reklam grubu -> [(kelime, eşleme)]
"Psikoterapi":{
 "Psikoterapi":[("bursa psikoterapi","Phrase"),("psikoterapi bursa","Phrase"),("bursa psikoterapist","Exact"),("psikoterapist bursa","Exact"),("bursa terapist","Exact"),("terapist bursa","Exact"),("bursa terapist önerisi","Phrase"),("bireysel terapi bursa","Phrase")],
 "Kaygı ve Panik":[("panik atak tedavisi bursa","Phrase"),("bursa panik atak","Phrase"),("anksiyete tedavisi bursa","Phrase"),("kaygı bozukluğu bursa","Phrase"),("depresyon terapisi bursa","Phrase"),("travma terapisi bursa","Phrase")]},
"Hipnoterapi":{
 "Hipnoterapi":[("bursa hipnoterapi","Exact"),("hipnoterapi bursa","Exact"),("bursa hipnoterapist","Exact"),("hipnoterapist bursa","Exact"),("bursa hipnoterapi ücretleri","Phrase"),("hipnoterapi","Exact")],
 "Hipnoz Tedavisi":[("bursa hipnoz","Exact"),("hipnoz bursa","Exact"),("bursa hipnoz uzmanı","Exact"),("hipnoz tedavisi bursa","Phrase"),("hipnoz terapisi bursa","Phrase"),("hipnoz terapi bursa","Phrase"),("hipnoz yapan doktor bursa","Phrase"),("hipnozla sigara bırakma bursa","Phrase")]},
"Çift terapisi":{
 "Çift Terapisi":[("çift terapisi bursa","Exact"),("bursa çift terapisi","Exact"),("evlilik terapisti bursa","Exact"),("bursa evlilik terapisti","Exact"),("bursa ilişki terapisti","Phrase"),("evlilik danışmanlığı bursa","Phrase")],
 "Aile Terapisi":[("bursa aile terapisi","Exact"),("aile terapisti bursa","Exact"),("bursa aile terapisti","Exact"),("aile terapisi bursa","Exact"),("bursa aile danışmanı","Exact"),("aile danışmanı bursa","Phrase")]},
}
# kampanyalar arası negatifler (aramalar doğru kampanyaya gitsin)
CROSS={
"Psikoterapi":["hipnoz","hipnoterapi","hipnoterapist","çift","evlilik","aile terapi","aile danışman","ilişki terapi","oyun terapi","hande çelik"],
"Hipnoterapi":["çift","evlilik","aile terapi","aile danışman","oyun terapi","hande çelik","eğitimi","sahne","film","parfüm","müziği","kitap","izle"],
"Çift terapisi":["hipnoz","hipnoterapi","oyun terapi","hande çelik","aile dizimi","aile hekimi"],
}
EXTRA_NEG=["yusuf kala","cem gündüz","ali algın","sadık cesur","ergoterapi","ergoterapist","emdr","meridyen","gtos","mora terapi","nöral terapi","ozon","manuel terapi","rezonans","scio","tms","cinsel terap"]
RSA={
"Psikoterapi|Psikoterapi":dict(path=("bursa","psikoterapi"),url=SITE+"/",
 H=["Bursa'da Psikoterapi","Uzm. Dr. Hande Ç. Mehmetoğlu","Bütüncül Psikoterapi","Beden ve Zihin Birlikte","Hekim Gözüyle Ruh Sağlığı","Bireysel Terapi Randevusu","Yetişkin ve Ergen Terapisi","Tahliller Temiz, Ağrı Var mı?","Uykusuzluk ve Stres","Aile Hekimliği Uzmanı","Online Terapi Seçeneği","Osmangazi, Efe Plaza","Gizlilik Esaslı Görüşme","Bursa'da Terapist Arıyorum","Randevu İçin Arayın"],
 D=["Psikoterapide bedendeki belirtilerle duygular arasındaki bağı birlikte ele alıyoruz.","Psikodinamik, bağlanma odaklı ve psikodrama temelli bütüncül bir yaklaşımla çalışıyoruz.","Aile hekimliği uzmanı ve psikoterapistle, gizlilik esaslı bireysel görüşmeler.","Yüz yüze Osmangazi'de ya da online görüşme. Randevu için arayın veya sitemizden yazın."]),
"Psikoterapi|Kaygı ve Panik":dict(path=("bursa","kaygi-panik"),url=SITE+"/",
 H=["Kaygı ve Panik Atak Desteği","Uzm. Dr. Hande Ç. Mehmetoğlu","Panik Atakta Yalnız Değilsiniz","Kaygı Döngüsünü Kıralım","Bursa'da Psikoterapi","Önce Hekim Değerlendirmesi","Uykusuzluk ve Stres","Bedensel Belirtiler ve Kaygı","Bütüncül Psikoterapi","Aile Hekimliği Uzmanı","Online Terapi Seçeneği","Osmangazi, Efe Plaza","Gizlilik Esaslı Görüşme","Bireysel Terapi Randevusu","Randevu İçin Arayın"],
 D=["Panik atak, kaygı ve stres yaşayanlar için bireysel psikoterapi. Aile hekimi gözüyle.","Çarpıntı, nefes darlığı gibi bedensel belirtileri önce hekim olarak değerlendiriyoruz.","Kaygıyla baş etmeyi birlikte öğreniyoruz. Süreci ilk görüşmede açıkça anlatıyoruz.","Yüz yüze Osmangazi'de ya da online görüşme. Randevu için arayın veya sitemizden yazın."]),
"Hipnoterapi|Hipnoterapi":dict(path=("bursa","hipnoterapi"),url=SITE+"/bursa-hipnoz/",
 H=["Bursa Hipnoterapi","Uzm. Dr. Hande Ç. Mehmetoğlu","Hekim Eşliğinde Hipnoterapi","Bakanlık Onaylı Hipnoz Eğitimi","Hipnozda Kontrol Sizde Kalır","Önce Hekim Değerlendirmesi","2010'dan Beri Hipnoz","Kaygı ve Stres İçin Hipnoz","Sigara Bırakmada Destek","Hipnoterapi Nasıl Uygulanır?","Aile Hekimliği Uzmanı","Osmangazi, Efe Plaza","Hipnoterapi Randevusu","Ücret Bilgisi İçin Arayın","Hemen Arayın"],
 D=["Tıbbi hipnoz, Bakanlık sertifikalı hekim tarafından, ön değerlendirmeyle uygulanır.","Hipnozda uyumazsınız; bilinciniz açık, kontrol sizdedir. Süreci ilk görüşmede anlatıyoruz.","Kaygı, stres ve alışkanlıklarla baş etmede hipnoz, terapinin parçası olarak kullanılır.","Osmangazi'de, metroya yakın. Randevu ve bilgi için arayın ya da web sitemizi ziyaret edin."]),
"Hipnoterapi|Hipnoz Tedavisi":dict(path=("bursa","hipnoz"),url=SITE+"/bursa-hipnoz/",
 H=["Bursa'da Hipnoz Tedavisi","Hipnoz Terapisi Bursa","Uzm. Dr. Hande Ç. Mehmetoğlu","Bursa Hipnoz Uzmanı Hekim","Hipnoz Yapan Doktor","Hipnozda Kontrol Sizde Kalır","Bakanlık Onaylı Hipnoz Eğitimi","Hipnozla Sigara Bırakma","Kaygı ve Stres İçin Hipnoz","Önce Hekim Değerlendirmesi","Hipnoz Kimlere Uygulanmaz?","Osmangazi, Efe Plaza","Hipnoz Randevusu","Aile Hekimliği Uzmanı","Hemen Arayın"],
 D=["Hipnoz tedavisi, sertifikalı hekim tarafından önce sağlık değerlendirmesiyle uygulanır.","Sigara, kaygı ve stresle baş etmede hipnoz bir programın parçası olarak kullanılır.","Hipnoz herkese uygulanmaz. Size uygun olup olmadığını ilk görüşmede birlikte görüyoruz.","Osmangazi'de, metroya yakın. Randevu ve bilgi için arayın ya da web sitemizi ziyaret edin."]),
"Çift terapisi|Çift Terapisi":dict(path=("bursa","cift-terapisi"),url=SITE+"/aile-danismani-cift-terapisti-bursa/",
 H=["Çift Terapisi Bursa","Uzm. Dr. Hande Ç. Mehmetoğlu","Evlilik Terapisti Bursa","Aynı Kavga Tekrar mı Ediyor?","İletişimi Yeniden Kurun","Satir Aile Terapisi Eğitimi","İlişki Danışmanlığı","Çift Görüşmesi Randevusu","Boşanma Sürecinde Destek","Online Görüşme Seçeneği","Gizlilik Esaslı Görüşme","Osmangazi, Efe Plaza","Aile Hekimliği Uzmanı","Ücret Bilgisi İçin Arayın","Hemen Arayın"],
 D=["Tekrarlayan kavgalar ve iletişim sorunlarında çift ve evlilik terapisi. Randevu alın.","Satir aile terapisi eğitimi almış hekimle, gizlilik esaslı çift görüşmeleri.","Kavganın altındaki ihtiyacı birlikte görmeye ve iletişimi yeniden kurmaya çalışıyoruz.","Yüz yüze Osmangazi'de ya da online. Bilgi ve randevu için arayın ya da sitemize bakın."]),
"Çift terapisi|Aile Terapisi":dict(path=("bursa","aile-terapisi"),url=SITE+"/aile-danismani-cift-terapisti-bursa/",
 H=["Bursa Aile Terapisi","Uzm. Dr. Hande Ç. Mehmetoğlu","Bursa Aile Danışmanı","Bakanlık Onaylı Aile Danışmanı","Aile İçi İletişim","Ebeveynlik Desteği","Ergenle İletişim Sorunları","Boşanma Sürecinde Destek","Aile Görüşmesi Randevusu","Satir Aile Terapisi Eğitimi","Online Görüşme Seçeneği","Gizlilik Esaslı Görüşme","Osmangazi, Efe Plaza","Aile Hekimliği Uzmanı","Hemen Arayın"],
 D=["Aile içi iletişim, ebeveynlik ve ergenlik dönemi sorunlarında aile danışmanlığı.","Bakanlık onaylı aile danışmanlığı eğitimi almış hekimle, gizlilik esaslı görüşmeler.","Boşanma sürecinde çocuklarla iletişim ve ebeveynlik konularında destek sunuyoruz.","Yüz yüze Osmangazi'de ya da online. Bilgi ve randevu için arayın ya da sitemize bakın."]),
}
SITELINK=[("Hakkımda","Hekim ve terapist olarak yolculuk",SITE+"/hakkimda/"),("Tıbbi Hipnoz","Hipnoz nasıl uygulanır?",SITE+"/bursa-hipnoz/"),("Çift ve Aile Terapisi","İletişimi yeniden kurmak",SITE+"/aile-danismani-cift-terapisti-bursa/"),("Çocuk Oyun Terapisi","Çocuklar oyunla anlatır",SITE+"/cocuk-oyun-terapisi-bursa/")]
CALLOUT=["Aile Hekimliği Uzmanı","Online Görüşme","Metroya Yakın","Gizlilik Esaslı","Bakanlık Onaylı Eğitimler"]
err=[]
for k,v in RSA.items():
    for h in v["H"]:
        if len(h)>30: err.append((k,"başlık",len(h),h))
    for d in v["D"]:
        if len(d)>90: err.append((k,"açıklama",len(d),d))
    for p in v["path"]:
        if len(p)>15: err.append((k,"yol",len(p),p))
    if len(v["H"])!=15 or len(v["D"])!=4: err.append((k,"adet",len(v["H"]),len(v["D"])))
for t,d,u in SITELINK:
    if len(t)>25 or len(d)>35: err.append(("sitelink",t,len(t),d,len(d)))
for c in CALLOUT:
    if len(c)>25: err.append(("callout",c,len(c)))
if err:
    for e in err: print("HATA",e)
    sys.exit(1)
with open(os.path.join(OUT,"1-anahtar-kelimeler.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["Campaign","Ad group","Keyword","Criterion Type"])
    for c,ags in K.items():
        for ag,kws in ags.items():
            for kw,m in kws: w.writerow([c,ag,kw,m])
with open(os.path.join(OUT,"2-kampanya-negatifleri.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["Campaign","Keyword","Criterion Type"])
    for c,negs in CROSS.items():
        for n in negs+EXTRA_NEG: w.writerow([c,n,"Campaign Negative Phrase"])
with open(os.path.join(OUT,"3-reklamlar.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f)
    w.writerow(["Campaign","Ad group","Ad type"]+[f"Headline {i}" for i in range(1,16)]+[f"Description {i}" for i in range(1,5)]+["Path 1","Path 2","Final URL"])
    for k,v in RSA.items():
        c,ag=k.split("|"); w.writerow([c,ag,"Responsive search ad"]+v["H"]+v["D"]+list(v["path"])+[v["url"]])
with open(os.path.join(OUT,"4-uzantilar.txt"),"w",encoding="utf-8") as f:
    f.write("SITE BAĞLANTILARI (metin ≤25, açıklama ≤35)\n")
    for t,d,u in SITELINK: f.write(f"- {t} | {d} | {u}\n")
    f.write("\nFRAGMANLAR (≤25)\n"+"\n".join("- "+c for c in CALLOUT)+"\n")
n=sum(len(x) for a in K.values() for x in a.values())
print("ok:",n,"anahtar kelime,",sum(len(v)+len(EXTRA_NEG) for v in CROSS.values()),"kampanya negatifi,",len(RSA),"reklam; tüm sınırlar uygun")
