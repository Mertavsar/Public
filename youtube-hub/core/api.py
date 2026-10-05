"""
YouTube Data API v3 + YouTube Analytics API istemcisi.

Harici kütüphane yok: urllib ile konuşur. Ağ katmanı (`transport`) dışarıdan
verilebilir; testler sahte bir transport ile Google'a hiç gitmeden çalışır.

Her çağrı:
  - kota maliyetini `on_quota` ile bildirir (panelde tahmini harcama),
  - 401'de token'ı bir kez yenileyip tekrar dener,
  - 429/5xx'te üstel bekleme ile en fazla 4 kez dener,
  - kota bittiğinde (quotaExceeded) tekrar denemez, QuotaExceeded fırlatır.
"""

import gzip
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from . import config

try:
    from zoneinfo import ZoneInfo
    _PT = ZoneInfo("America/Los_Angeles")
except Exception:  # tzdata yoksa kaba yaklaşım
    _PT = None


class ApiError(Exception):
    def __init__(self, status, reason, message):
        super().__init__(f"{status} {reason}: {message}")
        self.status = status
        self.reason = reason
        self.message = message


class QuotaExceeded(ApiError):
    pass


def quota_day(ts=None):
    """Kotanın sayıldığı gün (Pasifik saati)."""
    dt = datetime.fromtimestamp(ts or time.time(), tz=timezone.utc)
    if _PT is not None:
        dt = dt.astimezone(_PT)
    else:
        dt = datetime.fromtimestamp((ts or time.time()) - 8 * 3600, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def urllib_transport(method, url, headers=None, body=None):
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=config.HTTP_TIMEOUT) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read()


def parse_error(status, raw):
    reason, message = "unknown", raw[:300].decode("utf-8", "replace")
    try:
        err = json.loads(raw).get("error", {})
        if isinstance(err, dict):
            message = err.get("message", message)
            errors = err.get("errors") or []
            if errors:
                reason = errors[0].get("reason", reason)
            elif err.get("status"):
                reason = err["status"]
        elif isinstance(err, str):  # OAuth uç noktası: {"error": "invalid_grant"}
            reason = err
    except (ValueError, AttributeError):
        pass
    cls = QuotaExceeded if reason in ("quotaExceeded", "dailyLimitExceeded") else ApiError
    return cls(status, reason, message)


class YouTubeClient:
    """Tek bir kanalın token'ı ile çalışan istemci."""

    def __init__(self, creds, transport=None, on_quota=None, sleep=time.sleep):
        self.creds = creds
        self.transport = transport or urllib_transport
        self.on_quota = on_quota or (lambda method, units: None)
        self.sleep = sleep

    # ------------------------------------------------------------------ çekirdek

    def _request(self, method, url, params=None, body=None, content_type=None, quota=None,
                 raw=False):
        raw_out = raw
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode("utf-8")
            content_type = "application/json"

        refreshed = False
        for attempt in range(5):
            headers = {"Authorization": f"Bearer {self.creds.access_token()}",
                       "Accept": "application/json"}
            if content_type:
                headers["Content-Type"] = content_type
            status, _, payload = self.transport(method, url, headers, body)

            if quota:
                # Hatalı istekler de kota yer; Google başarısız çağrıyı da sayar.
                self.on_quota(quota, config.QUOTA_COST.get(quota, 1))

            if 200 <= status < 300:
                if raw_out:
                    return payload
                return json.loads(payload) if payload else {}
            err = parse_error(status, payload)
            if status == 401 and not refreshed:
                self.creds.access_token(force_refresh=True)
                refreshed = True
                continue
            if isinstance(err, QuotaExceeded):
                raise err
            if (status == 429 or status >= 500) and attempt < 4:
                self.sleep(2 ** (attempt + 1))
                continue
            raise err
        raise err  # pragma: no cover

    # ------------------------------------------------------------------ okuma

    def my_channel(self):
        data = self._request(
            "GET", f"{config.DATA_API}/channels",
            {"part": "snippet,statistics,contentDetails,brandingSettings", "mine": "true"},
            quota="channels.list")
        items = data.get("items") or []
        if not items:
            raise ApiError(404, "noChannel", "Bu Google hesabına bağlı bir YouTube kanalı yok.")
        return items[0]

    def upload_ids(self, uploads_playlist):
        """Kanalın tüm video ID'leri. search.list (100 birim) yerine
        playlistItems.list (1 birim / 50 video) kullanılır."""
        token = None
        while True:
            params = {"part": "contentDetails", "playlistId": uploads_playlist, "maxResults": 50}
            if token:
                params["pageToken"] = token
            data = self._request("GET", f"{config.DATA_API}/playlistItems", params,
                                 quota="playlistItems.list")
            for item in data.get("items", []):
                yield item["contentDetails"]["videoId"]
            token = data.get("nextPageToken")
            if not token:
                return

    def videos(self, ids):
        """videos.list tek çağrıda 50 ID alır."""
        ids = list(ids)
        for i in range(0, len(ids), 50):
            data = self._request(
                "GET", f"{config.DATA_API}/videos",
                {"part": "snippet,statistics,contentDetails,status", "id": ",".join(ids[i:i + 50]),
                 "maxResults": 50},
                quota="videos.list")
            yield from data.get("items", [])

    def branding(self, channel_id):
        data = self._request("GET", f"{config.DATA_API}/channels",
                             {"part": "brandingSettings", "id": channel_id},
                             quota="channels.list")
        items = data.get("items") or []
        if not items:
            raise ApiError(404, "channelNotFound", channel_id)
        return items[0].get("brandingSettings", {})

    def analytics(self, start, end, metrics, dimensions="day", filters=None, sort=None,
                  max_results=None):
        params = {"ids": "channel==MINE", "startDate": start, "endDate": end,
                  "metrics": ",".join(metrics), "dimensions": dimensions}
        if sort or dimensions == "day":
            params["sort"] = sort or "day"
        if filters:
            params["filters"] = filters
        if max_results:
            params["maxResults"] = max_results
        # Analytics API'nin kotası Data API'den ayrıdır; burada sayılmaz.
        data = self._request("GET", f"{config.ANALYTICS_API}/reports", params)
        cols = [h["name"] for h in data.get("columnHeaders", [])]
        return [dict(zip(cols, row)) for row in data.get("rows") or []]

    # ------------------------------------------------------------------ reporting api

    def _paged(self, url, key, params=None):
        params = dict(params or {})
        while True:
            data = self._request("GET", url, params)
            yield from data.get(key, [])
            if not data.get("nextPageToken"):
                return
            params["pageToken"] = data["nextPageToken"]

    def report_types(self):
        return list(self._paged(f"{config.REPORTING_API}/reportTypes", "reportTypes"))

    def reporting_jobs(self):
        return list(self._paged(f"{config.REPORTING_API}/jobs", "jobs"))

    def create_reporting_job(self, report_type):
        return self._request("POST", f"{config.REPORTING_API}/jobs",
                             body={"reportTypeId": report_type, "name": f"youtube-hub {report_type}"})

    def job_reports(self, job_id):
        return list(self._paged(f"{config.REPORTING_API}/jobs/{job_id}/reports", "reports"))

    def download(self, url):
        """Rapor CSV'si (gzip'li gelirse açılır)."""
        data = self._request("GET", url, raw=True)
        if data[:2] == b"\x1f\x8b":
            data = gzip.decompress(data)
        return data

    # ------------------------------------------------------------------ yazma

    def set_thumbnail(self, video_id, data, mime):
        return self._request(
            "POST", f"{config.UPLOAD_API}/thumbnails/set",
            {"videoId": video_id, "uploadType": "media"},
            body=data, content_type=mime, quota="thumbnails.set")

    def insert_banner(self, data, mime):
        """Görseli YouTube'a yükler ve URL döner. Kanalda görünmesi için ardından
        set_banner_url çağrılmalıdır."""
        res = self._request(
            "POST", f"{config.UPLOAD_API}/channelBanners/insert", {"uploadType": "media"},
            body=data, content_type=mime, quota="channelBanners.insert")
        return res["url"]

    def set_banner_url(self, channel_id, banner_url):
        """DİKKAT: channels.update brandingSettings parçasının TAMAMINI değiştirir.
        Sadece banner gönderilirse kanal açıklaması, anahtar kelimeler vb. silinir.
        Bu yüzden önce mevcut ayarlar okunur, sadece banner alanı değiştirilir."""
        current = self.branding(channel_id)
        merged = dict(current)
        merged["image"] = dict(current.get("image") or {}, bannerExternalUrl=banner_url)
        return self._request(
            "PUT", f"{config.DATA_API}/channels", {"part": "brandingSettings"},
            body={"id": channel_id, "brandingSettings": merged}, quota="channels.update")
