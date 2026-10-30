"""Blog kaynak metinlerinden WordPress (Gutenberg) HTML'i, SEO tablosu ve onay PDF'i üretir."""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent
SITE = "https://handecelikmehmetoglu.com.tr"
AUTHOR = ("Uzm. Dr. Hande Çelik Mehmetoğlu, aile hekimliği uzmanıdır. Bursa'da psikoterapi, "
          "tıbbi hipnoz, oyun terapisi, psikodrama ve aile danışmanlığı alanlarında yüz yüze ve "
          "online görüşmeler yapmaktadır.")
DISCLAIMER = "Bu yazı genel bilgilendirme amaçlıdır; muayene, tanı ve tedavinin yerine geçmez."
BANNED = [r"garanti", r"en iyi", r"kesin sonuç", r"mucize", r"psikolog", r"fiyat", r"ücret(?!siz)", r"\btl\b",
          r"%", r"osmangazi", r"satir", r"\byüzde\b"]


def parse(path):
    head, body = path.read_text().split("\n---\n", 1)
    meta = dict(l.split(": ", 1) for l in head.strip().splitlines())
    blocks, faq, lines = [], [], body.strip().splitlines()
    i = 0
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            i += 1; continue
        for kind, pat in (("ul", r"- "), ("ol", r"\d+\. ")):
            if re.match(pat, l):
                items = []
                while i < len(lines) and re.match(pat, lines[i]):
                    items.append(re.sub("^" + pat, "", lines[i])); i += 1
                blocks.append((kind, items)); break
        else:
            if l.startswith("? "):
                q, a = l[2:], lines[i + 1][2:]
                faq.append((q, a)); blocks.append(("faq", (q, a))); i += 2; continue
            if l.startswith("### "): blocks.append(("h3", l[4:]))
            elif l.startswith("## "): blocks.append(("h2", l[3:]))
            elif l.startswith("> "): blocks.append(("quote", l[2:]))
            else: blocks.append(("p", l))
            i += 1
    return meta, blocks, faq


def inline(t, absolute=False):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return re.sub(r"\[(.+?)\]\((.+?)\)",
                  lambda m: f'<a href="{(SITE if absolute else "") + m[2]}">{m[1]}</a>', t)


def plain(t):
    return re.sub(r"\[(.+?)\]\(.+?\)", r"\1", t.replace("**", ""))


def wp(meta, blocks, faq):
    out = []
    P = lambda t: f"<!-- wp:paragraph -->\n<p>{t}</p>\n<!-- /wp:paragraph -->"
    for kind, v in blocks:
        if kind == "p": out.append(P(inline(v)))
        elif kind == "h2": out.append(f'<!-- wp:heading -->\n<h2 class="wp-block-heading">{inline(v)}</h2>\n<!-- /wp:heading -->')
        elif kind == "h3": out.append(f'<!-- wp:heading {{"level":3}} -->\n<h3 class="wp-block-heading">{inline(v)}</h3>\n<!-- /wp:heading -->')
        elif kind == "quote": out.append(f'<!-- wp:quote -->\n<blockquote class="wp-block-quote">{P(inline(v))}</blockquote>\n<!-- /wp:quote -->')
        elif kind == "faq":
            out.append(f'<!-- wp:heading {{"level":3}} -->\n<h3 class="wp-block-heading">{inline(v[0])}</h3>\n<!-- /wp:heading -->')
            out.append(P(inline(v[1])))
        else:
            tag, attr = ("ol", ' {"ordered":true}') if kind == "ol" else ("ul", "")
            li = "".join(f"<!-- wp:list-item -->\n<li>{inline(x)}</li>\n<!-- /wp:list-item -->" for x in v)
            out.append(f'<!-- wp:list{attr} -->\n<{tag} class="wp-block-list">{li}</{tag}>\n<!-- /wp:list -->')
    out.append('<!-- wp:separator -->\n<hr class="wp-block-separator has-alpha-channel-opacity"/>\n<!-- /wp:separator -->')
    out.append(P(f"<strong>Yazar:</strong> {html.escape(AUTHOR, quote=False)}"))
    out.append(P(f"<em>{DISCLAIMER}</em>"))
    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in faq]}
    out.append("<!-- wp:html -->\n<script type=\"application/ld+json\">"
               + json.dumps(schema, ensure_ascii=False) + "</script>\n<!-- /wp:html -->")
    return "\n\n".join(out) + "\n"


def check(meta, blocks, faq):
    errs, text = [], " ".join(plain(v) if isinstance(v, str) else " ".join(map(plain, v)) for _, v in blocks)
    low = text.lower() + " " + meta["title"].lower()
    if len(meta["seo_title"]) > 60: errs.append(f"SEO başlık {len(meta['seo_title'])} > 60")
    if not 120 <= len(meta["meta"]) <= 160: errs.append(f"meta açıklama {len(meta['meta'])}")
    fk = meta["focus"].lower()
    first = plain(blocks[0][1]).lower()
    for where, s in (("SEO başlık", meta["seo_title"]), ("meta", meta["meta"]), ("ilk paragraf", first)):
        if fk not in s.lower(): errs.append(f"odak kelime {where} içinde yok")
    if "bursa" not in meta["seo_title"].lower() and "bursa" not in meta["title"].lower(): errs.append("başlıkta Bursa yok")
    for b in BANNED:
        if re.search(b, low): errs.append(f"yasaklı ifade: {b!r}")
    words = len(text.split())
    return words, low.count("bursa"), low.count(fk), errs


def preview(posts):
    css = """body{font-family:'DejaVu Serif',Georgia,serif;color:#1d1b2e;margin:0}
    .post{padding:28mm 22mm;page-break-after:always}
    h1{font-family:'DejaVu Sans',sans-serif;color:#0a0a48;font-size:22pt;line-height:1.2;margin:0 0 6mm}
    h2{font-family:'DejaVu Sans',sans-serif;color:#5640aa;font-size:14pt;margin:8mm 0 2mm}
    h3{font-family:'DejaVu Sans',sans-serif;font-size:11.5pt;margin:5mm 0 1mm}
    p,li{font-size:10.5pt;line-height:1.55}
    blockquote{border-left:3px solid #5b8a2f;margin:4mm 0;padding:1mm 4mm;background:#f4f7ef}
    table.seo{border-collapse:collapse;width:100%;font-family:'DejaVu Sans',sans-serif;font-size:8.5pt;margin-bottom:6mm}
    table.seo td{border:1px solid #cdc8fa;padding:1.5mm 2mm;vertical-align:top}
    table.seo td:first-child{background:#f2f0ff;width:32mm;font-weight:bold}
    .cover{padding:60mm 22mm;page-break-after:always}
    .cover h1{font-size:28pt}.muted{color:#666;font-size:10pt}"""
    parts = ['<div class="cover"><h1>Hipnoz Blog Yazıları</h1><p>Uzm. Dr. Hande Çelik Mehmetoğlu · Bursa</p>'
             '<p class="muted">5 yazı · WordPress için hazır · Onaya sunulan taslak</p><ol>'
             + "".join(f"<li>{html.escape(m['title'])}</li>" for m, _, _ in posts) + "</ol></div>"]
    for meta, blocks, faq in posts:
        rows = [("SEO başlık", meta["seo_title"]), ("Meta açıklama", meta["meta"]), ("Kalıcı bağlantı", "/" + meta["slug"] + "/"),
                ("Odak kelime", meta["focus"]), ("İkincil kelimeler", meta["secondary"]), ("Özet", meta["excerpt"]),
                ("Öne çıkan görsel", meta["image"] + " — alt metin: " + meta["alt"])]
        body = wp(meta, blocks, faq)
        body = re.sub(r"<!-- /?wp:[^>]*-->\n?", "", body)
        body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
        parts.append('<div class="post"><table class="seo">' + "".join(f"<tr><td>{k}</td><td>{html.escape(v)}</td></tr>" for k, v in rows)
                     + f"</table><h1>{html.escape(meta['title'])}</h1>{body}</div>")
    return f"<!doctype html><html lang='tr'><meta charset='utf-8'><style>{css}</style><body>{''.join(parts)}</body></html>"


posts, ok, rows = [], True, []
(ROOT / "wordpress").mkdir(exist_ok=True)
for f in sorted((ROOT / "kaynak").glob("*.txt")):
    meta, blocks, faq = parse(f)
    words, bursa, fkn, errs = check(meta, blocks, faq)
    print(f"{f.stem}: {words} kelime, Bursa {bursa}x, odak {fkn}x, SEO başlık {len(meta['seo_title'])}, meta {len(meta['meta'])}", errs or "ok")
    ok &= not errs
    (ROOT / "wordpress" / f"{f.stem}.html").write_text(wp(meta, blocks, faq))
    posts.append((meta, blocks, faq))
    rows.append(meta)
(ROOT / "onizleme.html").write_text(preview(posts))
md = ["# Hipnoz Blog Yazıları: WordPress SEO Bilgileri", ""]
for i, m in enumerate(rows, 1):
    md += [f"## {i}. {m['title']}", "", f"- Dosya: `wordpress/{i}-{m['slug']}.html`",
           f"- SEO başlık: {m['seo_title']}", f"- Meta açıklama: {m['meta']}", f"- Kalıcı bağlantı: `/{m['slug']}/`",
           f"- Odak anahtar kelime: {m['focus']}", f"- İkincil kelimeler: {m['secondary']}", f"- Özet: {m['excerpt']}",
           f"- Öne çıkan görsel: {m['image']}", f"- Görsel alt metni: {m['alt']}", ""]
(ROOT / "seo-bilgileri.md").write_text("\n".join(md))
sys.exit(0 if ok else 1)
