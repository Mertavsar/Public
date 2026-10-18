"""
Örnek veri (--demo) — Google bağlantısı olmadan paneli görmek ve göstermek için.
Uydurma kanallar; her açılışta aynı rakamlar üretilir.
"""

import random
from datetime import date, timedelta

from youtube import period, summarize

USER = {"id": 0, "email": "demo@ornek.com", "name": "Demo Kullanıcı", "picture": "", "plan": "beta"}

CHANNELS = [
    # id, ad, kullanıcı adı, abone, dönem trendi, kısa video ağırlığı
    ("demo-mutfak", "Mutfak Sırları", "@mutfaksirlari", 184000, 1.18, 0.4),
    ("demo-tekno", "Teknoloji Kutusu", "@teknolojikutusu", 92300, 0.82, 0.2),
    ("demo-gezgin", "Gezgin Çift", "@gezgincift", 41200, 1.42, 0.3),
    ("demo-oyun", "Oyun Atölyesi", "@oyunatolyesi", 12800, 0.95, 0.5),
    ("demo-kisa", "Kısa Bilgi", "@kisabilgi", 256000, 1.06, 0.95),
    ("demo-tarih", "Tarih Dedektifi", "@tarihdedektifi", 67500, 1.09, 0.1),
    ("demo-araba", "Garaj 34", "@garaj34", 28900, 0.88, 0.6),
    ("demo-finans", "Cebimdeki Para", "@cebimdekipara", 8400, 1.65, 0.7),
]
TITLES = [
    "5 dakikada evde pratik tarif", "Kimsenin bilmediği 3 püf noktası",
    "Bunu denemeden karar verme", "Bir haftalık deneyim: sonuç şaşırttı",
    "En çok sorulan soruya cevap", "Yeni başlayanlar için rehber",
    "Bu hatayı herkes yapıyor", "Ucuz mu pahalı mı? Karşılaştırma",
    "Bir günüm nasıl geçiyor", "İzleyici yorumlarını denedik",
    "1 ay boyunca her gün denedim", "Kimse bundan bahsetmiyor",
]


def _row(cid):
    return next((c for c in CHANNELS if c[0] == cid), None)


def channels():
    return [{"channel_id": c[0], "title": c[1], "handle": c[2], "thumb": ""} for c in CHANNELS]


def _series(cid, days):
    _, _, _, subs, trend, _ = _row(cid)
    rng = random.Random(cid)
    start, end = period(2 * days)
    base, out, d, i, total = subs * 0.02, [], start, 0, 2 * days
    while d <= end:
        growth = trend ** (i / total)
        weekly = 1 + 0.12 * (d.weekday() >= 5)
        spike = 2.4 if rng.random() < 0.035 else 1
        views = int(base * growth * weekly * spike * rng.uniform(0.88, 1.12))
        out.append({"d": str(d), "views": views,
                    "minutes": int(views * rng.uniform(0.6, 1.4)),
                    "subs": int(views * rng.uniform(0.002, 0.006)) - rng.randint(0, 6)})
        d += timedelta(days=1)
        i += 1
    return out


def summary(cid, days):
    _, title, handle, subs, _, _ = _row(cid)
    rng = random.Random(cid + "info")
    return {"id": cid, "title": title, "handle": handle, "thumb": "",
            "subscribers": subs, "total_views": subs * rng.randint(60, 140),
            "video_count": rng.randint(40, 600),
            **summarize(_series(cid, days), days)}


def _videos(cid):
    _, title, _, subs, _, shorts = _row(cid)
    rng = random.Random(cid + "videos")
    today, out = date.today(), []
    for n in range(20):
        sec = rng.randint(15, 59) if rng.random() < shorts else rng.randint(240, 1500)
        views = int(subs * rng.uniform(0.05, 1.2))
        out.append({"id": f"{cid}-v{n}", "title": rng.choice(TITLES), "thumb": "",
                    "published": str(today - timedelta(days=n * 3 + rng.randint(1, 3))),
                    "seconds": sec, "views": views,
                    "likes": int(views * rng.uniform(0.02, 0.06)),
                    "comments": int(views * rng.uniform(0.001, 0.004))})
    return out


def top_videos(cid, days, limit=25):
    rng = random.Random(f"{cid}{days}")
    out = []
    for v in sorted(_videos(cid), key=lambda v: -v["views"])[:limit]:
        pv = int(v["views"] * rng.uniform(0.2, 0.7) * min(days, 28) / 28)
        pct = rng.uniform(55, 110) if v["seconds"] < 60 else rng.uniform(25, 55)
        out.append({**v, "period_views": pv,
                    "period_hours": round(pv * v["seconds"] * pct / 100 / 3600, 1),
                    "avg_seconds": int(v["seconds"] * min(pct, 100) / 100),
                    "avg_pct": round(pct, 1),
                    "period_subs": int(pv * rng.uniform(0.001, 0.005))})
    return sorted(out, key=lambda v: -v["period_views"])


def detail(cid, days):
    return {**summary(cid, days), "top": top_videos(cid, days), "recent": _videos(cid)}


def exists(cid):
    return _row(cid) is not None
