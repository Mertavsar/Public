"""
Google OAuth 2.0 (PKCE) — iki ayrı amaç:

  login   → "Google ile giriş": sadece kimlik (e-posta, ad, fotoğraf). Hesap yoksa açılır.
  channel → "Kanal ekle": seçilen YouTube kanalına salt okunur erişim (refresh token).
            Google'ın hesap seçicisi, hesaptaki kanalları (marka hesapları dahil) listeler;
            seçilen kanal token'a bağlanır. YouTube API tek onayla bir hesaptaki TÜM
            kanalları vermez — her kanal bir kez seçilir.

Yerel modda istemci türü "Desktop app" (loopback), sunucuda "Web application"
(kayıtlı yönlendirme adresi) olmalıdır.
"""

import base64
import hashlib
import json
import os
import secrets
import threading
import time
import urllib.parse

from . import config
from .api import parse_error, urllib_transport


class AuthRevoked(Exception):
    """Kullanıcı erişimi kaldırdı veya refresh_token geçersiz → yeniden bağlanmalı."""


class SetupMissing(Exception):
    pass


def load_client(path=None):
    path = path or config.CLIENT_SECRET_PATH
    if not os.path.isfile(path):
        raise SetupMissing(
            f"OAuth istemci dosyası yok: {path}\n"
            "Google Cloud Console > APIs & Services > Credentials > Create credentials > "
            "OAuth client ID > Desktop app. İndirdiğin JSON'u bu yola kaydet.")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    block = raw.get("installed") or raw.get("web") or raw
    return {"client_id": block["client_id"], "client_secret": block.get("client_secret", "")}


def save_client(raw, path=None):
    """Kurulum sayfasından yüklenen OAuth istemci JSON'unu doğrulayıp kaydeder."""
    path = path or config.CLIENT_SECRET_PATH
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise ValueError("Dosya JSON değil. Google Cloud'dan indirdiğin client_secret dosyasını seç.")
    if not isinstance(data, dict):
        raise ValueError("Bu dosya bir OAuth istemci dosyası değil (client_id bulunamadı).")
    kind = "installed" if data.get("installed") else "web" if data.get("web") else None
    if not kind:
        raise ValueError("Bu dosya bir OAuth istemci dosyası değil (client_id bulunamadı).")
    if kind == "web" and not config.PUBLIC_URL:
        raise ValueError("Bu bir 'Web application' istemcisi. Yerel kullanımda Google Cloud'da "
                         "Application type olarak 'Desktop app' seçip yeni istemci oluştur.")
    block = data[kind]
    if not str(block.get("client_id", "")).endswith(".apps.googleusercontent.com"):
        raise ValueError("client_id geçersiz görünüyor.")
    if not block.get("client_secret"):
        raise ValueError("Dosyada client_secret yok.")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({kind: block}, f)
    return block["client_id"]


def id_claims(token):
    """Token yanıtındaki id_token'ın içeriği (e-posta, ad...). id_token doğrudan Google'ın
    token uç noktasından HTTPS ile alındığı için imza doğrulaması gerekmez."""
    raw = token.get("id_token")
    if not raw or raw.count(".") != 2:
        raise ValueError("Google kimlik bilgisi (id_token) dönmedi.")
    payload = raw.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    claims = json.loads(base64.urlsafe_b64decode(payload))
    if not claims.get("sub") or not claims.get("email"):
        raise ValueError("Google hesabının e-posta bilgisi alınamadı.")
    return claims


def _form_post(url, fields, transport):
    body = urllib.parse.urlencode(fields).encode()
    status, _, raw = transport("POST", url, {"Content-Type": "application/x-www-form-urlencoded"}, body)
    if not 200 <= status < 300:
        raise parse_error(status, raw)
    return json.loads(raw) if raw else {}


# ----------------------------------------------------------------------------
# ONAY AKIŞI
# ----------------------------------------------------------------------------

_PENDING = {}            # state -> (verifier, redirect_uri, created)
_PENDING_LOCK = threading.Lock()
_PENDING_TTL = 600


def start_flow(redirect_uri, scopes=None, purpose="channel", ctx=None, login_hint=None,
               client=None):
    """Onay adresini ve `state`'i döner. state tarayıcı çerezine de yazılmalı (giriş CSRF'i)."""
    client = client or load_client()
    state = secrets.token_urlsafe(24)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    with _PENDING_LOCK:
        cutoff = time.time() - _PENDING_TTL
        for k in [k for k, v in _PENDING.items() if v["created"] < cutoff]:
            del _PENDING[k]
        _PENDING[state] = {"verifier": verifier, "redirect_uri": redirect_uri, "created": time.time(),
                           "purpose": purpose, "ctx": ctx}
    params = {
        "client_id": client["client_id"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes or (config.LOGIN_SCOPES if purpose == "login" else config.CHANNEL_SCOPES)),
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "include_granted_scopes": "true",
    }
    if purpose == "login":
        params["prompt"] = "select_account"
    else:
        params["access_type"] = "offline"             # refresh_token için şart
        params["prompt"] = "consent select_account"   # her seferinde kanal seçtir
    if login_hint:
        params["login_hint"] = login_hint
    return f"{config.AUTH_URL}?{urllib.parse.urlencode(params)}", state


def finish_flow(state, code, client=None, transport=None):
    """Dönen: (token, amaç, bağlam)."""
    with _PENDING_LOCK:
        entry = _PENDING.pop(state, None)
    if not entry or time.time() - entry["created"] > _PENDING_TTL:
        raise ValueError("Geçersiz veya süresi dolmuş onay isteği. Yeniden dene.")
    client = client or load_client()
    tok = _form_post(config.TOKEN_URL, {
        "code": code,
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "redirect_uri": entry["redirect_uri"],
        "grant_type": "authorization_code",
        "code_verifier": entry["verifier"],
    }, transport or urllib_transport)
    if entry["purpose"] == "channel" and "refresh_token" not in tok:
        raise ValueError("Google refresh_token vermedi. myaccount.google.com/permissions "
                         "üzerinden uygulamanın erişimini kaldırıp yeniden dene.")
    return tok, entry["purpose"], entry["ctx"]


# ----------------------------------------------------------------------------
# TOKEN
# ----------------------------------------------------------------------------

class Credentials:
    """Bir kanalın token'ı. access_token gerektikçe yenilenir ve `save` ile saklanır."""

    def __init__(self, refresh_token, access_token=None, expires_at=0, save=None,
                 client=None, transport=None):
        self.refresh_token = refresh_token
        self._access = access_token
        self._expires = expires_at or 0
        self._save = save or (lambda access, expires: None)
        self._client = client
        self._transport = transport or urllib_transport
        self._lock = threading.Lock()

    def access_token(self, force_refresh=False):
        with self._lock:
            if force_refresh or not self._access or time.time() > self._expires - 60:
                self._refresh()
            return self._access

    def _refresh(self):
        client = self._client or load_client()
        try:
            tok = _form_post(config.TOKEN_URL, {
                "refresh_token": self.refresh_token,
                "client_id": client["client_id"],
                "client_secret": client["client_secret"],
                "grant_type": "refresh_token",
            }, self._transport)
        except Exception as e:
            if getattr(e, "reason", "") == "invalid_grant":
                raise AuthRevoked("Kanalın erişimi geçersiz; panelden yeniden bağla.") from e
            raise
        self._access = tok["access_token"]
        self._expires = int(time.time()) + int(tok.get("expires_in", 3600))
        self._save(self._access, self._expires)


def revoke(token, transport=None):
    try:
        _form_post(config.REVOKE_URL, {"token": token}, transport or urllib_transport)
    except Exception:
        pass  # zaten geçersizse sorun değil; yerel kayıt yine silinir
