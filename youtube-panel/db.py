"""
Veritabanı — kullanıcılar, oturumlar, bağlı kanallar.

SQLite ile başlar; tek dosya, kurulum yok. Kullanıcı sayısı büyüyünce aynı
tablolar Postgres'e taşınabilir.
"""

import hashlib
import secrets
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone

SESSION_DAYS = 30
STATE_SECONDS = 600

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,
    google_sub  TEXT UNIQUE,
    email       TEXT,
    name        TEXT,
    picture     TEXT,
    plan        TEXT NOT NULL DEFAULT 'beta',
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash  TEXT PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at  INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS channels (
    id            INTEGER PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel_id    TEXT NOT NULL,
    google_sub    TEXT,
    title         TEXT NOT NULL,
    handle        TEXT,
    thumb         TEXT,
    refresh_token TEXT NOT NULL,          -- şifreli
    added_at      TEXT NOT NULL,
    UNIQUE (user_id, channel_id)
);
CREATE INDEX IF NOT EXISTS channels_by_channel ON channels(channel_id);
CREATE INDEX IF NOT EXISTS channels_by_sub ON channels(google_sub);
CREATE TABLE IF NOT EXISTS oauth_states (
    state       TEXT PRIMARY KEY,
    user_id     INTEGER,
    created_at  INTEGER NOT NULL,
    mode        TEXT NOT NULL DEFAULT ''   -- '' tek kanal, 'toplu' ara sayfa, 'oto' otomatik döngü
);
"""

PATH = "app.db"


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@contextmanager
def conn():
    c = sqlite3.connect(PATH, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init(path):
    global PATH
    PATH = path
    with conn() as c:
        c.execute("PRAGMA journal_mode = WAL")
        c.executescript(SCHEMA)
        cols = [r["name"] for r in c.execute("PRAGMA table_info(oauth_states)")]
        if "mode" not in cols:  # eski veritabanı
            c.execute("ALTER TABLE oauth_states ADD COLUMN mode TEXT NOT NULL DEFAULT ''")


def _hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


# ----------------------------------------------------------------------------
# OTURUM
# ----------------------------------------------------------------------------

def create_session(user_id):
    token = secrets.token_urlsafe(32)
    with conn() as c:
        c.execute("DELETE FROM sessions WHERE expires_at < ?", (int(time.time()),))
        c.execute("INSERT INTO sessions VALUES (?, ?, ?)",
                  (_hash(token), user_id, int(time.time()) + SESSION_DAYS * 86400))
    return token


def session_user(token):
    if not token:
        return None
    with conn() as c:
        row = c.execute("""SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id
                           WHERE s.token_hash = ? AND s.expires_at > ?""",
                        (_hash(token), int(time.time()))).fetchone()
    return dict(row) if row else None


def delete_session(token):
    with conn() as c:
        c.execute("DELETE FROM sessions WHERE token_hash = ?", (_hash(token or ""),))


def save_state(user_id, mode=""):
    state = secrets.token_urlsafe(24)
    with conn() as c:
        c.execute("DELETE FROM oauth_states WHERE created_at < ?",
                  (int(time.time()) - STATE_SECONDS,))
        c.execute("INSERT INTO oauth_states (state, user_id, created_at, mode) VALUES (?, ?, ?, ?)",
                  (state, user_id, int(time.time()), mode))
    return state


def pop_state(state):
    """Geçerliyse (True, user_id, mode) döner; her state tek kullanımlıktır."""
    with conn() as c:
        row = c.execute("SELECT * FROM oauth_states WHERE state = ? AND created_at > ?",
                        (state or "", int(time.time()) - STATE_SECONDS)).fetchone()
        c.execute("DELETE FROM oauth_states WHERE state = ?", (state or "",))
    return (True, row["user_id"], row["mode"]) if row else (False, None, "")


# ----------------------------------------------------------------------------
# KULLANICI
# ----------------------------------------------------------------------------

def user_for_login(sub, channel_id):
    """
    Google ile giren kişinin paneli. Önce Google kimliğine, sonra daha önce bu
    kimlikle veya bu kanalla bağlanmış bir panele bakar. Böylece panele bağlı
    herhangi bir kanalın hesabıyla girmek aynı paneli açar.
    """
    with conn() as c:
        if sub:
            row = c.execute("SELECT id FROM users WHERE google_sub = ?", (sub,)).fetchone()
            if row:
                return row["id"]
            row = c.execute("""SELECT user_id FROM channels WHERE google_sub = ?
                               ORDER BY id LIMIT 1""", (sub,)).fetchone()
            if row:
                return row["user_id"]
        if channel_id:
            row = c.execute("""SELECT user_id FROM channels WHERE channel_id = ?
                               ORDER BY id LIMIT 1""", (channel_id,)).fetchone()
            if row:
                return row["user_id"]
    return None


def create_user(sub, email, name, picture):
    with conn() as c:
        cur = c.execute("""INSERT INTO users (google_sub, email, name, picture, created_at)
                           VALUES (?, ?, ?, ?, ?)""", (sub, email, name, picture, now_iso()))
        return cur.lastrowid


def user_plan(user_id):
    with conn() as c:
        row = c.execute("SELECT plan FROM users WHERE id = ?", (user_id,)).fetchone()
    return row["plan"] if row else None


def user_email(user_id):
    with conn() as c:
        row = c.execute("SELECT email FROM users WHERE id = ?", (user_id,)).fetchone()
    return row["email"] if row else None


def delete_user(user_id):
    with conn() as c:
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))


# ----------------------------------------------------------------------------
# KANAL
# ----------------------------------------------------------------------------

def list_channels(user_id):
    with conn() as c:
        rows = c.execute("SELECT * FROM channels WHERE user_id = ? ORDER BY id",
                         (user_id,)).fetchall()
    return [dict(r) for r in rows]


def get_channel(user_id, channel_id):
    with conn() as c:
        row = c.execute("SELECT * FROM channels WHERE user_id = ? AND channel_id = ?",
                        (user_id, channel_id)).fetchone()
    return dict(row) if row else None


def count_channels(user_id):
    with conn() as c:
        return c.execute("SELECT COUNT(*) FROM channels WHERE user_id = ?",
                         (user_id,)).fetchone()[0]


def upsert_channel(user_id, info, refresh_token_enc, sub):
    with conn() as c:
        c.execute("""INSERT INTO channels
                       (user_id, channel_id, google_sub, title, handle, thumb, refresh_token, added_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                     ON CONFLICT (user_id, channel_id) DO UPDATE SET
                       google_sub = excluded.google_sub, title = excluded.title,
                       handle = excluded.handle, thumb = excluded.thumb,
                       refresh_token = excluded.refresh_token""",
                  (user_id, info["id"], sub, info["title"], info.get("handle", ""),
                   info.get("thumb", ""), refresh_token_enc, now_iso()))


def delete_channel(user_id, channel_id):
    with conn() as c:
        c.execute("DELETE FROM channels WHERE user_id = ? AND channel_id = ?",
                  (user_id, channel_id))
