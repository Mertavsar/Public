#!/usr/bin/env python3
"""
Tek kaynak: meslek-matrisi.json
Bu script iki şey üretir:
  1. meslek-matrisi.md   — satış ekibinin okuyacağı doküman
  2. lead-brief.html     — araç; JSON, MATRIX işaretçileri arasına gömülür

Çalıştır:  python3 build.py
Matris değiştiğinde ikisi birden güncellenir; elle iki yerde düzenleme yapılmaz.
"""
import io, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(io.open(os.path.join(HERE, "meslek-matrisi.json"), encoding="utf-8"))
PROF = {p["key"]: p for p in data["profs"]}

# ---------------------------------------------------------------- markdown
out = []
w = out.append
w("# Meslek × Eğitim Kesişim Matrisi")
w("")
w("> **Bu dosya elle düzenlenmez.** Kaynak `meslek-matrisi.json`, üreten `build.py`.")
w("> Değişiklik JSON'a yazılır, `python3 build.py` çalıştırılır; doküman ve araç birlikte güncellenir.")
w("")
w("Satış ekibinin en büyük kozu **meslek** alanıdır. Bu dosya her meslek için üç şeyi verir:")
w("o mesleğin o eğitimle gerçek kesişimi, telefonda söylenecek giriş cümlesi ve o kişiye")
w("hangi dersin gösterileceği.")
w("")
w("## Kullanım kuralı")
w("")
w("1. Kesişim cümlesi **iddia değil sorudur.** Karşı taraf 'evet, aynen' derse konuşma açılmıştır;")
w("   'yok, alakası yok' derse kart çöpe gider ve kişiyi dinlersin.")
w("2. Giriş cümlesi kelimesi kelimesine okunmaz, kendi ağzınla söylenir.")
w("3. Ders adı **kanıttır**: 'sizin durumunuz için şu ders var' demek, genel övgüden güçlüdür.")
w("4. Fiyat bu dosyada yok ve olmayacak; fiyat zamanlaması `lead-brief.md` içindedir.")
w("5. Listede olmayan meslek için dosyanın sonundaki üç soruyu sor, kesişimi canlı kur.")
w("")

u = data["urun"]
w("## Ortak ürün gerçekleri (dört eğitimde de aynı)")
w("")
w("| Alan | Gerçek |")
w("|---|---|")
w("| Format | " + u["format"] + " |")
w("| Canlı yayın | " + u["canli"] + " |")
w("| Doküman | " + u["dokuman"] + " |")
w("| Sınav | " + u["sinav"] + " |")
w("| Sertifika | " + u["sertifika"] + " |")
w("| Fiyat | " + u["fiyat"] + " |")
w("")
w("> **AÇIK RİSK — " + u["sertifika_acik_soru"] + "**")
w("")
w("## Eğitmenler")
w("")
for k, v in data["egitmenler"].items():
    w("- **" + k + ":** " + v)
w("")
w("---")
w("")

for ckey, c in data["courses"].items():
    w("## " + c["label"])
    w("")
    w("**Eksen:** " + c["eksen"])
    w("")
    if c.get("eslestirme_kurali"):
        w("> **Eşleştirme kuralı:** " + c["eslestirme_kurali"])
        w("")
    if c.get("evrensel_sorular"):
        w("> **Her meslekte işe yarayan sorular:** " + c["evrensel_sorular"])
        w("")
    w("**Ders içeriği:** " + " · ".join(c.get("dersler", [])))
    w("")
    if c.get("kazanimlar"):
        w("**Kazanımlar:** " + " · ".join(c["kazanimlar"]))
        w("")
    for pkey, cell in c["cells"].items():
        w("### " + PROF.get(pkey, {}).get("name", pkey))
        w("")
        w("**Kesişim —** " + cell["kesisim"])
        w("")
        w("**Telefonda giriş —** *\"" + cell["giris"] + "\"*")
        w("")
        w("**Ona değecek iki çıktı —** " + " · ".join(cell["ciktilar"]))
        w("")
        w("**Beklenen itiraz —** " + cell["itiraz"])
        w("")
        if cell.get("ders"):
            w("**Gösterilecek ders —** " + cell["ders"])
            w("")
    w("---")
    w("")

w("## Listede olmayan meslek")
w("")
w("Varsayım üretme. Üç soru kesişimi canlı kurar:")
w("")
w("1. **Bu işte gün içinde kiminle konuşuyorsun?** (hitabet/hikâye/şiddetsiz iletişim için)")
w("2. **Bu iş bedenini nasıl yoruyor — ayakta mı, masada mı?** (pilates için)")
w("3. **Bu eğitimi kendin için mi, işin için mi düşünüyorsun?**")
w("")
w("Üçünün cevabı, matristeki en yakın satırı zaten söyler.")
w("")

md = "\n".join(out)
io.open(os.path.join(HERE, "meslek-matrisi.md"), "w", encoding="utf-8").write(md)

# ---------------------------------------------------------------- html enjeksiyonu
html_path = os.path.join(HERE, "lead-brief.html")
if os.path.exists(html_path):
    html = io.open(html_path, encoding="utf-8").read()
    payload = "  /* MATRIX:START — build.py üretir, elle düzenleme */\n  var MATRIX = " \
        + json.dumps(data, ensure_ascii=False, separators=(",", ":")) \
        + ";\n  /* MATRIX:END */"
    new, n = re.subn(
        r"  /\* MATRIX:START.*?/\* MATRIX:END \*/",
        lambda m: payload, html, flags=re.S)
    if n:
        io.open(html_path, "w", encoding="utf-8").write(new)
        print("lead-brief.html güncellendi")
    else:
        print("UYARI: lead-brief.html içinde MATRIX işaretçisi yok, enjeksiyon atlandı")

print("meslek-matrisi.md yazıldı — %d satır, %d hücre"
      % (len(out), sum(len(c["cells"]) for c in data["courses"].values())))
