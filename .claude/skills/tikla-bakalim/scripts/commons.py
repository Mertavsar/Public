#!/usr/bin/env python3
"""
Wikimedia Commons'tan serbest lisanslı gerçek fotoğraf bulur ve indirir.

Arama API'si (api.php) bu ortamın ortak çıkış IP'sini sık sık 429 ile
sınırlıyor; o yüzden normal sayfalar kullanılır: kategori sayfası → dosya
sayfası → lisans + özgün dosya bağlantısı. İstekler arası bekleme var,
User-Agent'ta kişisel bilgi YOK.

    python3 commons.py liste Category:Istanbul_in_the_1990s
    python3 commons.py bilgi "File:1_Million_TL_reverse.jpg"
    python3 commons.py indir "File:1_Million_TL_reverse.jpg" hedef.jpg [--genislik 1920]

Lisans kuralı (SKILL.md §2, telif): yalnız Public domain, CC0, CC BY, CC BY-SA
kabul edilir. CC BY / BY-SA için yazar + lisans videoda ve açıklamada anılır
(`indir` bunu .json yan dosyasına yazar). NC / ND / "fair use" → reddedilir.
"""
import html, json, re, sys, time, urllib.parse, urllib.request

UA = "Mozilla/5.0 (compatible; TiklaBakalimBot/1.0; educational video research)"
BASE = "https://commons.wikimedia.org"
OK = re.compile(r"(public domain|^pd[- ]|cc0|cc-zero|cc[ -]by(-sa)?([ -]\d|$)|copyrighted free use|flickrreview)", re.I)
BAD = re.compile(r"(\bnc\b|non-?commercial|\bnd\b|no ?deriv|fair use|non-free)", re.I)


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and i + 1 < tries:
                time.sleep(4 * (i + 1)); continue
            raise
    return b""


def liste(cat):
    page = get(f"{BASE}/wiki/{urllib.parse.quote(cat)}").decode("utf-8", "replace")
    files = sorted(set(re.findall(r'href="/wiki/(File:[^"#?]+)"', page)))
    return [urllib.parse.unquote(f) for f in files]


LIC_TPL = re.compile(r"\{\{\s*(?:self\s*\|\s*)?((?:cc[- ]?(?:by|zero|0)[^|}]*)|(?:pd[- ][^|}]*)|(?:public domain[^|}]*)|(?:gfdl[^|}]*)|(?:copyrighted free use[^|}]*)|(?:attribution[^|}]*)|(?:flickrreview[^|}]*)|(?:non-free[^|}]*)|(?:fair use[^|}]*))", re.I)


def bilgi(name):
    """Lisans, açıklama sayfasının ham wikitext'indeki şablonlardan okunur
    ({{cc-by-sa-4.0}}, {{self|cc-by-4.0}}, {{PD-old}} ...). HTML'deki site
    alt bilgisinin CC BY-SA lisansı yanıltıcı olurdu — o, metnin lisansı."""
    raw = get(f"{BASE}/w/index.php?title={urllib.parse.quote(name)}&action=raw").decode("utf-8", "replace")
    time.sleep(0.8)
    lic = []
    for m in LIC_TPL.finditer(raw):
        for part in re.split(r"\|", m.group(1)):
            part = part.strip()
            if part and part.lower() not in lic and not part.lower().startswith(("migration", "author")):
                lic.append(part.lower())
    field = lambda k: (re.search(rf"\|\s*{k}\s*=\s*(.*?)\n\s*\|", raw, re.S | re.I) or [None, ""])[1]
    strip = lambda t: re.sub(r"\s+", " ", re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]|\{\{[^}]*\}\}|<[^>]+>|\[https?://\S+ ([^\]]*)\]", r"\1\2", t)).strip()[:160]
    page = get(f"{BASE}/wiki/{urllib.parse.quote(name)}").decode("utf-8", "replace")
    full = re.search(r'href="(https://upload\.wikimedia\.org/wikipedia/commons/\w/\w\w/[^"]+)"', page)
    url = html.unescape(full.group(1)).split("?")[0] if full else ""
    ok = bool(lic) and any(OK.search(x) for x in lic) and not any(BAD.search(x) for x in lic)
    return {"dosya": name, "lisans": lic, "uygun": ok, "url": url, "yazar": strip(field("author")),
            "tarih": strip(field("date")), "aciklama": strip(field("description")),
            "sayfa": f"{BASE}/wiki/{urllib.parse.quote(name)}"}


def thumb(url, w):
    # /commons/a/ab/X.jpg -> /commons/thumb/a/ab/X.jpg/1920px-X.jpg
    m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons)/(\w)/(\w\w)/(.+)$", url)
    if not m:
        return url
    fn = m.group(4)
    return f"{m.group(1)}/thumb/{m.group(2)}/{m.group(3)}/{fn}/{w}px-{fn}"


def indir(name, out, w=1920):
    b = bilgi(name)
    if not b["uygun"]:
        sys.exit(f"RED: lisans uygun değil ({b['lisans']}) — {name}")
    data = None
    for u in (thumb(b["url"], w), b["url"]):
        try:
            data = get(u); break
        except Exception:
            time.sleep(2)
    if not data:
        sys.exit(f"HATA: indirilemedi {name}")
    open(out, "wb").write(data)
    json.dump(b, open(out + ".json", "w"), ensure_ascii=False, indent=1)
    print(f"{out}  {len(data)//1024} KB  {', '.join(b['lisans'])}  {b['yazar'][:50]}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "liste":
        for f in liste(sys.argv[2]):
            print(f)
    elif cmd == "bilgi":
        print(json.dumps(bilgi(sys.argv[2]), ensure_ascii=False, indent=1))
    elif cmd == "indir":
        w = int(sys.argv[sys.argv.index("--genislik") + 1]) if "--genislik" in sys.argv else 1920
        indir(sys.argv[2], sys.argv[3], w)
