import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import images, oauth  # noqa: E402
from core.api import QuotaExceeded  # noqa: E402
from core.service import Hub, parse_duration  # noqa: E402
from fake_google import FakeGoogle, jpeg, png  # noqa: E402

CLIENT = {"client_id": "cid", "client_secret": "sec"}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.g = FakeGoogle()
        self.hub = Hub(db_path=os.path.join(self.tmp.name, "t.db"), transport=self.g,
                       oauth_client=CLIENT, assets_dir=os.path.join(self.tmp.name, "assets"),
                       sleep=lambda s: None)
        self.cid = self.hub.register({"refresh_token": "refresh-xyz", "access_token": self.g.access,
                                      "expires_in": 3600})

    def tearDown(self):
        self.tmp.cleanup()


class TestSync(Base):
    def test_register_and_sync(self):
        self.assertEqual(self.cid, "UC_test")
        r = self.hub.sync_channel(self.cid)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["videos"], 120)
        self.assertEqual(r["days"], 28)
        vids = self.hub.videos(self.cid, limit=500)
        self.assertEqual(len(vids), 120)
        self.assertEqual(sum(v["is_short"] for v in vids), 60)
        ov = self.hub.overview(days=3650)
        self.assertEqual(ov["totals"]["subscribers"], 5000)
        self.assertEqual(ov["channels"][0]["period"]["views"], sum(d * 10 for d in range(1, 29)))

    def test_cheap_quota_path(self):
        """120 video: 3 sayfa playlistItems + 3 parti videos.list; search.list yok."""
        self.hub.sync_channel(self.cid)
        q = self.hub.quota_today()["by_method"]
        self.assertEqual(q["playlistItems.list"], 3)
        self.assertEqual(q["videos.list"], 3)
        self.assertNotIn("search.list", q)

    def test_deleted_videos_removed(self):
        self.hub.sync_channel(self.cid)
        del self.g.videos["vid000"]
        self.hub.sync_channel(self.cid)
        self.assertNotIn("vid000", {v["id"] for v in self.hub.videos(self.cid, 500)})

    def test_analytics_fallback_without_reach_metrics(self):
        self.g.analytics_reach = False
        r = self.hub.sync_channel(self.cid)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["days"], 28)
        self.assertTrue(r["notes"])

    def test_token_refresh_on_401(self):
        self.g.expire_next = True
        self.assertTrue(self.hub.sync_channel(self.cid)["ok"])

    def test_retry_on_5xx_then_quota_stops(self):
        self.g.fail_next = [(503, "backendError")]
        self.assertTrue(self.hub.sync_channel(self.cid)["ok"])
        self.g.fail_next = [(403, "quotaExceeded")]
        r = self.hub.sync_channel(self.cid)
        self.assertFalse(r["ok"])
        self.assertIn("quotaExceeded", r["error"])

    def test_revoked_token_reports_error(self):
        with self.hub.conn() as c:
            c.execute("UPDATE credentials SET refresh_token='revoked', expires_at=0")
        r = self.hub.sync_channel(self.cid)
        self.assertFalse(r["ok"])
        self.assertIn("yeniden bağla", r["error"])

    def test_disconnect_deletes_data(self):
        self.hub.sync_channel(self.cid)
        self.hub.disconnect(self.cid)
        self.assertEqual(self.hub.overview()["channels"], [])
        with self.hub.conn() as c:
            self.assertEqual(c.execute("SELECT COUNT(*) FROM videos").fetchone()[0], 0)


class TestImages(Base):
    def setUp(self):
        super().setUp()
        self.hub.sync_channel(self.cid)

    def test_thumbnail_backup_and_undo(self):
        info = self.hub.set_thumbnail("vid000", jpeg(1280, 720))  # vid000 = uzun video
        self.assertEqual(info["warnings"], [])
        self.assertIn("vid000", self.g.thumbs_set)
        acts = self.hub.actions()
        self.assertEqual(acts[0]["status"], "done")
        self.assertTrue(os.path.isfile(acts[0]["backup_asset"]))
        self.hub.undo(info["action_id"])
        self.assertEqual(self.hub.actions()[1]["status"], "undone")

    def test_reject_before_spending_quota(self):
        before = self.hub.quota_today()["used"]
        with self.assertRaises(images.ImageRejected):
            self.hub.set_thumbnail("vid000", jpeg(320, 180))
        with self.assertRaises(images.ImageRejected):
            self.hub.set_thumbnail("vid000", b"GIF89a....")
        self.assertEqual(self.hub.quota_today()["used"], before)

    def test_short_thumbnail_warns(self):
        info = self.hub.set_thumbnail("vid001", png(1080, 1920))  # vid001 = Shorts
        self.assertTrue(any("Shorts" in w for w in info["warnings"]))

    def test_banner_keeps_other_branding(self):
        self.hub.set_banner(self.cid, jpeg(2560, 1440))
        self.assertEqual(self.g.branding["channel"]["description"], "Açıklama korunmalı")
        self.assertEqual(self.g.branding["image"]["bannerExternalUrl"], "https://yt3.example/new-banner")

    def test_banner_too_small(self):
        with self.assertRaises(images.ImageRejected):
            self.hub.set_banner(self.cid, jpeg(1280, 720))


class TestUnits(unittest.TestCase):
    def test_duration(self):
        self.assertEqual(parse_duration("PT45S"), 45)
        self.assertEqual(parse_duration("PT1H2M3S"), 3723)
        self.assertEqual(parse_duration("P1DT1S"), 86401)
        self.assertIsNone(parse_duration("garbage"))

    def test_sniff(self):
        self.assertEqual(images.sniff(png(10, 20)), ("image/png", 10, 20))
        self.assertEqual(images.sniff(jpeg(1920, 1080)), ("image/jpeg", 1920, 1080))

    def test_oauth_flow_pkce_and_state(self):
        g = FakeGoogle()
        url = oauth.start_flow("http://127.0.0.1:7788/oauth/callback", client=CLIENT)
        self.assertIn("code_challenge_method=S256", url)
        self.assertIn("access_type=offline", url)
        state = dict(p.split("=", 1) for p in url.split("?", 1)[1].split("&"))["state"]
        with self.assertRaises(ValueError):
            oauth.finish_flow("wrong-state", "code", client=CLIENT, transport=g)
        tok = oauth.finish_flow(state, "code", client=CLIENT, transport=g)
        self.assertEqual(tok["refresh_token"], "refresh-xyz")
        with self.assertRaises(ValueError):  # state tek kullanımlık
            oauth.finish_flow(state, "code", client=CLIENT, transport=g)


if __name__ == "__main__":
    unittest.main()
