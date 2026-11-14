G={
"1 · Tıbbi Hipnoz":{
"H":["Bursa'da Tıbbi Hipnoz","Hekim Eşliğinde Hipnoz","Uzm. Dr. Hande Ç. Mehmetoğlu","Hipnoz Nedir, Nasıl Uygulanır?","Bakanlık Onaylı Hipnoz Eğitimi","Hipnozda Kontrol Sizde Kalır","Kaygı ve Stres İçin Hipnoz","Sigara Bırakmada Destek","Önce Hekim Değerlendirmesi","Osmangazi, Efe Plaza","Hipnoterapi Randevusu","Aile Hekimliği Uzmanı","2010'dan Beri Hipnoz","Online Ön Görüşme","Hemen Arayın"],
"D":["Tıbbi hipnoz, Bakanlık sertifikalı hekim tarafından, ön değerlendirmeyle uygulanır.","Hipnozda uyumazsınız; bilinciniz açık, kontrol sizdedir. Süreci ilk görüşmede anlatıyoruz.","Kaygı, stres ve alışkanlıklarla baş etmede hipnoz, terapinin parçası olarak kullanılır.","Osmangazi'de, metroya yakın. Randevu ve bilgi için arayın ya da web sitemizi ziyaret edin."]},
"2 · Psikoterapi (kaygı, panik, stres)":{
"H":["Bursa'da Psikoterapi","Kaygı ve Panik Atak Desteği","Uzm. Dr. Hande Ç. Mehmetoğlu","Bütüncül Psikoterapi","Beden ve Zihin Birlikte","Tahliller Temiz, Ağrı Var mı?","Uykusuzluk ve Stres","Bireysel Terapi Randevusu","Hekim Gözüyle Ruh Sağlığı","Yetişkin ve Ergen Terapisi","Online Terapi Seçeneği","Osmangazi, Efe Plaza","Aile Hekimliği Uzmanı","Gizlilik Esaslı Görüşme","Randevu İçin Arayın"],
"D":["Kaygı, panik atak, stres ve uyku sorunlarında bireysel psikoterapi. Aile hekimi gözüyle.","Bedeninizdeki belirtilerle duygularınız arasındaki bağı birlikte anlamaya çalışıyoruz.","Psikodinamik, bağlanma odaklı ve psikodrama temelli bütüncül bir yaklaşımla çalışıyoruz.","Yüz yüze Osmangazi'de ya da online görüşme. Randevu için arayın veya sitemizden yazın."]},
"3 · Aile ve çift danışmanlığı":{
"H":["Bursa Aile Danışmanlığı","Çift Terapisi Bursa","Uzm. Dr. Hande Ç. Mehmetoğlu","Aynı Kavga Tekrar mı Ediyor?","İletişimi Yeniden Kurun","Bakanlık Onaylı Aile Danışmanı","Ebeveynlik Desteği","Boşanma Sürecinde Destek","Aile İçi İletişim","Çift Görüşmesi Randevusu","Online Görüşme Seçeneği","Osmangazi, Efe Plaza","Gizlilik Esaslı Görüşme","Satir Aile Terapisi Eğitimi","Hemen Arayın"],
"D":["Tekrarlayan kavgalar ve iletişim sorunlarında çift ve aile danışmanlığı. Randevu alın.","Bakanlık onaylı aile danışmanlığı eğitimi almış hekimle, gizlilik esaslı görüşmeler.","Boşanma sürecinde çocuklarla iletişim ve ebeveynlik konularında destek sunuyoruz.","Yüz yüze Osmangazi'de ya da online. Bilgi ve randevu için arayın ya da sitemize bakın."]},
"4 · Çocuk oyun terapisi":{
"H":["Bursa Çocuk Oyun Terapisi","Çocuklar Oyunla Anlatır","Uzm. Dr. Hande Ç. Mehmetoğlu","Öfke Nöbeti ve Kaygı","Okula Uyum Sorunları","Kardeş Kıskançlığı","Ebeveyn Görüşmesi","Oyun Terapisi Nedir?","İki Çocuk Annesi Hekim","Çocuk ve Ergen Terapisi","Aile Hekimliği Uzmanı","Osmangazi, Efe Plaza","Oyun Terapisi Randevusu","Ebeveynlere Rehberlik","Hemen Arayın"],
"D":["Çocuklar duygularını oyunla anlatır. Öfke, kaygı ve uyum sorunlarında oyun terapisi.","Önce ebeveyn görüşmesi, sonra çocukla oyun seansları. Süreci adım adım anlatıyoruz.","Oyun terapisi eğitimi almış aile hekimliği uzmanıyla, çocuğun yaşına uygun çalışma.","Osmangazi'de, metroya yakın. Randevu ve bilgi için arayın ya da web sitemizi ziyaret edin."]},
}
ok=True
for g,v in G.items():
    for h in v["H"]:
        if len(h)>30: print("UZUN BAŞLIK",g,len(h),h); ok=False
    for d in v["D"]:
        if len(d)>90: print("UZUN AÇIKLAMA",g,len(d),d); ok=False
    print(g, len(v["H"]),"başlık,",len(v["D"]),"açıklama; en uzun başlık",max(map(len,v["H"])),"en uzun açıklama",max(map(len,v["D"])))
print("TAMAM" if ok else "DÜZELT")
