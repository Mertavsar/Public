"""
SQLite depolama. Tek dosya, kurulum yok.

Şema sürümlüdür: yeni tablo/kolon gerektiğinde MIGRATIONS listesine yeni bir adım
eklenir, eski veriler korunur. İleride Postgres'e geçişte bu şema birebir taşınır.
"""

import os
import sqlite3
import time
from contextlib import contextmanager

from . import config

MIGRATIONS = [
    # 1 — temel şema
    """
    CREATE TABLE channels (
        id               TEXT PRIMARY KEY,
        title            TEXT NOT NULL,
        handle           TEXT,
        description      TEXT,
        thumbnail_url    TEXT,
        banner_url       TEXT,
        uploads_playlist TEXT,
        country          TEXT,
        published_at     TEXT,
        subscribers      INTEGER,
        hidden_subs      INTEGER DEFAULT 0,
        views            INTEGER,
        video_count      INTEGER,
        connected_at     INTEGER NOT NULL,
        synced_at        INTEGER,
        sync_error       TEXT
    );

    -- Kanal başına bir token. Bir Google hesabındaki her marka kanalı ayrı onay
    -- ister; token o kanala bağlıdır.
    CREATE TABLE credentials (
        channel_id    TEXT PRIMARY KEY REFERENCES channels(id) ON DELETE CASCADE,
        refresh_token TEXT NOT NULL,
        access_token  TEXT,
        expires_at    INTEGER,
        scopes        TEXT
    );

    CREATE TABLE videos (
        id            TEXT PRIMARY KEY,
        channel_id    TEXT NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
        title         TEXT,
        published_at  TEXT,
        duration_s    INTEGER,
        is_short      INTEGER,
        privacy       TEXT,
        thumbnail_url TEXT,
        views         INTEGER,
        likes         INTEGER,
        comments      INTEGER,
        updated_at    INTEGER
    );
    CREATE INDEX videos_channel ON videos(channel_id, published_at);

    -- Her senkronizasyonda anlık sayaçların fotoğrafı. Analytics API 2-3 gün
    -- gecikmeli; "son 24 saatte ne oldu" sorusunu bu tablo cevaplar.
    CREATE TABLE video_snapshots (
        video_id    TEXT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
        captured_at INTEGER NOT NULL,
        views       INTEGER,
        likes       INTEGER,
        comments    INTEGER,
        PRIMARY KEY (video_id, captured_at)
    );

    CREATE TABLE channel_snapshots (
        channel_id  TEXT NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
        captured_at INTEGER NOT NULL,
        subscribers INTEGER,
        views       INTEGER,
        video_count INTEGER,
        PRIMARY KEY (channel_id, captured_at)
    );

    -- YouTube Analytics API günlük kanal metrikleri.
    CREATE TABLE channel_daily (
        channel_id   TEXT NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
        day          TEXT NOT NULL,
        views        INTEGER,
        minutes      INTEGER,
        avg_view_s   INTEGER,
        subs_gained  INTEGER,
        subs_lost    INTEGER,
        likes        INTEGER,
        comments     INTEGER,
        shares       INTEGER,
        impressions  INTEGER,
        ctr          REAL,
        PRIMARY KEY (channel_id, day)
    );

    -- Kanala yapılan her YAZMA işleminin kaydı (kapak, banner...). Kim, ne zaman,
    -- neyi, önceki hali neydi. Geri alma bu tablodan yürür.
    CREATE TABLE actions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at  INTEGER NOT NULL,
        channel_id  TEXT NOT NULL,
        video_id    TEXT,
        kind        TEXT NOT NULL,
        status      TEXT NOT NULL,
        new_asset   TEXT,
        backup_asset TEXT,
        detail      TEXT
    );

    -- Tahmini kota harcaması. Gün = Pasifik saati (Google'ın sıfırlama saati).
    CREATE TABLE quota_log (
        day    TEXT NOT NULL,
        method TEXT NOT NULL,
        units  INTEGER NOT NULL,
        at     INTEGER NOT NULL
    );
    CREATE INDEX quota_day ON quota_log(day);
    """,
]


def connect(path=None):
    path = path or config.DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fresh = not os.path.exists(path)
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    if fresh:
        # Token'lar bu dosyada; sadece sahibi okuyabilsin.
        os.chmod(path, 0o600)
    migrate(conn)
    return conn


@contextmanager
def session(path=None):
    """Bağlantı aç → iş bitince commit et ve KAPAT (hata olursa geri al)."""
    conn = connect(path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def migrate(conn):
    current = conn.execute("PRAGMA user_version").fetchone()[0]
    for i, sql in enumerate(MIGRATIONS[current:], start=current + 1):
        conn.executescript(sql)
        conn.execute(f"PRAGMA user_version = {i}")
        conn.commit()


def now():
    return int(time.time())
