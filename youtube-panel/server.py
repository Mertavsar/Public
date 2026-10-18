#!/usr/bin/env python3
"""
YouTube paneli — tüm kanallar tek ekranda.

Çalıştırmak için:   python3 youtube-panel/server.py
Örnek veriyle dene: python3 youtube-panel/server.py --demo
Sonra tarayıcıda:   http://127.0.0.1:7788

Bu panel sadece OKUR. İstenen izinler youtube.readonly ve yt-analytics.readonly'dir;
kanallarda hiçbir şeyi değiştiremez, video yükleyemez, silemez.

Her kanal bir kez "Kanal bağla" ile Google hesabından yetkilendirilir. Bir Google
hesabında birden fazla kanal (Brand Account) varsa, Google giriş ekranında hangi
kanalı bağlayacağını seçersin; her kanal için bir kez tekrarla.
"""

import http.server
import json
import os
import random
import re
import secrets
import socketserver
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from urllib.parse import parse_qs, urlparse

# ----------------------------------------------------------------------------
# AYARLAR
# ----------------------------------------------------------------------------

PORT = 7788
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_DIR, "data")
SECRET_FILE = os.path.join(DATA_DIR, "client_secret.json")
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")

REDIRECT_URI = f"http://127.0.0.1:{PORT}/oauth/callback"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
DATA_API = "https://www.googleapis.com/youtube/v3/"
ANALYTICS_API = "https://youtubeanalytics.googleapis.com/v2/reports"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

# YouTube Analytics verisi yaklaşık 2 gün gecikmeli gelir. Son günler eksik
# görünüp grafikte sahte bir düşüş çizmesin diye dönem bu kadar gün önce biter.
ANALYTICS_LAG_DAYS = 2

# Aynı veriyi bu süre boyunca tekrar çekme (kota ve hız için). "Yenile" atlar.
CACHE_SECONDS = 600

ALLOWED_DAYS = (7, 28, 90)
DEMO = "--demo" in sys.argv

STORE_LOCK = threading.Lock()
TOKENS = {}          # kanal id -> (access_token, bitiş zamanı)
CACHE = {}           # anahtar -> (zaman, veri)
PENDING_STATES = set()


class ApiError(Exception):
    pass


class AuthError(ApiError):
    """Yetki geri alınmış veya süresi dolmuş — kanal yeniden bağlanmalı."""


# ----------------------------------------------------------------------------
# YEREL KAYIT
# ----------------------------------------------------------------------------

def client_secret():
    """Google Cloud'dan indirilen OAuth istemci dosyası (Masaüstü uygulaması)."""
    try:
        data = json.load(open(SECRET_FILE, encoding="utf-8"))
    except (OSError, ValueError):
        return None
    sec = data.get("installed") or data.get("web") or {}
    if not sec.get("client_id") or not sec.get("client_secret"):
        return None
    return sec


def load_channels():
    try:
        return json.load(open(CHANNELS_FILE, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_channels(channels):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = CHANNELS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)
    os.chmod(tmp, 0o600)  # yenileme anahtarları burada; sadece sen oku
    os.replace(tmp, CHANNELS_FILE)


# ----------------------------------------------------------------------------
# GOOGLE
# ----------------------------------------------------------------------------

def http_json(url, form=None, token=None):
    headers = {"Authorization": "Bearer " + token} if token else {}
    body = urllib.parse.urlencode(form).encode() if form is not None else None
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as exc:
        try:
            err = json.load(exc)
        except ValueError:
            err = {}
        e = err.get("error")
        msg = (e.get("message") if isinstance(e, dict) else
               err.get("error_description") or e) or f"HTTP {exc.code}"
        if exc.code == 401 or e == "invalid_grant":
            raise AuthError(msg) from None
        raise ApiError(msg) from None
    except urllib.error.URLError as exc:
        raise ApiError(f"Google'a bağlanılamadı: {exc.reason}") from None


def access_token(cid, channel):
    cached = TOKENS.get(cid)
    if cached and cached[1] > time.time() + 60:
        return cached[0]
    sec = client_secret()
    if not sec:
        raise ApiError("data/client_secret.json bulunamadı. README'deki kurulumu yap.")
    resp = http_json(TOKEN_URL, form={
        "client_id": sec["client_id"],
        "client_secret": sec["client_secret"],
        "refresh_token": channel["refresh_token"],
        "grant_type": "refresh_token",
    })
    TOKENS[cid] = (resp["access_token"], time.time() + resp.get("expires_in", 3600))
    return resp["access_token"]


def yt(resource, token, **params):
    return http_json(DATA_API + resource + "?" + urllib.parse.urlencode(params), token=token)


def report(token, **params):
    """YouTube Analytics raporu -> satır başına sözlük listesi."""
    resp = http_json(ANALYTICS_API + "?" + urllib.parse.urlencode(params), token=token)
    names = [h["name"] for h in resp.get("columnHeaders", [])]
    return [dict(zip(names, row)) for row in resp.get("rows") or []]


def period(days):
    end = date.today() - timedelta(days=ANALYTICS_LAG_DAYS)
    return end - timedelta(days=days - 1), end


def iso_seconds(duration):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration or "")
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


# ----------------------------------------------------------------------------
# HESAPLAMA
# ----------------------------------------------------------------------------

def fill_days(rows, start, end):
    """Analytics hiç izlenmeyen günleri döndürmez; o günleri sıfırla doldur."""
    by_day = {r["day"]: r for r in rows}
    out, d = [], start
    while d <= end:
        r = by_day.get(str(d), {})
        out.append({
            "d": str(d),
            "views": int(r.get("views", 0)),
            "minutes": int(r.get("estimatedMinutesWatched", 0)),
            "subs": int(r.get("subscribersGained", 0)) - int(r.get("subscribersLost", 0)),
        })
        d += timedelta(days=1)
    return out


def change(cur, prev):
    return round((cur - prev) / prev * 100, 1) if prev else None


def summarize(series, days):
    """İki dönemlik günlük seri -> bu dönem, önceki dönem ve değişim."""
    prev, cur = series[:-days], series[-days:]
    views, prev_views = sum(x["views"] for x in cur), sum(x["views"] for x in prev)
    hours = sum(x["minutes"] for x in cur) / 60
    prev_hours = sum(x["minutes"] for x in prev) / 60
    subs, prev_subs = sum(x["subs"] for x in cur), sum(x["subs"] for x in prev)
    return {
        "views": views, "prev_views": prev_views, "views_change": change(views, prev_views),
        "hours": round(hours), "prev_hours": round(prev_hours),
        "hours_change": change(hours, prev_hours),
        "subs": subs, "prev_subs": prev_subs,
        "series": cur,
    }


def channel_info(item):
    st, sn = item.get("statistics", {}), item["snippet"]
    return {
        "id": item["id"],
        "title": sn["title"],
        "handle": sn.get("customUrl", ""),
        "thumb": sn.get("thumbnails", {}).get("default", {}).get("url", ""),
        "subscribers": None if st.get("hiddenSubscriberCount") else int(st.get("subscriberCount", 0)),
        "total_views": int(st.get("viewCount", 0)),
        "video_count": int(st.get("videoCount", 0)),
    }


def video_rows(token, ids):
    out = {}
    for i in range(0, len(ids), 50):
        resp = yt("videos", token, part="snippet,statistics,contentDetails",
                  id=",".join(ids[i:i + 50]))
        for v in resp.get("items", []):
            st = v.get("statistics", {})
            out[v["id"]] = {
                "id": v["id"],
                "title": v["snippet"]["title"],
                "thumb": v["snippet"].get("thumbnails", {}).get("default", {}).get("url", ""),
                "published": v["snippet"]["publishedAt"][:10],
                "seconds": iso_seconds(v["contentDetails"].get("duration")),
                "views": int(st.get("viewCount", 0)),
                "likes": int(st.get("likeCount", 0)),
                "comments": int(st.get("commentCount", 0)),
            }
    return out


def channel_summary(cid, channel, days):
    tok = access_token(cid, channel)
    items = yt("channels", tok, part="snippet,statistics", id=cid).get("items")
    if not items:
        raise ApiError("Kanal bulunamadı veya erişim kaldırılmış.")
    start, end = period(2 * days)
    rows = report(tok, ids="channel==MINE", startDate=start, endDate=end, dimensions="day",
                  metrics="views,estimatedMinutesWatched,subscribersGained,subscribersLost",
                  sort="day")
    return {**channel_info(items[0]), **summarize(fill_days(rows, start, end), days)}


def channel_detail(cid, channel, days):
    tok = access_token(cid, channel)
    summary = channel_summary(cid, channel, days)
    start, end = period(days)
    top = report(tok, ids="channel==MINE", startDate=start, endDate=end, dimensions="video",
                 metrics="views,estimatedMinutesWatched,averageViewDuration,"
                         "averageViewPercentage,likes,comments,subscribersGained",
                 sort="-views", maxResults=25)
    ch = yt("channels", tok, part="contentDetails", id=cid)["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    recent_ids = [p["contentDetails"]["videoId"] for p in
                  yt("playlistItems", tok, part="contentDetails", playlistId=uploads,
                     maxResults=20).get("items", [])]
    videos = video_rows(tok, list(dict.fromkeys(recent_ids + [r["video"] for r in top])))
    top_out = []
    for r in top:
        v = videos.get(r["video"])
        if not v:
            continue
        top_out.append({**v,
                        "period_views": int(r["views"]),
                        "period_hours": round(int(r["estimatedMinutesWatched"]) / 60, 1),
                        "avg_seconds": int(r["averageViewDuration"]),
                        "avg_pct": round(float(r["averageViewPercentage"]), 1),
                        "period_subs": int(r["subscribersGained"])})
    return {**summary, "top": top_out,
            "recent": [videos[i] for i in recent_ids if i in videos]}


# ----------------------------------------------------------------------------
# ÖRNEK VERİ (--demo) — Google bağlantısı olmadan paneli görmek için
# ----------------------------------------------------------------------------

DEMO_CHANNELS = [
    ("demo-mutfak", "Mutfak Sırları", "@mutfaksirlari", 184000, 1.12),
    ("demo-tekno", "Teknoloji Kutusu", "@teknolojikutusu", 92300, 0.81),
    ("demo-gezgin", "Gezgin Çift", "@gezgincift", 41200, 1.35),
    ("demo-oyun", "Oyun Atölyesi", "@oyunatolyesi", 12800, 0.97),
    ("demo-kisa", "Kısa Bilgi", "@kisabilgi", 256000, 1.04),
]
DEMO_TITLES = [
    "5 dakikada evde pratik tarif", "Kimsenin bilmediği 3 püf noktası",
    "Bunu denemeden karar verme", "Bir haftalık deneyim: sonuç şaşırttı",
    "En çok sorulan soruya cevap", "Yeni başlayanlar için rehber",
    "Bu hatayı herkes yapıyor", "Ucuz mu pahalı mı? Karşılaştırma",
    "Bir günüm nasıl geçiyor", "İzleyici yorumlarını denedik",
]


def demo_series(cid, days):
    _, _, _, subs, trend = next(c for c in DEMO_CHANNELS if c[0] == cid)
    rng = random.Random(cid)
    start, end = period(2 * days)
    base, out, d, i, total = subs * 0.02, [], start, 0, 2 * days
    while d <= end:
        growth = trend ** (i / total)
        weekly = 1 + 0.12 * (d.weekday() >= 5)
        spike = 2.6 if rng.random() < 0.04 else 1
        views = int(base * growth * weekly * spike * rng.uniform(0.85, 1.15))
        out.append({"d": str(d), "views": views,
                    "minutes": int(views * rng.uniform(0.6, 1.4)),
                    "subs": int(views * rng.uniform(0.002, 0.006)) - rng.randint(0, 6)})
        d += timedelta(days=1)
        i += 1
    return out


def demo_summary(cid, days):
    _, title, handle, subs, _ = next(c for c in DEMO_CHANNELS if c[0] == cid)
    rng = random.Random(cid + "info")
    return {"id": cid, "title": title, "handle": handle, "thumb": "",
            "subscribers": subs, "total_views": subs * rng.randint(60, 140),
            "video_count": rng.randint(40, 600),
            **summarize(demo_series(cid, days), days)}


def demo_detail(cid, days):
    summary = demo_summary(cid, days)
    rng = random.Random(cid + str(days))
    today = date.today()
    recent = []
    for n in range(20):
        sec = rng.choice([rng.randint(15, 59), rng.randint(240, 1500)])
        views = int(summary["subscribers"] * rng.uniform(0.05, 1.2))
        recent.append({"id": f"{cid}-v{n}", "title": DEMO_TITLES[n % len(DEMO_TITLES)],
                       "thumb": "", "published": str(today - timedelta(days=n * 3 + 1)),
                       "seconds": sec, "views": views,
                       "likes": int(views * rng.uniform(0.02, 0.06)),
                       "comments": int(views * rng.uniform(0.001, 0.004))})
    top = []
    for v in sorted(recent, key=lambda v: -v["views"])[:12]:
        pv = int(v["views"] * rng.uniform(0.2, 0.7))
        pct = rng.uniform(55, 110) if v["seconds"] < 60 else rng.uniform(25, 55)
        top.append({**v, "period_views": pv,
                    "period_hours": round(pv * v["seconds"] * pct / 100 / 3600, 1),
                    "avg_seconds": int(v["seconds"] * min(pct, 100) / 100),
                    "avg_pct": round(pct, 1),
                    "period_subs": int(pv * rng.uniform(0.001, 0.005))})
    top.sort(key=lambda v: -v["period_views"])
    return {**summary, "top": top, "recent": recent}


# ----------------------------------------------------------------------------
# PANEL VERİSİ
# ----------------------------------------------------------------------------

def cached(key, fresh, fn):
    hit = CACHE.get(key)
    if hit and not fresh and hit[0] > time.time() - CACHE_SECONDS:
        return hit[1]
    value = fn()
    CACHE[key] = (time.time(), value)
    return value


def safe(fn, cid, channel, days):
    try:
        return fn(cid, channel, days)
    except AuthError as exc:
        TOKENS.pop(cid, None)
        return {"id": cid, "title": channel.get("title", cid), "error": str(exc), "reauth": True}
    except (ApiError, KeyError, ValueError) as exc:
        return {"id": cid, "title": channel.get("title", cid), "error": str(exc)}


def overview(days, fresh):
    start, end = period(days)
    base = {"days": days, "start": str(start), "end": str(end), "demo": DEMO}
    if DEMO:
        return {**base, "configured": True,
                "channels": [demo_summary(c[0], days) for c in DEMO_CHANNELS]}
    with STORE_LOCK:
        channels = load_channels()

    def one(item):
        cid, ch = item
        return cached(("summary", cid, days), fresh,
                      lambda: safe(channel_summary, cid, ch, days))

    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(one, channels.items()))
    return {**base, "configured": client_secret() is not None, "channels": rows}


def detail(cid, days, fresh):
    start, end = period(days)
    base = {"days": days, "start": str(start), "end": str(end)}
    if DEMO:
        if not any(c[0] == cid for c in DEMO_CHANNELS):
            return None
        return {**base, **demo_detail(cid, days)}
    with STORE_LOCK:
        ch = load_channels().get(cid)
    if not ch:
        return None
    return {**base, **cached(("detail", cid, days), fresh,
                             lambda: safe(channel_detail, cid, ch, days))}


# ----------------------------------------------------------------------------
# GOOGLE GİRİŞİ
# ----------------------------------------------------------------------------

def auth_redirect():
    sec = client_secret()
    state = secrets.token_urlsafe(16)
    PENDING_STATES.add(state)
    return AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": sec["client_id"],
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",           # kalıcı yenileme anahtarı için
        "prompt": "consent select_account",  # her seferinde hesap/kanal seçtir
        "state": state,
    })


def finish_auth(query):
    if query.get("error"):
        raise ApiError(f"Google girişi iptal edildi ({query['error'][0]}).")
    state = (query.get("state") or [""])[0]
    if state not in PENDING_STATES:
        raise ApiError("Giriş isteği tanınmadı. Panelden tekrar 'Kanal bağla'ya bas.")
    PENDING_STATES.discard(state)
    sec = client_secret()
    tok = http_json(TOKEN_URL, form={
        "code": query["code"][0],
        "client_id": sec["client_id"],
        "client_secret": sec["client_secret"],
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    })
    if not tok.get("refresh_token"):
        raise ApiError("Google kalıcı anahtar vermedi. Tekrar dene.")
    items = yt("channels", tok["access_token"], part="snippet", mine="true").get("items")
    if not items:
        raise ApiError("Seçilen Google hesabında YouTube kanalı yok. Girişte kanalı seç.")
    info = items[0]
    with STORE_LOCK:
        channels = load_channels()
        channels[info["id"]] = {"title": info["snippet"]["title"],
                                "refresh_token": tok["refresh_token"],
                                "added": str(date.today())}
        save_channels(channels)
    TOKENS[info["id"]] = (tok["access_token"], time.time() + tok.get("expires_in", 3600))
    for key in [k for k in CACHE if k[1] == info["id"]]:
        CACHE.pop(key, None)


# ----------------------------------------------------------------------------
# HTTP
# ----------------------------------------------------------------------------

def message_page(text):
    return f"""<!doctype html><meta charset="utf-8"><title>YouTube Paneli</title>
<body style="font:15px/1.6 system-ui;max-width:560px;margin:60px auto;padding:0 16px">
<p>{text}</p><p><a href="/">Panele dön</a></p></body>""".encode("utf-8")


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, body, ctype, code=200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8", code)

    def _redirect(self, url):
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        days = int(q.get("days", ["28"])[0]) if q.get("days", ["28"])[0].isdigit() else 28
        days = days if days in ALLOWED_DAYS else 28
        fresh = q.get("fresh") == ["1"]

        if url.path in ("/", "/index.html"):
            try:
                body = open(os.path.join(APP_DIR, "index.html"), "rb").read()
            except OSError:
                self.send_error(500, "index.html bulunamadi")
                return
            self._send(body, "text/html; charset=utf-8")
        elif url.path == "/api/overview":
            self._json(overview(days, fresh))
        elif url.path.startswith("/api/channel/"):
            data = detail(url.path.rsplit("/", 1)[-1], days, fresh)
            self._json(data or {"error": "Kanal bulunamadı"}, 200 if data else 404)
        elif url.path == "/oauth/start":
            if DEMO:
                self._send(message_page("Örnek veri modundasın. Gerçek kanal bağlamak için "
                                        "paneli <code>--demo</code> olmadan başlat."),
                           "text/html; charset=utf-8")
            elif not client_secret():
                self._send(message_page("Önce <code>youtube-panel/data/client_secret.json</code> "
                                        "dosyasını koy. Adımlar README'de."),
                           "text/html; charset=utf-8")
            else:
                self._redirect(auth_redirect())
        elif url.path == "/oauth/callback":
            try:
                finish_auth(q)
            except (ApiError, KeyError) as exc:
                self._send(message_page(f"Kanal bağlanamadı: {exc}"),
                           "text/html; charset=utf-8", 400)
                return
            self._redirect("/")
        else:
            self.send_error(404)

    def do_POST(self):
        m = re.fullmatch(r"/api/channel/([\w-]+)/remove", urlparse(self.path).path)
        if not m or DEMO:
            self.send_error(404)
            return
        with STORE_LOCK:
            channels = load_channels()
            removed = channels.pop(m.group(1), None)
            save_channels(channels)
        TOKENS.pop(m.group(1), None)
        self._json({"ok": removed is not None})


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    if DEMO:
        print("ÖRNEK VERİ MODU — Google'a bağlanmaz, uydurma kanallar gösterir.")
    elif not client_secret():
        print("UYARI: youtube-panel/data/client_secret.json yok. Kanal bağlanamaz.")
        print("Kurulum adımları: youtube-panel/README.md\n")
    print(f"YouTube paneli:  http://127.0.0.1:{PORT}")
    print("Durdurmak için Ctrl+C\n")
    with Server(("127.0.0.1", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKapatıldı.")


if __name__ == "__main__":
    main()
