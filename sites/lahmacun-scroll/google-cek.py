#!/usr/bin/env python3
"""İşletmenin Google kaydından puanı, yorumları, adresi, telefonu ve saatleri çeker.

Kullanım:
    GOOGLE_API_KEY=... python3 google-cek.py

Çıktı: google/yer.json ve yorum yazarlarının küçük profil fotoğrafları. Site bu dosyayı okur;
dosya yoksa Yorumlar bölümünde yalnızca başlık görünür. Galeri, işletmenin kendi fotoğraflarıdır (foto/).

Doğru işletme: "Kuzu Lahmacun" adında başka bir işletme de var. Bu betik yalnızca aşağıdaki
CID'ye sahip kaydı kabul eder (müşterinin verdiği Google Haritalar linkindeki
0x14cac70024e8cd37:0xb736f664a11ad600). Arama başka bir yer döndürürse durur; tahmin etmez.

Google Places API (New) kullanır. Yorumlar Google'ın seçtiği en fazla 5 yorumdur.
Gereken: Google Cloud projesinde "Places API (New)" açık bir API anahtarı.
"""
import io, json, os, sys, urllib.parse, urllib.request
from PIL import Image

CID = "13202010269743240704"          # 0xb736f664a11ad600
ARAMA = "Kuzu Lahmacun Erenköy Kadıköy İstanbul"
API = "https://places.googleapis.com/v1"
KOK = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(KOK, "google")
KEY = os.environ.get("GOOGLE_API_KEY", "").strip()


def istek(url, body=None, fields=None):
    h = {"Content-Type": "application/json"}
    if KEY:
        h["X-Goog-Api-Key"] = KEY          # yoksa ortamın ağ anahtarı başlığı ekler
    if fields:
        h["X-Goog-FieldMask"] = fields
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=h, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Google hata verdi ({e.code}): {e.read().decode()[:400]}")


def yer_bul():
    sonuc = json.loads(istek(f"{API}/places:searchText", {"textQuery": ARAMA, "languageCode": "tr"},
                             "places.id,places.displayName,places.googleMapsUri,places.formattedAddress"))
    adaylar = sonuc.get("places", [])
    for p in adaylar:
        if f"cid={CID}" in p.get("googleMapsUri", ""):
            return p["id"]
    liste = "\n".join(f"  - {p.get('displayName', {}).get('text')} | {p.get('formattedAddress')} | {p.get('googleMapsUri')}" for p in adaylar)
    sys.exit(f"Müşterinin kaydı (cid={CID}) arama sonuçlarında yok; yanlış işletmeyi almamak için durdum.\n{liste}")


def avatar_kaydet(url, n):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            im = Image.open(io.BytesIO(r.read())).convert("RGB")
        im.thumbnail((96, 96), Image.LANCZOS)
        yol = f"google/kisi-{n}.jpg"
        im.save(os.path.join(KOK, yol), quality=85)
        return yol
    except Exception:
        return None


def main():
    os.makedirs(OUT, exist_ok=True)
    pid = yer_bul()
    alanlar = ("id,displayName,formattedAddress,shortFormattedAddress,nationalPhoneNumber,rating,userRatingCount,"
               "googleMapsUri,regularOpeningHours,reviews")
    y = json.loads(istek(f"{API}/places/{pid}?languageCode=tr", fields=alanlar))
    if f"cid={CID}" not in y.get("googleMapsUri", ""):
        sys.exit("Ayrıntılar başka bir kayda ait çıktı; durdum.")

    for f in os.listdir(OUT):
        if f.endswith(".jpg"):
            os.remove(os.path.join(OUT, f))

    yorumlar = []
    for i, r in enumerate(y.get("reviews", []), 1):
        a = r.get("authorAttribution", {})
        metin = (r.get("originalText") or r.get("text") or {}).get("text", "")
        yorumlar.append({
            "author": a.get("displayName", ""), "uri": a.get("uri", ""),
            "photo": avatar_kaydet(a["photoUri"], i) if a.get("photoUri") else None,
            "rating": r.get("rating"), "date": r.get("publishTime", ""), "text": metin,
        })

    hedef = os.path.join(OUT, "yer.json")
    veri = {
        "cid": CID, "placeId": y["id"], "name": y.get("displayName", {}).get("text", ""),
        "address": y.get("formattedAddress", ""), "phone": y.get("nationalPhoneNumber", ""),
        "rating": y.get("rating"), "count": y.get("userRatingCount"), "mapsUri": y.get("googleMapsUri", ""),
        "hours": y.get("regularOpeningHours", {}).get("weekdayDescriptions", []),
        "reviews": yorumlar,
    }
    json.dump(veri, open(hedef, "w"), ensure_ascii=False, indent=1)
    print(f"{veri['name']} | {veri['address']}\npuan {veri['rating']} ({veri['count']} değerlendirme), "
          f"{len(yorumlar)} yorum → {hedef}")


if __name__ == "__main__":
    main()
