"""
YouTube Hub — yerel panel sunucusu.

Sadece bu bilgisayardan erişilir (127.0.0.1). Kanallara yazan her istek
(kapak, banner, geri alma, bağlantı kesme) panel açılırken üretilen gizli bir
anahtar ister; başka bir web sitesi tarayıcın üzerinden kanalına işlem yaptıramaz.
"""

import json
import os
import re
import secrets
import sys
import threading
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import config, oauth  # noqa: E402
from core.images import ImageRejected  # noqa: E402
from core.service import Hub  # noqa: E402

WEB_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_TOKEN = secrets.token_urlsafe(32)
MAX_UPLOAD = 55 * 1024 * 1024


def redirect_uri():
    return f"http://{config.HOST}:{config.PORT}/oauth/callback"


class Handler(BaseHTTPRequestHandler):
    hub = None  # serve() içinde atanır

    def log_message(self, fmt, *args):
        if os.environ.get("YTHUB_DEBUG"):
            super().log_message(fmt, *args)

    # ------------------------------------------------------------------ yardımcılar

    def _host_ok(self):
        # DNS rebinding koruması: sadece yerel ad kabul edilir.
        host = (self.headers.get("Host") or "").lower()
        return host in (f"127.0.0.1:{config.PORT}", f"localhost:{config.PORT}")

    def _send(self, status, body, ctype="application/json; charset=utf-8", headers=None):
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
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status, message):
        self._send(status, {"error": message})

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_UPLOAD:
            raise ImageRejected("Dosya çok büyük.")
        return self.rfile.read(n) if n else b""

    # ------------------------------------------------------------------ GET

    def do_GET(self):
        if not self._host_ok():
            return self._error(403, "Geçersiz host")
        url = urlparse(self.path)
        path, q = url.path, parse_qs(url.query)
        try:
            if path == "/":
                html = open(os.path.join(WEB_DIR, "index.html"), encoding="utf-8").read()
                return self._send(200, html.replace("__SESSION_TOKEN__", SESSION_TOKEN),
                                  "text/html; charset=utf-8")
            if path == "/api/setup":
                try:
                    oauth.load_client()
                    ready, msg = True, ""
                except oauth.SetupMissing as e:
                    ready, msg = False, str(e)
                return self._send(200, {"ready": ready, "message": msg, "redirect_uri": redirect_uri(),
                                        "scopes": config.SCOPES})
            if path == "/api/portfolio":
                return self._send(200, self.hub.portfolio(_days(q)))
            if path == "/api/top-videos":
                return self._send(200, self.hub.top_videos(
                    _days(q), channel_id=q.get("channel", [None])[0], kind=q.get("kind", [None])[0],
                    limit=min(200, int(q.get("limit", ["25"])[0]))))
            if path == "/api/reporting":
                return self._send(200, self.hub.reporting_status(q.get("channel", [None])[0]))
            m = re.fullmatch(r"/api/videos/([\w-]+)/trend", path)
            if m:
                return self._send(200, self.hub.video_trend(m.group(1)))
            if path == "/api/breakdowns":
                return self._send(200, self.hub.breakdowns(_days(q), channel_id=q.get("channel", [None])[0]))
            if path == "/api/sync":
                return self._send(200, self.hub.sync_state)
            if path == "/api/actions":
                return self._send(200, self.hub.actions())
            m = re.fullmatch(r"/api/channels/([\w-]+)/(videos|daily)", path)
            if m:
                cid, what = m.groups()
                data = self.hub.videos(cid) if what == "videos" else self.hub.daily(cid)
                return self._send(200, data)
            if path == "/oauth/start":
                try:
                    target = oauth.start_flow(redirect_uri())
                except oauth.SetupMissing:
                    target = "/?oauth_error=setup"
                return self._send(302, "", headers={"Location": target})
            if path == "/oauth/callback":
                return self._oauth_callback(q)
            return self._error(404, "Bulunamadı")
        except oauth.SetupMissing as e:
            return self._error(400, str(e))
        except Exception as e:
            traceback.print_exc()
            return self._error(500, str(e))

    def _oauth_callback(self, q):
        if "error" in q:
            return self._send(302, "", headers={"Location": "/?oauth_error=" + quote(q["error"][0])})
        try:
            token = oauth.finish_flow(q.get("state", [""])[0], q.get("code", [""])[0])
            cid = self.hub.register(token)
        except Exception as e:
            traceback.print_exc()
            msg = str(e).replace("\n", " ")[:300]
            return self._send(400, f"<meta charset=utf-8><p>Bağlantı başarısız: {_esc(msg)}</p>"
                                   f"<p><a href='/'>Panele dön</a></p>", "text/html; charset=utf-8")
        threading.Thread(target=self.hub.sync_channel, args=(cid,), daemon=True).start()
        return self._send(302, "", headers={"Location": f"/?connected={cid}"})

    # ------------------------------------------------------------------ POST

    def do_POST(self):
        if not self._host_ok():
            return self._error(403, "Geçersiz host")
        if not secrets.compare_digest(self.headers.get("X-Hub-Token", ""), SESSION_TOKEN):
            return self._error(403, "Oturum anahtarı geçersiz; sayfayı yenile.")
        path = urlparse(self.path).path
        try:
            if path == "/api/setup/client-secret":
                n = int(self.headers.get("Content-Length") or 0)
                if n > 64 * 1024:
                    raise ValueError("Dosya çok büyük; bu bir OAuth istemci dosyası değil.")
                oauth.save_client(self.rfile.read(n))
                return self._send(200, {"ready": True})
            if path == "/api/sync":
                started = self.hub.sync_all_async()
                return self._send(202 if started else 409,
                                  {"started": started, **self.hub.sync_state})
            m = re.fullmatch(r"/api/videos/([\w-]+)/thumbnail", path)
            if m:
                return self._send(200, self.hub.set_thumbnail(m.group(1), self._body()))
            m = re.fullmatch(r"/api/channels/([\w-]+)/banner", path)
            if m:
                return self._send(200, self.hub.set_banner(m.group(1), self._body()))
            m = re.fullmatch(r"/api/channels/([\w-]+)/disconnect", path)
            if m:
                self.hub.disconnect(m.group(1))
                return self._send(200, {"ok": True})
            m = re.fullmatch(r"/api/actions/(\d+)/undo", path)
            if m:
                return self._send(200, self.hub.undo(int(m.group(1))))
            return self._error(404, "Bulunamadı")
        except (ImageRejected, ValueError) as e:
            return self._error(400, str(e))
        except KeyError as e:
            return self._error(404, str(e.args[0]) if e.args else "Bulunamadı")
        except Exception as e:
            traceback.print_exc()
            return self._error(502, str(e))


def _days(q):
    try:
        d = int(q.get("days", ["28"])[0])
    except ValueError:
        d = 28
    return d if d in config.WINDOWS else 28


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))


def serve(hub=None, open_browser=True):
    url = f"http://{config.HOST}:{config.PORT}"
    try:
        httpd = ThreadingHTTPServer((config.HOST, config.PORT), Handler)
    except OSError:
        # Port dolu: büyük ihtimalle panel zaten açık. Tarayıcıda onu göster.
        print(f"Panel zaten çalışıyor olabilir → {url}")
        if open_browser:
            webbrowser.open(url)
        return 1
    Handler.hub = hub or Hub()
    print(f"YouTube Hub hazır → {url}")
    print("Bu pencere açık kaldığı sürece panel çalışır. Kapatmak için Ctrl+C.")
    if open_browser:
        threading.Timer(0.6, webbrowser.open, args=(url,)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKapatıldı.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    serve()
