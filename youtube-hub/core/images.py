"""
Görsel doğrulama — YouTube'a göndermeden ÖNCE.

Reddedilecek bir dosyayı yüklemek 50 birim kota yakar. Bu modül türü, boyutu ve
çözünürlüğü yerelde kontrol eder (Pillow gerekmez, dosya başlığını okur).
"""

import struct

from . import config


class ImageRejected(ValueError):
    pass


def sniff(data):
    """(mime, genişlik, yükseklik) veya ImageRejected."""
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        w, h = struct.unpack(">II", data[16:24])
        return "image/png", w, h
    if data[:2] == b"\xff\xd8":
        return ("image/jpeg",) + _jpeg_size(data)
    raise ImageRejected("Sadece JPG veya PNG kabul ediliyor.")


def _jpeg_size(data):
    i = 2
    n = len(data)
    while i + 9 < n:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7 or marker == 0xFF:
            i += 1 if marker == 0xFF else 2
            continue
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        # SOF0..SOF15 (DHT=C4, JPG=C8, DAC=CC hariç) çözünürlüğü taşır
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        i += 2 + seg_len
    raise ImageRejected("JPG dosyası okunamadı (bozuk olabilir).")


def check_thumbnail(data, is_short=False):
    """Kapak için doğrula. Dönen: {mime, width, height, warnings[]}"""
    if len(data) > config.THUMB_MAX_BYTES:
        raise ImageRejected(f"Dosya {len(data) // (1024 * 1024)} MB; sınır "
                            f"{config.THUMB_MAX_BYTES // (1024 * 1024)} MB.")
    mime, w, h = sniff(data)
    warnings = []
    if is_short:
        # Shorts: 9:16, en kısa kenar >= 640 önerilir.
        if min(w, h) < config.THUMB_MIN_WIDTH:
            raise ImageRejected(f"Çözünürlük {w}x{h}; en kısa kenar en az {config.THUMB_MIN_WIDTH} px olmalı.")
        if abs(w / h - 9 / 16) > 0.02:
            warnings.append(f"{w}x{h} dikey 9:16 değil; Shorts kapağında kırpılabilir.")
        warnings.append("Shorts: bu kapak arama/kanal sayfasında görünür, Shorts rafındaki "
                        "dikey görseli API değiştiremez.")
    else:
        if w < config.THUMB_MIN_WIDTH:
            raise ImageRejected(f"Genişlik {w} px; en az {config.THUMB_MIN_WIDTH} px olmalı.")
        if abs(w / h - 16 / 9) > 0.02:
            warnings.append(f"{w}x{h} 16:9 değil; YouTube kenarlara siyah bant ekleyebilir.")
        if w < 1280:
            warnings.append("1280x720 veya üstü önerilir.")
    return {"mime": mime, "width": w, "height": h, "warnings": warnings}


def check_banner(data):
    if len(data) > config.BANNER_MAX_BYTES:
        raise ImageRejected(f"Banner en fazla {config.BANNER_MAX_BYTES // (1024 * 1024)} MB olabilir.")
    mime, w, h = sniff(data)
    mw, mh = config.BANNER_MIN_SIZE
    if w < mw or h < mh:
        raise ImageRejected(f"Banner {w}x{h}; en az {mw}x{mh} olmalı (önerilen 2560x1440).")
    warnings = []
    if abs(w / h - 16 / 9) > 0.02:
        warnings.append("16:9 değil; YouTube kırpacak.")
    warnings.append("Tüm cihazlarda görünen güvenli alan ortadaki 1546x423 px.")
    return {"mime": mime, "width": w, "height": h, "warnings": warnings}
