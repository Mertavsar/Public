"""
Hub servisi — panelin ve komut satırının konuştuğu tek katman.

Arayüz (web, CLI, ileride MCP sunucusu veya mobil) asla doğrudan API'ye ya da
veritabanına gitmez; buradaki fonksiyonları çağırır. Yeni bir arayüz eklemek bu
yüzden ucuzdur.
"""

import csv
import hashlib
import io
import json
import os
import re
import threading
import time
from datetime import date, timedelta

from . import config, db
from .api import ApiError, QuotaExceeded, YouTubeClient, quota_day, urllib_transport
from .images import check_banner, check_thumbnail
from .oauth import AuthRevoked, Credentials, revoke

_DURATION = re.compile(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def parse_duration(iso):
    m = _DURATION.fullmatch(iso or "")
    if not m:
        return None
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return ((d * 24 + h) * 60 + mi) * 60 + s


def best_thumb(thumbnails):
    for key in ("maxres", "standard", "high", "medium", "default"):
        if key in (thumbnails or {}):
            return thumbnails[key]["url"]
    return None


def _int(v):
    return int(v) if v not in (None, "") else None


def _sum(rows, key):
    vals = [r[key] for r in rows if r[key] is not None]
    return sum(vals) if vals else None


def _agg(rows):
    """Günlük satırları tek dönem özetine indirger."""
    views = _sum(rows, "views") or 0
    minutes = _sum(rows, "minutes") or 0
    gained, lost = _sum(rows, "subs_gained") or 0, _sum(rows, "subs_lost") or 0
    likes, comments, shares = (_sum(rows, k) or 0 for k in ("likes", "comments", "shares"))
    impressions = _sum(rows, "impressions")
    weighted = [(r["ctr"], r["impressions"]) for r in rows
                if r["ctr"] is not None and r["impressions"]]
    return {
        "views": views, "minutes": minutes, "subs_gained": gained, "subs_lost": lost,
        "subs_net": gained - lost, "likes": likes, "comments": comments, "shares": shares,
        # Ortalama izleme süresi = toplam izlenme süresi / izlenme (günlük ortalamaların
        # ortalaması değil — o yanıltır).
        "avg_view_s": round(minutes * 60 / views) if views else None,
        "engagement": (likes + comments + shares) / views if views else None,
        "impressions": impressions,
        "ctr": (sum(c * i for c, i in weighted) / sum(i for _, i in weighted)) if weighted else None,
        "days_with_data": len({r["day"] for r in rows}),
    }


def _pct(cur, prev):
    if cur is None or not prev:
        return None
    return (cur - prev) / prev


def _change(cur, prev):
    return {
        "views": _pct(cur["views"], prev["views"]),
        "minutes": _pct(cur["minutes"], prev["minutes"]),
        "avg_view_s": _pct(cur["avg_view_s"], prev["avg_view_s"]),
        "uploads": _pct(cur.get("uploads"), prev.get("uploads")),
        "engagement": _pct(cur["engagement"], prev["engagement"]),
        "subs_net_diff": cur["subs_net"] - prev["subs_net"],
    }


def _series(rows, days):
    """Gün gün toplam; verisi olmayan gün 0 değil None (gecikme / eksik veri)."""
    acc = {}
    for r in rows:
        d = acc.setdefault(r["day"], {"views": 0, "minutes": 0, "subs_net": 0})
        d["views"] += r["views"] or 0
        d["minutes"] += r["minutes"] or 0
        d["subs_net"] += (r["subs_gained"] or 0) - (r["subs_lost"] or 0)
    return [{"day": d, **acc[d]} if d in acc else {"day": d, "views": None, "minutes": None,
                                                   "subs_net": None} for d in days]


class Hub:
    def __init__(self, db_path=None, transport=None, oauth_client=None, assets_dir=None,
                 sleep=time.sleep):
        self.db_path = db_path or config.DB_PATH
        self.transport = transport or urllib_transport
        self.oauth_client = oauth_client
        self.assets_dir = assets_dir or config.ASSETS_DIR
        self.sleep = sleep
        self._sync_lock = threading.Lock()
        self.sync_state = {"running": False, "started_at": None, "finished_at": None, "results": []}
        db.connect(self.db_path).close()  # şemayı hazırla

    def conn(self):
        return db.session(self.db_path)

    # ------------------------------------------------------------------ istemci

    def _log_quota(self, method, units):
        with self.conn() as c:
            c.execute("INSERT INTO quota_log(day, method, units, at) VALUES (?,?,?,?)",
                      (quota_day(), method, units, db.now()))

    def _client(self, creds):
        return YouTubeClient(creds, transport=self.transport, on_quota=self._log_quota,
                             sleep=self.sleep)

    def client(self, channel_id):
        with self.conn() as c:
            row = c.execute("SELECT * FROM credentials WHERE channel_id=?", (channel_id,)).fetchone()
        if not row:
            raise KeyError(f"Kanal bağlı değil: {channel_id}")

        def save(access, expires):
            with self.conn() as c2:
                c2.execute("UPDATE credentials SET access_token=?, expires_at=? WHERE channel_id=?",
                           (access, expires, channel_id))

        creds = Credentials(row["refresh_token"], row["access_token"], row["expires_at"], save,
                            client=self.oauth_client, transport=self.transport)
        return self._client(creds)

    # ------------------------------------------------------------------ kanal bağlama

    def register(self, token):
        """OAuth'tan dönen token ile kanalı kaydeder, kanal ID'sini döner."""
        creds = Credentials(token["refresh_token"], token.get("access_token"),
                            int(time.time()) + int(token.get("expires_in", 3600)),
                            client=self.oauth_client, transport=self.transport)
        ch = self._client(creds).my_channel()
        with self.conn() as c:
            self._upsert_channel(c, ch)
            c.execute("""INSERT INTO credentials(channel_id, refresh_token, access_token, expires_at, scopes)
                         VALUES (?,?,?,?,?)
                         ON CONFLICT(channel_id) DO UPDATE SET refresh_token=excluded.refresh_token,
                           access_token=excluded.access_token, expires_at=excluded.expires_at,
                           scopes=excluded.scopes""",
                      (ch["id"], creds.refresh_token, creds._access, creds._expires,
                       token.get("scope", "")))
        return ch["id"]

    def disconnect(self, channel_id):
        with self.conn() as c:
            row = c.execute("SELECT refresh_token FROM credentials WHERE channel_id=?",
                            (channel_id,)).fetchone()
            if row:
                revoke(row["refresh_token"], self.transport)
            # Kanal verisi ve geçmiş de silinir: kullanıcı erişimi kaldırınca verisini
            # tutmaya devam etmek YouTube API politikalarına aykırı.
            c.execute("DELETE FROM channels WHERE id=?", (channel_id,))

    def _upsert_channel(self, c, ch):
        sn, st = ch.get("snippet", {}), ch.get("statistics", {})
        branding = ch.get("brandingSettings", {})
        c.execute("""
            INSERT INTO channels(id, title, handle, description, thumbnail_url, banner_url,
                uploads_playlist, country, published_at, subscribers, hidden_subs, views,
                video_count, connected_at)
            VALUES (:id,:title,:handle,:description,:thumb,:banner,:uploads,:country,:pub,
                :subs,:hidden,:views,:vids,:now)
            ON CONFLICT(id) DO UPDATE SET title=excluded.title, handle=excluded.handle,
                description=excluded.description, thumbnail_url=excluded.thumbnail_url,
                banner_url=excluded.banner_url, uploads_playlist=excluded.uploads_playlist,
                country=excluded.country, subscribers=excluded.subscribers,
                hidden_subs=excluded.hidden_subs, views=excluded.views,
                video_count=excluded.video_count
        """, {
            "id": ch["id"], "title": sn.get("title", ch["id"]), "handle": sn.get("customUrl"),
            "description": sn.get("description"), "thumb": best_thumb(sn.get("thumbnails")),
            "banner": (branding.get("image") or {}).get("bannerExternalUrl"),
            "uploads": (ch.get("contentDetails", {}).get("relatedPlaylists") or {}).get("uploads"),
            "country": sn.get("country"), "pub": sn.get("publishedAt"),
            "subs": _int(st.get("subscriberCount")), "hidden": int(bool(st.get("hiddenSubscriberCount"))),
            "views": _int(st.get("viewCount")), "vids": _int(st.get("videoCount")), "now": db.now(),
        })
        c.execute("INSERT OR REPLACE INTO channel_snapshots VALUES (?,?,?,?,?)",
                  (ch["id"], db.now(), _int(st.get("subscriberCount")),
                   _int(st.get("viewCount")), _int(st.get("videoCount"))))

    # ------------------------------------------------------------------ senkronizasyon

    def sync_channel(self, channel_id):
        """Kanal + tüm videolar + günlük analitik. Maliyet: ~3 + 2×(video/50) birim."""
        result = {"channel_id": channel_id, "ok": True, "videos": 0, "days": 0, "notes": []}
        try:
            yt = self.client(channel_id)
            ch = yt.my_channel()
            if ch["id"] != channel_id:
                raise ApiError(409, "channelMismatch", "Token başka bir kanala ait.")
            with self.conn() as c:
                self._upsert_channel(c, ch)
            uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
            result["videos"] = self._sync_videos(yt, channel_id, uploads)
            result["days"] = self._sync_analytics(yt, channel_id, result["notes"])
            try:
                result["reports"] = self._sync_reporting(yt, channel_id, result["notes"])
            except QuotaExceeded:
                raise
            except ApiError as e:
                # Reporting API açılmamış olabilir; analizi durdurmaz.
                result["notes"].append(f"Reporting API: {e.reason} — Google Cloud'da açık mı?")
            error = None
        except (AuthRevoked, QuotaExceeded, ApiError, KeyError) as e:
            result.update(ok=False, error=str(e))
            error = str(e)
        with self.conn() as c:
            c.execute("UPDATE channels SET synced_at=?, sync_error=? WHERE id=?",
                      (db.now(), error, channel_id))
        return result

    def _sync_videos(self, yt, channel_id, uploads):
        ids = list(yt.upload_ids(uploads))
        # API çağrıları yazma işlemi AÇILMADAN bitmeli: kota kaydı ayrı bağlantıyla
        # yazılır ve açık bir yazma kilidi onu bekletir.
        items = list(yt.videos(ids))
        now = db.now()
        with self.conn() as c:
            for v in items:
                sn, st = v.get("snippet", {}), v.get("statistics", {})
                dur = parse_duration(v.get("contentDetails", {}).get("duration"))
                row = (v["id"], channel_id, sn.get("title"), sn.get("publishedAt"), dur,
                       int(dur is not None and dur <= config.SHORTS_MAX_SECONDS),
                       v.get("status", {}).get("privacyStatus"), best_thumb(sn.get("thumbnails")),
                       _int(st.get("viewCount")), _int(st.get("likeCount")),
                       _int(st.get("commentCount")), now)
                c.execute("""INSERT INTO videos VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                             ON CONFLICT(id) DO UPDATE SET title=excluded.title,
                               published_at=excluded.published_at, duration_s=excluded.duration_s,
                               is_short=excluded.is_short, privacy=excluded.privacy,
                               thumbnail_url=excluded.thumbnail_url, views=excluded.views,
                               likes=excluded.likes, comments=excluded.comments,
                               updated_at=excluded.updated_at""", row)
                c.execute("INSERT OR REPLACE INTO video_snapshots VALUES (?,?,?,?,?)",
                          (v["id"], now, row[8], row[9], row[10]))
            # YouTube'da silinmiş videolar yerelde de silinir.
            known = {r[0] for r in c.execute("SELECT id FROM videos WHERE channel_id=?", (channel_id,))}
            gone = known - set(ids)
            c.executemany("DELETE FROM videos WHERE id=?", [(g,) for g in gone])
        return len(ids)

    def _sync_analytics(self, yt, channel_id, notes):
        end = date.today()
        start = end - timedelta(days=config.ANALYTICS_DAYS)
        metrics = config.ANALYTICS_METRICS + config.ANALYTICS_REACH_METRICS
        try:
            rows = yt.analytics(start.isoformat(), end.isoformat(), metrics)
        except ApiError as e:
            if e.status != 400:
                raise
            notes.append("Kapak gösterimi/CTR metrikleri alınamadı; temel metriklerle devam edildi.")
            rows = yt.analytics(start.isoformat(), end.isoformat(), config.ANALYTICS_METRICS)
        with self.conn() as c:
            for r in rows:
                c.execute("INSERT OR REPLACE INTO channel_daily VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (
                    channel_id, r["day"], r.get("views"), r.get("estimatedMinutesWatched"),
                    r.get("averageViewDuration"), r.get("subscribersGained"),
                    r.get("subscribersLost"), r.get("likes"), r.get("comments"),
                    r.get("shares"), r.get("videoThumbnailImpressions"),
                    r.get("videoThumbnailImpressionsClickRate")))
        if rows:
            # Dönemler bugünden değil, verinin geldiği son günden geriye sayılır;
            # yoksa Analytics gecikmesi son dönemi yapay olarak düşük gösterir.
            anchor = date.fromisoformat(max(r["day"] for r in rows))
            for days in config.WINDOWS:
                try:
                    self._sync_window(yt, channel_id, anchor, days, notes)
                except QuotaExceeded:
                    raise
                except ApiError as e:
                    notes.append(f"{days} günlük dönem analizi alınamadı: {e.reason}")
        return len(rows)

    def _sync_window(self, yt, channel_id, anchor, days, notes):
        """Bir dönem için en iyi videolar + kırılımlar (trafik, içerik türü, ülke)."""
        start = (anchor - timedelta(days=days - 1)).isoformat()
        end = anchor.isoformat()
        try:
            vids = yt.analytics(start, end, config.TOP_VIDEO_METRICS, dimensions="video",
                                sort="-views", max_results=config.TOP_VIDEOS_PER_WINDOW)
        except ApiError as e:
            if e.status != 400:
                raise
            vids = yt.analytics(start, end, config.TOP_VIDEO_METRICS_FALLBACK, dimensions="video",
                                sort="-views", max_results=config.TOP_VIDEOS_PER_WINDOW)
        breakdowns = {}
        for dim, metrics in config.BREAKDOWNS.items():
            try:
                breakdowns[dim] = yt.analytics(
                    start, end, metrics, dimensions=dim, sort="-views",
                    max_results=config.TOP_COUNTRIES if dim == "country" else None)
            except QuotaExceeded:
                raise
            except ApiError as e:
                if e.status >= 500:
                    raise
                notes.append(f"{dim} kırılımı alınamadı ({days} gün): {e.reason}")
        now = db.now()
        with self.conn() as c:
            c.execute("DELETE FROM video_window WHERE channel_id=? AND window_days=?", (channel_id, days))
            for r in vids:
                c.execute("""INSERT INTO video_window VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                    channel_id, days, r["video"], start, end, r.get("views"),
                    r.get("estimatedMinutesWatched"), r.get("averageViewDuration"),
                    r.get("averageViewPercentage"), r.get("subscribersGained"), r.get("likes"),
                    r.get("comments"), r.get("shares"), now))
            c.execute("DELETE FROM channel_breakdown WHERE channel_id=? AND window_days=?",
                      (channel_id, days))
            for dim, rows in breakdowns.items():
                for r in rows:
                    c.execute("INSERT OR REPLACE INTO channel_breakdown VALUES (?,?,?,?,?,?,?,?,?)", (
                        channel_id, days, dim, str(r[dim]), r.get("views"),
                        r.get("estimatedMinutesWatched"), start, end, now))

    def sync_all(self):
        if not self._sync_lock.acquire(blocking=False):
            return None  # zaten çalışıyor
        try:
            self.sync_state.update(running=True, started_at=db.now(), finished_at=None, results=[])
            with self.conn() as c:
                ids = [r["channel_id"] for r in c.execute("SELECT channel_id FROM credentials")]
            for cid in ids:
                self.sync_state["results"].append(self.sync_channel(cid))
            return self.sync_state["results"]
        finally:
            self.sync_state.update(running=False, finished_at=db.now())
            self._sync_lock.release()

    def sync_all_async(self):
        if self.sync_state["running"]:
            return False
        threading.Thread(target=self.sync_all, daemon=True).start()
        return True

    # ------------------------------------------------------------------ reporting api

    def _sync_reporting(self, yt, channel_id, notes):
        """Rapor işlerini garanti et, yeni günlük CSV'leri indirip video_daily'ye işle."""
        with self.conn() as c:
            jobs = {r["kind"]: dict(r) for r in c.execute(
                "SELECT * FROM reporting_jobs WHERE channel_id=?", (channel_id,))}
        if len(jobs) < len(config.REPORT_TYPE_PREFIXES):
            jobs.update(self._ensure_jobs(yt, channel_id, jobs, notes))
        new_files = 0
        touched_days = set()
        for kind in ("basic", "reach"):  # reach, basic'in satırlarının üstüne yazar
            job = jobs.get(kind)
            if not job:
                continue
            with self.conn() as c:
                seen = {r[0] for r in c.execute(
                    "SELECT report_id FROM reporting_files WHERE channel_id=? AND kind=?", (channel_id, kind))}
            reports = [r for r in yt.job_reports(job["job_id"]) if r["id"] not in seen]
            # Aynı gün için yeniden üretilen rapor eskisinin yerini alır: eskiden yeniye işle.
            for rep in sorted(reports, key=lambda r: r.get("createTime", "")):
                rows = self._parse_report(yt.download(rep["downloadUrl"]), kind)
                with self.conn() as c:
                    for (vid, day), v in rows.items():
                        self._upsert_video_day(c, channel_id, vid, day, kind, v)
                        touched_days.add(day)
                    c.execute("INSERT OR REPLACE INTO reporting_files VALUES (?,?,?,?,?,?)",
                              (rep["id"], channel_id, kind, (rep.get("startTime") or "")[:10],
                               len(rows), db.now()))
                new_files += 1
        if touched_days:
            self._fill_daily_reach(channel_id, touched_days)
        return new_files

    def _ensure_jobs(self, yt, channel_id, existing, notes):
        types = [t["id"] for t in yt.report_types()]
        remote = {j["reportTypeId"]: j for j in yt.reporting_jobs()}
        out = {}
        for kind, prefix in config.REPORT_TYPE_PREFIXES.items():
            if kind in existing:
                continue
            candidates = sorted((t for t in types if t.startswith(prefix)
                                 and t[len(prefix):].isdigit()), key=lambda t: int(t[len(prefix):]))
            if not candidates:
                notes.append(f"Reporting API'de '{prefix}*' rapor türü bulunamadı.")
                continue
            rtype = candidates[-1]
            job = remote.get(rtype) or yt.create_reporting_job(rtype)
            row = {"channel_id": channel_id, "kind": kind, "report_type": rtype,
                   "job_id": job["id"], "created_at": db.now()}
            with self.conn() as c:
                c.execute("INSERT OR REPLACE INTO reporting_jobs VALUES (:channel_id,:kind,:report_type,:job_id,:created_at)", row)
            if rtype not in remote:
                notes.append(f"Reporting API işi oluşturuldu ({rtype}); ilk raporlar ~24 saat içinde gelir.")
            out[kind] = row
        return out

    @staticmethod
    def _parse_report(data, kind):
        """CSV → {(video_id, gün): toplamlar}. Ülke/abone durumu gibi alt kırılımlar toplanır."""
        acc = {}
        for r in csv.DictReader(io.StringIO(data.decode("utf-8-sig"))):
            d = r.get("date", "")
            day = f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 and d.isdigit() else d[:10]
            key = (r.get("video_id") or "", day)
            a = acc.setdefault(key, {"views": 0, "minutes": 0.0, "likes": 0, "comments": 0, "shares": 0,
                                     "subs_gained": 0, "subs_lost": 0, "impressions": 0, "clicks": 0.0})
            num = lambda k: float(r.get(k) or 0)
            if kind == "basic":
                a["views"] += int(num("views"))
                a["minutes"] += num("watch_time_minutes")
                a["likes"] += int(num("likes"))
                a["comments"] += int(num("comments"))
                a["shares"] += int(num("shares"))
                a["subs_gained"] += int(num("subscribers_gained"))
                a["subs_lost"] += int(num("subscribers_lost"))
            else:
                imp = int(num("video_thumbnail_impressions"))
                a["impressions"] += imp
                a["clicks"] += imp * num("video_thumbnail_impressions_ctr")
        for a in acc.values():
            a["ctr"] = a["clicks"] / a["impressions"] if a["impressions"] else None
        return acc

    @staticmethod
    def _upsert_video_day(c, channel_id, vid, day, kind, v):
        if kind == "basic":
            c.execute("""INSERT INTO video_daily(video_id, day, channel_id, views, minutes, likes, comments,
                           shares, subs_gained, subs_lost) VALUES (?,?,?,?,?,?,?,?,?,?)
                         ON CONFLICT(video_id, day) DO UPDATE SET views=excluded.views,
                           minutes=excluded.minutes, likes=excluded.likes, comments=excluded.comments,
                           shares=excluded.shares, subs_gained=excluded.subs_gained,
                           subs_lost=excluded.subs_lost""",
                      (vid, day, channel_id, v["views"], round(v["minutes"], 2), v["likes"], v["comments"],
                       v["shares"], v["subs_gained"], v["subs_lost"]))
        else:
            c.execute("""INSERT INTO video_daily(video_id, day, channel_id, impressions, ctr) VALUES (?,?,?,?,?)
                         ON CONFLICT(video_id, day) DO UPDATE SET impressions=excluded.impressions,
                           ctr=excluded.ctr""", (vid, day, channel_id, v["impressions"], v["ctr"]))

    def _fill_daily_reach(self, channel_id, days):
        """Analytics API kapak gösterimi vermediyse kanal günlüğünü Reporting verisiyle tamamla."""
        with self.conn() as c:
            for day in days:
                r = c.execute("""SELECT SUM(impressions) imp, SUM(impressions * ctr) clicks FROM video_daily
                                 WHERE channel_id=? AND day=? AND impressions IS NOT NULL""",
                              (channel_id, day)).fetchone()
                if r["imp"]:
                    c.execute("""UPDATE channel_daily SET impressions=?, ctr=? WHERE channel_id=? AND day=?
                                 AND impressions IS NULL""",
                              (r["imp"], (r["clicks"] or 0) / r["imp"], channel_id, day))

    def reporting_status(self, channel_id=None):
        sql = """SELECT ch.id channel_id, ch.title,
                   (SELECT GROUP_CONCAT(report_type, ', ') FROM reporting_jobs j WHERE j.channel_id=ch.id) jobs,
                   (SELECT MIN(day) FROM video_daily v WHERE v.channel_id=ch.id) first_day,
                   (SELECT MAX(day) FROM video_daily v WHERE v.channel_id=ch.id) last_day,
                   (SELECT COUNT(DISTINCT day) FROM video_daily v WHERE v.channel_id=ch.id) days,
                   (SELECT COUNT(*) FROM reporting_files f WHERE f.channel_id=ch.id) files
                 FROM channels ch {}"""
        with self.conn() as c:
            if channel_id:
                return [dict(r) for r in c.execute(sql.format("WHERE ch.id=?"), (channel_id,))]
            return [dict(r) for r in c.execute(sql.format(""))]

    def video_trend(self, video_id):
        with self.conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM video_daily WHERE video_id=? ORDER BY day", (video_id,))]

    # ------------------------------------------------------------------ analiz (panel)

    def portfolio(self, days=28):
        """Tüm kanallar: seçili dönem ve bir önceki eşit uzunluktaki dönem.

        Dönem, Analytics verisinin geldiği son günde biter (bugünde değil).
        """
        with self.conn() as c:
            last = c.execute("SELECT MAX(day) FROM channel_daily").fetchone()[0]
            channels = [dict(r) for r in c.execute(
                "SELECT * FROM channels ORDER BY subscribers DESC NULLS LAST, connected_at")]
            for ch in channels:
                ch["views_24h"] = self._delta_24h(c, ch["id"])
            anchor = date.fromisoformat(last) if last else None
            daily, uploads = [], []
            if anchor:
                prev_start = (anchor - timedelta(days=2 * days - 1)).isoformat()
                daily = c.execute("SELECT * FROM channel_daily WHERE day>=? AND day<=?",
                                  (prev_start, anchor.isoformat())).fetchall()
                uploads = c.execute("""SELECT channel_id, substr(published_at,1,10) d FROM videos
                                       WHERE substr(published_at,1,10)>=? AND substr(published_at,1,10)<=?""",
                                    (prev_start, anchor.isoformat())).fetchall()

        common = {"subscribers": sum(ch["subscribers"] or 0 for ch in channels),
                  "lifetime_views": sum(ch["views"] or 0 for ch in channels),
                  "views_24h": sum(ch["views_24h"] or 0 for ch in channels)}
        if not anchor:
            empty = dict(_agg([]), uploads=0)
            for ch in channels:
                ch.update(cur=dict(empty), prev=dict(empty), change=_change(empty, empty),
                          series=[], prev_series=[], share=None)
            return {"days": days, "anchor": None, "period": None, "previous": None,
                    "channels": channels,
                    "totals": {"cur": empty, "prev": dict(empty), "change": _change(empty, empty), **common},
                    "series": [], "prev_series": [], "quota": self.quota_today()}

        cur_days = [(anchor - timedelta(days=days - 1 - i)).isoformat() for i in range(days)]
        prev_days = [(anchor - timedelta(days=2 * days - 1 - i)).isoformat() for i in range(days)]
        cur_set = set(cur_days)
        by_ch = {}
        for r in daily:
            by_ch.setdefault(r["channel_id"], []).append(r)
        up_by_ch = {}
        for u in uploads:
            key = "cur" if u["d"] in cur_set else "prev"
            up_by_ch.setdefault(u["channel_id"], {"cur": 0, "prev": 0})[key] += 1

        for ch in channels:
            rows = by_ch.get(ch["id"], [])
            cur = [r for r in rows if r["day"] in cur_set]
            prev = [r for r in rows if r["day"] not in cur_set]
            ch["cur"], ch["prev"] = _agg(cur), _agg(prev)
            ups = up_by_ch.get(ch["id"], {"cur": 0, "prev": 0})
            ch["cur"]["uploads"], ch["prev"]["uploads"] = ups["cur"], ups["prev"]
            ch["change"] = _change(ch["cur"], ch["prev"])
            ch["series"] = _series(cur, cur_days)
            ch["prev_series"] = _series(prev, prev_days)

        cur_all = [r for r in daily if r["day"] in cur_set]
        prev_all = [r for r in daily if r["day"] not in cur_set]
        tot_cur, tot_prev = _agg(cur_all), _agg(prev_all)
        tot_cur["uploads"] = sum(ch["cur"]["uploads"] for ch in channels)
        tot_prev["uploads"] = sum(ch["prev"]["uploads"] for ch in channels)
        for ch in channels:
            ch["share"] = (ch["cur"]["views"] / tot_cur["views"]) if tot_cur["views"] else None
        return {
            "days": days, "anchor": anchor.isoformat(),
            "period": {"start": cur_days[0], "end": cur_days[-1]},
            "previous": {"start": prev_days[0], "end": prev_days[-1]},
            "channels": channels,
            "totals": {"cur": tot_cur, "prev": tot_prev, "change": _change(tot_cur, tot_prev), **common},
            "series": _series(cur_all, cur_days),
            "prev_series": _series(prev_all, prev_days),
            "quota": self.quota_today(),
        }

    def top_videos(self, days=28, channel_id=None, kind=None, limit=25):
        """Dönemin en çok izlenen videoları — tüm kanallarda veya tek kanalda."""
        sql = ["""SELECT w.*, v.title, v.thumbnail_url, v.published_at, v.is_short, v.duration_s,
                         v.views AS lifetime_views, ch.title AS channel_title
                  FROM video_window w JOIN channels ch ON ch.id = w.channel_id
                  LEFT JOIN videos v ON v.id = w.video_id
                  WHERE w.window_days = ?"""]
        args = [days]
        if channel_id:
            sql.append("AND w.channel_id = ?")
            args.append(channel_id)
        if kind in ("short", "long"):
            sql.append("AND v.is_short = ?")
            args.append(1 if kind == "short" else 0)
        sql.append("ORDER BY w.views DESC LIMIT ?")
        args.append(limit)
        with self.conn() as c:
            return [dict(r) for r in c.execute(" ".join(sql), args)]

    def breakdowns(self, days=28, channel_id=None):
        """İzlenme kaynakları, içerik türü, ülkeler. Kanal verilmezse tüm kanalların toplamı."""
        sql = """SELECT dimension, key, SUM(views) views, SUM(minutes) minutes
                 FROM channel_breakdown WHERE window_days = ? {} GROUP BY dimension, key
                 ORDER BY views DESC"""
        args = [days]
        if channel_id:
            sql, args = sql.format("AND channel_id = ?"), args + [channel_id]
        else:
            sql = sql.format("")
        out = {dim: [] for dim in config.BREAKDOWNS}
        with self.conn() as c:
            for r in c.execute(sql, args):
                out.setdefault(r["dimension"], []).append(
                    {"key": r["key"], "views": r["views"] or 0, "minutes": r["minutes"] or 0})
        for dim, rows in out.items():
            total = sum(r["views"] for r in rows)
            for r in rows:
                r["share"] = r["views"] / total if total else None
        out["country"] = out.get("country", [])[:config.TOP_COUNTRIES]
        return out

    def _delta_24h(self, c, channel_id):
        """Anlık sayaçlardan son ~24 saatteki izlenme artışı (Analytics gecikmesini atlar)."""
        latest = c.execute("""SELECT captured_at, views FROM channel_snapshots WHERE channel_id=?
                              ORDER BY captured_at DESC LIMIT 1""", (channel_id,)).fetchone()
        if not latest:
            return None
        older = c.execute("""SELECT views FROM channel_snapshots WHERE channel_id=? AND captured_at<=?
                             ORDER BY captured_at DESC LIMIT 1""",
                          (channel_id, latest["captured_at"] - 20 * 3600)).fetchone()
        if not older or older["views"] is None or latest["views"] is None:
            return None
        return latest["views"] - older["views"]

    def videos(self, channel_id, limit=200):
        with self.conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM videos WHERE channel_id=? ORDER BY published_at DESC LIMIT ?",
                (channel_id, limit))]

    def daily(self, channel_id, days=90):
        since = (date.today() - timedelta(days=days)).isoformat()
        with self.conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM channel_daily WHERE channel_id=? AND day>=? ORDER BY day",
                (channel_id, since))]

    def quota_today(self):
        with self.conn() as c:
            rows = c.execute("SELECT method, SUM(units) u FROM quota_log WHERE day=? GROUP BY method",
                             (quota_day(),)).fetchall()
        used = sum(r["u"] for r in rows)
        return {"day": quota_day(), "used": used, "limit": config.DAILY_QUOTA,
                "by_method": {r["method"]: r["u"] for r in rows}}

    def actions(self, limit=100):
        with self.conn() as c:
            return [dict(r) for r in c.execute(
                """SELECT a.*, ch.title channel_title, v.title video_title FROM actions a
                   LEFT JOIN channels ch ON ch.id=a.channel_id LEFT JOIN videos v ON v.id=a.video_id
                   ORDER BY a.id DESC LIMIT ?""", (limit,))]

    # ------------------------------------------------------------------ yazma: görseller

    def _store_asset(self, channel_id, kind, data, mime):
        ext = "png" if mime == "image/png" else "jpg"
        folder = os.path.join(self.assets_dir, channel_id, kind)
        os.makedirs(folder, exist_ok=True)
        name = f"{time.strftime('%Y%m%d-%H%M%S')}-{hashlib.sha256(data).hexdigest()[:10]}.{ext}"
        path = os.path.join(folder, name)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def _backup_remote(self, channel_id, kind, url):
        """Değiştirmeden önce mevcut görseli indir; geri alma bunu kullanır."""
        if not url:
            return None
        try:
            status, headers, raw = self.transport("GET", url, {}, None)
            if status != 200 or not raw:
                return None
            mime = "image/png" if raw[:4] == b"\x89PNG" else "image/jpeg"
            return self._store_asset(channel_id, kind + "-backup", raw, mime)
        except Exception:
            return None

    def _record(self, c, channel_id, video_id, kind, status, new_asset, backup, detail):
        cur = c.execute("""INSERT INTO actions(created_at, channel_id, video_id, kind, status,
                             new_asset, backup_asset, detail) VALUES (?,?,?,?,?,?,?,?)""",
                        (db.now(), channel_id, video_id, kind, status, new_asset, backup,
                         json.dumps(detail, ensure_ascii=False)))
        return cur.lastrowid

    def set_thumbnail(self, video_id, data):
        with self.conn() as c:
            v = c.execute("SELECT * FROM videos WHERE id=?", (video_id,)).fetchone()
        if not v:
            raise KeyError(f"Video bulunamadı (önce senkronize et): {video_id}")
        info = check_thumbnail(data, is_short=bool(v["is_short"]))
        new_path = self._store_asset(v["channel_id"], "thumbnail", data, info["mime"])
        backup = self._backup_remote(v["channel_id"], "thumbnail", v["thumbnail_url"])
        try:
            res = self.client(v["channel_id"]).set_thumbnail(video_id, data, info["mime"])
        except Exception as e:
            with self.conn() as c:
                self._record(c, v["channel_id"], video_id, "thumbnail", "failed", new_path, backup,
                             {"error": str(e)})
            raise
        url = best_thumb((res.get("items") or [{}])[0])
        with self.conn() as c:
            if url:
                c.execute("UPDATE videos SET thumbnail_url=? WHERE id=?", (url, video_id))
            info["action_id"] = self._record(c, v["channel_id"], video_id, "thumbnail", "done",
                                             new_path, backup, {"warnings": info["warnings"], "url": url})
        info["url"] = url
        return info

    def set_banner(self, channel_id, data):
        info = check_banner(data)
        with self.conn() as c:
            ch = c.execute("SELECT banner_url FROM channels WHERE id=?", (channel_id,)).fetchone()
        if not ch:
            raise KeyError(f"Kanal bağlı değil: {channel_id}")
        new_path = self._store_asset(channel_id, "banner", data, info["mime"])
        backup = self._backup_remote(channel_id, "banner", ch["banner_url"])
        yt = self.client(channel_id)
        try:
            url = yt.insert_banner(data, info["mime"])
            yt.set_banner_url(channel_id, url)
        except Exception as e:
            with self.conn() as c:
                self._record(c, channel_id, None, "banner", "failed", new_path, backup, {"error": str(e)})
            raise
        with self.conn() as c:
            c.execute("UPDATE channels SET banner_url=? WHERE id=?", (url, channel_id))
            info["action_id"] = self._record(c, channel_id, None, "banner", "done", new_path, backup,
                                             {"warnings": info["warnings"], "url": url})
        info["url"] = url
        return info

    def undo(self, action_id):
        """Bir kapak/banner değişikliğini yedekteki görselle geri alır."""
        with self.conn() as c:
            a = c.execute("SELECT * FROM actions WHERE id=?", (action_id,)).fetchone()
        if not a or a["status"] != "done":
            raise ValueError("Geri alınabilecek tamamlanmış bir işlem değil.")
        if not a["backup_asset"] or not os.path.isfile(a["backup_asset"]):
            raise ValueError("Bu işlemin yedeği yok; geri alınamaz.")
        with open(a["backup_asset"], "rb") as f:
            data = f.read()
        if a["kind"] == "thumbnail":
            res = self.set_thumbnail(a["video_id"], data)
        elif a["kind"] == "banner":
            res = self.set_banner(a["channel_id"], data)
        else:
            raise ValueError(f"Desteklenmeyen işlem: {a['kind']}")
        with self.conn() as c:
            c.execute("UPDATE actions SET status='undone' WHERE id=?", (action_id,))
        return res
