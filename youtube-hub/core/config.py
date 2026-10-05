"""
Tüm ayarlar tek yerde. Değiştirmen gereken her şey burada.

Gizli dosyalar (OAuth istemci bilgisi, veritabanı, token'lar) `youtube-hub/data/`
altında durur ve git'e girmez.
"""

import os

HUB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("YTHUB_DATA_DIR", os.path.join(HUB_DIR, "data"))
DB_PATH = os.path.join(DATA_DIR, "hub.sqlite3")
CLIENT_SECRET_PATH = os.path.join(DATA_DIR, "client_secret.json")
ASSETS_DIR = os.path.join(DATA_DIR, "assets")      # yüklenen + yedeklenen görseller

# ----------------------------------------------------------------------------
# ÜRÜN / SUNUCU
# ----------------------------------------------------------------------------

# Ürün adı. YouTube marka kuralları gereği adında "YouTube" geçmemeli.
APP_NAME = os.environ.get("YTHUB_APP_NAME", "Kanalist")
CONTACT_EMAIL = os.environ.get("YTHUB_CONTACT_EMAIL", "")

# Sunucuda yayınlarken herkese açık adres (ör. https://kanalist.com). Boşsa yerel mod:
# sadece bu bilgisayar, http://127.0.0.1:PORT
PUBLIC_URL = os.environ.get("YTHUB_PUBLIC_URL", "").rstrip("/")
HOST = os.environ.get("YTHUB_HOST", "0.0.0.0" if PUBLIC_URL else "127.0.0.1")
PORT = int(os.environ.get("YTHUB_PORT", "7788"))

SESSION_DAYS = 30
# Sunucu açıkken kanallar bu aralıkla kendiliğinden senkronize edilir (0 = kapalı).
AUTOSYNC_HOURS = float(os.environ.get("YTHUB_AUTOSYNC_HOURS", "6"))


def base_url():
    return PUBLIC_URL or f"http://127.0.0.1:{PORT}"

# ----------------------------------------------------------------------------
# GOOGLE / YOUTUBE
# ----------------------------------------------------------------------------

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"
DATA_API = "https://www.googleapis.com/youtube/v3"
UPLOAD_API = "https://www.googleapis.com/upload/youtube/v3"
ANALYTICS_API = "https://youtubeanalytics.googleapis.com/v2"
REPORTING_API = "https://youtubereporting.googleapis.com/v1"

# Giriş: sadece kimlik (e-posta, ad, fotoğraf).
LOGIN_SCOPES = ["openid", "email", "profile"]

# Kanal bağlama: SALT OKUNUR. Analiz için yeterli; kullanıcıya güven verir ve Google
# doğrulamasını kolaylaştırır.
CHANNEL_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
if os.environ.get("YTHUB_MONETARY") == "1":
    CHANNEL_SCOPES.append("https://www.googleapis.com/auth/yt-analytics-monetary.readonly")

# Kapak/banner değiştirmek için ek izin — sadece kullanıcı bu özelliği kullanmak
# istediğinde ayrıca istenir.
WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"

# "Google ile devam et": giriş + kanal onayı TEK ekranda. Google aynı akışta hesabı ve
# YouTube kanalını seçtirir; giriş biter bitmez kanal bağlanmış olur.
SIGNIN_SCOPES = LOGIN_SCOPES + CHANNEL_SCOPES
SCOPES = CHANNEL_SCOPES  # geriye uyum

# Data API v3 birim maliyetleri (docs: determine_quota_cost). Günlük varsayılan
# kota proje başına 10.000 birim, Pasifik saatiyle gece yarısı sıfırlanır.
# Google bu tabloyu değiştirebilir; panel sadece TAHMİNİ harcamayı gösterir,
# gerçek değer Google Cloud Console > Quotas ekranındadır.
DAILY_QUOTA = 10_000
QUOTA_COST = {
    "channels.list": 1,
    "playlistItems.list": 1,
    "videos.list": 1,
    "search.list": 100,
    "videos.update": 50,
    "thumbnails.set": 50,
    "channelBanners.insert": 50,
    "channels.update": 50,
    "watermarks.set": 50,
}

# ----------------------------------------------------------------------------
# GÖRSEL KURALLARI
# ----------------------------------------------------------------------------

# thumbnails.set üst sınırı 2026-09'da 2 MB'tan 50 MB'a çıktı. Kanal doğrulanmamışsa
# (telefon doğrulaması) YouTube özel kapak kabul etmez — bu bir API sınırı değil.
THUMB_MAX_BYTES = 50 * 1024 * 1024
THUMB_MIN_WIDTH = 640
THUMB_TYPES = ("image/jpeg", "image/png")

# Kanal banner'ı: en az 2048x1152, önerilen 2560x1440, en fazla 6 MB.
BANNER_MAX_BYTES = 6 * 1024 * 1024
BANNER_MIN_SIZE = (2048, 1152)

# ----------------------------------------------------------------------------
# SENKRONİZASYON
# ----------------------------------------------------------------------------

# Analytics API'den geriye dönük kaç gün çekilsin. Veri ~2-3 gün gecikmeli gelir.
# 400 gün: 90 günlük dönemi önceki 90 günle ve geçen yılla kıyaslamaya yeter.
ANALYTICS_DAYS = 400

# Panelin dönem seçenekleri. Her senkronda her dönem için en iyi videolar ve
# kırılımlar (trafik kaynağı, içerik türü, ülke) ayrıca çekilir.
WINDOWS = (7, 28, 90)
TOP_VIDEOS_PER_WINDOW = 50   # kanal başına, dönem başına (API üst sınırı 200)
TOP_COUNTRIES = 10

# Temel günlük kanal metrikleri. Her kanal için geçerlidir.
ANALYTICS_METRICS = [
    "views", "estimatedMinutesWatched", "averageViewDuration",
    "subscribersGained", "subscribersLost", "likes", "comments", "shares",
]
# 2026-01-15'te eklenen kapak gösterimi metrikleri. Desteklenmezse sistem bunları
# atlayıp temel metriklerle devam eder.
ANALYTICS_REACH_METRICS = ["videoThumbnailImpressions", "videoThumbnailImpressionsClickRate"]

# Dönemin en iyi videoları raporu (dimensions=video). Desteklenmezse kısa listeye düşülür.
TOP_VIDEO_METRICS = [
    "views", "estimatedMinutesWatched", "averageViewDuration", "averageViewPercentage",
    "subscribersGained", "likes", "comments", "shares",
]
TOP_VIDEO_METRICS_FALLBACK = ["views", "estimatedMinutesWatched", "averageViewDuration"]

# Kırılımlar: boyut -> (metrikler, sıralama, en fazla satır)
BREAKDOWNS = {
    "insightTrafficSourceType": ["views", "estimatedMinutesWatched"],
    "creatorContentType": ["views", "estimatedMinutesWatched"],
    "country": ["views", "estimatedMinutesWatched"],
}

# Shorts için API'de bir bayrak yok. Süre bu eşiğin altındaysa "muhtemelen Shorts"
# sayılır (Shorts 2024-10'dan beri 3 dakikaya kadar olabiliyor). Kesin değildir.
SHORTS_MAX_SECONDS = 180

# ----------------------------------------------------------------------------
# REPORTING API (toplu günlük CSV raporları)
# ----------------------------------------------------------------------------

# Rapor işi bir kez oluşturulur; YouTube o günden itibaren her gün bir rapor üretir
# ve işin oluşturulmasından önceki 30 günü de geriye dönük doldurur. Raporlar
# 30-60 gün indirilebilir kalır — bu yüzden düzenli senkron önemli.
# Önek eşleşmesi: YouTube yeni sürüm çıkarırsa (a3 → a4) en yenisi seçilir.
REPORT_TYPE_PREFIXES = {
    "basic": "channel_basic_a",        # video × gün: izlenme, süre, beğeni, abone ±
    "reach": "channel_reach_basic_a",  # video × gün: kapak gösterimi, tıklama oranı
}

HTTP_TIMEOUT = 60
