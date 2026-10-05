"""
Hub servisi — panelin ve komut satırının konuştuğu tek katman.

Arayüz (web, CLI, ileride MCP sunucusu veya mobil) asla doğrudan API'ye ya da
veritabanına gitmez; buradaki fonksiyonları çağırır. Yeni bir arayüz eklemek bu
yüzden ucuzdur.
"""

import hashlib
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
        return len(rows)

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

    # ------------------------------------------------------------------ okuma (panel)

    def overview(self, days=28):
        since = (date.today() - timedelta(days=days)).isoformat()
        out = []
        with self.conn() as c:
            for ch in c.execute("SELECT * FROM channels ORDER BY subscribers DESC NULLS LAST"):
                ch = dict(ch)
                daily = c.execute("""SELECT day, views, subs_gained, subs_lost, minutes, impressions, ctr
                                     FROM channel_daily WHERE channel_id=? AND day>=? ORDER BY day""",
                                  (ch["id"], since)).fetchall()
                ch["period"] = {
                    "days": days,
                    "views": sum(r["views"] or 0 for r in daily),
                    "minutes": sum(r["minutes"] or 0 for r in daily),
                    "subs_net": sum((r["subs_gained"] or 0) - (r["subs_lost"] or 0) for r in daily),
                    "impressions": sum(r["impressions"] or 0 for r in daily) or None,
                    "series": [{"day": r["day"], "views": r["views"] or 0} for r in daily],
                }
                ch["views_24h"] = self._delta_24h(c, ch["id"])
                ch["shorts"] = c.execute("SELECT COUNT(*) FROM videos WHERE channel_id=? AND is_short=1",
                                         (ch["id"],)).fetchone()[0]
                out.append(ch)
        totals = {
            "channels": len(out),
            "subscribers": sum(ch["subscribers"] or 0 for ch in out),
            "views": sum(ch["views"] or 0 for ch in out),
            "videos": sum(ch["video_count"] or 0 for ch in out),
            "period_views": sum(ch["period"]["views"] for ch in out),
            "period_subs_net": sum(ch["period"]["subs_net"] for ch in out),
            "views_24h": sum(ch["views_24h"] or 0 for ch in out),
        }
        return {"channels": out, "totals": totals, "quota": self.quota_today()}

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
