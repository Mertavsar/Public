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
                out.update(refresh_token="refresh-xyz", scope="youtube")
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
        if p.endswith("/channels") and method == "GET":
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
            metrics = q["metrics"].split(",")
            if "videoThumbnailImpressions" in metrics and not self.analytics_reach:
                return 400, {}, json.dumps({"error": {"code": 400, "message": "Unknown metric",
                                                      "errors": [{"reason": "badRequest"}]}}).encode()
            cols = [{"name": "day"}] + [{"name": m} for m in metrics]
            rows = [[f"2026-09-{d:02d}"] + [d * 10 for _ in metrics] for d in range(1, 29)]
            return self._ok({"columnHeaders": cols, "rows": rows})
        return 404, {}, b'{"error": {"code": 404, "message": "no route"}}'

    @staticmethod
    def _ok(obj):
        return 200, {}, json.dumps(obj).encode()
