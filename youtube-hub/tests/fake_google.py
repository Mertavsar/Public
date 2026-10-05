"""Google'ı taklit eden sahte transport. Testler gerçek ağa hiç çıkmaz."""

import json
import struct
import zlib
from urllib.parse import parse_qs, urlparse


def png(w, h):
    """Geçerli küçük bir PNG başlığı + gövde (piksel verisi önemsiz)."""
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IEND", b"")


def jpeg(w, h):
    sof = b"\xff\xc0" + struct.pack(">HBHHB", 17, 8, h, w, 3) + b"\x00" * 9
    app0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x00" * 9
    return b"\xff\xd8" + app0 + sof + b"\xff\xd9"


class FakeGoogle:
    def __init__(self, channel_id="UC_test", n_videos=120, analytics_reach=True):
        self.channel_id = channel_id
        self.videos = {f"vid{i:03d}": {"views": 1000 + i, "dur": "PT45S" if i % 2 else "PT10M3S"}
                       for i in range(n_videos)}
        self.analytics_reach = analytics_reach
        self.calls = []
        self.access = "tok-1"
        self.expire_next = False
        self.fail_next = []          # [(status, reason)]
        self.branding = {"channel": {"title": "Test", "description": "Açıklama korunmalı",
                                     "keywords": "a b"},
                         "image": {"bannerExternalUrl": "https://yt3.example/old-banner"}}
        self.thumbs_set = {}
        self.fail_dims = set()
        self.login_claims = {"sub": "g-1", "email": "ali@example.com", "name": "Ali", "picture": ""}
        self.granted_scope = ("https://www.googleapis.com/auth/youtube.readonly "
                              "https://www.googleapis.com/auth/yt-analytics.readonly")
        self.reporting_enabled = True
        self.jobs = {}
        self.reports = {}   # job_id -> [report]
        self.windows_seen = []

    # ------------------------------------------------------------------
    def __call__(self, method, url, headers=None, body=None):
        u = urlparse(url)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        self.calls.append((method, u.path, q))
        if u.netloc.startswith("i.ytimg") or u.netloc.startswith("yt3."):
            return 200, {}, jpeg(1280, 720)
        if u.path == "/token":
            form = {k: v[0] for k, v in parse_qs(body.decode()).items()}
            if form.get("refresh_token") == "revoked":
                return 400, {}, json.dumps({"error": "invalid_grant"}).encode()
            self.access = f"tok-{len(self.calls)}"
            out = {"access_token": self.access, "expires_in": 3600}
            if form["grant_type"] == "authorization_code":
                import base64
                b64 = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()
                out.update(refresh_token="refresh-xyz", scope=self.granted_scope,
                           id_token=f"{b64({'alg': 'RS256'})}.{b64(self.login_claims)}.sig")
            return 200, {}, json.dumps(out).encode()
        if u.path == "/revoke":
            return 200, {}, b""

        if headers.get("Authorization") != f"Bearer {self.access}" or self.expire_next:
            self.expire_next = False
            return 401, {}, json.dumps({"error": {"code": 401, "message": "expired",
                                                  "errors": [{"reason": "authError"}]}}).encode()
        if self.fail_next:
            status, reason = self.fail_next.pop(0)
            return status, {}, json.dumps({"error": {"code": status, "message": reason,
                                                     "errors": [{"reason": reason}]}}).encode()

        p = u.path
        if u.netloc.startswith("youtubereporting"):
            return self._reporting(method, p, body)
        if u.netloc.startswith("download.example"):
            return 200, {}, self.report_csv[p]
        if p.endswith("/channels") and method == "GET":
            if getattr(self, "no_channel", False):
                return self._ok({"items": []})
            if q["part"] == "brandingSettings":
                return self._ok({"items": [{"id": self.channel_id, "brandingSettings": self.branding}]})
            return self._ok({"items": [{
                "id": self.channel_id,
                "snippet": {"title": "Test Kanal", "customUrl": "@test",
                            "thumbnails": {"default": {"url": "https://yt3.example/a.jpg"}}},
                "statistics": {"subscriberCount": "5000", "viewCount": "900000",
                               "videoCount": str(len(self.videos)), "hiddenSubscriberCount": False},
                "contentDetails": {"relatedPlaylists": {"uploads": "UU_test"}},
                "brandingSettings": self.branding}]})
        if p.endswith("/channels") and method == "PUT":
            self.branding = json.loads(body)["brandingSettings"]
            return self._ok({"id": self.channel_id, "brandingSettings": self.branding})
        if p.endswith("/playlistItems"):
            ids = sorted(self.videos)
            start = int(q.get("pageToken", 0))
            page = ids[start:start + 50]
            out = {"items": [{"contentDetails": {"videoId": i}} for i in page]}
            if start + 50 < len(ids):
                out["nextPageToken"] = str(start + 50)
            return self._ok(out)
        if p.endswith("/videos"):
            ids = q["id"].split(",")
            assert len(ids) <= 50
            return self._ok({"items": [{
                "id": i, "snippet": {"title": f"Video {i}", "publishedAt": "2026-09-01T10:00:00Z",
                                     "thumbnails": {"high": {"url": f"https://i.ytimg.com/vi/{i}/hq.jpg"}}},
                "statistics": {"viewCount": str(self.videos[i]["views"]), "likeCount": "10",
                               "commentCount": "2"},
                "contentDetails": {"duration": self.videos[i]["dur"]},
                "status": {"privacyStatus": "public"}} for i in ids if i in self.videos]})
        if p.endswith("/thumbnails/set"):
            self.thumbs_set[q["videoId"]] = body
            return self._ok({"items": [{"maxres": {"url": f"https://i.ytimg.com/vi/{q['videoId']}/maxres.jpg"}}]})
        if p.endswith("/channelBanners/insert"):
            return self._ok({"url": "https://yt3.example/new-banner"})
        if p.endswith("/reports"):
            return self._report(q)
        return 404, {}, b'{"error": {"code": 404, "message": "no route"}}'

    def _report(self, q):
        from datetime import date, timedelta
        metrics = q["metrics"].split(",")
        dim = q.get("dimensions")
        if dim in self.fail_dims or ("videoThumbnailImpressions" in metrics and not self.analytics_reach):
            return 400, {}, json.dumps({"error": {"code": 400, "message": "Unknown",
                                                  "errors": [{"reason": "badRequest"}]}}).encode()
        cols = [{"name": dim}] + [{"name": m} for m in metrics]
        if dim == "day":
            # Gerçekçi gecikme: son 2 günün verisi yok. Son 28 gün 200, öncesi 100 izlenme.
            start, end = date.fromisoformat(q["startDate"]), date.fromisoformat(q["endDate"]) - timedelta(days=2)
            rows, d = [], start
            while d <= end:
                recent = (end - d).days < 28
                vals = {"views": 200 if recent else 100, "estimatedMinutesWatched": 60,
                        "averageViewDuration": 18, "subscribersGained": 3, "subscribersLost": 1,
                        "likes": 10, "comments": 2, "shares": 1,
                        "videoThumbnailImpressions": 1000, "videoThumbnailImpressionsClickRate": 0.05}
                rows.append([d.isoformat()] + [vals.get(m, 0) for m in metrics])
                d += timedelta(days=1)
            self.day_range = (q["startDate"], end.isoformat())
        elif dim == "video":
            ids = sorted(self.videos, key=lambda i: -self.videos[i]["views"])[:int(q.get("maxResults", 200))]
            rows = [[i] + [self.videos[i]["views"] if m == "views" else 5 for m in metrics] for i in ids]
            self.windows_seen.append((q["startDate"], q["endDate"]))
        else:
            data = {"insightTrafficSourceType": [("SHORTS", 600), ("YT_SEARCH", 300), ("RELATED_VIDEO", 100)],
                    "creatorContentType": [("SHORTS", 700), ("VIDEO_ON_DEMAND", 300)],
                    "country": [("TR", 800), ("DE", 150), ("AZ", 50)]}[dim]
            rows = [[k] + [v if m == "views" else v // 10 for m in metrics] for k, v in data]
        return self._ok({"columnHeaders": cols, "rows": rows})

    def _reporting(self, method, p, body):
        if not self.reporting_enabled:
            return 403, {}, json.dumps({"error": {"code": 403, "message": "API not enabled",
                                                  "errors": [{"reason": "accessNotConfigured"}]}}).encode()
        if p.endswith("/reportTypes"):
            return self._ok({"reportTypes": [{"id": t} for t in (
                "channel_basic_a2", "channel_basic_a3", "channel_reach_basic_a1",
                "channel_reach_combined_a1", "channel_basic_a3_beta")]})
        if p.endswith("/jobs") and method == "GET":
            return self._ok({"jobs": list(self.jobs.values())})
        if p.endswith("/jobs") and method == "POST":
            rt = json.loads(body)["reportTypeId"]
            job = {"id": f"job-{rt}", "reportTypeId": rt}
            self.jobs[job["id"]] = job
            return self._ok(job)
        if p.endswith("/reports"):
            job_id = p.split("/")[-2]
            return self._ok({"reports": self.reports.get(job_id, [])})
        return 404, {}, b"{}"

    def add_report(self, report_type, rid, day, csv_text, created="2026-10-01T00:00:00Z"):
        """Bir rapor işine indirilebilir CSV ekle."""
        self.report_csv = getattr(self, "report_csv", {})
        path = f"/r/{rid}"
        self.report_csv[path] = csv_text.encode()
        self.reports.setdefault(f"job-{report_type}", []).append({
            "id": rid, "startTime": f"{day}T07:00:00Z", "createTime": created,
            "downloadUrl": f"https://download.example{path}"})

    @staticmethod
    def _ok(obj):
        return 200, {}, json.dumps(obj).encode()
