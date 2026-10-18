#!/usr/bin/env python3
"""
YouTube paneli — kanalı olan herkes Google ile giriş yapar, tüm kanallarını
tek panelde görür.

Kurulum:       pip install -r youtube-panel/requirements.txt
Örnek veriyle: python3 youtube-panel/app.py --demo
Gerçek:        python3 youtube-panel/app.py          (youtube-panel/.env gerekir)
Sunucuda:      uvicorn app:app --app-dir youtube-panel --host 0.0.0.0 --port 8000

Panel sadece OKUR: kanallarda hiçbir şeyi değiştiremez, video yükleyemez, silemez.
"""

import os
import sys
import threading
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from cryptography.fernet import Fernet, InvalidToken
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

import db
import demo
import youtube as yt

APP_DIR = os.path.dirname(os.path.abspath(__file__))


def load_env():
    """youtube-panel/.env dosyasındaki AYAR=değer satırlarını ortama yükler."""
    path = os.path.join(APP_DIR, ".env")
    if not os.path.isfile(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()

# ----------------------------------------------------------------------------
# AYARLAR — hepsi .env veya ortam değişkeninden
# ----------------------------------------------------------------------------

APP_NAME = os.environ.get("APP_NAME", "Kanalist")
PORT = int(os.environ.get("PORT", "8000"))
BASE_URL = os.environ.get("BASE_URL", f"http://localhost:{PORT}").rstrip("/")
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(APP_DIR, "data"))
DEMO = "--demo" in sys.argv or os.environ.get("DEMO") == "1"

REDIRECT_URI = BASE_URL + "/oauth/callback"
COOKIE = "oturum"
SECURE_COOKIE = BASE_URL.startswith("https://")

# Paket başına kanal sınırı. Ödeme sistemi bağlanınca kullanıcının paketi
# (users.plan) buna göre değişir; beta süresince herkes "beta"dadır.
PLAN_LIMITS = {"beta": 50, "free": 2, "pro": 15, "agency": 100}

# Aynı veriyi bu süre boyunca tekrar çekme (kota ve hız için). "Yenile" atlar.
CACHE_SECONDS = 600
ALLOWED_DAYS = (7, 28, 90)

TOKENS = {}   # kanal satır id -> (access_token, bitiş zamanı)
CACHE = {}    # (kanal satır id, tür, gün) -> (zaman, veri)
CACHE_LOCK = threading.Lock()
POOL = ThreadPoolExecutor(max_workers=16)
FERNET = None


def configured():
    return bool(yt.CLIENT["id"] and yt.CLIENT["secret"])


def setup():
    global FERNET
    os.makedirs(DATA_DIR, exist_ok=True)
    if DEMO:
        return
    db.init(os.environ.get("DATABASE_PATH", os.path.join(DATA_DIR, "app.db")))
    yt.CLIENT["id"] = os.environ.get("GOOGLE_CLIENT_ID", "")
    yt.CLIENT["secret"] = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    key = os.environ.get("SECRET_KEY")
    if not key:
        # Geliştirme kolaylığı: anahtar yoksa üret ve sakla. Sunucuda SECRET_KEY
        # mutlaka ortamdan verilmeli; kaybolursa kayıtlı kanal anahtarları açılamaz.
        path = os.path.join(DATA_DIR, "secret.key")
        if not os.path.isfile(path):
            with open(path, "w") as f:
                f.write(Fernet.generate_key().decode())
            os.chmod(path, 0o600)
        key = open(path).read().strip()
    FERNET = Fernet(key.encode())


setup()
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=os.path.join(APP_DIR, "static")), name="static")


@app.middleware("http")
async def security_headers(request, call_next):
    resp = await call_next(request)
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "same-origin"
    return resp


# ----------------------------------------------------------------------------
# OTURUM
# ----------------------------------------------------------------------------

def current_user(request):
    if DEMO:
        return demo.USER
    return db.session_user(request.cookies.get(COOKIE))


def require_user(request):
    user = current_user(request)
    if not user:
        raise HTTPException(401, "Oturum yok")
    return user


def page(name):
    html = open(os.path.join(APP_DIR, "static", name), encoding="utf-8").read()
    return HTMLResponse(html.replace("{{APP_NAME}}", APP_NAME),
                        headers={"Cache-Control": "no-store"})


def back_with_error(message):
    return RedirectResponse("/?hata=" + urllib.parse.quote(message), status_code=303)


# ----------------------------------------------------------------------------
# KANAL VERİSİ
# ----------------------------------------------------------------------------

def access_token(row):
    hit = TOKENS.get(row["id"])
    if hit and hit[1] > time.time() + 60:
        return hit[0]
    try:
        refresh_token = FERNET.decrypt(row["refresh_token"].encode()).decode()
    except InvalidToken:
        raise yt.AuthError("Kanal anahtarı çözülemedi; kanalı yeniden bağla.") from None
    resp = yt.refresh(refresh_token)
    TOKENS[row["id"]] = (resp["access_token"], time.time() + resp.get("expires_in", 3600))
    return resp["access_token"]


def forget(row_id):
    TOKENS.pop(row_id, None)
    with CACHE_LOCK:
        for key in [k for k in CACHE if k[0] == row_id]:
            CACHE.pop(key, None)


def cached(key, fresh, fn):
    with CACHE_LOCK:
        hit = CACHE.get(key)
    if hit and not fresh and hit[0] > time.time() - CACHE_SECONDS:
        return hit[1]
    value = fn()
    with CACHE_LOCK:
        CACHE[key] = (time.time(), value)
    return value


def safe(fn, row):
    """Bir kanalın hatası diğerlerini durdurmasın; hata satırı olarak döner."""
    try:
        return fn()
    except yt.AuthError as exc:
        TOKENS.pop(row["id"], None)
        return {"id": row["channel_id"], "title": row["title"], "thumb": row.get("thumb", ""),
                "error": str(exc), "reauth": True}
    except (yt.ApiError, KeyError, ValueError, IndexError) as exc:
        return {"id": row["channel_id"], "title": row["title"], "thumb": row.get("thumb", ""),
                "error": str(exc)}


def parse_days(request):
    raw = request.query_params.get("days", "28")
    days = int(raw) if raw.isdigit() else 28
    return days if days in ALLOWED_DAYS else 28


def is_fresh(request):
    return request.query_params.get("fresh") == "1"


def span(days):
    start, end = yt.period(days)
    return {"days": days, "start": str(start), "end": str(end)}


# ----------------------------------------------------------------------------
# SAYFALAR VE GİRİŞ
# ----------------------------------------------------------------------------

@app.get("/")
def index(request: Request):
    return page("app.html" if current_user(request) else "landing.html")


@app.get("/giris")
def login(request: Request):
    """Google ile giriş. Oturum açıksa, seçilen kanalı mevcut panele ekler."""
    if DEMO:
        return back_with_error("Örnek veri modundasın; gerçek giriş için --demo olmadan başlat.")
    if not configured():
        return back_with_error("Sunucu ayarları eksik: GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET.")
    user = current_user(request)
    if user and db.count_channels(user["id"]) >= PLAN_LIMITS.get(user["plan"], 0):
        return back_with_error("Paketindeki kanal sınırına ulaştın.")
    state = db.save_state(user["id"] if user else None)
    return RedirectResponse(yt.auth_url(REDIRECT_URI, state), status_code=303)


@app.get("/oauth/callback")
def oauth_callback(request: Request):
    q = request.query_params
    valid, state_user = db.pop_state(q.get("state"))
    if q.get("error"):
        return back_with_error("Google girişi iptal edildi.")
    if not valid or not q.get("code"):
        return back_with_error("Giriş isteğinin süresi doldu. Tekrar dene.")
    try:
        tok = yt.exchange_code(q["code"], REDIRECT_URI)
        if not tok.get("refresh_token"):
            return back_with_error("Google kalıcı erişim vermedi. Tekrar dene.")
        who = yt.userinfo(tok["access_token"])
        try:
            info = yt.my_channel(tok["access_token"])
        except yt.ApiError:
            info = None
    except yt.ApiError as exc:
        return back_with_error(f"Google ile bağlantı kurulamadı: {exc}")

    sub = who.get("sub")
    user_id = state_user or db.user_for_login(sub, info and info["id"])
    if user_id is None:
        user_id = db.create_user(sub, who.get("email"),
                                 who.get("name") or (info and info["title"]), who.get("picture"))

    target, error = "/", None
    if info:
        existing = db.get_channel(user_id, info["id"])
        limit = PLAN_LIMITS.get(db.user_plan(user_id), 0)
        if not existing and db.count_channels(user_id) >= limit:
            error = "Paketindeki kanal sınırına ulaştın; kanal eklenmedi."
        else:
            db.upsert_channel(user_id, info, FERNET.encrypt(tok["refresh_token"].encode()).decode(), sub)
            if existing:
                forget(existing["id"])
            target = "/#/kanal/" + urllib.parse.quote(info["id"])
    else:
        error = ("Bu Google hesabında YouTube kanalı yok. Girişte kanalın bağlı olduğu "
                 "hesabı veya kanalı seç.")

    resp = back_with_error(error) if error else RedirectResponse(target, status_code=303)
    if state_user is None:
        resp.set_cookie(COOKIE, db.create_session(user_id), max_age=db.SESSION_DAYS * 86400,
                        httponly=True, samesite="lax", secure=SECURE_COOKIE)
    return resp


@app.post("/cikis")
def logout(request: Request):
    if not DEMO:
        db.delete_session(request.cookies.get(COOKIE))
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie(COOKIE)
    return resp


# ----------------------------------------------------------------------------
# API
# ----------------------------------------------------------------------------

def user_channels(user):
    return demo.channels() if DEMO else db.list_channels(user["id"])


@app.get("/api/me")
def me(request: Request):
    user = require_user(request)
    return {
        "app_name": APP_NAME,
        "demo": DEMO,
        "user": {k: user.get(k) for k in ("name", "email", "picture", "plan")},
        "limit": PLAN_LIMITS.get(user["plan"], 0),
        "channels": [{"id": c["channel_id"], "title": c["title"], "handle": c.get("handle", ""),
                      "thumb": c.get("thumb", "")} for c in user_channels(user)],
    }


@app.get("/api/overview")
def overview(request: Request):
    user, days, fresh = require_user(request), parse_days(request), is_fresh(request)
    if DEMO:
        return {**span(days), "channels": [demo.summary(c["channel_id"], days)
                                           for c in demo.channels()]}

    def one(row):
        return cached((row["id"], "summary", days), fresh, lambda: safe(
            lambda: yt.channel_summary(access_token(row), row["channel_id"], days), row))

    return {**span(days), "channels": list(POOL.map(one, db.list_channels(user["id"])))}


@app.get("/api/channel/{cid}")
def channel(cid: str, request: Request):
    user, days, fresh = require_user(request), parse_days(request), is_fresh(request)
    if DEMO:
        if not demo.exists(cid):
            raise HTTPException(404, "Kanal bulunamadı")
        return {**span(days), **demo.detail(cid, days)}
    row = db.get_channel(user["id"], cid)
    if not row:
        raise HTTPException(404, "Kanal bulunamadı")
    return {**span(days), **cached((row["id"], "detail", days), fresh, lambda: safe(
        lambda: yt.channel_detail(access_token(row), cid, days), row))}


@app.get("/api/top-videos")
def top_videos(request: Request):
    """Tüm kanallarda dönemin en çok izlenen videoları."""
    user, days, fresh = require_user(request), parse_days(request), is_fresh(request)
    rows = user_channels(user)

    def one(row):
        if DEMO:
            vids = demo.top_videos(row["channel_id"], days, 10)
        else:
            vids = cached((row["id"], "top", days), fresh, lambda: safe(
                lambda: yt.top_videos(access_token(row), days, 10), row))
            if isinstance(vids, dict):  # bu kanalda hata var; listeyi bozmasın
                return []
        return [{**v, "channel": {"id": row["channel_id"], "title": row["title"],
                                  "thumb": row.get("thumb", "")}} for v in vids]

    videos = [v for chunk in POOL.map(one, rows) for v in chunk]
    return {**span(days), "videos": sorted(videos, key=lambda v: -v["period_views"])[:20]}


@app.delete("/api/channel/{cid}")
def remove_channel(cid: str, request: Request):
    user = require_user(request)
    if DEMO:
        raise HTTPException(400, "Örnek veri modunda kanal kaldırılamaz")
    row = db.get_channel(user["id"], cid)
    if not row:
        raise HTTPException(404, "Kanal bulunamadı")
    try:
        yt.revoke(FERNET.decrypt(row["refresh_token"].encode()).decode())
    except InvalidToken:
        pass
    db.delete_channel(user["id"], cid)
    forget(row["id"])
    return {"ok": True}


@app.delete("/api/account")
def delete_account(request: Request):
    """Hesabı ve tüm bağlı kanal anahtarlarını kalıcı olarak siler."""
    user = require_user(request)
    if DEMO:
        raise HTTPException(400, "Örnek veri modunda hesap silinemez")
    for row in db.list_channels(user["id"]):
        try:
            yt.revoke(FERNET.decrypt(row["refresh_token"].encode()).decode())
        except InvalidToken:
            pass
        forget(row["id"])
    db.delete_user(user["id"])
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(COOKIE)
    return resp


if __name__ == "__main__":
    import uvicorn

    if DEMO:
        print("ÖRNEK VERİ MODU — Google'a bağlanmaz, uydurma kanallar gösterir.")
    elif not configured():
        print("UYARI: GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET yok. Giriş çalışmaz.")
        print("Kurulum: youtube-panel/README.md\n")
    print(f"{APP_NAME}:  {BASE_URL}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
