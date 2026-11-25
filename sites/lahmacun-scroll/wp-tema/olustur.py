#!/usr/bin/env python3
"""Siteyi (../index.html) WordPress temasına çevirir ve yüklenecek zip'leri üretir.

Kullanım:
    python3 wp-tema/olustur.py 1.0.0

Tek kaynak index.html'dir: sitede yapılan her değişiklik bu betikle yeni tema sürümüne geçer.
index.html'deki <!--wp:ad--> ... <!--/wp:ad--> işaretli bölümler WordPress'te panelden gelen
PHP bölümleriyle değişir (bant, menu, galeri, sss, ziyaret, yil).

Çıktı (dagitim/, depoya konmaz):
    kuzu-lahmacun-<sürüm>.zip         tam tema: Görünüm → Temalar → Yeni ekle → Tema yükle
    kuzu-lahmacun-<sürüm>-hafif.zip   kareler hariç; sunucu büyük zip'i kabul etmezse bu yüklenir
    kuzu-sahne-kareler.zip            hafif sürümle birlikte: wp-content/uploads/ içine açılır
"""
import html, json, os, re, shutil, sys, zipfile

SURUM = sys.argv[1] if len(sys.argv) > 1 else "1.0.0"
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMA_KAYNAK = os.path.join(SITE, "wp-tema", "kaynak")
OUT = os.path.join(SITE, "wp-tema", "dagitim")
T = os.path.join(OUT, "kuzu-lahmacun")
HARITA = "https://www.google.com/maps?cid=13202010269743240704"
YORUM = "https://search.google.com/local/writereview?placeid=ChIJN83oJADHyhQRANYaoWT2Nrc"

s = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()


def between(a, b, text=s):
    i = text.index(a) + len(a)
    return text[i:text.index(b, i)]


def strip_tags(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()


shutil.rmtree(T, ignore_errors=True)
shutil.copytree(TEMA_KAYNAK, T)

# ── CSS ve JS ────────────────────────────────────────────────────────────────
css = between("<style>\n", "</style>")
css += """
/* WordPress: yönetici çubuğu açıkken üst çubuk onun altına iner */
body.admin-bar .topbar { top: 32px; }
@media (max-width: 782px) { body.admin-bar .topbar { top: 46px; } }
"""
open(os.path.join(T, "assets", "site.css"), "w", encoding="utf-8").write(css)
js_start = s.index("<script>\n((") + len("<script>\n")
js = s[js_start:s.index("</script>", js_start)]
open(os.path.join(T, "assets", "site.js"), "w", encoding="utf-8").write(js)

# ── Ana sayfa şablonu ────────────────────────────────────────────────────────
body = between('<body>\n', '<script src="https://cdn.jsdelivr.net/npm/lenis')
php_bolum = {
    "bant": "<?php kuzu_bant(); ?>",
    "menu": "<?php kuzu_menu(); ?>",
    "galeri": "<?php kuzu_galeri(); ?>\n",
    "sss": "<?php kuzu_sss(); ?>",
    "ziyaret": "<?php kuzu_ziyaret(); ?>",
    "yil": "© <?php echo esc_html( wp_date( 'Y' ) ); ?>",
    "videolar": "<?php kuzu_videolar(); ?>",
    "nav-videolar": "<?php kuzu_nav_videolar(); ?>",
    "siparis-menu": "<?php kuzu_siparis( 'menu' ); ?>",
    "siparis-final": "<?php kuzu_siparis( 'final' ); ?>",
    "lab": None,   # deneme kutusu sitede gizli kalır
}
for ad, yerine in php_bolum.items():
    m = re.search(rf"<!--wp:{ad}-->(.*?)<!--/wp:{ad}-->", body, flags=re.S)
    assert m, f"işaret bulunamadı: {ad}"
    body = body[:m.start()] + (m.group(1) if yerine is None else yerine) + body[m.end():]
assert "<!--wp:" not in body
body = body.replace(HARITA, "<?php echo esc_url( kuzu_harita_linki() ); ?>")
body = body.replace(YORUM, "<?php echo esc_url( kuzu_yorum_linki() ); ?>")
body = re.sub(r'(?<=["\s,])(foto/|logo-beyaz\.svg|logo\.svg|favicon\.svg)', r"<?php echo KUZU_URI; ?>\1", body)
assert "<?xml" not in body
aciklama = re.search(r'<meta name="description" content="([^"]*)">', s).group(1)
front = f"""<?php
/**
 * Ana sayfa: kaydırmaya bağlı lezzet şovu. Bu dosya wp-tema/olustur.py ile index.html'den üretilir;
 * elle değiştirmeyin. Panelden gelen bölümler inc/bolumler.php içindedir.
 */
if ( ! defined( 'ABSPATH' ) ) {{
	exit;
}}
?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{aciklama}">
<meta name="theme-color" content="#0b5236">
<link rel="icon" href="<?php echo esc_url( KUZU_URI . 'favicon.svg' ); ?>" type="image/svg+xml">
<link rel="preload" href="<?php echo esc_url( KUZU_URI . 'logo-beyaz.svg' ); ?>" as="image" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
{body}<?php kuzu_google_json(); ?>
<?php wp_footer(); ?>
</body>
</html>
"""
open(os.path.join(T, "front-page.php"), "w", encoding="utf-8").write(front)

# ── Panelin varsayılanları (sitedeki içerikten) ──────────────────────────────
menu = []
for kart in re.findall(r'<article class="card"><h3 class="tag">(.*?)</h3><ul class="prices">(.*?)</ul></article>', s, flags=re.S):
    for urun, fiyat in re.findall(r"<li><span>(.*?)</span><i class=\"dots\"></i><b>(.*?)</b></li>", kart[1]):
        menu.append(f"{strip_tags(kart[0])} | {strip_tags(urun)} | {strip_tags(fiyat)}")
sss = []
for soru, cevap in re.findall(r'<details class="q"><summary>(.*?)</summary><p>(.*?)</p></details>', s, flags=re.S):
    sss.append(f"{html.unescape(soru)}\n{html.unescape(re.sub(r'<a href=\"tel:[^\"]*\">(.*?)</a>', r'\\1', cevap))}")
bant = [strip_tags(x) for x in re.findall(r"<span>(.*?)</span>", between("<!--wp:bant-->", "<!--/wp:bant-->"))]
bant = list(dict.fromkeys(bant))
galeri = []
for fig in re.findall(r'<figure class="slide.*?</figure>', between("<!--wp:galeri-->", "<!--/wp:galeri-->"), flags=re.S):
    ad = re.search(r'src="foto/(.*?)-m\.jpg"', fig).group(1)
    galeri.append([
        ad,
        strip_tags(re.search(r'<span class="script">(.*?)</span>', fig).group(1)),
        strip_tags(re.search(r"<small>(.*?)</small>", fig).group(1)),
        html.unescape(re.search(r'alt="(.*?)"', fig).group(1)),
        re.search(r"object-position: (.*?)\"", fig).group(1),
        int(re.search(r'height="(\d+)"', fig).group(1)),
    ])
galeri_yazi = strip_tags(re.search(r'id="galTitle">.*?</h2>\s*<p>(.*?)</p>', s, flags=re.S).group(1))
varsayilan = {
    "telefon": "0533 440 43 27",
    "adres": "Hatboyu Sk. No:3A, Çeşme Mah., Erenköy, 34738 Kadıköy/İstanbul",
    "saatler": "Pazartesi–Cuma 11:00–21:00\nCumartesi–Pazar 11:00–22:00",
    "menu": "\n".join(menu),
    "menu_notu": strip_tags(re.search(r'<p class="menu-note">(.*?)</p>', s).group(1)),
    "sss": "\n\n".join(sss),
    "bant": "\n".join(bant),
    "galeri": "",
    "galeri_yazi": galeri_yazi,
    "videolar": "",
    "video_baslik": strip_tags(re.search(r'id="vidTitle">(.*?)</h2>', s).group(1)),
    "video_yazi": strip_tags(re.search(r'id="vidTitle">.*?</h2>\s*<p>(.*?)</p>', s, flags=re.S).group(1)),
    "siparis_yemeksepeti": "",
    "siparis_trendyol": "",
    "siparis_getir": "",
    "siparis_migros": "",
    "siparis_diger": "",
    "yer_id": "ChIJN83oJADHyhQRANYaoWT2Nrc",
    "cid": "13202010269743240704",
}


def php(v):
    if isinstance(v, str):
        return "'" + v.replace("\\", "\\\\").replace("'", "\\'") + "'"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, list):
        return "array( " + ", ".join(php(x) for x in v) + " )"
    raise TypeError(v)


satirlar = "\n".join(f"\t\t{php(k)} => {php(v)}," for k, v in varsayilan.items())
gsat = "\n".join(f"\t\t{php(g)}," for g in galeri)
open(os.path.join(T, "inc", "varsayilan.php"), "w", encoding="utf-8").write(f"""<?php
/** Panelde bir alan boş bırakılırsa kullanılan içerik (olustur.py index.html'den üretir). */
if ( ! defined( 'ABSPATH' ) ) {{
	exit;
}}

function kuzu_varsayilan() {{
	return array(
{satirlar}
	);
}}

/** Temayla gelen galeri: dosya adı, başlık, alt yazı, alt metin, kadraj, yükseklik. */
function kuzu_varsayilan_galeri() {{
	return array(
{gsat}
	);
}}
""")

# ── Dosyalar ─────────────────────────────────────────────────────────────────
A = os.path.join(T, "assets")
for f in ("logo-beyaz.svg", "logo.svg", "favicon.svg"):
    shutil.copy(os.path.join(SITE, f), A)
shutil.copytree(os.path.join(SITE, "foto"), os.path.join(A, "foto"))
for d in ("frames", "frames-mobil"):
    shutil.copytree(os.path.join(SITE, d), os.path.join(A, "sahne", d))
yer = os.path.join(SITE, "google", "yer.json")
if os.path.exists(yer):
    os.makedirs(os.path.join(A, "yorum"))
    ilk = []
    for i, r in enumerate(json.load(open(yer, encoding="utf-8"))["reviews"], 1):
        r = dict(r)
        if r.get("photo") and os.path.exists(os.path.join(SITE, r["photo"])):
            shutil.copy(os.path.join(SITE, r["photo"]), os.path.join(A, "yorum", f"kisi-{i}.jpg"))
            r["photo"] = f"yorum/kisi-{i}.jpg"
        else:
            r["photo"] = ""
        ilk.append({k: r.get(k, "") for k in ("author", "uri", "photo", "rating", "date", "text")})
    json.dump({"reviews": ilk}, open(os.path.join(A, "yorumlar-ilk.json"), "w", encoding="utf-8"), ensure_ascii=False)

open(os.path.join(T, "style.css"), "w", encoding="utf-8").write(f"""/*
Theme Name: Kuzu Lahmacun
Theme URI: https://www.google.com/maps?cid=13202010269743240704
Author: Ajans
Description: Kuzu Lahmacun & Kilis Tava, Erenköy. Kaydırdıkça hamurun açılıp lahmacuna dönüştüğü lezzet şovu; menü, iletişim, merak edilenler, galeri ve Google yorumları panelden (Kuzu Lahmacun) düzenlenir.
Version: {SURUM}
Requires at least: 6.0
Tested up to: 6.8
Requires PHP: 7.4
License: Proprietary
Text Domain: kuzu-lahmacun
*/
/* Asıl stiller assets/site.css içindedir. */
""")

# ── Zip'ler ──────────────────────────────────────────────────────────────────
def paketle(zip_yolu, kok, ad, atla=None):
    with zipfile.ZipFile(zip_yolu, "w") as z:
        for d, _, fs in os.walk(kok):
            for f in sorted(fs):
                p = os.path.join(d, f)
                rel = os.path.relpath(p, kok)
                if atla and atla(rel):
                    continue
                kip = zipfile.ZIP_STORED if f.endswith((".jpg", ".png")) else zipfile.ZIP_DEFLATED
                z.write(p, os.path.join(ad, rel), compress_type=kip)
    return os.path.getsize(zip_yolu)


tam = os.path.join(OUT, f"kuzu-lahmacun-{SURUM}.zip")
hafif = os.path.join(OUT, f"kuzu-lahmacun-{SURUM}-hafif.zip")
kare = os.path.join(OUT, "kuzu-sahne-kareler.zip")
mb = lambda n: f"{n / 1048576:.1f} MB"
print("tam:  ", mb(paketle(tam, T, "kuzu-lahmacun")), tam)
print("hafif:", mb(paketle(hafif, T, "kuzu-lahmacun", lambda r: r.startswith(os.path.join("assets", "sahne")))), hafif)
print("kare: ", mb(paketle(kare, os.path.join(A, "sahne"), "kuzu-sahne")), kare)
