"""
Google / YouTube katmanı.

Sadece OKUR. İstenen izinler youtube.readonly ve yt-analytics.readonly'dir;
kanallarda hiçbir şey değiştirilemez.
"""

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
DATA_API = "https://www.googleapis.com/youtube/v3/"
ANALYTICS_API = "https://youtubeanalytics.googleapis.com/v2/reports"

# Giriş ve kanal bağlama tek adımdır: Google ile giren kişinin kanalı panele gelir.
SCOPES = [
    "openid", "email", "profile",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

# YouTube Analytics verisi yaklaşık 2 gün gecikmeli gelir. Son günler eksik
# görünüp grafikte sahte bir düşüş çizmesin diye dönem bu kadar gün önce biter.
ANALYTICS_LAG_DAYS = 2

CLIENT = {"id": "", "secret": ""}


class ApiError(Exception):
    pass


class AuthError(ApiError):
    """Yetki geri alınmış veya süresi dolmuş — kanal yeniden bağlanmalı."""


# ----------------------------------------------------------------------------
# HTTP
# ----------------------------------------------------------------------------

def http_json(url, form=None, token=None):
    headers = {"Authorization": "Bearer " + token} if token else {}
    body = urllib.parse.urlencode(form).encode() if form is not None else None
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
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


def yt(resource, token, **params):
    return http_json(DATA_API + resource + "?" + urllib.parse.urlencode(params), token=token)


def report(token, **params):
    """YouTube Analytics raporu -> satır başına sözlük listesi."""
    resp = http_json(ANALYTICS_API + "?" + urllib.parse.urlencode(params), token=token)
    names = [h["name"] for h in resp.get("columnHeaders", [])]
    return [dict(zip(names, row)) for row in resp.get("rows") or []]


# ----------------------------------------------------------------------------
# GİRİŞ
# ----------------------------------------------------------------------------

def auth_url(redirect_uri, state):
    return AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": CLIENT["id"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "state": state,
        "access_type": "offline",            # kalıcı yenileme anahtarı için
        "prompt": "consent select_account",  # her seferinde hesap/kanal seçtir
    })


def exchange_code(code, redirect_uri):
    return http_json(TOKEN_URL, form={
        "code": code,
        "client_id": CLIENT["id"],
        "client_secret": CLIENT["secret"],
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    })


def refresh(refresh_token):
    return http_json(TOKEN_URL, form={
        "client_id": CLIENT["id"],
        "client_secret": CLIENT["secret"],
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    })


def revoke(token):
    """Kanal panelden kaldırılınca Google'daki izni de geri al. Hata önemsiz."""
    try:
        http_json(REVOKE_URL, form={"token": token})
    except ApiError:
        pass


def userinfo(access_token):
    """Giriş yapan Google kimliği. Brand Account seçildiyse e-posta olmayabilir."""
    try:
        return http_json(USERINFO_URL, token=access_token)
    except ApiError:
        return {}


# ----------------------------------------------------------------------------
# HESAPLAMA
# ----------------------------------------------------------------------------

def period(days):
    end = date.today() - timedelta(days=ANALYTICS_LAG_DAYS)
    return end - timedelta(days=days - 1), end


def iso_seconds(duration):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration or "")
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


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
        "series": cur, "prev_series": prev,
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
            thumbs = v["snippet"].get("thumbnails", {})
            out[v["id"]] = {
                "id": v["id"],
                "title": v["snippet"]["title"],
                "thumb": (thumbs.get("medium") or thumbs.get("default") or {}).get("url", ""),
                "published": v["snippet"]["publishedAt"][:10],
                "seconds": iso_seconds(v["contentDetails"].get("duration")),
                "views": int(st.get("viewCount", 0)),
                "likes": int(st.get("likeCount", 0)),
                "comments": int(st.get("commentCount", 0)),
            }
    return out


# ----------------------------------------------------------------------------
# KANAL VERİSİ
# ----------------------------------------------------------------------------

def my_channel(token):
    items = yt("channels", token, part="snippet,statistics", mine="true").get("items")
    if not items:
        raise ApiError("Seçilen Google hesabında YouTube kanalı yok. Girişte kanalı seç.")
    return channel_info(items[0])


def channel_summary(token, cid, days):
    items = yt("channels", token, part="snippet,statistics", id=cid).get("items")
    if not items:
        raise ApiError("Kanal bulunamadı veya erişim kaldırılmış.")
    start, end = period(2 * days)
    rows = report(token, ids="channel==MINE", startDate=start, endDate=end, dimensions="day",
                  metrics="views,estimatedMinutesWatched,subscribersGained,subscribersLost",
                  sort="day")
    return {**channel_info(items[0]), **summarize(fill_days(rows, start, end), days)}


def top_videos(token, days, limit=25):
    """Dönemin en çok izlenen videoları, video bilgileriyle birlikte."""
    start, end = period(days)
    rows = report(token, ids="channel==MINE", startDate=start, endDate=end, dimensions="video",
                  metrics="views,estimatedMinutesWatched,averageViewDuration,"
                          "averageViewPercentage,likes,comments,subscribersGained",
                  sort="-views", maxResults=limit)
    videos = video_rows(token, [r["video"] for r in rows])
    out = []
    for r in rows:
        v = videos.get(r["video"])
        if not v:
            continue
        out.append({**v,
                    "period_views": int(r["views"]),
                    "period_hours": round(int(r["estimatedMinutesWatched"]) / 60, 1),
                    "avg_seconds": int(r["averageViewDuration"]),
                    "avg_pct": round(float(r["averageViewPercentage"]), 1),
                    "period_subs": int(r["subscribersGained"])})
    return out


def channel_detail(token, cid, days):
    summary = channel_summary(token, cid, days)
    ch = yt("channels", token, part="contentDetails", id=cid)["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    recent_ids = [p["contentDetails"]["videoId"] for p in
                  yt("playlistItems", token, part="contentDetails", playlistId=uploads,
                     maxResults=20).get("items", [])]
    recent = video_rows(token, recent_ids)
    return {**summary, "top": top_videos(token, days),
            "recent": [recent[i] for i in recent_ids if i in recent]}
