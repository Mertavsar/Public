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
        self.assertGreater(r["days"], 300)
        vids = self.hub.videos(self.cid, limit=500)
        self.assertEqual(len(vids), 120)
        self.assertEqual(sum(v["is_short"] for v in vids), 60)

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
        self.assertGreater(r["days"], 300)
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
        self.assertEqual(self.hub.portfolio()["channels"], [])
        with self.hub.conn() as c:
            self.assertEqual(c.execute("SELECT COUNT(*) FROM videos").fetchone()[0], 0)


class TestAnalysis(Base):
    def setUp(self):
        super().setUp()
        self.r = self.hub.sync_channel(self.cid)

    def test_period_anchored_to_last_data_day(self):
        p = self.hub.portfolio(28)
        self.assertEqual(p["anchor"], self.g.day_range[1])   # bugün değil, son veri günü
        self.assertEqual(p["period"]["end"], p["anchor"])

    def test_period_vs_previous(self):
        t = self.hub.portfolio(28)["totals"]
        self.assertEqual(t["cur"]["views"], 28 * 200)
        self.assertEqual(t["prev"]["views"], 28 * 100)
        self.assertAlmostEqual(t["change"]["views"], 1.0)
        self.assertEqual(t["cur"]["subs_net"], 28 * 2)
        # 60 dk × 28 gün / 5600 izlenme = 18 sn
        self.assertEqual(t["cur"]["avg_view_s"], 18)
        self.assertAlmostEqual(t["cur"]["ctr"], 0.05)

    def test_series_cover_every_day(self):
        p = self.hub.portfolio(7)
        self.assertEqual(len(p["series"]), 7)
        self.assertEqual(len(p["prev_series"]), 7)
        self.assertTrue(all(d["views"] == 200 for d in p["series"]))

    def test_windows_synced(self):
        self.assertEqual(len(self.g.windows_seen), 3)
        for days in (7, 28, 90):
            top = self.hub.top_videos(days, limit=5)
            self.assertEqual(len(top), 5)
            self.assertEqual(top[0]["video_id"], "vid119")   # en çok izlenen
            self.assertEqual(top[0]["channel_title"], "Test Kanal")
        shorts = self.hub.top_videos(28, kind="short", limit=100)
        self.assertTrue(shorts and all(v["is_short"] for v in shorts))

    def test_breakdowns(self):
        b = self.hub.breakdowns(28)
        self.assertEqual(b["creatorContentType"][0]["key"], "SHORTS")
        self.assertAlmostEqual(b["creatorContentType"][0]["share"], 0.7)
        self.assertEqual(b["country"][0]["key"], "TR")
        self.assertEqual(self.hub.breakdowns(28, channel_id="yok")["country"], [])

    def test_breakdown_failure_does_not_fail_sync(self):
        self.g.fail_dims = {"creatorContentType"}
        r = self.hub.sync_channel(self.cid)
        self.assertTrue(r["ok"], r)
        self.assertTrue(any("creatorContentType" in n for n in r["notes"]))
        self.assertEqual(self.hub.breakdowns(28)["creatorContentType"], [])
        self.assertTrue(self.hub.breakdowns(28)["country"])

    def test_empty_portfolio(self):
        self.hub.disconnect(self.cid)
        p = self.hub.portfolio(28)
        self.assertIsNone(p["anchor"])
        self.assertEqual(p["totals"]["subscribers"], 0)

    def test_connected_but_not_synced(self):
        with self.hub.conn() as c:
            c.execute("DELETE FROM channel_daily")
        p = self.hub.portfolio(28)
        self.assertIsNone(p["anchor"])
        self.assertEqual(p["channels"][0]["cur"]["views"], 0)
        self.assertEqual(p["totals"]["subscribers"], 5000)


class TestReporting(Base):
    BASIC = ("date,channel_id,video_id,live_or_on_demand,subscribed_status,country_code,views,comments,likes,"
             "dislikes,shares,watch_time_minutes,average_view_duration_seconds,subscribers_gained,subscribers_lost\n"
             "20260920,UC_test,vid001,on_demand,subscribed,TR,100,1,10,0,2,50.5,30,3,1\n"
             "20260920,UC_test,vid001,on_demand,unsubscribed,DE,40,0,4,0,1,20,30,1,0\n"
             "20260920,UC_test,vid002,on_demand,subscribed,TR,7,0,1,0,0,3,25,0,0\n")
    REACH = ("date,channel_id,video_id,video_thumbnail_impressions,video_thumbnail_impressions_ctr\n"
             "20260920,UC_test,vid001,1000,0.05\n")

    def test_jobs_created_once_with_latest_types(self):
        r = self.hub.sync_channel(self.cid)
        self.assertTrue(r["ok"], r)
        self.assertEqual(sorted(j["reportTypeId"] for j in self.g.jobs.values()),
                         ["channel_basic_a3", "channel_reach_basic_a1"])
        self.assertTrue(any("ilk raporlar" in n for n in r["notes"]))
        self.hub.sync_channel(self.cid)
        self.assertEqual(len(self.g.jobs), 2)  # tekrar oluşturulmaz

    def test_reports_aggregated_per_video_day(self):
        self.hub.sync_channel(self.cid)   # işler oluşur
        self.g.add_report("channel_basic_a3", "r1", "2026-09-20", self.BASIC)
        self.g.add_report("channel_reach_basic_a1", "r2", "2026-09-20", self.REACH)
        r = self.hub.sync_channel(self.cid)
        self.assertEqual(r["reports"], 2)
        t = {d["day"]: d for d in self.hub.video_trend("vid001")}["2026-09-20"]
        self.assertEqual(t["views"], 140)            # TR + DE toplandı
        self.assertAlmostEqual(t["minutes"], 70.5)
        self.assertEqual(t["subs_gained"], 4)
        self.assertEqual(t["impressions"], 1000)     # reach, basic'i silmeden eklendi
        self.assertAlmostEqual(t["ctr"], 0.05)
        st = self.hub.reporting_status(self.cid)[0]
        self.assertEqual(st["days"], 1)
        self.assertEqual(st["files"], 2)
        # aynı rapor ikinci kez indirilmez
        self.assertEqual(self.hub.sync_channel(self.cid)["reports"], 0)

    def test_regenerated_report_replaces_day(self):
        self.hub.sync_channel(self.cid)
        self.g.add_report("channel_basic_a3", "old", "2026-09-20", self.BASIC, created="2026-09-21T00:00:00Z")
        fixed = self.BASIC.replace(",100,1,10,", ",500,1,10,")
        self.g.add_report("channel_basic_a3", "new", "2026-09-20", fixed, created="2026-09-25T00:00:00Z")
        self.hub.sync_channel(self.cid)
        t = {d["day"]: d for d in self.hub.video_trend("vid001")}["2026-09-20"]
        self.assertEqual(t["views"], 540)

    def test_reporting_disabled_does_not_fail_sync(self):
        self.g.reporting_enabled = False
        r = self.hub.sync_channel(self.cid)
        self.assertTrue(r["ok"], r)
        self.assertTrue(any("Reporting API" in n for n in r["notes"]))
        self.assertTrue(self.hub.portfolio(28)["anchor"])


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

    def test_save_client_validates(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "data", "client_secret.json")
            good = {"installed": {"client_id": "123-abc.apps.googleusercontent.com", "client_secret": "s",
                                  "redirect_uris": ["http://localhost"]}}
            import json
            self.assertTrue(oauth.save_client(json.dumps(good).encode(), path).endswith(".com"))
            self.assertEqual(oct(os.stat(path).st_mode & 0o777), "0o600")
            self.assertEqual(oauth.load_client(path)["client_secret"], "s")
            for bad, msg in [(b"not json", "JSON"),
                             (json.dumps({"web": good["installed"]}).encode(), "Desktop app"),
                             (json.dumps({"foo": 1}).encode(), "OAuth istemci")]:
                with self.assertRaises(ValueError) as cm:
                    oauth.save_client(bad, path)
                self.assertIn(msg, str(cm.exception))

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
