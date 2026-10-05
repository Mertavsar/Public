"""Sunucu üzerinden uçtan uca: tanıtım, giriş, kanal bağlama, oturum, sahiplik, CSRF."""

import http.client
import json
import os
import re
import sys
import tempfile
import threading
import time
import unittest
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import config  # noqa: E402
from core.service import Hub  # noqa: E402
from fake_google import FakeGoogle, jpeg  # noqa: E402
from web import server  # noqa: E402

CLIENT = {"client_id": "cid.apps.googleusercontent.com", "client_secret": "sec"}


class WebTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.old = (config.PORT, config.APP_NAME, config.AUTOSYNC_HOURS)
        cls.g = FakeGoogle()
        cls.hub = Hub(db_path=os.path.join(cls.tmp.name, "t.db"), transport=cls.g, oauth_client=CLIENT,
                      assets_dir=os.path.join(cls.tmp.name, "a"), sleep=lambda s: None)
        cls.httpd = server.make_server(cls.hub, port=0)
        config.PORT = cls.httpd.server_address[1]
        config.APP_NAME = "Kanalist"
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        config.PORT, config.APP_NAME, config.AUTOSYNC_HOURS = cls.old
        cls.tmp.cleanup()

    def req(self, method, path, cookies=None, headers=None, body=None, host=None):
        c = http.client.HTTPConnection("127.0.0.1", config.PORT, timeout=10)
        h = {"Host": host or f"127.0.0.1:{config.PORT}", **(headers or {})}
        if cookies:
            h["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())
        c.request(method, path, body=body, headers=h)
        r = c.getresponse()
        data = r.read()
        set_cookies = {}
        for k, v in r.getheaders():
            if k.lower() == "set-cookie":
                name, val = v.split(";", 1)[0].split("=", 1)
                set_cookies[name] = val
        return r.status, dict(r.getheaders()), data, set_cookies

    def login(self):
        st, h, _, ck = self.req("GET", "/auth/google")
        self.assertEqual(st, 302)
        self.assertTrue(h["Location"].startswith("https://accounts.google.com/"))
        state = parse_qs(urlparse(h["Location"]).query)["state"][0]
        self.assertEqual(ck["kh_oauth"], state)
        self.last_location = h["Location"]
        return state, ck

    def callback(self, state, ck):
        st, h, _, ck2 = self.req("GET", f"/oauth/callback?state={state}&code=c", cookies=ck)
        return h["Location"], ck2.get("kh_session")

    def test_flow(self):
        # tanıtım ve yasal sayfalar herkese açık
        st, _, body, _ = self.req("GET", "/")
        self.assertEqual(st, 200)
        self.assertIn("Kanalist", body.decode())
        self.assertNotIn("__APP_NAME__", body.decode())
        for page in ("/gizlilik", "/kosullar", "/giris", "/static/site.css"):
            self.assertEqual(self.req("GET", page)[0], 200, page)
        self.assertEqual(self.req("GET", "/yok-boyle-sayfa")[0], 404)
        # oturumsuz
        st, h, _, _ = self.req("GET", "/panel")
        self.assertEqual((st, h["Location"]), (302, "/giris"))
        self.assertEqual(self.req("GET", "/api/portfolio")[0], 401)
        self.assertEqual(self.req("GET", "/", host="evil.com")[0], 403)

        # giriş: çerezdeki state eşleşmezse reddedilir
        state, ck = self.login()
        self.assertIn("youtube.readonly", self.last_location)          # giriş ve kanal onayı tek ekranda
        st, h, _, _ = self.req("GET", f"/oauth/callback?state={state}&code=c")
        self.assertIn("hata=state", h["Location"])
        st, h, _, ck2 = self.req("GET", f"/oauth/callback?state={state}&code=c", cookies=ck)
        self.assertEqual((st, h["Location"]), (302, "/panel?connected=UC_test"))  # kanal girişte bağlandı
        session = {"kh_session": ck2["kh_session"]}
        for _ in range(100):
            if self.hub.portfolio()["anchor"]:
                break
            time.sleep(0.05)

        # ek kanal akışı: e-posta ipucuyla, her seferinde onay
        st, h, _, ck3 = self.req("GET", "/kanal-ekle", cookies=session)
        loc = h["Location"]
        self.assertIn("login_hint=ali%40example.com", loc)
        self.assertIn("prompt=consent", loc)
        st2 = parse_qs(urlparse(loc).query)["state"][0]
        st, h, _, _ = self.req("GET", f"/oauth/callback?state={st2}&code=c", cookies={**session, **ck3})
        self.assertEqual(h["Location"], "/panel?connected=UC_test")

        # panel ve veri
        st, _, body, _ = self.req("GET", "/panel", cookies=session)
        html = body.decode()
        self.assertEqual(st, 200)
        self.assertIn("ali@example.com", html)
        csrf = re.search(r'const CSRF = "([^"]+)"', html).group(1)
        st, _, body, _ = self.req("GET", "/api/portfolio?days=28", cookies=session)
        self.assertEqual([c["id"] for c in json.loads(body)["channels"]], ["UC_test"])
        self.assertEqual(json.loads(self.req("GET", "/api/me", cookies=session)[2])["email"], "ali@example.com")

        # CSRF
        self.assertEqual(self.req("POST", "/api/sync", cookies=session)[0], 403)
        self.assertIn(self.req("POST", "/api/sync", cookies=session, headers={"X-CSRF-Token": csrf})[0], (202, 409))

        # salt okunur bağlı kanalda kapak → ek izin gerekir
        st, _, body, _ = self.req("POST", "/api/videos/vid000/thumbnail", cookies=session,
                                  headers={"X-CSRF-Token": csrf}, body=jpeg(1280, 720))
        self.assertEqual(st, 403)
        self.assertTrue(json.loads(body)["need_write"])
        self.assertIn("auth%2Fyoutube", self.req("GET", "/kanal-ekle?yazma=1", cookies=session)[1]["Location"])

        # başka kullanıcı bu kanalı göremez ve dokunamaz
        other = self.hub.login({"sub": "g-2", "email": "veli@example.com"})
        tok, csrf2 = self.hub.create_session(other["id"])
        s2 = {"kh_session": tok}
        self.assertEqual(json.loads(self.req("GET", "/api/portfolio", cookies=s2)[2])["channels"], [])
        self.assertEqual(self.req("GET", "/api/channels/UC_test/videos", cookies=s2)[0], 404)
        self.assertEqual(self.req("GET", "/api/top-videos?channel=UC_test", cookies=s2)[0], 404)
        self.assertEqual(self.req("GET", "/api/videos/vid000/trend", cookies=s2)[0], 404)
        self.assertEqual(self.req("POST", "/api/channels/UC_test/disconnect", cookies=s2,
                                  headers={"X-CSRF-Token": csrf2})[0], 404)
        self.assertTrue(self.hub.owns(1, "UC_test"))

        # çıkış
        st, _, _, ck = self.req("POST", "/cikis", cookies=session, headers={"X-CSRF-Token": csrf})
        self.assertEqual((st, ck["kh_session"]), (200, ""))
        self.assertEqual(self.req("GET", "/api/portfolio", cookies=session)[0], 401)
        # giriş yapmış kullanıcı /giris'e gelirse panele yönlenir
        self.assertEqual(self.req("GET", "/giris", cookies=s2)[1].get("Location"), "/panel")

    def test_login_variants(self):
        g = self.g
        old = (dict(g.login_claims), g.granted_scope)
        try:
            # YouTube izin kutusu boş bırakıldı → giriş olur, kanal yok
            g.login_claims, g.granted_scope = {"sub": "g-izin", "email": "izin@example.com"}, "openid email profile"
            loc, tok = self.callback(*self.login())
            self.assertEqual(loc, "/panel?hata=izin")
            self.assertEqual(self.hub.channel_ids(self.hub.session_user(tok)["id"]), [])
            # hesapta YouTube kanalı yok
            g.granted_scope, g.no_channel = old[1], True
            g.login_claims = {"sub": "g-yok", "email": "yok@example.com"}
            loc, _ = self.callback(*self.login())
            self.assertEqual(loc, "/panel?hata=kanal_yok")
            g.no_channel = False
            # marka kanalı kimliğiyle giriş → kanalın sahibi olan hesaba girilir
            owner = self.hub.login({"sub": "g-sahip", "email": "sahip@example.com"})
            self.hub.link_channel(owner["id"], "UC_test")
            g.login_claims = {"sub": "marka-1", "email": "kanal@pages.plusgoogle.com"}
            loc, tok = self.callback(*self.login())
            self.assertIn(self.hub.session_user(tok)["id"], {owner["id"], 1})
            self.assertTrue(self.hub.owns(self.hub.session_user(tok)["id"], "UC_test"))
        finally:
            g.login_claims, g.granted_scope, g.no_channel = old[0], old[1], False

    def test_setup_upload_requires_token(self):
        st, _, _, _ = self.req("POST", "/api/setup/client-secret", body=b"{}")
        self.assertEqual(st, 403)


if __name__ == "__main__":
    unittest.main()
