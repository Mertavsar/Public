"""
Web sunucusu — tanıtım sayfası, Google ile giriş, kullanıcı paneli ve API.

Sayfalar:
  /            tanıtım (herkese açık)
  /giris       Google ile giriş
  /panel       kullanıcı paneli (oturum gerekir)
  /kanal-ekle  YouTube kanalı bağla (oturum gerekir)
  /kurulum     ilk kurulum: Google OAuth istemcisi (sadece bu bilgisayardan)
  /gizlilik, /kosullar

Güvenlik:
  - Oturum: HttpOnly + SameSite=Lax çerez; sunucuda sadece özeti tutulur.
  - Yazan her istek oturuma bağlı CSRF anahtarı ister (X-CSRF-Token).
  - Kullanıcı sadece kendine bağlı kanalların verisini görür ve değiştirir.
  - Google dönüşünde `state` hem sunucu hafızasında hem tarayıcı çerezinde eşleşmeli.
  - Host başlığı denetlenir (DNS rebinding).
"""

import json
import os
import re
import secrets
import sys
import threading
import time
import traceback
import webbrowser
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import config, oauth  # noqa: E402
from core.images import ImageRejected  # noqa: E402
from core.service import Hub, NeedsWriteScope  # noqa: E402

WEB_DIR = os.path.dirname(os.path.abspath(__file__))
SETUP_TOKEN = secrets.token_urlsafe(32)   # kurulum sayfasının CSRF anahtarı (süreç başına)
MAX_UPLOAD = 55 * 1024 * 1024
SESSION_COOKIE = "kh_session"
STATE_COOKIE = "kh_oauth"
STATIC_TYPES = {"css": "text/css; charset=utf-8", "svg": "image/svg+xml", "png": "image/png",
                "ico": "image/x-icon", "js": "text/javascript; charset=utf-8"}


def redirect_uri():
    return f"{config.base_url()}/oauth/callback"


def _page(name, **values):
    with open(os.path.join(WEB_DIR, name), encoding="utf-8") as f:
        html = f.read()
    values.setdefault("APP_NAME", config.APP_NAME)
    values.setdefault("CONTACT_EMAIL", config.CONTACT_EMAIL or "—")
    values.setdefault("YEAR", time.strftime("%Y"))
    for k, v in values.items():
        html = html.replace(f"__{k}__", _esc(str(v)))
    return html


class Handler(BaseHTTPRequestHandler):
    hub = None  # serve() içinde atanır

    def log_message(self, fmt, *args):
        if os.environ.get("YTHUB_DEBUG"):
            super().log_message(fmt, *args)

    # ------------------------------------------------------------------ yardımcılar

    def _host_ok(self):
        host = (self.headers.get("Host") or "").lower()
        allowed = {f"127.0.0.1:{config.PORT}", f"localhost:{config.PORT}"}
        if config.PUBLIC_URL:
            allowed.add(urlparse(config.PUBLIC_URL).netloc.lower())
        return host in allowed

    def _is_local(self):
        return self.client_address[0] in ("127.0.0.1", "::1") and not config.PUBLIC_URL

    def _cookies(self):
        c = SimpleCookie()
        try:
            c.load(self.headers.get("Cookie") or "")
        except Exception:
            return {}
        return {k: v.value for k, v in c.items()}

    def _cookie(self, name, value, max_age):
        secure = "; Secure" if config.base_url().startswith("https://") else ""
        return f"{name}={value}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}{secure}"

    def _user(self):
        return self.hub.session_user(self._cookies().get(SESSION_COOKIE))

    def _send(self, status, body, ctype="application/json; charset=utf-8", headers=None, cookies=()):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False, default=str).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        for c in cookies:
            self.send_header("Set-Cookie", c)
        self.end_headers()
        self.wfile.write(body)

    def _html(self, body, status=200, cookies=()):
        self._send(status, body, "text/html; charset=utf-8", cookies=cookies)

    def _redirect(self, location, cookies=()):
        self._send(302, "", headers={"Location": location}, cookies=cookies)

    def _error(self, status, message, **extra):
        self._send(status, {"error": message, **extra})

    def _body(self, limit=MAX_UPLOAD):
        n = int(self.headers.get("Content-Length") or 0)
        if n > limit:
            raise ImageRejected("Dosya çok büyük.")
        return self.rfile.read(n) if n else b""

    # ------------------------------------------------------------------ GET

    def do_GET(self):
        if not self._host_ok():
            return self._error(403, "Geçersiz host")
        url = urlparse(self.path)
        path, q = url.path.rstrip("/") or "/", parse_qs(url.query)
        try:
            # --- herkese açık sayfalar
            m = re.fullmatch(r"/static/([\w-]+\.(css|svg|png|ico|js))", path)
            if m:
                fp = os.path.join(WEB_DIR, "static", m.group(1))
                if not os.path.isfile(fp):
                    return self._error(404, "Bulunamadı")
                with open(fp, "rb") as f:
                    return self._send(200, f.read(), STATIC_TYPES[m.group(2)])
            if path == "/":
                return self._html(_page("landing.html"))
            if path in ("/gizlilik", "/kosullar"):
                return self._html(_page("privacy.html" if path == "/gizlilik" else "terms.html"))
            if path == "/giris":
                if self._user():
                    return self._redirect("/panel")
                return self._html(_page("login.html"))
            if path == "/kurulum":
                return self._html(_page("setup.html", SETUP_TOKEN=SETUP_TOKEN,
                                        MODE="yerel" if not config.PUBLIC_URL else "sunucu",
                                        REDIRECT_URI=redirect_uri()))
            if path == "/api/me":
                u = self._user()
                return self._send(200, {"logged_in": bool(u), "app_name": config.APP_NAME,
                                        **({"email": u["email"], "name": u["name"], "picture": u["picture"]}
                                           if u else {})})
            if path == "/api/setup":
                return self._send(200, {"ready": _client_ready(), "local": self._is_local(),
                                        "redirect_uri": redirect_uri()})

            # --- Google
            if path == "/auth/google":
                return self._start_flow("login")
            if path == "/oauth/callback":
                return self._oauth_callback(q)

            # --- oturum gerektirenler
            user = self._user()
            if path in ("/panel", "/kanal-ekle", "/oauth/start"):
                if not user:
                    return self._redirect("/giris")
                if path == "/panel":
                    return self._html(_page("panel.html", CSRF=user["csrf"], USER_EMAIL=user["email"],
                                            USER_NAME=user["name"] or user["email"],
                                            USER_PICTURE=user["picture"] or ""))
                return self._start_flow("channel", user, write="yazma" in q)
            if path.startswith("/api/"):
                if not user:
                    return self._error(401, "Oturum yok; yeniden giriş yap.")
                return self._api_get(path, q, user)
            return self._html(_page("notfound.html"), status=404)
        except Exception as e:
            traceback.print_exc()
            return self._error(500, str(e))

    def _api_get(self, path, q, user):
        ids = self.hub.channel_ids(user["id"])
        channel = q.get("channel", [None])[0]
        if channel and channel not in ids:
            return self._error(404, "Kanal bulunamadı.")
        if path == "/api/portfolio":
            return self._send(200, self.hub.portfolio(_days(q), channel_ids=ids))
        if path == "/api/top-videos":
            return self._send(200, self.hub.top_videos(
                _days(q), channel_id=channel, kind=q.get("kind", [None])[0],
                limit=min(200, int(q.get("limit", ["25"])[0])), channel_ids=ids))
        if path == "/api/breakdowns":
            return self._send(200, self.hub.breakdowns(_days(q), channel_id=channel, channel_ids=ids))
        if path == "/api/reporting":
            return self._send(200, [r for r in self.hub.reporting_status(channel) if r["channel_id"] in ids])
        if path == "/api/sync":
            return self._send(200, self.hub.sync_state_for(f"user:{user['id']}"))
        if path == "/api/actions":
            return self._send(200, self.hub.actions(channel_ids=ids))
        m = re.fullmatch(r"/api/videos/([\w-]+)/trend", path)
        if m:
            if self.hub.video_channel(m.group(1)) not in ids:
                return self._error(404, "Video bulunamadı.")
            return self._send(200, self.hub.video_trend(m.group(1)))
        m = re.fullmatch(r"/api/channels/([\w-]+)/(videos|daily)", path)
        if m:
            cid, what = m.groups()
            if cid not in ids:
                return self._error(404, "Kanal bulunamadı.")
            return self._send(200, self.hub.videos(cid) if what == "videos" else self.hub.daily(cid))
        return self._error(404, "Bulunamadı")

    # ------------------------------------------------------------------ Google akışı

    def _start_flow(self, purpose, user=None, write=False):
        try:
            if purpose == "login":
                url, state = oauth.start_flow(redirect_uri(), purpose="login", client=self.hub.oauth_client)
            else:
                scopes = config.CHANNEL_SCOPES + ([config.WRITE_SCOPE] if write else [])
                url, state = oauth.start_flow(redirect_uri(), scopes=scopes, purpose="channel",
                                              ctx=user["id"], login_hint=user["email"],
                                              client=self.hub.oauth_client)
        except oauth.SetupMissing:
            return self._redirect("/kurulum" if self._is_local() else "/giris?hata=kurulum")
        return self._redirect(url, cookies=[self._cookie(STATE_COOKIE, state, 600)])

    def _oauth_callback(self, q):
        state = q.get("state", [""])[0]
        clear = self._cookie(STATE_COOKIE, "", 0)
        user = self._user()
        back = "/panel" if user else "/giris"
        if "error" in q:
            return self._redirect(f"{back}?hata={quote(q['error'][0])}", cookies=[clear])
        if not state or not secrets.compare_digest(self._cookies().get(STATE_COOKIE, ""), state):
            return self._redirect(f"{back}?hata=state", cookies=[clear])
        try:
            token, purpose, ctx = oauth.finish_flow(state, q.get("code", [""])[0],
                                                    client=self.hub.oauth_client, transport=self.hub.transport)
            if purpose == "login":
                return self._finish_login(token, clear)
            if not user or user["id"] != ctx:
                return self._redirect("/giris?hata=oturum", cookies=[clear])
            cid = self.hub.register(token, user_id=user["id"])
        except Exception as e:
            traceback.print_exc()
            return self._redirect(f"{back}?hata=baglanti&mesaj={quote(str(e)[:200])}", cookies=[clear])
        threading.Thread(target=self.hub.sync_channel, args=(cid,), daemon=True).start()
        return self._redirect(f"/panel?connected={quote(cid)}", cookies=[clear])

    def _finish_login(self, token, clear):
        """Tek adımlı giriş: kimlik + Google'da seçilen kanal. Kanal varsa hemen bağlanır."""
        claims = oauth.id_claims(token)
        ch, why = self.hub.channel_from_token(token)
        u = self.hub.login(claims, channel_id=ch["id"] if ch else None)
        session, _ = self.hub.create_session(u["id"])
        cookies = [clear, self._cookie(SESSION_COOKIE, session, config.SESSION_DAYS * 86400)]
        if not ch:
            # YouTube izni verilmedi ya da hesapta kanal yok: giriş yine tamam.
            nxt = "/panel" if self.hub.channel_ids(u["id"]) else f"/panel?hata={why}"
            return self._redirect(nxt, cookies=cookies)
        cid, new = ch["id"], not self.hub.owns(u["id"], ch["id"])
        if token.get("refresh_token"):
            self.hub.register(token, user_id=u["id"])
        elif self.hub.has_credentials(cid):
            self.hub.link_channel(u["id"], cid)
        else:
            # Google bu kez kalıcı anahtar vermedi (uygulama daha önce onaylanmış);
            # kanal ekleme akışı onayı yeniden ister.
            return self._redirect("/kanal-ekle", cookies=cookies)
        if new:
            threading.Thread(target=self.hub.sync_channel, args=(cid,), daemon=True).start()
            return self._redirect(f"/panel?connected={quote(cid)}", cookies=cookies)
        return self._redirect("/panel", cookies=cookies)

    # ------------------------------------------------------------------ POST

    def do_POST(self):
        if not self._host_ok():
            return self._error(403, "Geçersiz host")
        path = urlparse(self.path).path
        try:
            if path == "/api/setup/client-secret":
                # Sadece bu bilgisayardan ve kurulum sayfasının anahtarıyla.
                if not self._is_local():
                    return self._error(403, "Kurulum sadece sunucunun kendisinden yapılabilir.")
                if not secrets.compare_digest(self.headers.get("X-CSRF-Token", ""), SETUP_TOKEN):
                    return self._error(403, "Kurulum anahtarı geçersiz; sayfayı yenile.")
                oauth.save_client(self._body(limit=64 * 1024))
                return self._send(200, {"ready": True})

            user = self._user()
            if not user:
                return self._error(401, "Oturum yok; yeniden giriş yap.")
            if not secrets.compare_digest(self.headers.get("X-CSRF-Token", ""), user["csrf"]):
                return self._error(403, "Oturum anahtarı geçersiz; sayfayı yenile.")
            return self._api_post(path, user)
        except NeedsWriteScope as e:
            return self._error(403, str(e), need_write=True)
        except (ImageRejected, ValueError) as e:
            return self._error(400, str(e))
        except KeyError as e:
            return self._error(404, str(e.args[0]) if e.args else "Bulunamadı")
        except Exception as e:
            traceback.print_exc()
            return self._error(502, str(e))

    def _api_post(self, path, user):
        ids = self.hub.channel_ids(user["id"])
        if path == "/cikis":
            self.hub.logout(self._cookies().get(SESSION_COOKIE))
            return self._send(200, {"ok": True}, cookies=[self._cookie(SESSION_COOKIE, "", 0)])
        if path == "/api/sync":
            key = f"user:{user['id']}"
            started = self.hub.sync_all_async(ids, key=key)
            return self._send(202 if started else 409, {"started": started, **self.hub.sync_state_for(key)})
        m = re.fullmatch(r"/api/videos/([\w-]+)/thumbnail", path)
        if m:
            if self.hub.video_channel(m.group(1)) not in ids:
                return self._error(404, "Video bulunamadı.")
            return self._send(200, self.hub.set_thumbnail(m.group(1), self._body()))
        m = re.fullmatch(r"/api/channels/([\w-]+)/(banner|disconnect)", path)
        if m:
            cid, what = m.groups()
            if cid not in ids:
                return self._error(404, "Kanal bulunamadı.")
            if what == "banner":
                return self._send(200, self.hub.set_banner(cid, self._body()))
            self.hub.disconnect(cid, user_id=user["id"])
            return self._send(200, {"ok": True})
        m = re.fullmatch(r"/api/actions/(\d+)/undo", path)
        if m:
            if self.hub.action_channel(int(m.group(1))) not in ids:
                return self._error(404, "İşlem bulunamadı.")
            return self._send(200, self.hub.undo(int(m.group(1))))
        return self._error(404, "Bulunamadı")


def _client_ready():
    try:
        oauth.load_client()
        return True
    except oauth.SetupMissing:
        return False


def _days(q):
    try:
        d = int(q.get("days", ["28"])[0])
    except ValueError:
        d = 28
    return d if d in config.WINDOWS else 28


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))


def _autosync(hub):
    """Sunucu açıkken eski kalan kanalları arka planda senkronize eder. Reporting API
    raporları 30-60 gün sonra silindiği için bu, veri boşluğunu önler."""
    interval = config.AUTOSYNC_HOURS * 3600
    time.sleep(5)
    while True:
        try:
            stale = hub.stale_channels(interval)
            if stale:
                hub.sync_all(stale, key="auto")
        except Exception:
            traceback.print_exc()
        time.sleep(600)


def make_server(hub=None, port=None):
    Handler.hub = hub or Hub()
    return ThreadingHTTPServer((config.HOST, config.PORT if port is None else port), Handler)


def serve(hub=None, open_browser=True):
    url = config.base_url()
    try:
        httpd = make_server(hub)
    except OSError:
        # Port dolu: büyük ihtimalle uygulama zaten açık. Tarayıcıda onu göster.
        print(f"{config.APP_NAME} zaten çalışıyor olabilir → {url}")
        if open_browser:
            webbrowser.open(url)
        return 1
    print(f"{config.APP_NAME} hazır → {url}")
    print("Bu pencere açık kaldığı sürece çalışır. Kapatmak için Ctrl+C.")
    if config.AUTOSYNC_HOURS > 0:
        threading.Thread(target=_autosync, args=(Handler.hub,), daemon=True).start()
    if open_browser and not config.PUBLIC_URL:
        threading.Timer(0.6, webbrowser.open, args=(url,)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKapatıldı.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    serve()
